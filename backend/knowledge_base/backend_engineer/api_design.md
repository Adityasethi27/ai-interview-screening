# API Design

## REST principles
REST models a system as **resources** identified by URLs, manipulated with a small
set of HTTP verbs. It is stateless: each request carries everything needed to
process it, so any server instance can handle any request — which is what makes
horizontal scaling and load balancing straightforward.

- **GET** retrieves a resource and must be *safe* (no side effects) and
  *idempotent*.
- **POST** creates a resource or triggers a process; not idempotent by default.
- **PUT** replaces a resource and is idempotent.
- **PATCH** partially updates a resource.
- **DELETE** removes a resource and is idempotent.

Use nouns for resources (`/users/123/orders`), not verbs. Keep hierarchies shallow
and predictable.

## Status codes
Communicate outcomes with the right code:
- **2xx** success: 200 OK, 201 Created (return the new resource / its location),
  204 No Content.
- **4xx** client errors: 400 Bad Request (malformed), 401 Unauthorized (not
  authenticated), 403 Forbidden (authenticated but not allowed), 404 Not Found,
  409 Conflict (e.g. duplicate), 422 Unprocessable Entity (validation), 429 Too
  Many Requests (rate limited).
- **5xx** server errors: 500 Internal Server Error, 503 Service Unavailable.
Never return 200 with an error body — clients and proxies rely on status codes.

## Idempotency
An operation is idempotent if performing it multiple times has the same effect as
performing it once. GET, PUT, DELETE are naturally idempotent; POST is not. For
unsafe operations that clients may retry (payments, order creation), support an
**idempotency key**: the client sends a unique key, the server stores the result
for that key and returns the same response on retries, preventing duplicates.

## Validation and error handling
Validate at the boundary: types, ranges, required fields, and business rules.
Return structured, machine-readable errors (a consistent JSON shape with a code,
message, and field details) so clients can react programmatically. Fail fast and
never leak stack traces or internal identifiers to callers. Distinguish client
errors (4xx, do not retry) from transient server errors (5xx, safe to retry with
backoff).

## Versioning
APIs evolve; versioning avoids breaking existing clients. Options: URL versioning
(`/v1/...`), header versioning, or content negotiation. Prefer additive,
backward-compatible changes (new optional fields) and reserve version bumps for
breaking changes. Document deprecation timelines.

## Pagination, filtering, sorting
Never return unbounded lists. Use **cursor-based** pagination for large or
frequently changing datasets (stable, efficient) or offset/limit for simple cases
(can drift and is slow deep into the list). Support filtering and sorting via query
parameters, and cap page sizes.

## Idempotent, resilient clients
Design responses so clients can be resilient: include resource IDs, use ETags for
optimistic concurrency (`If-Match`), and return `Retry-After` on 429/503. Rate
limiting protects the service; communicate limits in headers.

## Contract-first and documentation
Define the contract (OpenAPI/JSON Schema) before implementation so frontend and
backend can work in parallel and generate clients/validators. A clear contract is
the interface boundary that keeps a system modular.

## Authentication vs authorization
**Authentication** proves *who* you are (tokens, sessions). **Authorization**
decides *what* you may do (roles, scopes, ownership checks). Keep them separate;
enforce authorization on every request at the resource level, never trust the
client to hide actions it should not perform.
