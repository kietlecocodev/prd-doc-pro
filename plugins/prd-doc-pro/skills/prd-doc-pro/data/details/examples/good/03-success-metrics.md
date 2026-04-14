# Good Example: Success Metrics (Mobile PLG SaaS)

**Score: 10/10** — Baseline, target, timeframe, formula, guardrails

---

## Success Metrics

### Primary Metrics

| Metric | Baseline | Target | Timeframe | How We Measure |
|--------|----------|--------|-----------|---------------|
| D7 Retention | 22% | 35% | 90 days post-launch | Firebase Analytics cohort report, filtered by users who completed onboarding |
| Free-to-Paid Conversion | 3.1% | 5.0% | 60 days | RevenueCat dashboard: (trial_started → subscription_activated) / total_signups × 100 |
| Time to First Value (TTFV) | 4.2 minutes | <2 minutes | 30 days | Median time from `app_first_open` to `first_project_created` event in Amplitude |
| Push Notification Opt-in | N/A (new) | ≥60% | 30 days | Firebase: `notification_permission_granted` / `notification_permission_prompted` × 100 |

### Leading Indicators (weekly tracking)

| Indicator | Current | Watch For | Action If Triggered |
|-----------|---------|-----------|-------------------|
| Onboarding completion rate | 48% | Drop below 40% | Review onboarding funnel for new friction points |
| D1 retention | 35% | Drop below 30% | Investigate first-session experience changes |
| Session frequency (sessions/user/week) | 2.1 | Drop below 1.5 | Check push notification delivery and content relevance |

### Guardrail Metrics (must not regress)

| Guardrail | Current Baseline | Threshold | Monitoring |
|-----------|-----------------|-----------|------------|
| Crash-free session rate | 99.4% | Must stay ≥99.2% | Firebase Crashlytics — PagerDuty alert if below threshold |
| App cold start time | 1.8s | Must stay ≤2.5s | Firebase Performance — P95 on target device class |
| App store rating | 4.3 | Must not drop below 4.0 | Weekly manual check + AppFollow alerts |
| Existing user D30 retention | 14% | Must not drop below 12% | Amplitude cohort — compare pre/post launch cohorts |
| Support ticket volume | 210/month | Must not increase >25% (≤263/month) | Zendesk weekly count — Slack alert |

### Anti-Metrics (what we explicitly won't optimize for)

- **Total time-in-app**: We want efficient sessions, not infinite scroll. Increasing time-in-app by making tasks slower is a failure.
- **Raw DAU**: A spike from push notification spam is not real engagement. DAU must come from organic returns.
- **Free user count**: Growing free users without improving conversion is vanity. We track free-to-paid, not free signups.

---

## Why This Is Good

| Criterion | How It's Met |
|-----------|-------------|
| Every metric has a baseline | Current values stated or "N/A (new)" with explanation |
| Every metric has a target | Specific number, not "improve" or "increase" |
| Every metric has a timeframe | 30/60/90 days post-launch |
| Every metric has measurement method | Tool name + event/query specified |
| Guardrails defined | 5 metrics that must NOT regress, with explicit thresholds |
| Leading indicators | Early warning metrics with action triggers |
| Anti-metrics | Explicitly states what NOT to optimize for and why |
| Mobile-specific | Crash-free rate, cold start time, app store rating, push opt-in |
