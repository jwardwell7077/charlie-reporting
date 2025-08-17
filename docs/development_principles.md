# Development Principles

## Minimal Entry / Minimal Exit

We standardize on a *Minimal Entry / Minimal Exit* principle:

> Each component exposes the *fewest necessary public entry points* and leaves every object or return value in a **fully validated, deterministic state** immediately upon exit—no hidden optional wrapper layers, deferred side effects, or lazy back-filling unless there is a clearly measured cost justification.

### Why

* **Debuggability:** Fewer indirection layers make stack traces and mental models shallow and fast to reason about.
* **Determinism:** State is complete right after construction or a top-level function returns—no later implicit mutation surprises.
* **Test Focus:** Unit tests exercise one canonical path (e.g. `Roster()` / `Roster.from_csv`) instead of duplicating scenarios through convenience wrappers.
* **Refactor Safety:** Minimal surface area shrinks blast radius; fewer public symbols to preserve.
* **Performance Clarity:** Any future introduction of lazy loading must document measurable cost savings.

### Application Examples

| Area | Before (Anti-Pattern) | After (Applied Principle) |
|------|-----------------------|----------------------------|
| Roster loading | `load_roster()` free wrapper + constructor + alt loader | Single class (`Roster`) with canonical constructor and `from_csv` classmethod only |
| Generators | Multiple ad-hoc functions building rows | Unified `build()` method on concrete generator subclasses |
| Service orchestration | Hidden module globals for roster/RNG | Explicit instance fields injected/constructed deterministically |

### Contribution Guidelines

When adding or modifying code:

1. Prefer *one* obvious construction path. If you supply an alternate (e.g. a classmethod like `from_source`), ensure it reduces caller friction without duplicating logic.
2. Avoid free-function wrappers that do nothing but call a constructor—delete them unless they add *real* abstraction.
3. Validate invariants (sizes, value domains, configuration presence) immediately in `__init__` / factory before storing state.
4. Keep public API surface lean—only export what external modules must use (`__all__` discipline).
5. Do not introduce hidden singletons or cross-module mutable caches without a profiling note.
6. Lazy initialization is allowed only with a documented performance rationale and must remain transparent (idempotent, thread-safe if applicable).
7. Eliminate dead alternate paths rapidly; deprecate loudly if temporary.

### Review Checklist Snippet

Use this lightweight checklist during PR reviews:

* [ ] Is there exactly one obvious way to construct / obtain the object?
* [ ] Are all invariants validated up-front?
* [ ] Any wrapper / alias truly necessary? (If removed, do tests become *clearer*?)
* [ ] Are public exports minimal and intentional?
* [ ] Any lazy behavior justified with a note or metric? (If not, initialize eagerly.)

### Roster Case Study (Concrete)

The `Roster` class self-loads when instantiated with no args, performing:

```text
__init__ -> _load_csv -> validate size (== 100) -> role bucketing
```

At return from `__init__`, the object is fully usable—no follow-up `load()` call or wrapping helper required. The removed `load_roster()` free function exemplified a redundant entry point replaced by this principle.

---
*Adhering to Minimal Entry / Minimal Exit keeps the system predictable and makes scaling the codebase painless.*
