# Bad Example: Success Metrics (Mobile PLG SaaS)

**Score: 1/10** — No baselines, no targets, no timeframes, unmeasurable

---

## Success Metrics

- Improve user engagement
- Increase retention
- More users should convert to paid
- App should be stable and performant
- Users should be satisfied

---

## What's Wrong (Annotated)

| Metric Attempt | Antipattern | What's Missing |
|---------------|-------------|---------------|
| "Improve user engagement" | **Unquantified** | What IS engagement? DAU? Session length? Feature usage? By how much? From what baseline? |
| "Increase retention" | **No baseline or target** | Retention of which cohort? D1? D7? D30? Current rate? Target rate? By when? |
| "More users should convert to paid" | **Vague** | How many more? From what %? Free trial or freemium? What counts as "converted"? |
| "App should be stable" | **Untestable** | What crash rate is acceptable? What's the current rate? How is it measured? |
| "Users should be satisfied" | **Unmeasurable** | NPS? CSAT? App store rating? Support tickets? What's the current score? |

### Additional Problems
- **No guardrails**: Nothing protecting against regressions
- **No timeframe**: When would we check if these succeeded?
- **No measurement method**: No tool, event, or query specified
- **No leading indicators**: No way to detect problems early
- **Not mobile-specific**: No crash rate, no app store rating, no push metrics

## How to Fix

For each "metric," apply this template:

```
Metric: [specific name]
Definition: [exactly what it measures]
Current baseline: [number, or "TBD — instrument before launch"]
Target: [specific number]
Timeframe: [by when]
Measurement: [tool + event/query]
```

Then add:
- 3-5 guardrail metrics with explicit "must not exceed/drop below" thresholds
- 2-3 leading indicators with weekly tracking cadence
- 1-2 anti-metrics (what you explicitly won't optimize for)
