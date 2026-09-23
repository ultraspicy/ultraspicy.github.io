---
title: Eventual Consistent Consumers
description: How to let consumers eventually converge to its producer 
pubDate: 2026-09-23
tags: [backend, core]
draft: false
---

## Introduction 
Building a consistent state downstream is one of the most common pipeline tasks. This problem can be abstracted as as the following diagram 

Source system (DB) -> CDC producer -> Kafka broker -> consumer (Flink, Hive, another DB, workflows)

The goal is for the consumer to converge to the same state as the source. 

## How consumer converge to its producer
The first question we ask is, “what makes the consumer not converge?”. Most common discrepancies are 
 - Producer emits duplicated events for one source change.
 - Consumers process messages in different order, so an early message is taken as the latest one.
 - It is also possible that the producer's change is not populated. This can be easily mitigated by the CDC enforcing at-least-once semantics for producer.

Based on that, we design the pipeline to be 
 - The consumer keeps the latest accepted state per entity together with a mark. A mark is a data structure that carries different keys describing when the event is produced from different perspectives. Only events with a higher mark will be applied. From this we build an eventual consistency between the source system and consumer
 - Every message carries the full state of the entity, instead of a delta. By this design, we don’t have to aggregate a list of events to construct the incoming entity, and the comparison between incoming entities and stored entities is greatly simplified and more robust against disordering/ill-formatting. 
 - Anything the consumer emits downstream(a diff or a trigger) is derived by comparing stored entities from consumers (current_state) against the new events(new proposed state). This builds idempotency at the consumer layer, if its upstream doesn’t have this property.

Event Mark carry the following metadata:
 - _offset: Kafka offset, or the source field value when ordering by a source field
 - _partition: Kafka partition, or a sentinel: -1 means "check disabled”
 - _cluster: the cluster or region the consumer read from
 - _ts: producer sequence tokens (timestamp as fallback)
 - _custom_offset, the customized offset populated by producer

With these rules, applying the same message twice is a no-op, and applying two messages in the wrong order still converges to the newest. The core problem now is about choosing the ordering key that defines "newer". We will list out common candidates and their pros/cons. However, there is no silver bullet in the real production system and “what is the newest” needs careful tradeoff by combining several solutions together in a decision tree.

### Ordering options
#### Option1: 
We can use the _partition and _offset, which comes from Kafka Broker. These two fields are always present and offset always strictly increasing. Kafka guarantees the ordering of event consuming will in the same order of offset within a partition, which resolves the message ordering problem on our behalf.  

However, it must take some good assumptions from its producer - producers need to design the partition strategy that all changes within a single entity will go to the same partition. partition count must be treated as frozen/versioned for a keyed topic, and _cluster exists because cross-cluster offsets are never comparable.

#### Option2:
Use the producer's stamp. This is commonly used when CDC events for one entity spread across all partitions. However under this scenario, the consumer is completely at the mercy of its producer’s wellbeing. If the producer's stamping mechanism is skewed, so are consumers. This may sound rare but actually isn’t. 

For example, a common way for producer stamping events is through a Binlog event carrying a unix-second timestamp. However, these ts keep their statement-start stamp, so 
a long statement (bulk update) can therefore commit after a short statement (single-row update). Now the stamp ordering deviates from the commit order.
Unix-second cannot differentiate events within the same second
Primary failover can move the clock. If the new primary’s clock runs two seconds behind then every entity updated in the window around the failover gets a post-failover event that looks older than its pre-failover event, and the consumer drops all of them.

There are indeed some commit-ordered stamping, like GTID sequence numbers and Postgres LSNs are commit-ordered, which is much more favorable.

#### Option3: customized field
Similar to the producer's event timestamp, now we fully rely on the producer to define an offset field for consumers. It shares the same vulnerabilities with option2, but it is extremely useful when backfill and other infra changes. During such a special period,  Option 1 is unavailable and Option 2 is unreliable, and we need to define the semantics of ordering out of the table and let consumers reconstruct a set of entities directly from the source system.

For incoming message m:
  0. No stored mark            -> accept.
  1. m.partition == -1          -> accept. Intentional disable as an operational escape hatch
  2. m.(cluster, partition) == s.(cluster, partition), both real partitions
                                -> m.offset > s.offset: accept
                                   m.offset < s.offset: drop
                                   equal: drop as duplicate
  3. Else, both stamp present, stamps are under same token type and same source epoch
                                -> m.stamp > s.stamp: accept
                                   m.stamp < s.stamp: drop
                                   equal: fall through to 4
  4. Else compare custom_offset field  -> greater accepts, otherwise drop.
                                   Missing on either side:  Exception, emit log metric

