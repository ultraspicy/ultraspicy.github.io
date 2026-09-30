---
title:  Key ML/LLM concepts (WIP)
description: core concepts beofore you entering the LLM world
pubDate: 2026-09-29
tags: [ML]
draft: false
---

This article is just a copy of my daily notes, so it may not be well-structured.

## Meta
**Training**: optimize the loss, given (prompt, response, reward)

Overall there are four layers accross the stack
 - layer 1: Tensor/autograd framework (Tensorflow, Pytorch), it provides numeric and matrix multiplication capabilites
 - layer 2: traning liraries (HuggingFace, Megatron FSDP)
 - layer 3: inference engine (SGLang, vLLM)
 - layer 4: post training orchestration (Miles)

**Policy**: The model being trained, acting = generating text
**Rollout**: letting the current policy act and record what happens

Model training then can be simplified as [todo: add diagram] rollout-> Reward -> Advantage -> weight sync and weight update -> other rollout -> ...

From input and output perspective
 - rollout: input -> generated response
 - Reward: generated response -> scalar
 - advantage: scalar -> group-relative training signal
 - update: advantage -> weight change

We use "rollout engine" and "inference engine" interchangably. Given the size of current model, we need a group of GPU (abstracted as placement group, shorted as PG) to host. Couple of options for parallelism
 - PP: pipeline parallelism, split the model by depth
 - EP: expert parallelism, split one layer's expert accross GPUs
 - TP: tensor parallelism, split one big matrix (expensive, better done within a single node)
 - DP: data parallelism, splits requests and host couple of same copies of model to scale the throughput of interfere cluster.
 - CP: context parllelism, splits the sequence across GPUs. Each GPU handles a different chunk of the tokens.

**Training is homogeneous, but rollout is heterougeneous**
 - Megatron traning job is a signle Single-Program-Multiple-Data(SPMD) collective, model shareded by (TP, DP, PP, CT) and every rank is one cell in that grid. We often use **world_size** to describe model size, where world_size = TP * DP * PP * CT
 - Rollout engine never talks to each out. Each is a standalone server. The more powerful rollout engine is , the higher throughput it could be.

And some data communitation toolbox
 - NCCL: a GPU-to-GPU collective communication library
 - Gloo, a CPU collective library

## LLM

**Embedding** maps each token to a vector that captures aspects of its meaning. As a degenerate case, imagine a vocabulary of just (Y, N): a single bit 1/0 is enough to tell them apart, and there is no further meaning to capture. Real vocabularies are different. Words like "dog", "eat", and "love" have rich, overlapping properties: "dog" is a noun, "eat" is a verb, and "love" can be either.

As an idealized picture, we can imagine each dimension of the embedding vector answering one question about the word. If dimension $i$ encodes "is it a verb?", then $e_i(\text{eat})$ would be large, $e_i(\text{dog})$ small, and $e_i(\text{love})$ somewhere in between, since a single fixed vector must represent both of its senses. (Resolving which sense is meant in a given sentence is the job of later layers, such as attention.)

In practice, learned embeddings don't align features with individual axes. Features correspond to *directions* in the space, and it helps when different features point in nearly orthogonal directions, so that changing one, like "is it a verb", doesn't disturb another, like "is it positive or negative". High-dimensional spaces make this easy: they contain far more nearly orthogonal directions than their dimensions.

**Attention** is how we enrich each token's representation with context. Essentially, it is a soft lookup: for each token $i$, we build a query $q_i$, compare it against the key $k_j$ of every token $j$, turn the scores into weights, and output the weighted sum of all tokens' values.

We fix $W_q$, $W_k$, and $W_v$ as learned projections that map a token vector $x$ to its query, key, and value:

$$
q = xW_q, \qquad k = xW_k, \qquad v = xW_v
$$

This simple equation has some meaning behind it:

 - $q$ is a query, what this token is looking for.
 - $k$ is a key, what this token advertises about itself.
 - $v$ is a value, what this token actually hands over once it's been selected.

