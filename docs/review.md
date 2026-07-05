---
layout: default
---
# Code Review Methodology

This document describes the code review methodology used throughout the
Arduino Web monorepo. Reviews are performed per-phase as part of the
development workflow, covering correctness, security, maintainability,
testing coverage, and documentation accuracy.

## Review Process

Each phase of development goes through a structured review cycle after
implementation and testing. The review follows this sequence:

1. **Scope definition** — Identify the files, changes, and criteria for review.
2. **Criteria checklist** — Define specific checks per category (see below).
3. **Findings identification** — Classify each issue by severity and type.
4. **Fix and re-verify** — Address findings, then confirm resolution.
5. **Verdict** — Approve, request changes, or block.

## Finding Classification

Issues are classified along two axes:

### Severity

| Severity | Meaning | Examples |
|----------|---------|---------|
| **Critical** | Security vulnerability or data loss | Missing authentication (CWE-306), hardcoded secrets (CWE-798), no CSRF protection (CWE-352) |
| **High** | Incorrect behavior, broken functionality, or stale docs that mislead | Wrong port numbers in docs, nonexistent API endpoints documented, stale env vars |
| **Medium** | Inconsistency, missing coverage, or technical debt | Missing phase entries, missing Liquid protection, incomplete test coverage |
| **Low** | Style, formatting, or minor inaccuracies | Typos, duplicate headers, stale phase references in user-facing text |

### Finding Type

| Type | Meaning | Action |
|------|---------|--------|
| **Warning** | Functional or correctness issue that should be fixed | Must fix before merge |
| **Suggestion** | Improvement that adds value but is not blocking | Should fix, but may defer |
| **Nit** | Minor style or consistency issue | Fix opportunistically |

## Review Categories

### Correctness

- Function signatures match actual usage
- Logic handles edge cases (empty input, timeouts, duplicates)
- Error paths are handled (exceptions caught, fallbacks present)
- Concurrency safety (thread locks, atomic operations)

### Security

- Authentication and authorization enforced
- Secrets not hardcoded or logged
- Input validation and sanitization
- CSRF protection on state-changing endpoints
- Rate limiting on public endpoints
- Session hardening (secure cookies, expiry)

### Performance

- Unnecessary I/O or computation avoided
- Data structure choices appropriate for access patterns
- Connection pooling or reuse where applicable
- Streaming vs buffering trade-offs considered

### Maintainability

- Code follows project conventions (linting, formatting)
- Duplication minimized (shared modules extracted)
- Configuration centralized (env vars, CLI args, TOML)
- Comments explain rationale, not mechanics

### Testing Coverage

- Unit tests cover core logic paths
- Integration tests cover end-to-end flows
- Edge cases and error paths tested
- Board-dependent tests skip gracefully when hardware absent

### Documentation Accuracy

- README and docs match actual code behavior
- API routes documented match Flask route definitions
- Port numbers, env vars, and CLI flags match implementation
- Stale phase references not present in user-facing docs
- Links resolve to existing files

## Review Structure

Reviews are documented in `agent-docs/REVIEW_JOURNAL.md` with the following format:

```
## <date> — <phase description>

### Scope
<summary of what is being reviewed>

### <Category> Section
<Specific findings with file paths and line references>

### Summary

| Severity | Count | Key Items |
|----------|-------|-----------|
| Warning | N | List of functional issues |
| Suggestion | N | List of improvements |
| Nit | N | List of style issues |

**Overall Verdict**: ✅ Good to merge / ⚠️ Changes required / ❌ Blocked
```

Findings reference specific file paths and line numbers to enable
quick navigation to the source.

## Verification Passes

After fixes are applied, a verification pass confirms:

- **Grep/pattern match** — No stale references, typos, or broken links remain
- **Visual inspection** — Changed sections read correctly in context
- **Structure integrity** — Front matter, Liquid tags, code blocks balanced
- **Side-effect check** — Bulk operations (replaceAll, sed) didn't introduce unintended changes
- **Regression** — `nox -s all_tests` passes (8/8 sessions)
- **Jekyll build** — `bundle exec jekyll build` emits 0 errors

## Review Tools

| Tool | Purpose |
|------|---------|
| `git diff` | Review changes before committing |
| `grep` / `rg` | Find stale references, pattern matching |
| Visual inspection | Read modified sections in context |
| `nox -s all_tests` | Regression testing |
| `bundle exec jekyll build` | Documentation build verification |

## Related Documentation

| Document | Description |
|----------|-------------|
| [`agent-docs/REVIEW_PLAN.md`](../agent-docs/REVIEW_PLAN.md) | Agent-facing review plans per phase |
| [`agent-docs/REVIEW_JOURNAL.md`](../agent-docs/REVIEW_JOURNAL.md) | Agent-facing review findings journal |
| [`docs/architecture.md`](architecture.md) | System architecture and design decisions |
| [`docs/tests.md`](tests.md) | Testing methodology and coverage |
