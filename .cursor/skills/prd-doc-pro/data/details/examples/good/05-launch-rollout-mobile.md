# Good Example: Launch & Rollout Plan (Mobile App)

**Score: 10/10** — Phased, measurable gates, rollback plan, mobile-aware

---

## Launch & Rollout Plan

### Pre-Launch Checklist
- [ ] All P0 acceptance criteria passing in QA
- [ ] Crash-free session rate ≥99.5% in internal testing
- [ ] Performance benchmarks met on target device class (iPhone 12 / Pixel 6)
- [ ] App Store / Play Store metadata updated (screenshots, description, what's new)
- [ ] Privacy Nutrition Label (iOS) and Data Safety Section (Android) updated
- [ ] Demo account credentials prepared for Apple App Review
- [ ] Review notes written explaining each new feature for Apple reviewers
- [ ] Feature flags configured: `feature_v2_transfer` = OFF for production

### Rollout Phases

| Phase | Timeline | Audience | Gate Criteria to Advance |
|-------|----------|----------|------------------------|
| **Phase 0: Internal** | Week 1 (Mon-Fri) | Team of 25 (all platforms) | Zero P0 bugs. Crash-free ≥99.5%. All flows completable. |
| **Phase 1: Canary** | Week 2 (Mon-Wed) | 2% of users via feature flag | Crash-free ≥99.3%. No error rate spike >2x baseline. No P0 bugs from Sentry. |
| **Phase 2: Limited** | Week 2 (Thu) - Week 3 (Wed) | 10% of users | D1 retention of test group ≥ control group. Conversion funnel not degraded. Support tickets <5 about new feature. |
| **Phase 3: Broad** | Week 3 (Thu-Fri) | 50% of users | All Phase 2 gates hold at 50%. App store rating stable (no drop >0.1 star). |
| **Phase 4: GA** | Week 4 (Mon) | 100% of users | 48h stability at 50% with no rollback triggers hit. |

### Rollback Triggers (any ONE triggers immediate rollback)

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Crash-free rate drops | Below 99.0% (current: 99.4%) | Feature flag OFF within 5 minutes. Incident channel opened. |
| Uninstall rate spikes | >6%/month (current: 4.2%) | Feature flag OFF. Root cause analysis within 24h. |
| App store rating drops | Below 3.8 (current: 4.3) | Feature flag OFF. Review new 1-star reviews for pattern. |
| P0 bug reported by 3+ users | Any P0 with repro steps from 3+ unique users | Feature flag OFF. Hotfix branch created. |
| Error rate spikes | >5x baseline on any monitored endpoint | Feature flag OFF. Backend investigation. |

### Rollback Mechanism
1. **Feature flag** (`feature_v2_transfer`): Server-side toggle via LaunchDarkly. Disables new UI within 5 minutes for all users. Old flow preserved as fallback.
2. **Backend rollback**: API version N-1 remains deployed alongside N. Feature flag routes to N-1 endpoints.
3. **Emergency App Store submission**: If a client-side hotfix is needed, use Apple's expedited review (available for critical fixes). Timeline: 24-48h. Android: <24h via Play Console managed publishing.
4. **Communication**: If >1% of users affected, in-app banner: "We've temporarily reverted to the previous transfer flow while we fix an issue. Your data is safe."

### Post-Launch Monitoring (first 14 days)
- **Daily**: Crash-free rate, error rate, feature flag engagement, support ticket volume
- **Every 3 days**: D1 retention comparison (test vs control), conversion funnel, app store rating trend
- **Weekly**: D7 retention, full funnel analysis, user feedback summary from reviews + support

---

## Why This Is Good

| Criterion | How It's Met |
|-----------|-------------|
| Phased rollout | 5 phases from internal → 2% → 10% → 50% → 100% |
| Measurable gates | Each phase has specific numeric criteria to advance |
| Rollback triggers | 5 explicit triggers with thresholds and actions |
| Rollback mechanism | Feature flag + backend + emergency app store process |
| Mobile-specific | App store review timeline, app store rating monitoring, feature flag (no web-style instant deploy) |
| Communication plan | User-facing messaging for rollback scenario |
| Post-launch monitoring | Daily/3-day/weekly cadence with specific metrics |
