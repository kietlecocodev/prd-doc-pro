#!/usr/bin/env python3
"""Tests for PRD Doc Pro core search engine and all modules."""

import sys
import os
import unittest

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from core import search, search_domain, load_all_rows, AVAILABLE_DOMAINS, CSV_CONFIG
from reviewer import review_prd, parse_prd, render_scorecard
from exporter import export_prd
from platform import generate_mobile_checklist, generate_platform_differences


class TestCoreSearch(unittest.TestCase):
    """Test BM25 search engine across all domains."""

    def test_all_domains_exist(self):
        """Every configured domain should have a loadable CSV."""
        for domain in AVAILABLE_DOMAINS:
            rows = load_all_rows(domain)
            self.assertGreater(len(rows), 0, f"Domain '{domain}' has no rows")

    def test_search_returns_results(self):
        """Basic search should return results for known queries."""
        result = search("saas onboarding activation", domain="product-type")
        self.assertGreater(result["count"], 0)
        self.assertIn("results", result)

    def test_search_unknown_domain(self):
        """Unknown domain should return error."""
        result = search("test", domain="nonexistent")
        self.assertIn("error", result)

    def test_search_all_domains(self):
        """Cross-domain search should return results from multiple domains."""
        result = search("mobile push notification permission")
        self.assertGreater(result["count"], 0)

    def test_mobile_product_types(self):
        """Mobile-specific product types should be findable."""
        result = search_domain("mobile fintech payment app", "product-type", max_results=3)
        types = [r.get("Product Type", "") for r in result["results"]]
        self.assertTrue(any("Mobile" in t or "Fintech" in t for t in types),
                        f"Expected mobile product type, got: {types}")

    def test_mobile_metrics(self):
        """Mobile-specific metrics should be findable."""
        result = search_domain("crash rate app store retention", "metric", max_results=5)
        names = [r.get("Metric Name", "") for r in result["results"]]
        self.assertTrue(any("Crash" in n or "App Store" in n or "Retention" in n for n in names),
                        f"Expected mobile metrics, got: {names}")

    def test_platform_rules(self):
        """Platform rules domain should return results."""
        result = search_domain("in-app purchase apple ios", "platform-rules", max_results=3)
        self.assertGreater(result["count"], 0)

    def test_mobile_ux(self):
        """Mobile UX domain should return results."""
        result = search_domain("bottom navigation tab bar", "mobile-ux", max_results=3)
        self.assertGreater(result["count"], 0)

    def test_mobile_antipatterns(self):
        """Mobile antipatterns should be findable."""
        result = search_domain("permission spam notification abuse", "antipattern", max_results=3)
        names = [r.get("Antipattern Name", "") for r in result["results"]]
        self.assertTrue(any("Permission" in n or "Notification" in n for n in names),
                        f"Expected mobile antipatterns, got: {names}")

    def test_mobile_user_stories(self):
        """Mobile user stories should be findable."""
        result = search_domain("push notification biometric offline", "user-story", max_results=3)
        self.assertGreater(result["count"], 0)


