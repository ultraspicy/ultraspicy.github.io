---
title: How to design a workflow orchestration framework (Temporal.io)
description: understand workflow primitives and how to use them
pubDate: 1970-10-22
tags: [backend]
draft: true
---

Workflow orchetration is one of the most frequent recurring software engineering problem. Workflow is meta abstraction of any complex business process that involves in multiple steps and may span into hours even months. And this concept is extremely useful in builing agentic serivce, since all tasks can be abstracted as a workflow. Here are some concrete example examples:
 - UberEats uses workflow to manage the lifecycle of a delivery order.
 - Online shopping wraps {reserve, charge, email} into a workflow.
 - As soon as an agent join meeting, it kicks off the workflow. Every activities like taking notes, summerize insights, taking action

So we need to build a plafform to run scalable, fault-tolerant, and long-running workflows.

Scalable means we should be able to horizontally scale the platform capacity, fault tolerant means we need to auto-recover from failure during the life cycle of the workflow.

Overall Design
 - Asbut
 - administrative task: the task to move workflow forward. This task doesn't do any real work like I/O, API call, but just focus on tracking the progress of workflow by running workflow code up to the next blocking point.
 - activity task: run certain activity function with certain input. The worker runs activity code and replies with the result or failure. Activity tasks can be paralleled

A toy example:
