````markdown
# URL Shortener

A progressively engineered URL shortener built with FastAPI, PostgreSQL, Kafka, Redis, Docker, and SQLAlchemy.

This project is intentionally developed through versions. Each architectural change is introduced to solve a real limitation discovered in the previous version.

The goal is not to add technologies for the sake of complexity, but to understand the problem, evaluate the trade-offs, implement a solution, and observe what problem appears next.

---

## Engineering Journey

### v1.0.0 — The First Complete Version

The initial goal was simple:

> Build a working URL shortener with a clean backend rather than just exposing a collection of CRUD endpoints.

### Features

- Create shortened URLs
- Base62 short-code generation
- PostgreSQL persistence
- URL redirection
- URL expiration
- Click counting
- Health checks
- Application logging

### Why v1.0.0?

The core URL-shortening workflow was functional end-to-end.

The system was intentionally kept simple before introducing distributed-system components.

---

## Problem #1 — Observability

Once the basic application worked, another problem became apparent:

> How do I know what the application is actually doing when something goes wrong?

### Solution — Logging & Health Checks

Application logging and health checks were introduced to make the service observable rather than treating it as a black box.

This also established the foundation for debugging and monitoring future versions.

---

# Kafka — Asynchronous Click Analytics

## Problem

The initial implementation updated `click_count` directly during the redirect request.

Conceptually:

```text
Request
   ↓
PostgreSQL
   ↓
Update click count
   ↓
Redirect
````

The user does not need the analytics update to complete before receiving the redirect.

This added unnecessary database work to the latency-sensitive redirect path.

## Decision

Move click analytics outside the request path using Kafka.

```text
                 ┌──→ Redirect
Request → API ───┤
                 └──→ Kafka → Analytics Consumer → PostgreSQL
```

## Implementation

* Kafka through Docker Compose
* Confluent Kafka Python client
* Kafka click-event topic
* Kafka producer
* Kafka consumer
* Asynchronous delivery callbacks
* Background polling worker
* Graceful producer shutdown

### Asynchronous Producer

The producer was initially tested with synchronous flushing.

However, waiting for Kafka delivery directly inside the redirect path would reduce the benefit of asynchronous processing.

The producer was therefore changed to use a background polling worker:

```text
Request
   ↓
Kafka Producer
   ↓
Return redirect

Background Worker
   ↓
poll()
   ↓
Delivery Callback
```

This allows Kafka delivery callbacks to be handled independently of incoming redirect requests.

---

# Redis — Caching the Redirect Path

## Problem

Kafka solved the analytics bottleneck, but every redirect still required a PostgreSQL lookup.

```text
Request
   ↓
PostgreSQL
   ↓
Find original URL
   ↓
Redirect
```

For a read-heavy URL shortener, repeatedly querying PostgreSQL for the same URL mapping is unnecessary.

If a popular URL receives thousands of redirects, the database could receive thousands of identical lookup requests.

## Decision

Introduce Redis as a cache for URL mappings.

PostgreSQL remains the source of truth.

Redis is an optimization layer.

## Cache-Aside Strategy

```text
Request
   ↓
Redis
   │
   ├── HIT ──────→ Redirect
   │
   └── MISS
         ↓
     PostgreSQL
         ↓
     Store in Redis
         ↓
       Redirect
```

The first request may require PostgreSQL.

Subsequent requests can be served directly from Redis.

## Cached Data

The cached representation contains the information required by the redirect path:

```json
{
  "original_url": "https://example.com",
  "expires_at": "..."
}
```

Click counts remain in PostgreSQL because analytics are handled separately through Kafka.

---

## URL Expiration & Redis TTL

Caching introduced another consistency problem.

An expired URL should not remain usable simply because it still exists in Redis.

The cached record therefore retains its `expires_at` value.

Redis also receives a TTL based on the remaining lifetime of the URL.

```text
PostgreSQL
    ↓
expires_at
    ↓
