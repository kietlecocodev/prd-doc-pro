# Good Example: User Stories with AC (Mobile E-commerce)

**Score: 10/10** — Specific persona, clear value, testable AC, mobile-aware

---

## US-1: Quick Reorder

**As a returning customer who bought coffee beans last month**, I want to reorder my previous purchase with one tap from the home screen **so that** I can restock in under 10 seconds without browsing the catalog.

### Acceptance Criteria

**Given** the user has at least 1 previous order,
**When** they open the app,
**Then** a "Reorder" card appears on the home screen showing their last purchased item with product image, name, price, and quantity.

**Given** the user taps "Reorder",
**When** the item is in stock,
**Then** the item is added to cart and the user is taken directly to checkout (skip cart screen).

**Given** the user taps "Reorder",
**When** the item is out of stock,
**Then** a bottom sheet shows: "This item is currently unavailable" with 2 options: "Notify Me When Available" and "See Similar Products."

**Given** the user taps "Reorder",
**When** the price has changed since their last order,
**Then** the new price is shown with a strikethrough of the old price before adding to cart. User must confirm.

**Given** the user has no previous orders,
**Then** the "Reorder" card is not shown (empty state handled by the "Discover" section).

### Non-Functional
- Reorder card loads within 500ms of home screen render
- Product image is cached locally (no network call for display)
- One-tap reorder completes in ≤2 taps total (tap Reorder → tap Pay)
- Haptic feedback (light impact) on "Reorder" tap confirmation

### Edge Cases
- Item discontinued: Show "This product has been discontinued" + "See Similar"
- Multiple previous orders: Show most recent. "See All Previous Orders" link below
- User on slow 3G: Skeleton loading for product image, text loads first

---

## US-2: Push for Abandoned Cart

**As a shopper who added items to my cart but didn't complete checkout**, I want to receive a reminder notification 2 hours later **so that** I can complete my purchase before the items sell out.

### Acceptance Criteria

**Given** a user has items in cart and closes the app without completing checkout,
**When** 2 hours have passed,
**Then** a push notification is sent: "[Item name] is still in your cart — complete your order before it sells out" with the product thumbnail.

**Given** the user taps the notification,
**Then** the app opens directly to the cart screen (deep link: `myapp://cart`).

**Given** an item in the cart has gone out of stock since abandonment,
**Then** the notification copy changes to: "An item in your cart is selling fast — check out now" and the cart screen shows the out-of-stock item flagged.

**Given** the user has already completed the purchase (via web or another device),
**Then** no notification is sent.

**Given** the user has push notifications disabled for "Promotions" category,
**Then** no abandoned cart notification is sent (this falls under Promotions, not Transactional).

- [ ] Maximum 1 abandoned cart notification per 24-hour period
- [ ] No abandoned cart notification sent between 10pm-8am local time (quiet hours)
- [ ] Notification-to-purchase conversion tracked as `cart_recovery_notification_converted`

---

## Why These Are Good

| Criterion | US-1 | US-2 |
|-----------|------|------|
| Specific persona | "returning customer who bought coffee beans" | "shopper who added items but didn't checkout" |
| Clear value (so that) | "restock in under 10 seconds" | "complete purchase before items sell out" |
| Testable AC | Every AC has Given/When/Then with exact behavior | Every AC has Given/When/Then with exact behavior |
| Edge cases | Out of stock, price change, no orders, slow network | Already purchased, out of stock, quiet hours, opt-out |
| Mobile-specific | Cached image, haptic feedback, 2-tap max | Deep link, push notification, quiet hours |
| Sprint-sized | One feature (reorder card), completable independently | One feature (abandoned cart push), completable independently |
| No implementation details | Says "loads within 500ms" not "use Redis cache" | Says "2 hours later" not "use a cron job" |