class TestReviewer(unittest.TestCase):
    """Test PRD review engine."""

    GOOD_PRD = """
# Feature PRD

## Problem Statement
62% of users abandon onboarding before step 3. This costs $28K/mo in lost MRR.
Support tickets tagged 'onboarding-fail' increased 34% QoQ. Casual subscribers
and power users are both affected, with power users compensating via workarounds.

## Target Users
### Sarah — Casual User
Role: Marketing manager. Goal: quick setup. Frustration: too many steps. Comfort: beginner.
### Marcus — Power User
Role: Developer. Goal: API integration. Frustration: no docs. Comfort: advanced.

## Goals & Objectives
1. Increase onboarding completion from 40% to 70% within 60 days
2. Reduce support tickets from 340/mo to 170/mo within 60 days

## Success Metrics
| Metric | Baseline | Target | Timeframe |
|--------|----------|--------|-----------|
| Completion rate | 40% | 70% | 60 days post-launch |
| Support tickets | 340/mo | <170/mo | 60 days |
Tracked via Mixpanel onboarding_completed event. Formula: completed / started × 100.
Crash-free session rate must stay above 99.2%.

## User Stories
As a first-time subscriber, I want a 3-step onboarding flow so that I reach value in under 60 seconds.
Given the user completes step 1, when they tap Next, then step 2 loads within 500ms.
Given the user skips a step, then the step is marked optional and doesn't block progress.
As a power user setting up API access, I want inline code examples so that I can make my first API call in under 5 minutes.

## Out of Scope
- Enterprise SSO integration — Phase 2
- Custom branding for onboarding — not planned
- Mobile tablet layout — post-GA
- Offline onboarding — not applicable

## Guardrail Metrics
D30 retention must not drop below 18%. App cold start must not exceed 2.5s.

## Edge Cases
What if the user loses connection during onboarding? Data saved locally, sync on reconnect.
What if the user has no data? Empty state with sample data option.
"""

    BAD_PRD = """
# PRD

## Problem
Users don't like the app. We need to make it better.

## Users
Users of the app.

## Goals
- Make it better
- Add new features

## Stories
- As a user, I want to do things.
"""

    def test_good_prd_scores_high(self):
        result = review_prd(self.GOOD_PRD)
        self.assertGreaterEqual(result["score"], 70, f"Good PRD scored {result['score']}")

    def test_bad_prd_scores_low(self):
        result = review_prd(self.BAD_PRD)
        self.assertLessEqual(result["score"], 40, f"Bad PRD scored {result['score']}")

    def test_missing_sections_detected(self):
        result = review_prd(self.BAD_PRD)
        self.assertGreater(len(result["sections_missing_critical"]), 0)

    def test_scorecard_renders(self):
        result = review_prd(self.GOOD_PRD)
        ascii_output = render_scorecard(result, "ascii")
        self.assertIn("OVERALL SCORE", ascii_output)
        md_output = render_scorecard(result, "markdown")
        self.assertIn("Overall Score", md_output)

    def test_fill_in_required_for_missing(self):
        result = review_prd(self.BAD_PRD)
        self.assertGreater(len(result["fill_in_required"]), 0)

    def test_mobile_detection(self):
        mobile_prd = "# PRD\n## Problem\nOur iOS and Android mobile app has issues."
        result = review_prd(mobile_prd)
        self.assertTrue(result["is_mobile"])

    def test_parse_prd_detects_sections(self):
        sections = parse_prd(self.GOOD_PRD)
        self.assertIn("problem_statement", sections)
        self.assertIn("user_stories", sections)
        self.assertIn("success_metrics", sections)


class TestExporter(unittest.TestCase):
    """Test PRD export formats."""

    SAMPLE = "# Title\n\n## Section\n\n**Bold** and `code`\n\n- Item 1\n- Item 2\n\n| A | B |\n|---|---|\n| 1 | 2 |"

    def test_confluence_export(self):
        result = export_prd(self.SAMPLE, "confluence")
        self.assertIn("h1.", result)
        self.assertIn("h2.", result)

    def test_html_export(self):
        result = export_prd(self.SAMPLE, "html")
        self.assertIn("<h1>", result)
        self.assertIn("<strong>", result)

    def test_text_export(self):
        result = export_prd(self.SAMPLE, "text")
        self.assertNotIn("#", result)
        self.assertNotIn("**", result)

    def test_notion_export(self):
        result = export_prd(self.SAMPLE, "notion")
        self.assertIn("Notion", result)

    def test_unknown_format(self):
        result = export_prd(self.SAMPLE, "pdf")
        self.assertIn("Error", result)


class TestPlatform(unittest.TestCase):
    """Test mobile platform intelligence."""

    def test_generate_checklist(self):
        checklist = generate_mobile_checklist(["ios", "android"])
        self.assertIn("iOS", checklist)
        self.assertIn("Android", checklist)
        self.assertIn("- [ ]", checklist)

    def test_platform_differences(self):
        diff = generate_platform_differences(["ios", "android"])
        self.assertIn("iOS", diff)
        self.assertIn("Android", diff)
        self.assertIn("Navigation", diff)

    def test_feature_detection(self):
        checklist = generate_mobile_checklist(
            ["ios", "android"],
            features=["push notification payment biometric"],
            product_type="Mobile Fintech",
        )
        self.assertIn("Push Notification", checklist)
        self.assertIn("Payment", checklist)
        self.assertIn("Biometric", checklist)

    def test_single_platform(self):
        diff = generate_platform_differences(["ios"])
        self.assertEqual(diff, "")  # No diff for single platform


if __name__ == "__main__":
    unittest.main()