During Backfill/Bootstrap, the priority is to fully reconstruct a consumer state consistent with a state of source system at some timestamp, serving as the initial state for all follow-up ingestion. Here we define (cluster = NULL, partition = NULL, stamp = snapshot time,
custom_offset = (if deleted then MAX, otherwise updated_at), so deleted record will not resurrect, and live traffic after a backfill routes to rule 3. 

#### Timestamp as customized offset 
Although we mentioned using timestamp as the custom offset in bootstrap and backfill, we need to be aware that timestamp may silently introduce some inconsistencies for live ingestion, and thus is only good for bootstrap/backfill
 - tombstones. A delete often carries no data column changes. For example, use custom_offset = update_at will capture some deleted records as non-deleted rows.
 - Nulls. Timestamps a lot of times are nullable, we need to define fallback, or some data will be silently dropped.
 - Ties. Some timestamps use a unix second. A second-granularity column cannot correctly identify which is the newest update if multiple transactions happen within the same second.
 - Partial Writes. Bulk fixes, backfills may only update certain columns (ALTER TABLE ) but not touch the column you used.

## Cross-topic dependencies
The above discussion is for single-topic. But what if our consumer needs to build some joint view of multiple topics. For example, on-line stores want to build a joined view of the store and its items, with store update and item update in separate topics. Assume A refers B, we can build forward/reverse path to maintain the joint view as following:
 - Forward path (poll based). An A event arrives, the consumer of A reads the current state of B, and builds the joint view.
 - Reverse path(push based). A B event arrives, the consumer of B looks up every A that references B, and rebuilds all joint views.

But there are some exceptions

### Case1: B doesn’t exist yet 
Build A's view with the B fields empty, persist A, record the missing key, and schedule a delayed retry that rebuilds the view once B is present. B's own arrival also repairs it through the reverse path, whichever comes first. Given the retry from A has a budget (usually a couple of minutes), after the budget is exhausted the hole stays until the next event for either side.

You maybe ask why we need explicitly build forward path, given reverse path will recompute joint view anyways
 - B may never emit an event at all. For example, CDC from B is disabled temporarily.
 - Reverse-path-only has no notion of "how long has this been broken." In cases where B is a dangling reference, like B is deleted, retry from A gives it a bound - after a certain time, we know the joint view cannot be built, log it and potentially trigger an alert.

### Case2 Update race 
An A event sets a reference to B, and B is updated, within milliseconds of each other on different consumer threads.

## missing diagram

The fix is a hedge from A's side. Whenever an An event sets or changes its link, keep a snapshot of the B state that was merged (B_v1), and schedule a check for a few seconds later, long enough for any racing write to have landed.

At retry:
 - Guard. Read the served view of A and verify it still shows (A, B_v1).  This make concurrent checks mutually exclusive
  - If yes, the snapshot is a faithful picture of what is being served, so proceed to Recompute.
  - If not, the view has moved on, either because A was re-linked to another B’. Then another retry will be scheduled for new (A, B’) for reconciliation.
The reverse path already applied v2. At this point we know no race update happens, return.
 - Recompute. Build the latest (A, B) by fetching B from the store. In the common no-race case, recompute has nothing to build. In rare cases, we rebuild the joint view of (A, B_v2) by keeping the latest B.

## Retry queue mechanics
We have a generic retry topic, so retry queue is used for every kind of deferred retry in the job, like dependent events are missing, retry for race update. Each message names the view and the retry type so the consumer can dispatch it. 

Also, remember retry may carry “due time”, the ts of when the retry should be run. However, Kafka has no delayed delivery, and it is an anti-pattern to put thread in sleep in consumer code (Head-of-line blocking, even worse it impacts consumer group liveness). So in consumer, we also need to have a scheduler, so consumers can keep polling without blocking. The scheduler will manage the lifecycle of retry, like popping entries as they come due, dispatching them for actual processing, recovering from retry instance crash. A schedule itself is complex though to be a separate topic that we will cover in another article.

It is preferable to suppress retries during backfill. Missing dependencies are the normal while sibling topics are behind, so nearly every event would spawn a retry and flood the queue. And a retry budget of a couple of minutes cannot outlast a lag of hours. Holes created during catch-up heal as the topics catch up.

## Conclusion
This article introduces an approach to let consumers reliably converge to its producer, with a detailed walkthrough of event marks, and their pros and cons. Later, we introduced a cross-topic dependency problem and solved it by a forward/reverse path, then introduced how to deal with corner cases like topic missing, race update. Last, we mentioned how to build a retry queue and introduced another topic “how to build a scheduler”.
