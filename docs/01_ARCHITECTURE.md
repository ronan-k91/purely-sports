# Purely Sports Architecture

## Goals

- Keep domain rules independent from delivery and storage concerns.
- Make external sports data replaceable and observable.
- Prefer explicit contracts, small modules, and testable boundaries.

## Layers

1. **Presentation** handles user interaction and rendering.
2. **Application** coordinates use cases and maps domain results to views.
3. **Domain** owns sports concepts, invariants, and business rules.
4. **Infrastructure** integrates APIs, persistence, messaging, and telemetry.

## Boundaries

Dependencies should point toward the domain. External services enter through ports with adapters at the infrastructure edge. Cross-cutting concerns such as logging, configuration, and error handling should remain consistent and easy to test.
