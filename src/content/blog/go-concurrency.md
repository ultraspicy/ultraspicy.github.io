---
title: Concurrency in Golang
description: Go concurrency primitives and their usecases
pubDate: 2026-10-23
tags: [backend, core]
draft: false
---

This article will review 4 concurrency primitives: mutex, RWMutex, atomic.Pointer[T], and channels.

## Mutex
Mutex stands for MUTual EXclusive. It is self-explanatory: goroutines acquiring mutex will have exclusive RW access to data. Mutex works like a ticket system in a sense that any number of goroutines can apply for acquiring the ticket from mutex, and mutex will hand it over to one goroutine at a time. Underneath, it uses a CPU instruction called CAS (compare-and-swap). Uncontended CAS takes roughly 10 ns, which makes mutex a very performant option.

### Code example
Go, like the majority of programming languages, implements mutex as a standalone data structure. As shown in the code example below, `mu` is the mutex that ensures `value` is updated by at most one goroutine at a time, but `value` and its protector `mu` are two separate fields. So it is the responsibility of the API to always respect the mutex and call Lock() and Unlock() when accessing the critical sections. Our toy example is simple, but in real world, it is not trivial to write code that keeps entering and exiting critical sections correctly, and bugs like deadlocks or a forgotten lock are notoriously hard to debug.
```go
type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.value++
}

func (c *Counter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()

    return c.value
}

// in main()
var c Counter
var wg sync.WaitGroup

for i := 0; i < 10; i++ {
    wg.Add(1)
    go func() { // spawn a goroutine
        defer wg.Done()
        c.Inc()
    }()
}
wg.Wait()
assert.Equal(10, c.Value())
```
### Usecase: multi-variable invariant
This is the most generic option when it comes to coordinating multiple goroutines on the same data. Usually, we use mutex to protect multi-variable invariants, for example
 - in an accounting system, debit and credit should always be equal. So code to change debit and credit should be wrapped under a mutex.
 - data in Cache B is derived from Cache A, accessible by a couple of goroutines. To make states of the two caches consistent, reads and writes can be wrapped under a mutex.

## RWMutex
RWMutex can optimize concurrency by letting readers not block each other while a writer excludes everyone. This is a very natural idea given READ volume dominates in most software. The mental model of RWMutex is also similar to mutex, but now the mutex will give two types of ticket. READ tickets will not be exclusive to other READ tickets, but WRITE ticket will acquire exclusive access.

### Code example
Reusing the above Counter example, but this time we will print the value 5 times via 5 goroutines that read the value. But we don't have control when the scheduler will start the write goroutine, so this code snippet could print any mix of five 0s and 1s.
```go
// merely for demo, this is a bad example in real world
type Counter struct {
    mu    sync.RWMutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()

    c.value++
}

func (c *Counter) Value() int {
    c.mu.RLock()
    defer c.mu.RUnlock()

    return c.value
}

// in main()
var c Counter
var wg sync.WaitGroup

// 5 concurrent readers
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        fmt.Print(c.Value())
    }()
}
// 1 writer
wg.Add(1)
go func() {
    defer wg.Done()
    c.Inc()
}()
wg.Wait()
```
### Usecase: heavy reader AND long critical section
In fact, the above code example is slower than merely using mutex, even though it seems to unblock 5 readers simultaneously. Why? Multiple reader goroutines may sit on different CPU cores, so cores need to move the RWMutex's cache line from core to core, which takes around 100 ns. If our critical section is just a value increment, RWMutex is overkill as the extra cost to sync the cache line on different CPU cores outweighs the gain.

Last, let's take a look at how the RWMutex differentiates RW locks and keeps writers from starving. Inside RWMutex, there are two counters: current readers and waiting readers. Behind the scenes, the above code example will go through the following
  - 2 reader goroutines come, RWMutex updates current_reader = 2, readerWait = 0. Then they enter Value()
  - the writer goroutine comes and takes an internal mutex for writer serialization. The writer sees current_reader = 2. It parks and updates current_reader = 2 - (1 << 30), readerWait = 2.
  - 3 new readers come and update current_reader = 2 - (1 << 30) + 3.  RWMutex notices the current_reader is a negative number, meaning a writer is parked and waiting. RWMutex will wait for the ongoing readers to finish, but blocks new readers from entering the Value().
  - the first 2 readers finish, and accordingly current_reader = 2 - (1 << 30) + 3 - 2, readerWait = 2 - 2 = 0. Now the waiting reader count is 0, so RWMutex wakes the writer to increment the counter.
  - Writer finishes, updates current_reader = 2 - (1 << 30) + 3 - 2 + (1 << 30) = 3. RWMutex notices the current_reader is positive again, so it issues read tickets for the goroutines to access Value() again.
  - the latter 3 readers finish, current_reader = 0, readerWait = 0

