# Bad Example: User Stories (Mobile E-commerce)

**Score: 1/10** — Generic persona, no AC, epic-sized, no mobile context

---

## User Stories

1. As a user, I want to browse products and add them to my cart so I can buy things.

2. As a user, I want to search for products.

3. As a user, I want to sign up, log in, manage my profile, update my address, change my password, and set notification preferences so that I can use the app.

4. As a user, I want the checkout to work correctly and be fast.

---

## What's Wrong (Annotated)

### Story 1: "Browse and add to cart"
| Antipattern | Issue |
|-------------|-------|
| **Generic persona** | "As a user" — who? A first-time visitor? A returning customer? A bargain hunter? |
| **Missing so-that** | "so I can buy things" is meaningless — every e-commerce app lets you buy things |
| **No AC** | What does "browse" mean? Grid or list? How many products per page? What happens when you add to cart? Animation? Confirmation? |
| **No mobile context** | No mention of touch targets, loading states, or mobile-specific interactions |

### Story 2: "Search for products"
| Antipattern | Issue |
|-------------|-------|
| **No so-that clause** | Why does the user want to search? What problem does search solve for them? |
| **No AC at all** | What does search look like? Autocomplete? Filters? What happens with no results? |
| **Too vague** | This is a feature name, not a user story |

### Story 3: Epic disguised as story
| Antipattern | Issue |
|-------------|-------|
| **Epic-sized** | Contains 6 separate features: signup, login, profile, address, password, notifications |
| **Cannot be completed in a sprint** | Each of these is a separate sprint-sized story |
| **No AC** | Which login methods? Social? Email? Biometric? What are the password rules? |

### Story 4: Vague AC
| Antipattern | Issue |
|-------------|-------|
| **"Work correctly"** | Not testable. What does "correctly" mean? |
| **"Be fast"** | Not measurable. How fast? 1 second? 5 seconds? Under what conditions? |
| **Prescriptive vagueness** | Describes desired quality without any way to verify it |

## How to Fix Each

**Story 1** → Split into: browse catalog (with grid/list toggle), view product detail, add to cart (with animation and undo). Each with 3+ AC.

**Story 2** → "As a shopper looking for a specific product, I want autocomplete search suggestions as I type so that I find products faster with fewer keystrokes on my phone's small keyboard." Add AC for empty results, recent searches, filter chips.

**Story 3** → Split into 6 stories. Each with its own persona and AC. "As a new user downloading the app for the first time, I want to sign up with my email or Apple ID so that I can start shopping within 30 seconds."

**Story 4** → "Checkout completes in ≤3 taps from cart. Payment confirmation screen renders within 2 seconds of payment success. Failed payment shows specific error with retry button."
