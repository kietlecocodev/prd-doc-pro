# Good Example: Edge Cases (Mobile-Specific)

**Score: 10/10** — Comprehensive mobile edge cases with exact behaviors

---

## Edge Cases & Error Handling

### Network & Connectivity
| Scenario | Expected Behavior |
|----------|-----------------|
| User loses connection mid-form-submission | Data saved locally. Toast: "You're offline — we'll submit when you're back online." Queue icon appears in nav bar. Auto-retry when connectivity resumes. |
| User is on slow 3G (<1 Mbps) | Images load as progressive JPEG (blur → sharp). Text content loads first. Skeleton screens for images. No timeout for 30 seconds. |
| User is on airplane mode and opens the app | App loads from local cache. Persistent top banner: "You're offline." All read features work from cache. Write actions queued with visual indicator. |
| WiFi connected but no internet (captive portal) | Detect via connectivity check (ping). Show: "WiFi connected but no internet access." Same behavior as offline mode. |

### Device & OS
| Scenario | Expected Behavior |
|----------|-----------------|
| App backgrounded during a multi-step flow | State preserved in memory. User returns to exact step they left. Session timeout: 15 minutes — after that, restart from last saved checkpoint, not from scratch. |
| Phone call interrupts during video recording | Recording paused automatically. On return: "Your recording was paused. Resume or save what you have?" |
| Low battery (<15%) | Non-essential background sync paused. GPS tracking frequency reduced from 5s to 30s intervals. Banner: "Low battery — some features paused to save power." |
| Low storage (<100MB free) | Prevent large downloads. Toast: "Low storage — clear space to download offline content." Cache cleanup offered: "Free up [X]MB by clearing cached content?" |
| App killed by OS (memory pressure) | On relaunch: restore last active screen from saved state. Unsent data preserved in local queue. No crash report generated (this is normal OS behavior). |
| User on a 4-year-old device (low RAM, slow CPU) | Animations reduced automatically (respect system "Reduce Motion" setting). Image resolution downscaled. List virtualization: only 20 items in memory at a time. |

### Permissions
| Scenario | Expected Behavior |
|----------|-----------------|
| User denies camera permission | Feature still usable via "Choose from Library" alternative. Settings link shown: "To use the camera, enable it in Settings > [App Name] > Camera." |
| User denies location then later wants location features | In-context prompt: "This feature uses your location. Tap to open Settings and enable location access." Direct link to app settings. |
| User denies push notifications | App continues normally. Settings page shows: "Notifications are off. Enable them to get updates about [specific value]." Never re-prompt via OS dialog (iOS prevents it). |
| User revokes a previously granted permission (via OS Settings) | App detects revoked permission on next use. Graceful degradation — feature works without the permission if possible, shows in-context settings link if not. |

### Data & Sync
| Scenario | Expected Behavior |
|----------|-----------------|
| User edits the same record on two devices | Last-write-wins with conflict detection. If conflict detected within 5 minutes: show both versions and let user choose. If >5 minutes: merge non-conflicting fields, flag conflicting fields for review. |
| User uninstalls and reinstalls the app | Account data preserved on server. Local cache cleared. Re-login required. Onboarding skipped (server flag: `onboarding_completed`). Previous subscription detected via receipt validation. |
| API returns unexpected data format | App displays last cached version of the data. Silent error logged to Sentry with payload sample. No crash. No blank screen. |
| Backend is down (500 errors) | Cached data displayed with timestamp: "Last updated 2 hours ago." Retry button available. Auto-retry every 30 seconds (max 5 attempts, then stop). No infinite retry loops. |

### Accessibility Edge Cases
| Scenario | Expected Behavior |
|----------|-----------------|
| User has Dynamic Type set to maximum (xxxLarge) | All text scales proportionally. Layouts reflow (no truncation of critical text). Buttons remain tappable (min 44pt). Horizontal scrolling never required. |
| User has VoiceOver/TalkBack enabled | All screens navigable. Images have descriptive labels. Dynamic content changes announced. Custom gestures have tap-based alternatives. Modals trap focus correctly. |
| User has "Reduce Motion" enabled | All animations replaced with cross-fade transitions. Parallax effects disabled. Auto-playing video paused by default. |

---

## Why This Is Good

- **Categorized by scenario type**: Network, device, permissions, data, accessibility
- **Exact behaviors specified**: Not "handle gracefully" but exactly what the user sees
- **Copy included**: Actual error message text, not "show an error"
- **Fallback chains**: Primary action → graceful degradation → informative error
- **Mobile-specific**: Every scenario is a real mobile situation, not desktop thinking
- **Accessibility as edge case**: Treats a11y as a first-class edge case category