Stacking the vectors of all $n$ tokens as rows gives matrices $Q$, $K$, and $V$. The simplest version of attention uses the raw scores directly as weights:

$$
\text{SimpleAttention}(Q, K, V) = QK^{\top} V
$$

 - $QK^{\top}$ is an $n \times n$ table of scores: entry $(i, j)$ is $q_i \cdot k_j$, how well token $j$'s key matches token $i$'s query.
 - $QK^{\top} V$ then gives each token $i$ a new representation: the sum of all tokens' values $v_j$, weighted by those scores.

In practice, we use

$$
\text{Attention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
$$

The softmax (applied to each row) turns scores into proper weights, positive and summing to 1, so each output is an average of values. Dividing by $\sqrt{d_k}$ keeps the scores from growing with the dimension, which would otherwise saturate the softmax and make gradients vanish.

**Causal Attention** follows the same equation above, but masks out every score where a token would look at a later position. Before the softmax, we add a mask $M$ that sets all entries above the diagonal to $-\infty$:

$$
M_{ij} = \begin{cases} 0 & j \le i \\ -\infty & j > i \end{cases}
\\
\text{CausalAttention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}} + M\right)V
$$

Since $e^{-\infty} = 0$, each token $i$ gives zero weight to every future token, and the softmax renormalizes the remaining weights over positions $1, \dots, i$. This mimics autoregressive generation, where the model only ever sees the text produced so far.

Without the mask, the model could simply attend to position $i+1$ and copy the very token it is supposed to predict. Training loss would collapse, but the model would learn nothing useful, since at generation time the future doesn't exist yet.

### Inference
Inference can be simplified as one prefill followed by many decode steps. The full pipeline is: request → API server → tokenizer → scheduler → prefill → (many rounds of) decode → detokenizer → API server → response. [todo:add diagram] In practice, detokenization runs incrementally so tokens can be streamed back as they are generated.

**Prefill**: The prompt arrives all at once, say 2000 tokens. The model runs a single forward pass over all 2000 tokens in parallel: at each layer it computes $(Q, K, V)$, performs full causal attention, and writes the 2000 pairs $(k_i, v_i)$ into the KV cache. The pass produces logits at every position, but only those at the last position are used, to sample the first generated token. Because every matmul has thousands of rows, prefill is compute-bound.

**Decode**: Every subsequent step processes exactly one new token per sequence. At each layer, it computes that token's $(q, k, v)$, appends $(k, v)$ to the cache, and attends against everything cached; the final logits are then sampled to produce the next token. Decode is memory-bound: producing one token requires reading all the weights and the sequence's entire KV cache, while the arithmetic is tiny.

To make better use of the GPU, we batch many sequences' decode steps together. This amortizes the weight reads, since all sequences share the same weights. The KV cache, however, is per sequence and cannot be shared, so for long contexts it dominates memory traffic and limits how large the batch can be. Modern schedulers use continuous batching: new requests' prefills are mixed in with ongoing decodes, and finished sequences leave the batch immediately. We will have a separate article talking about how continuous batching works in detail.

And some techincal terms that is useful when exploring source code:

**Rank**: a rank is the ID number of one process in a distributed job. Rank fundamentally identifies a process, so same code, different rank, dfferent behavior.

**Ray**: a distributed-compute layer that gives you a single logical scheduler over a mixed CPU/GPU fleet. It either assumes that fleet already exists or get it from something like k8s underneath.

**Ray actor/Task**: ray actor is a python class that runs in its own worker process, usually on a remote machine in a cluster, and keep state between calls. It's Ray's building block for long lived stateful services. Ray task is stateless function call. It sends inputs, get outputs, and nothing persist. An actor is created once, holds thing in memory, and answer method calls for as long as it lives.

**Placement_group**: a reservation of one or more bundles, where each bundle is a set of resources that Ray guarentees can be placed together according to a strategy.