## atomic.Pointer[T]
atomic.Pointer[T] holds a single pointer and lets you read or replace it atomically. It has 4 APIs:
 - Load() to load the value
 - Store(v) for unconditional writes
 - Swap(new) stores new and returns the previous pointer in one atomic step
 - CompareAndSwap(old, new) for conditional update.

Its core implementation is a typed wrapper around atomic load, store, swap and CAS on one word. Because it only swaps the pointer, each update must place the new value at a new address rather than modify in place. This design gives it clear advantages and disadvantages
 - extremely fast, with just a few machine instructions which take 5-20 ns.
 - non-blocking. Updating means creating a new copy of this value, so readers can still refer to and use the stale value until they finish. The old value stays reachable until the last reader drops it, so if T holds a connection or file handle the writer cannot close it right after Store.
 - must follow copy-on-write discipline, allocate a new value every time you update.
 - Copy-on-write nature means there is no guarantee that two readers see the same snapshot

### Code example
The generic `T any` in atomic pointer doesn't support any arithmetic, so we need to implement the increment ourselves. The code example demonstrates CAS retry loop in `Inc()` - multiple goroutines may run the `Inc()` simultaneously, their updates are guarded by `old` and serialized by `CompareAndSwap`.
```go
type Counter struct {
    value atomic.Pointer[int64]
}

// in reality we can use atomic.Int64.Add
// use atomic.Pointer as demonstration of how
// atomic update works in general
func (c *Counter) Inc() {
    // CAS retry loop.
    for {
        old := c.value.Load()
        next := int64(1)
        if old != nil {
            next = *old + 1
        }

        if c.value.CompareAndSwap(old, &next) {
            return
        }
    }
}
func (c *Counter) Value() int64 {
    p := c.value.Load()
    if p == nil {
        return 0
    }
    return *p
}

// in main()
var c Counter
c.Inc()
v := c.Value()
```
### Usecase: readers never contend
With RWMutex, every RLock does an atomic add on one shared counter. An atomic add is a write, and a cache line can only be written by one core at a time, so five readers on five cores take turns pulling that line across the interconnect, roughly 100 ns per hop. With atomic.Pointer, Load is a plain read. Reads do not invalidate other cores' copies, so every core keeps its own copy of the line and five simultaneous Loads cost the same as one. So it is the right tool for one specific pattern: an immutable snapshot that is replaced wholesale and read very often. Load() and Store() are single machine instructions and lock free.

## chan
A proverb says "Do not communicate by sharing memory; instead, share memory by communicating." Go channels coordinate goroutines by sending values and signals, quite different from managing access control to protect a shared state. Four channel rules to keep in mind: a receive from a closed channel returns the zero value immediately, a receive from a nil channel blocks forever, a send to a closed channel panics, and a send to a nil channel blocks forever. Only the sender should close, and closing twice panics.

Why do we prefer channels over mutexes?
 - Channels are more flexible in defining the invocation flow between goroutines, like the main goroutine waiting for two competing channels (a nice way to implement timeout, one is a timer, one is the real task) to signal. Also you may as well implement a mutex using a channel, via `select` syntax.
 - A value handed over a channel has one owner at a time, so most state stays local to one goroutine, thus the program is more straightforward to reason and test against, less error prone and easier to debug. All these benefits will accumulate over time to save huge engineering cost. The single-owner rule is promoted by using channels in Go, but is completely enforced by Rust's ownership system.

