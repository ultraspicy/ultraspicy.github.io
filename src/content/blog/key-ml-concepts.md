---
title:  LLM Architecture and Terminogies Overview
description: core concepts beofore you entering the LLM world
pubDate: 2026-09-29
tags: [ML]
draft: false
---

## Terminogies
**Training**: optimize the loss, given (prompt, response, reward)

Overall there are four layers accross the stack
 - layer 1: Tensor/autograd framework (Tensorflow, Pytorch), it provides numeric and matrix multiplication capabilites
 - layer 2: traning liraries (HuggingFace, Megatron FSDP)
 - layer 3: inference engine (SGLang, vLLM)
 - layer 4: post training orchestration (Miles)

**Policy**: The model being trained, acting = generating text

**Rollout**: letting the current policy act and record what happens

**logits** are raw, unnormalized screos over the vocabulary, before softmax turns them into probabilities.

**FFN** stands for Feed-forward network. The information flows in one direction, from input to output without loop. The typology of such is a DAG.

**MLP** stands for multi-layer perception. It is built from dense layer plus activations, a specific architecture of FFN.

**Host memory**: system Ram, attached to CPU

**Device memory**: VRAM/HBM on the GPU card. "staging through host memory" means GPU A copies data up to system RAM over PCIe then GPU B copies it back down over PCIe.

**Scheduler**: a scheduler is the component that decides which work runs on which machines, and when. It sits between the task and hardware. Every scheduler answers the same three questions
 - Placement: which node or worker has the resources this task asked for. Ray uses placement_group
 - Ordering: when several task are waiting, which goes first
 - Constraints: rules beyond resources, such as "keep these actor on the same node" or "speed them accross nodes". Ray uses scheduling_stragety

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

## LLM Architecture

### **Embedding**
maps each token to a vector that captures aspects of its meaning. As a degenerate case, imagine a vocabulary of just (Y, N): a single bit 1/0 is enough to tell them apart, and there is no further meaning to capture. Real vocabularies are different. Words like "dog", "eat", and "love" have rich, overlapping properties: "dog" is a noun, "eat" is a verb, and "love" can be either.

As an idealized picture, we can imagine each dimension of the embedding vector answering one question about the word. If dimension $i$ encodes "is it a verb?", then $e_i(\text{eat})$ would be large, $e_i(\text{dog})$ small, and $e_i(\text{love})$ somewhere in between, since a single fixed vector must represent both of its senses. (Resolving which sense is meant in a given sentence is the job of later layers, such as attention.)

In practice, learned embeddings don't align features with individual axes. Features correspond to *directions* in the space, and it helps when different features point in nearly orthogonal directions, so that changing one, like "is it a verb", doesn't disturb another, like "is it positive or negative". High-dimensional spaces make this easy: they contain far more nearly orthogonal directions than their dimensions. Using Google's Word2Vec as an example

$$
\vec{v}_{\text{love}} = \begin{bmatrix} -0.05371 & 0.03857 & 0.08349 & \dots & -0.00705 \end{bmatrix} \in \mathbb{R}^{1 \times 300}
$$

### **Attention**
is how we enrich each token's representation with context. Essentially, it is a soft lookup: for each token $i$, we build a query $q_i$, compare it against the key $k_j$ of every token $j$, turn the scores into weights, and output the weighted sum of all tokens' values.

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

### **Causal Attention**
follows the same equation above, but masks out every score where a token would look at a later position. Before the softmax, we add a mask $M$ that sets all entries above the diagonal to $-\infty$:

$$
M_{ij} = \begin{cases} 0 & j \le i \\ -\infty & j > i \end{cases}
\\
\text{CausalAttention}(Q, K, V) = \text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}} + M\right)V
$$

Since $e^{-\infty} = 0$, each token $i$ gives zero weight to every future token, and the softmax renormalizes the remaining weights over positions $1, \dots, i$. This mimics autoregressive generation, where the model only ever sees the text produced so far.

Without the mask, the model could simply attend to position $i+1$ and copy the very token it is supposed to predict. Training loss would collapse, but the model would learn nothing useful, since at generation time the future doesn't exist yet.

### **MLP**
is where per-token nonlinear feature transformation happens. It is just the equation
$$
\text{MLP}(x) = \big( \sigma(x \cdot W_{gate}) \odot (x \cdot W_{up}) \big) \cdot W_{down}
$$
The activation $\sigma$ is the nonlinearity. $W_{gate}$ decides which hidden units pass through for a given token.  $W_{up}$ and $W_{gate}$ both project into a wider hidden space of size $h$, so the block has many independent nonlinear units. $W_{down}$ projects back to $d$. Conceptually, the MLP is a per-token attention over $h$ learned memory slots (without softmax): $x$ is the query, the column of $W_{gate}$ and $W_{up}$ are keys, the gated product $\sigma(W_{gate}x) \odot (W_{up}x)$ gives each slot's weight, and the rowss of $W_{down}$ are the values that get summed into the output.

