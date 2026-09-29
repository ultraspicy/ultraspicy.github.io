---
title:  Key ML concepts when building LLMs (WIP)
description: core concepts beofore you entering the LLM world
pubDate: 2026-09-15
tags: [ML]
draft: false
---

## Meta
Training: optimize the loss, given (prompt, response, reward)

Overall there are four layers accross the stack
 - layer 1: Tensor/autograd framework (Tensorflow, Pytorch), it provides numeric and matrix multiplication capabilites
 - layer 2: traning liraries (HuggingFace, Megatron FSDP)
 - layer 3: inference engine (SGLang, vLLM)
 - layer 4: post training orchestration (Miles)

Policy: The model being trained, acting = generating text
Rollout: letting the current policy act and record what happens

Model training then can be simplified as rollout-> Reward -> Advantage -> weight sync and weight update -> other rollout -> ...

From input and output perspective
 - rollout: input -> generated response
 - Reward: generated response -> scalar
 - advantage: scalar -> group-relative training signal
 - update: advantage -> weight change

We use "rollout engine" and "inference engine" interchangably. Given the size of current model, we need a group of GPU (called placement group, shorted as PG) to host. Couple of options for parallelism
 - PP: pipeline parallelism, split the model by depth
 - EP: expert parallelism, split one layer's expert accross GPUs
 - TP: tensor parallelism, split one big matrix (expensive, better done within a single node)
 - DP: data parallelism, splits requests and host couple of same copies of model to scale the throughput of interfere cluster.
 - CP: context parllelism, splits the sequence across GPUs. Each GPU handles a different chunk of the tokens.
  
And data communitation toolbox  
 - NCCL: a GPU-to-GPU collective communication library
 - Gloo, a CPU collective library

## LLM 
**Training is homogeneous, but rollout is heterougeneous**
 - Megatron traning job is a signle Single-Program-Multiple-Data collective, model shareded by (TP, DP, PP, CT) and every rank is one cell in that grid. We often use **world_size** to describe model size, where world_size = TP * DP * PP * CT
 - Rollout engine never talks to each out. Each is a standalone server.


### Inference
**Rank**: a rank is the ID number of one process in a distributed job. Rank fundamentally identifies a process, so same code, different rank, dfferent behavior.
**Ray**: a distributed-compute layer that gives you a single logical scheduler over a mixed CPU/GPU fleet. It either assumes that fleet already exists or get it from something like k8s underneath.
**Ray actor/Task**: ray actor is a python class that runs in its own worker process, usually on a remote machine in a cluster, and keep state between calls. It's Ray's building block for long lived stateful services. Ray task is stateless function call. It sends inputs, get outputs, and nothing persist. An actor is created once, holds thing in memory, and answer method calls for as long as it lives.
**Placement_group**: a reservation of one or more bundles, where each bundle is a set of resources that Ray guarentees can be placed together according to a strategy.

