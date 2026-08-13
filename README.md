# URL Shortener

A URL shortener built incrementally to explore backend engineering,
distributed systems, scalability, and reliability.

This project is intentionally developed through versions. Each version
exists because the previous version introduced a real limitation.

---

## Engineering Journey

### v1.0.0 — The First Complete Version

The first goal was simple:

> Build a working URL shortener with a clean backend rather than just
> exposing a collection of CRUD endpoints.

#### Problem

The application needed to:

- accept a long URL
- generate a short code
- store the mapping
- redirect users
- track basic click counts

#### Implementation

- FastAPI for the API layer
- PostgreSQL for persistent storage
- SQLAlchemy for database access
- URL expiration handling
- Click counting
- Basic health checking
- Application logging

### Why v1.0.0?

This version was considered the first complete baseline because the
core URL-shortening workflow was functional end-to-end.

It wasn't designed to be highly scalable yet.

That was intentional.

The goal was to establish a working system before introducing
complexity.

---

## Problem #1 — Observability

Once the basic application worked, another problem became apparent:

> How do I know what the application is actually doing when something
> goes wrong?

### Solution — Logging & Health Checks

A health endpoint and application logging were introduced to make the
service observable rather than treating it as a black box.

This established the foundation for debugging later versions.

---

# v2.0.0 — Event-Driven Click Analytics

## Problem

In v1.0.0, the redirect request was also responsible for updating
`click_count`.

That meant the critical redirect path was coupled to a database write.

Conceptually:

Request → PostgreSQL → update click count → redirect

The user doesn't actually need the click count updated before receiving
the redirect.

This introduced unnecessary work into a latency-sensitive path.

## Decision

Move click analytics outside the request path using Kafka.

## Implementation

```text
                 ┌──→ Redirect
Request → API ───┤
                 └──→ Kafka → Analytics Consumer → PostgreSQL