### Code example 1: close(shutdownCh) for shutdown broadcast
```go
// struct{} is the empty struct and takes zero bytes,
// so the channel carries no data, only the event.
shutdownCh := make(chan struct{})
ticker := time.NewTicker(500 * time.Millisecond)

// N workers, all listening on the same channel
worker := func() {
    for {
        select {
        case <-shutdownCh:   // closed channel: receive returns immediately
            return
        case <-ticker.C:       // otherwise keep doing periodic work
            doWork()
        }
    }
}
for i := 0; i < N; i++ {
    go worker()
}

// ... later, one call stops all N workers
close(shutdownCh)
```
A send on a channel wakes exactly one receiver, but a close wakes all of them: once `close(shutdownCh)` runs, every receive on it returns the zero value immediately, so all N workers exit on the same event. This is why shutdown signals are a closed channel rather than N sends, and why `context.Done()` is implemented the same way. One caveat: `select` picks randomly among ready cases, so a worker may run one more `doWork()` after the channel is closed.

### Code example 2: chan of size 1 for coalescing wake-up
```go
wake := make(chan struct{}, 1)

// any number of producers, from any goroutine
func signal() {
    select {
        case wake <- struct{}{}:   // slot was empty: a wake-up is now pending
        default:                   // slot already full: a wake-up is already pending, do nothing
    }
}

// exactly one consumer
func loop() {
    for {
        select {
            case <-wake:           // take the pending wake-up, slot is empty again
                doTheWork()
            case <-shutdown:
                return
        }
    }
}
```
A plain send on a full buffered channel blocks until a receiver makes room. In `signal()` we add a `default`, so producers never block. N signals from producers are collapsed into one wake-up. This pattern is useful for a batching endpoint or a reducer implementation, where a single consumer can pair with N producers.

### Code example 3: buffered channel for semaphore
```go
// under limiter's code
sem := make(chan struct{}, N)

// under worker's code
sem <- struct{}{}
doWork()
<-sem
```
This is a classic usage of a buffered channel as a semaphore. The concurrency limiter defines the limit as a semaphore queue, workers put a token in before work and take one out after, so there could be at most N workers working simultaneously.

### Code example 4: Cancellable mutex from one channel plus ctx.Done()
```go
func NewMutex() Mutex {
    ch := make(chan struct{}, 1)
    ch <- struct{}{}
    return &mutex{
        ch: ch,
    }
}

func (m *mutex) Lock(ctx context.Context) error {
    select {
        case <-m.ch:
            return nil
        // if context deadline exceeded, the channel of
        // ctx is closed. A closed channel immediately
        // returns a zero value, so err returned
        case <-ctx.Done():
            return ctx.Err()
    }
}

func (m *mutex) Unlock() {
    select {
        case m.ch <- struct{}{}:
        default:
            panic("unlock of unlocked mutex")
    }
}
```
This example shows how to use a channel of size 1 to implement a mutex. It works like a ticket in an envelope - init is to place the ticket inside the envelope; lock is to take the ticket out; unlock is to put a ticket back - exactly the same as the idea of mutex. But in `Lock()` we combine the condition of acquiring lock with the condition of context deadline. This is what I called "Channel is more flexible", in the sense that we can customize the flow of goroutine invocation arbitrarily.

### Code example 5: unbuffered channel for rendezvous handoff
```go
// we use https://pkg.go.dev/context in this example

matcher := &taskMatcherImpl{
    // an unbuffered channel
    taskC: make(chan *InternalTask),
}
```
A producer blocked on `taskC <- task` and a poller blocked on `<-taskC` meet, and the task changes hands in one atomic step. Both sides wrap it in select with `ctx.Done()`, so if the poller's long-poll expires or the producer's RPC is cancelled, nobody is left holding a task that the other party never saw. This pattern makes ownership transfer explicit and exactly-once. Because there is no buffer, a send succeeds only when a receiver is waiting at that instant. That is why this fits the case where pollers are plentiful and almost always ready, and why the matcher falls back to persisting the task when no poller is there.

## Conclusion
A quick recap: Mutex for multi-field invariants, RWMutex for long read-heavy sections, atomic.Pointer for one read-mostly immutable snapshot, channels for ownership transfer and signaling. Each option gives its own characteristics and unique advantages. In real production code, we usually combine them together - for example, if we implement a consistent hash ring to decide key membership, we usually use channel to signal the worker to update the ring, use atomic.Pointer as the guard for the value of the ring, and use mutex to wrap around code that derives a consistent side table.

Later in another article, we will compare the concurrent primitives between Rust and Go. The Rust compiler eliminates data races by its ownership system at compile time, which makes it harder to get past the compiler but at the same time, much safer to run once the code can compile!
