# Good Example: Out of Scope (Mobile SaaS)

**Score: 10/10** — Explicit, categorized, with rationale and future timeline

---

## Out of Scope (V1)

### Features Deferred to V2 (Q3 2026)
| Item | Rationale | Owner |
|------|-----------|-------|
| Scheduled / recurring transfers | Requires backend scheduler service (not yet built). Scoped for Q3. | @backend-team |
| Multi-currency support | Requires FX rate integration + compliance review per currency. Phase 2. | @compliance + @backend |
| Social payments (split bills, group requests) | User research shows 68% interest but adds 3 sprints of scope. Phase 2. | @product |

### Features Explicitly Not Planned
| Item | Rationale |
|------|-----------|
| Tablet-optimized layout | User analytics: <2% of sessions are on tablet. Phone-first for V1. |
| Android widget for balance | Low demand (12 requests in last 6 months). Revisit when Android MAU > 50K. |
| Crypto / digital asset transfers | Regulatory complexity. Not aligned with current business strategy. |
| Web app for transfers | Mobile-only product. Web is for account management only (separate team). |

### Platform Exclusions
| Item | Rationale |
|------|-----------|
| iOS 14 and below | <3% of user base. Minimum: iOS 15+. |
| Android API <26 (Android 7 and below) | <2% of user base. Minimum: API 26+ (Android 8.0). |
| Huawei AppGallery | <0.5% of user base. Google Play only for V1. |

### Integration Exclusions
| Item | Rationale | Alternative |
|------|-----------|-------------|
| Direct bank-to-bank transfers | Requires banking license in each market. | Use payment processor (Stripe) as intermediary. |
| Plaid integration for account linking | Cost ($0.30/link) not justified at current scale (<5K users). | Manual account entry for V1. Revisit at 20K users. |

---

## Why This Is Good

| Criterion | How It's Met |
|-----------|-------------|
| Explicit and specific | Names exact features, platforms, and integrations excluded |
| Categorized | Deferred vs not-planned vs platform vs integration — different audiences care about different categories |
| Rationale for every item | Not just "out of scope" but WHY — prevents debate during sprint |
| Timeline for deferred items | "Q3 2026" not "Phase 2 someday" — stakeholders know when to expect it |
| Owner assigned for deferred | Someone is responsible for picking it up later |
| Data-driven exclusions | "<2% of sessions on tablet" — decisions backed by evidence |
| Alternatives offered | Where relevant, states what IS available instead (Stripe instead of direct bank) |