### **Transformer block(single-head)**
can be simplified as one attention + one MLP.
$$
h_{simple} = x + \text{Attention}(x)
\\
\text{Transformer}_{simple}(x) = h_{simple} + \text{MLP}(h_{simple})
$$
Interpretation: for current token, attention enriches its contextual meaning via attention layer, the MLP takes over from this contextual-rich representation and transform its meaning. The residual add both attention and MLP over the input, so the final output cover its original meaning, contextual info, and features derived from both. In real world scenario, for faster coverging and numeric stability, we add normalziation
$$
h = x + \text{Attention}\big(\text{Norm}(x)\big)
\\
\text{Transformer}(x) = h + \text{MLP}\big(\text{Norm}(h)\big)
$$

### **Transformer(single-head)**
Using above as the building block, a transformer is a stacked such block. For example, input prompt with 100 words, using an embedding of 300 dimension, text will be encoded as the input $X_{(100,300)}^{(0)}$. Then go through the first transformer block as follows
$$
H^{(1)} = X^{(0)} + \text{Attention}^{(1)}\big(\text{Norm}(X^{(0)})\big)
\\
X^{(1)} = \text{Transformer}^{(1)}(X^{(0)}) = H^{(1)} + \text{MLP}^{(1)}\big(\text{Norm}(H^{(1)})\big)
$$
then following the second tranformer block
$$
H^{(2)} = X^{(1)} + \text{Attention}^{(2)}\big(\text{Norm}(X^{(1)})\big)
\\
X^{(2)} = \text{Transformer}^{(2)}(X^{(1)}) = H^{(2)} + \text{MLP}^{(2)}\big(\text{Norm}(H^{(2)})\big)
$$
until the very last layer. Note the output of final layer $X^{(n)}$ has shape (seq_len, hidden) same as input. The final step is to convert $X^{(n)}$ to logits by
$$
\text{logits} = \text{Norm}_{\text{final}}\big(X^{(n)}\big)\, W_{out}^{\top} \in \mathbb{R}^{(\text{seq\_len},\ \text{vocab})}
$$

If we are in autoregressive generation, then sample the next token via the last row $z$ of logits
$$
p_v = \frac{\exp(z_v / T)}{\sum_{u=1}^{|V|} \exp(z_u / T)}
$$
where T is the temperature.

The above is an oversimplified illustration that ignores details such as normalization choices, activation functions and their mathematical implications, sampling strategies, and how multi-head attention works. These will be covered in "Attention at Its Finest".

## Inference
Inference can be simplified as one prefill followed by many decode steps. The full pipeline is: request → API server → tokenizer → scheduler → prefill → (many rounds of) decode → detokenizer → API server → response. [todo:add diagram] In practice, detokenization runs incrementally so tokens can be streamed back as they are generated.

### **Prefill**
The prompt arrives all at once, say 2000 tokens. The model runs a single forward pass over all 2000 tokens in parallel: at each layer it computes $(Q, K, V)$, performs full causal attention, and writes the 2000 pairs $(k_i, v_i)$ into the KV cache. The pass produces logits at every position, but only those at the last position are used, to sample the first generated token. Because every matmul has thousands of rows, prefill is compute-bound.

### **Decode**
Every subsequent step processes exactly one new token per sequence. At each layer, it computes that token's $(q, k, v)$, appends $(k, v)$ to the cache, and attends against everything cached; the final logits are then sampled to produce the next token. Decode is memory-bound: producing one token requires reading all the weights and the sequence's entire KV cache, while the arithmetic is tiny.

To make better use of the GPU, we batch many sequences' decode steps together. This amortizes the weight reads, since all sequences share the same weights. The KV cache, however, is per sequence and cannot be shared, so for long contexts it dominates memory traffic and limits how large the batch can be. Modern schedulers use continuous batching: new requests' prefills are mixed in with ongoing decodes, and finished sequences leave the batch immediately. We will have a separate article talking about how continuous batching works in detail.

### **techincal terms**

**Rank**: a rank is the ID number of one process in a distributed job. Rank fundamentally identifies a process, so same code, different rank, dfferent behavior.

**Ray**: a distributed-compute layer that gives you a single logical scheduler over a mixed CPU/GPU fleet. It either assumes that fleet already exists or get it from something like k8s underneath.

**Ray actor/Task**: ray actor is a python class that runs in its own worker process, usually on a remote machine in a cluster, and keep state between calls. It's Ray's building block for long lived stateful services. Ray task is stateless function call. It sends inputs, get outputs, and nothing persist. An actor is created once, holds thing in memory, and answer method calls for as long as it lives.

**Placement_group**: a reservation of one or more bundles, where each bundle is a set of resources that Ray guarentees can be placed together according to a strategy.

## GPU

**Collective**: is a communication pattern that a whole group of participants executes together, as opposed to point to point communication where one sender talks to one receiver. It is commonly used in all-reduce contract, a contract that everyone gets the reduced result.