Redis
 ├── cached URL
 ├── expires_at
 └── TTL until expiration
```

This provides two layers of protection:

1. Application-level expiration validation
2. Automatic Redis eviction

---

## Redis Failure Handling

Redis is not the source of truth.

If Redis becomes unavailable:

```text
Redis ❌
   ↓
Cache failure
   ↓
PostgreSQL
   ↓
Redirect
```

The application falls back to PostgreSQL instead of failing the redirect.

Similarly, if Redis is unavailable while writing a newly fetched URL to the cache, the redirect can still succeed.

This follows an important design principle:

> A cache failure should degrade performance, not correctness.

---

# Current Architecture

```text
                         ┌───────────────┐
                         │   PostgreSQL  │
                         │ Source of     │
                         │ Truth         │
                         └───────┬───────┘
                                 │
                                 │ Cache Miss
                                 ▼
┌──────────┐              ┌───────────────┐
│  Client  │ ───────────→ │    FastAPI    │
└──────────┘              └───────┬───────┘
                                  │
                         ┌────────┴────────┐
                         │                 │
                         ▼                 ▼
                      Redis             Kafka
                       Cache              │
                         │                ▼
                         │          Analytics Consumer
                         │                │
                         │                ▼
                         │          PostgreSQL
                         │
                         ▼
                      Redirect
```

---

# Technology Stack

| Component     | Technology        | Purpose                         |
| ------------- | ----------------- | ------------------------------- |
| API           | FastAPI           | HTTP API and redirects          |
| Database      | PostgreSQL        | Persistent source of truth      |
| ORM           | SQLAlchemy        | Database access                 |
| Cache         | Redis             | Fast URL lookups                |
| Messaging     | Kafka             | Asynchronous click events       |
| Kafka Client  | Confluent Kafka   | Producer/consumer integration   |
| Containers    | Docker Compose    | Local infrastructure            |
| Configuration | Pydantic Settings | Environment-based configuration |
| Logging       | Python Logging    | Application observability       |

---

# Project Structure

```text
URL_shortner/
│
├── app/
│   ├── api/
│   ├── cache/
│   ├── core/
│   ├── events/
│   ├── models/
│   ├── schemas/
│   └── services/
│
├── infrastructure/
│   ├── kafka/
│   │   └── compose.yaml
│   │
│   └── redis/
│       └── compose.yaml
│
├── .env
├── requirements.txt
└── README.md
```

---

# Engineering Principles

### Solve problems, don't collect technologies

A new technology should exist because the existing architecture has a limitation that justifies it.

### Keep the source of truth clear

PostgreSQL is responsible for persistent URL state.

Redis is a cache.

Kafka is an event transport.

Each component has a different responsibility.

### Keep the critical path small

The redirect operation should perform as little work as possible.

```text
Request
   ↓
Cache
   ↓
Redirect
```

Analytics and other background work should not unnecessarily delay the redirect.

### Failure should be contained

A failure in an optimization layer should not automatically become a failure of the core service.

### Complexity should be earned

Future architectural changes will be introduced when the system encounters a problem that justifies them.

---

# Future Roadmap

The project is intentionally unfinished.

Planned areas of exploration include:

* Kafka reliability and delivery guarantees
* Consumer groups and partitioning
* Event idempotency
* Retry strategies
* Dead-letter topics
* Redis cache invalidation
* Cache stampede protection
* Prometheus metrics
* Grafana dashboards
* OpenTelemetry tracing
* Load testing
* Horizontal scaling
* Load balancing
* Database scaling
* Dedicated analytics infrastructure
* Deployment and CI/CD

The architecture will evolve based on the problems encountered rather than following a predetermined list of technologies.

---

# Development Philosophy

This repository is less about building the world's best URL shortener and more about documenting the process of turning a simple backend application into a progressively more reliable and scalable system.

Each version represents a set of engineering decisions, trade-offs, failures, and improvements.

```
```
