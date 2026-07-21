# System Design, Scalability, and Reliability

## Vertical vs horizontal scaling
- **Vertical scaling** adds more CPU/RAM to one machine: simple but bounded and a
  single point of failure.
- **Horizontal scaling** adds more machines behind a load balancer: near-unbounded
  but requires statelessness, coordination, and data partitioning.
Stateless services scale horizontally most easily because any instance can serve
any request; push session state to a shared store (Redis) or signed tokens.

## Load balancing
A load balancer distributes traffic across instances (round-robin, least-connections,
or hashing). It provides health checks (removing unhealthy instances), enables
zero-downtime deploys, and is often where TLS terminates. Sticky sessions route a
user to the same instance but undermine even distribution and resilience — prefer
stateless services.

## Caching
Caching stores expensive-to-compute or frequently-read data closer to the consumer.
Layers include client, CDN, application (in-memory/Redis), and database caches.
- **Cache-aside (lazy loading)**: app checks cache, on miss reads DB and populates
  the cache. Simple; first request is slow and stale data is possible.
- **Write-through**: writes go to cache and DB together — consistent but slower
  writes.
- **Write-back**: write to cache, flush to DB later — fast but risks data loss.
Key concerns: **eviction** (LRU/LFU/TTL), **invalidation** (the hard part — stale
data), and the **thundering herd** when a hot key expires (mitigate with locks or
staggered TTLs). Caching trades freshness for latency and load reduction.

## Concurrency, async, and the event loop
Backends handle many requests at once. **Threads/processes** offer parallelism but
cost memory and context switching. **Asynchronous, non-blocking I/O** (event loop)
lets one thread juggle thousands of I/O-bound requests by yielding while waiting on
the network or disk — ideal for I/O-bound web services. CPU-bound work still needs
multiple cores/processes. Watch for **race conditions** on shared state; guard with
locks, atomic operations, or by avoiding shared mutable state.

## Message queues and asynchronous processing
Queues (Kafka, RabbitMQ, SQS) decouple producers from consumers. They smooth
traffic spikes (**backpressure**), enable retries, and let slow work (emails,
image processing) run outside the request path. Delivery is usually **at-least-once**,
so consumers must be **idempotent**. Queues add eventual consistency and operational
complexity in exchange for resilience and throughput.

## Reliability patterns
- **Timeouts** prevent a slow dependency from tying up resources indefinitely.
- **Retries with exponential backoff and jitter** handle transient failures without
  synchronized retry storms.
- **Circuit breakers** stop calling a failing dependency for a cooldown, failing
  fast and letting it recover.
- **Bulkheads** isolate resource pools so one overloaded dependency cannot sink the
  whole service.
- **Graceful degradation**: serve reduced functionality (cached/stale data) instead
  of a hard failure.

## Rate limiting
Protect services from abuse and overload with algorithms like **token bucket**
(allows bursts up to a limit) or **sliding window**. Return 429 with `Retry-After`.
Rate limiting also enforces fairness across tenants.

## Security fundamentals
- Hash passwords with a slow, salted algorithm (bcrypt/argon2), never store
  plaintext.
- Use parameterized queries to prevent **SQL injection**; validate and encode all
  input/output to prevent injection and XSS.
- Enforce authentication and authorization on every request; apply least privilege.
- Use TLS everywhere; keep secrets out of code (environment variables / secret
  managers).
- Defend against CSRF for cookie-based auth; use short-lived tokens with refresh.

## Observability
You cannot operate what you cannot see. **Logs** (structured, correlated by request
ID), **metrics** (latency percentiles, error rates, throughput), and **traces**
(request flow across services) together let you detect, diagnose, and fix issues.
Track the **four golden signals**: latency, traffic, errors, and saturation. Alert
on symptoms users feel (p99 latency, error rate), not just resource usage.
