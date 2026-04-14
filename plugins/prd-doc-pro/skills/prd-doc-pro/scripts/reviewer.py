#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Doc Pro Reviewer — scores PRD documents against a comprehensive rubric.

Parses a PRD markdown file, detects which sections exist, evaluates each
section against quality criteria, and produces a scorecard with actionable
fix suggestions. Designed for SaaS mobile product PRDs.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from core import search_domain


# ──────────────────────────────────────────────
# Section detection patterns
# ──────────────────────────────────────────────

SECTION_PATTERNS = {
    "executive_summary": r"(?i)^#{1,3}\s*(executive\s+summary|overview|tldr|tl;dr)",
    "problem_statement": r"(?i)^#{1,3}\s*(problem\s+statement|problem|the\s+problem|pain\s+point|user\s+pain)",
    "target_users": r"(?i)^#{1,3}\s*(target\s+users?|personas?|target\s+audience|user\s+segments?|who\s+is\s+this\s+for)",
    "goals_objectives": r"(?i)^#{1,3}\s*(goals?|objectives?|okr|goals?\s*(and|&)\s*objectives?|success\s+criteria)",
    "success_metrics": r"(?i)^#{1,3}\s*(success\s+metrics?|kpi|metrics?|measurement|how\s+we\s+measure)",
    "user_stories": r"(?i)^#{1,3}\s*(user\s+stor(y|ies)|requirements|functional\s+requirements?|features?|use\s+cases?)",
    "acceptance_criteria": r"(?i)^#{1,3}\s*(acceptance\s+criteria|ac\b|definition\s+of\s+done|done\s+criteria)",
    "out_of_scope": r"(?i)^#{1,3}\s*(out\s+of\s+scope|non[- ]?goals?|what\s+we.*not|exclusions?|scope\s+exclusion)",
    "guardrail_metrics": r"(?i)^#{1,3}\s*(guardrail|guard\s+rail|do\s+not\s+regress|protect|safety\s+metrics?)",
    "edge_cases": r"(?i)^#{1,3}\s*(edge\s+cases?|error\s+handling|failure\s+modes?|boundary|exception|what\s+if)",
    "design_ux": r"(?i)^#{1,3}\s*(design|ux|ui|wireframe|mockup|user\s+experience|visual|layout)",
    "technical": r"(?i)^#{1,3}\s*(technical|architecture|tech\s+spec|implementation|system\s+design|api|data\s+model)",
    "dependencies": r"(?i)^#{1,3}\s*(dependenc|blocked|prerequisite|upstream|downstream|integration)",
    "launch_rollout": r"(?i)^#{1,3}\s*(launch|rollout|release|go[- ]?live|deployment|rollback|phased)",
    "risks": r"(?i)^#{1,3}\s*(risk|mitigation|contingenc|threat|what\s+could\s+go\s+wrong)",
    "open_questions": r"(?i)^#{1,3}\s*(open\s+questions?|tbd|to\s+be\s+determined|unresolved|decisions?\s+needed)",
    "changelog": r"(?i)^#{1,3}\s*(changelog|change\s+log|revision|version\s+history|updates?)",
    "mobile_considerations": r"(?i)^#{1,3}\s*(mobile|platform|ios|android|app\s+store|play\s+store|device|responsive|offline)",
    "non_functional": r"(?i)^#{1,3}\s*(non[- ]?functional|nfr|performance|scalability|security|reliability|availability)",
    "stakeholder_map": r"(?i)^#{1,3}\s*(stakeholder|raci|responsible|accountable|consulted|informed|decision\s+maker)",
}


# ──────────────────────────────────────────────
# Rubric — each check is a (name, description, checker_fn) tuple
# checker_fn receives section_text and full_text, returns (pass, detail)
# ──────────────────────────────────────────────

def _has_numbers(text: str) -> bool:
    return bool(re.search(r"\d+[%$€£]|\d{2,}|\$\d|\d+\s*(percent|users?|customers?|requests?|seconds?|ms|minutes?|hours?|days?|weeks?|months?)", text, re.I))


def _has_specific_persona(text: str) -> bool:
    generic = re.findall(r"(?i)\bas\s+a\s+user\b", text)
    specific = re.findall(r"(?i)\bas\s+a[n]?\s+(?!user\b)\w+", text)
    return len(specific) > len(generic)


def _has_so_that(text: str) -> bool:
    stories = re.findall(r"(?i)\bas\s+a", text)
    so_thats = re.findall(r"(?i)\bso\s+that\b", text)
    if not stories:
        return True  # no stories = not applicable
    return len(so_thats) >= len(stories) * 0.5


def _count_ac(text: str) -> int:
    patterns = [
        r"(?i)given\s+.+when\s+.+then\s+",
        r"(?i)acceptance\s+criteria",
        r"(?im)^[\s]*[-*]\s*\[[\sx]?\]",  # checkbox items
        r"(?im)^[\s]*(?:AC|ac)[\s-]*\d",
    ]
    count = 0
    for p in patterns:
        count += len(re.findall(p, text))
    return count


def _has_baseline_target(text: str) -> bool:
    baseline = bool(re.search(r"(?i)(baseline|current(ly)?|today|as[- ]is|from\s+\d)", text))
    target = bool(re.search(r"(?i)(target|goal|to\s+\d|reach\s+\d|achieve|increase.*to|decrease.*to|improve.*to|within\s+\d)", text))
    return baseline and target


def _has_timeframe(text: str) -> bool:
    return bool(re.search(r"(?i)(by\s+(q[1-4]|january|february|march|april|may|june|july|august|september|october|november|december|end\s+of|week|sprint)|within\s+\d+\s*(day|week|month|quarter|sprint)|\d+\s*days?|\d+\s*weeks?|\d+\s*months?|timeline|deadline|due\s+date|\d{4}[-/]\d{2}|post[- ]?launch|timeframe|ongoing)", text))


def _has_formula(text: str) -> bool:
    return bool(re.search(r"(?i)(formula|calculated|=|÷|×|ratio|rate\s*=|sum\s+of|count\s+of|number\s+of.*divided)", text))


def _mentions_solution_in_problem(text: str) -> bool:
    solution_words = re.findall(r"(?i)\b(build|implement|add|create|develop|replace|migrate|install|deploy|integrate|use\s+\w+\s+library)\b", text)
    pain_words = re.findall(r"(?i)\b(pain|struggle|frustrated|confused|fail|error|slow|expensive|waste|lose|abandon|churn|drop|decline|complain)\b", text)
    return len(solution_words) > len(pain_words) + 1


def _has_mobile_context(text: str) -> bool:
    return bool(re.search(r"(?i)\b(mobile|ios|android|app\s+store|play\s+store|push\s+notif|offline|gesture|touch|swipe|tap|biometric|camera|gps|location|deep\s*link|responsive|device|screen\s+size|portrait|landscape)\b", text))


def _has_offline_handling(text: str) -> bool:
    return bool(re.search(r"(?i)\b(offline|no\s+connect|network\s+(fail|error|unavailable)|airplane|cached?|sync|queue)", text))


def _has_permission_strategy(text: str) -> bool:
    return bool(re.search(r"(?i)\b(permission|allow|deny|grant|camera\s+access|location\s+access|notification\s+access|photo\s+library|microphone|att\b|app\s+tracking|privacy\s+prompt)", text))


def _is_testable_ac(text: str) -> bool:
    vague = len(re.findall(r"(?i)\b(works?\s+correctly|is\s+fast|is\s+good|is\s+nice|is\s+clean|looks?\s+good|performs?\s+well|is\s+user[- ]friendly|intuitive|seamless)\b", text))
    measurable = len(re.findall(r"(?i)\b(within\s+\d|less\s+than\s+\d|at\s+least\s+\d|exactly\s+\d|returns?\s+\d|shows?\s+(error|message|dialog|toast)|displays?|navigates?\s+to|redirects?\s+to|must\s+(not\s+)?exceed|<\s*\d|>\s*\d|\d+\s*(ms|s|seconds?|MB|KB|px))\b", text))
    return measurable > vague


# ──────────────────────────────────────────────
# Rubric definition
# ──────────────────────────────────────────────

RUBRIC = {
    "problem_statement": {
        "weight": 15,
        "section_required": True,
        "checks": [
            {
                "id": "quantified_pain",
                "name": "Problem is quantified with data",
                "desc": "Includes specific numbers: %, counts, dollar amounts, time impacts",
                "check": lambda sec, full: (
                    _has_numbers(sec),
                    "Add specific data: %, user counts, dollar impact, time wasted"
                ),
            },
            {
                "id": "no_solution_leaking",
                "name": "Describes pain, not a solution",
                "desc": "Problem statement talks about user pain, not a feature to build",
                "check": lambda sec, full: (
                    not _mentions_solution_in_problem(sec),
                    "Rewrite to describe what users suffer, not what to build. Ask: 'What pain does the user feel?'"
                ),
            },
            {
                "id": "user_impact",
                "name": "States who is affected and how",
                "desc": "Names specific user types and describes their pain",
                "check": lambda sec, full: (
                    bool(re.search(r"(?i)(user|customer|team|admin|manager|developer|patient|student|buyer|seller|merchant|creator|viewer|subscriber|member)", sec)),
                    "Name the specific people affected (not just 'users') and how they suffer"
                ),
            },
            {
                "id": "business_impact",
                "name": "Connects to business outcome",
                "desc": "Links the problem to revenue, retention, cost, or strategic goal",
                "check": lambda sec, full: (
                    bool(re.search(r"(?i)(revenue|churn|retention|cost|conversion|arr|mrr|nps|support\s+ticket|ltv|cac|roi|profit|loss|cancel|downgrade)", sec)),
                    "Add business impact: revenue at risk, churn caused, support cost, conversion loss"
                ),
            },
        ],
    },
    "target_users": {
        "weight": 10,
        "section_required": True,
        "checks": [
            {
                "id": "specific_personas",
                "name": "Personas are specific and named",
                "desc": "Uses named roles, not generic 'users'",
                "check": lambda sec, full: (
                    _has_specific_persona(sec) or bool(re.search(r"(?i)(persona|segment|role|archetype|profile).*:", sec)),
                    "Define 2-3 specific personas with names, roles, and context. Never use generic 'user'"
                ),
            },
            {
                "id": "persona_context",
                "name": "Personas have context and motivation",
                "desc": "Each persona includes what they do, why they care, and what frustrates them",
                "check": lambda sec, full: (
                    len(sec.split()) > 50,
                    "Each persona needs: role description, key goal, main frustration, technical comfort level"
                ),
            },
        ],
    },
    "goals_objectives": {
        "weight": 10,
        "section_required": True,
        "checks": [
            {
                "id": "goals_not_features",
                "name": "Goals describe outcomes, not features",
                "desc": "Goals state WHY (business outcomes) not WHAT (features to build)",
                "check": lambda sec, full: (
                    bool(re.search(r"(?i)(increase|decrease|reduce|improve|achieve|enable|ensure|maintain|grow)", sec))
                    and not bool(re.search(r"(?i)^#{1,3}\s*(add|build|create|implement|deploy)\b", sec, re.M)),
                    "Goals should start with outcome verbs (increase, reduce, improve), not build verbs (add, create, implement)"
                ),
            },
            {
                "id": "goals_measurable",
                "name": "Goals are measurable",
                "desc": "Each goal has a specific, quantifiable target",
                "check": lambda sec, full: (
                    _has_numbers(sec),
                    "Add numbers to every goal: 'Increase X from Y% to Z% by Q2'"
                ),
            },
        ],
    },
    "success_metrics": {
        "weight": 15,
        "section_required": True,
        "checks": [
            {
                "id": "has_baseline",
                "name": "Metrics include baselines",
                "desc": "Current/baseline values are stated for each metric",
                "check": lambda sec, full: (
                    _has_baseline_target(sec),
                    "Every metric needs: current baseline → target value. If unknown, state 'Baseline TBD — instrument before launch'"
                ),
            },
            {
                "id": "has_timeframe",
                "name": "Metrics have timeframes",
                "desc": "Each metric states when the target should be hit",
                "check": lambda sec, full: (
                    _has_timeframe(sec),
                    "Add timeframe to each metric: 'within 30 days of launch', 'by end of Q2'"
                ),
            },
            {
                "id": "has_formula",
                "name": "Metrics have measurement method",
                "desc": "States how each metric is calculated or where it's tracked",
                "check": lambda sec, full: (
                    _has_formula(sec) or bool(re.search(r"(?i)(track|measure|instrument|mixpanel|amplitude|firebase|analytics|event|dashboard|report)", sec)),
                    "For each metric, state: how it's calculated and where it's tracked (tool/dashboard)"
                ),
            },
            {
                "id": "mobile_metrics",
                "name": "Includes mobile-specific KPIs",
                "desc": "For mobile products: crash rate, ANR, app store rating, session length, push opt-in",
                "check": lambda sec, full: (
                    _has_mobile_context(full) and (
                        bool(re.search(r"(?i)(crash|anr|app\s+store\s+rat|session\s+length|push\s+opt|install|uninstall|dau|mau|retention\s+d[137]|app\s+size)", sec))
                        or not _has_mobile_context(full)
                    ),
                    "Add mobile KPIs: crash-free rate, app store rating, DAU/MAU, D1/D7/D30 retention, session length"
                ),
            },
        ],
    },
    "user_stories": {
        "weight": 20,
        "section_required": True,
        "checks": [
            {
                "id": "specific_persona_in_stories",
                "name": "Stories use specific personas",
                "desc": "Uses named persona, not 'As a user'",
                "check": lambda sec, full: (
                    _has_specific_persona(sec),
                    "Replace every 'As a user' with a specific persona: 'As a sales manager', 'As a first-time subscriber'"
                ),
            },
            {
                "id": "has_so_that",
                "name": "Stories have 'so that' clauses",
                "desc": "Every story explains the value/outcome",
                "check": lambda sec, full: (
                    _has_so_that(sec),
                    "Add 'so that [outcome]' to every story — it's the business justification"
                ),
            },
            {
                "id": "has_acceptance_criteria",
                "name": "Stories have acceptance criteria",
                "desc": "At least 3 AC per story, using Given/When/Then or checklist format",
                "check": lambda sec, full: (
                    _count_ac(sec) >= 3 or bool(re.search(r"(?i)(given|when|then|criteria|checkbox|\[[\sx]?\])", sec)),
                    "Add at least 3 acceptance criteria per story. Use Given/When/Then for complex flows"
                ),
            },
            {
                "id": "ac_is_testable",
                "name": "Acceptance criteria are testable",
                "desc": "AC uses measurable language, not 'works correctly' or 'is fast'",
                "check": lambda sec, full: (
                    _is_testable_ac(sec),
                    "Replace vague AC ('works correctly', 'is fast') with measurable criteria ('loads in <2s', 'shows error toast')"
                ),
            },
            {
                "id": "sprint_sized",
                "name": "Stories are sprint-sized",
                "desc": "No epic-sized stories that bundle multiple features",
                "check": lambda sec, full: (
                    len(re.findall(r"(?i)\band\s+(also|then|additionally|furthermore|plus)\b", sec)) < 3,
                    "Split stories that contain 'and also', 'and then' — each story should be completable in 1 sprint"
                ),
            },
        ],
    },
    "out_of_scope": {
        "weight": 5,
        "section_required": True,
        "checks": [
            {
                "id": "explicit_exclusions",
                "name": "Exclusions are explicit and specific",
                "desc": "Lists specific features/items that are NOT included, not vague statements",
                "check": lambda sec, full: (
                    len(re.findall(r"(?im)^[\s]*[-*•]\s+\S", sec)) >= 3,
                    "List at least 3 specific items that are out of scope with brief rationale"
                ),
            },
        ],
    },
    "guardrail_metrics": {
        "weight": 8,
        "section_required": False,
        "checks": [
            {
                "id": "guardrails_exist",
                "name": "Guardrail metrics are defined",
                "desc": "Lists metrics that must NOT regress when the feature ships",
                "check": lambda sec, full: (
                    bool(re.search(r"(?i)(must\s+not|should\s+not|do\s+not|cannot|doesn't|won't|not\s+(drop|decrease|increase|exceed|regress|degrade)|floor|ceiling|threshold|maintain|protect)", sec or full)),
                    "Add 2-3 guardrail metrics: 'D30 retention must not drop below 65%', 'P95 latency must stay under 200ms'"
                ),
            },
        ],
    },
    "edge_cases": {
        "weight": 7,
        "section_required": False,
        "checks": [
            {
                "id": "edge_cases_listed",
                "name": "Edge cases are documented",
                "desc": "Error states, empty states, boundary conditions, failure modes listed",
                "check": lambda sec, full: (
                    bool(re.search(r"(?i)(what\s+if|error|empty|no\s+data|no\s+connection|timeout|invalid|malformed|exceed|boundary|overflow|zero|null|duplicate|concurrent|race\s+condition|offline|killed|expir|fallback|queue|delay|multiple\s+device)", sec or full)),
                    "Document edge cases: What if input is invalid? What if network fails? What if data is empty? What if user has no permissions?"
                ),
            },
            {
                "id": "mobile_edge_cases",
                "name": "Mobile-specific edge cases covered",
                "desc": "Offline, background/foreground, interruptions, low battery, slow network",
                "check": lambda sec, full: (
                    not _has_mobile_context(full) or bool(re.search(r"(?i)(offline|background|foreground|interrupt|low\s+battery|slow\s+(network|connection)|airplane|phone\s+call|notification\s+interrupt|app\s+kill|force\s+close|memory\s+warning)", sec or full)),
                    "Add mobile edge cases: offline mode, app backgrounded, phone call interruption, low battery, slow 3G"
                ),
            },
        ],
    },
    "design_ux": {
        "weight": 5,
        "section_required": False,
        "checks": [
            {
                "id": "design_referenced",
                "name": "Design assets or principles referenced",
                "desc": "Links to mockups, wireframes, or states design principles",
                "check": lambda sec, full: (
                    bool(re.search(r"(?i)(figma|sketch|wireframe|mockup|prototype|design\s+system|component|layout|navigation|flow)", sec or full)),
                    "Link to design assets (Figma, wireframes) or describe key design principles and navigation flow"
                ),
            },
        ],
    },
    "launch_rollout": {
        "weight": 5,
        "section_required": False,
        "checks": [
            {
                "id": "rollout_plan",
                "name": "Rollout strategy defined",
                "desc": "Phased rollout, feature flags, or launch criteria specified",
                "check": lambda sec, full: (
                    bool(re.search(r"(?i)(phase|rollout|feature\s+flag|canary|beta|staged|gradual|percent|%\s+of\s+users?|a/b\s+test|rollback|kill\s+switch)", sec or full)),
                    "Define rollout strategy: phased rollout %, feature flags, beta criteria, rollback triggers"
                ),
            },
        ],
    },
}

# Sections that must exist in any good PRD
CRITICAL_SECTIONS = ["problem_statement", "target_users", "success_metrics", "user_stories", "out_of_scope"]
HIGH_SECTIONS = ["goals_objectives", "guardrail_metrics", "edge_cases", "launch_rollout"]
MOBILE_SECTIONS = ["mobile_considerations"]


# ──────────────────────────────────────────────
# PRD Parser
# ──────────────────────────────────────────────

def parse_prd(text: str) -> Dict[str, str]:
    """Parse a PRD markdown file into sections by detecting headers."""
    sections_found: Dict[str, str] = {}
    lines = text.split("\n")

    # Find all section boundaries
    boundaries: List[Tuple[int, str]] = []
    for i, line in enumerate(lines):
        for sec_key, pattern in SECTION_PATTERNS.items():
            if re.match(pattern, line.strip()):
                boundaries.append((i, sec_key))
                break

    # Extract text between boundaries
    for idx, (line_num, sec_key) in enumerate(boundaries):
        if idx + 1 < len(boundaries):
            end_line = boundaries[idx + 1][0]
        else:
            end_line = len(lines)
        section_text = "\n".join(lines[line_num:end_line])
        sections_found[sec_key] = section_text

    return sections_found


# ──────────────────────────────────────────────
# Review Engine
# ──────────────────────────────────────────────

def review_prd(text: str, strict: bool = False, is_mobile: bool = False) -> Dict:
    """
    Review a PRD document and produce a detailed scorecard.

    Returns:
        {
            "score": int (0-100),
            "grade": str,
            "sections_found": [...],
            "sections_missing": [...],
            "section_scores": {section: {score, max, checks: [...]}},
            "top_issues": [...],
            "suggestions": [...],
            "fill_in_required": [...],
        }
    """
    # Auto-detect mobile context
    if not is_mobile:
        is_mobile = _has_mobile_context(text)

    sections = parse_prd(text)
    full_text = text

    total_score = 0
    total_max = 0
    section_scores = {}
    all_issues = []
    fill_in_required = []

    # Score each rubric section
    for rubric_key, rubric in RUBRIC.items():
        weight = rubric["weight"]
        checks = rubric["checks"]
        section_text = sections.get(rubric_key, "")
        section_exists = rubric_key in sections

        sec_score = 0
        sec_max = 0
        check_results = []

        if not section_exists and rubric["section_required"]:
            # Missing required section — zero score, flag as critical issue
            sec_max = weight
            all_issues.append({
                "severity": "CRITICAL",
                "section": rubric_key,
                "issue": f"Missing required section: {rubric_key.replace('_', ' ').title()}",
                "fix": f"Add a '{rubric_key.replace('_', ' ').title()}' section to your PRD",
                "impact": weight,
            })
            fill_in_required.append({
                "section": rubric_key.replace("_", " ").title(),
                "what_to_fill": _get_fill_guidance(rubric_key),
            })
        elif section_exists:
            for check in checks:
                # Skip mobile-specific checks for non-mobile products
                if "mobile" in check["id"] and not is_mobile:
                    continue

                check_weight = weight / len(checks)
                sec_max += check_weight
                passed, detail = check["check"](section_text, full_text)

                if passed:
                    sec_score += check_weight
                    check_results.append({
                        "id": check["id"],
                        "name": check["name"],
                        "passed": True,
                    })
                else:
                    check_results.append({
                        "id": check["id"],
                        "name": check["name"],
                        "passed": False,
                        "fix": detail,
                    })
                    severity = "HIGH" if check_weight >= 3 else "MEDIUM"
                    all_issues.append({
                        "severity": severity,
                        "section": rubric_key,
                        "issue": f"{check['name']}: {check['desc']}",
                        "fix": detail,
                        "impact": check_weight,
                    })
        else:
            # Optional section not present — partial penalty in strict mode
            if strict:
                sec_max = weight * 0.3
                all_issues.append({
                    "severity": "LOW",
                    "section": rubric_key,
                    "issue": f"Optional section missing: {rubric_key.replace('_', ' ').title()}",
                    "fix": f"Consider adding '{rubric_key.replace('_', ' ').title()}' for a more complete PRD",
                    "impact": weight * 0.3,
                })
            else:
                sec_max = 0

        total_score += sec_score
        total_max += sec_max if sec_max > 0 else 0

        section_scores[rubric_key] = {
            "score": round(sec_score, 1),
            "max": round(sec_max, 1),
            "pct": round((sec_score / sec_max * 100) if sec_max > 0 else 0),
            "checks": check_results,
            "exists": section_exists,
        }

    # Check for missing critical and high sections in full doc
    found_keys = set(sections.keys())
    missing_critical = [s for s in CRITICAL_SECTIONS if s not in found_keys]
    missing_high = [s for s in HIGH_SECTIONS if s not in found_keys]
    missing_mobile = [s for s in MOBILE_SECTIONS if s not in found_keys] if is_mobile else []

    # Calculate final score
    final_score = round((total_score / total_max * 100) if total_max > 0 else 0)
    final_score = max(0, min(100, final_score))

    # Grade
    if final_score >= 90:
        grade = "EXCELLENT"
    elif final_score >= 75:
        grade = "GOOD"
    elif final_score >= 60:
        grade = "NEEDS WORK"
    elif final_score >= 40:
        grade = "WEAK"
    else:
        grade = "CRITICAL"

    # Sort issues by severity and impact
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    all_issues.sort(key=lambda x: (severity_order.get(x["severity"], 9), -x["impact"]))

    # Generate actionable suggestions from knowledge base
    suggestions = _generate_suggestions(all_issues, is_mobile)

    return {
        "score": final_score,
        "grade": grade,
        "is_mobile": is_mobile,
        "sections_found": sorted(found_keys),
        "sections_missing_critical": missing_critical,
        "sections_missing_high": missing_high,
        "sections_missing_mobile": missing_mobile,
        "section_scores": section_scores,
        "top_issues": all_issues[:10],
        "all_issues": all_issues,
        "suggestions": suggestions,
        "fill_in_required": fill_in_required,
    }


def _get_fill_guidance(section_key: str) -> str:
    """Return specific guidance on what to fill in for a missing section."""
    guidance = {
        "problem_statement": (
            "Write 2-3 sentences describing the user pain with specific data.\n"
            "Required: (1) Who is affected? (2) What do they suffer? (3) How bad is it (numbers)? (4) What's the business impact?\n"
            "Example: '62% of users who sign up abandon onboarding before step 3. Exit surveys show confusion at the connect-your-data step. "
            "This costs ~140 potential activations/week at current signup volume ($28K/mo in lost MRR).'"
        ),
        "target_users": (
            "Define 2-3 specific personas. For each persona include:\n"
            "- Name/role (e.g., 'Sarah — Sales Manager')\n"
            "- What they do day-to-day\n"
            "- Their primary goal with your product\n"
            "- Their main frustration today\n"
            "- Technical comfort level (beginner/intermediate/advanced)"
        ),
        "goals_objectives": (
            "List 2-4 measurable goals. Each goal needs:\n"
            "- Outcome verb (Increase/Reduce/Improve)\n"
            "- Specific metric with baseline → target\n"
            "- Timeframe\n"
            "Example: 'Increase onboarding completion rate from 40% → 70% within 60 days of launch'"
        ),
        "success_metrics": (
            "Define 3-5 success metrics. Each metric needs:\n"
            "- Metric name and definition\n"
            "- Formula or measurement method\n"
            "- Current baseline (or 'TBD — instrument before launch')\n"
            "- Target value and timeframe\n"
            "- Tracking tool (Mixpanel, Amplitude, Firebase, etc.)\n"
            "For mobile: include crash-free rate, app store rating, DAU/MAU, retention curves"
        ),
        "user_stories": (
            "Write 5-10 user stories in format: 'As a [specific persona], I want to [action] so that [outcome]'\n"
            "Each story needs:\n"
            "- Specific persona (never 'As a user')\n"
            "- Clear action\n"
            "- Business value ('so that' clause)\n"
            "- 3+ acceptance criteria (Given/When/Then or checklist)\n"
            "- Edge cases for that story"
        ),
        "out_of_scope": (
            "List 5+ specific items NOT included in this release:\n"
            "- Feature name + brief reason (e.g., 'Scheduled imports — Phase 2')\n"
            "- Platform exclusions (e.g., 'Tablet-optimized layout — post-GA')\n"
            "- Integration exclusions\n"
            "Write this BEFORE requirements to prevent scope creep"
        ),
        "guardrail_metrics": (
            "List 2-3 metrics that must NOT regress when this ships:\n"
            "- Format: '[Metric] must not [drop below / exceed] [threshold]'\n"
            "- Example: 'D30 retention of existing users must not drop below 65%'\n"
            "- Example: 'App cold start time must stay under 2s'\n"
            "- Example: 'Support ticket volume must not increase by more than 10%'"
        ),
        "edge_cases": (
            "For each user story, document:\n"
            "- What if the input is invalid?\n"
            "- What if the network fails?\n"
            "- What if the user has no data (empty state)?\n"
            "- What if they're on a slow connection?\n"
            "For mobile: What if app is backgrounded? Phone call interrupts? Low battery? Offline?"
        ),
    }
    return guidance.get(section_key, "Fill in this section with relevant detail for your product.")


def _generate_suggestions(issues: List[Dict], is_mobile: bool) -> List[str]:
    """Generate search commands the user can run to get help fixing issues."""
    suggestions = []
    seen_domains = set()

    for issue in issues[:5]:
        section = issue["section"]
        if section in ("problem_statement", "goals_objectives") and "antipattern" not in seen_domains:
            suggestions.append(f'python3 search.py "problem statement quantified evidence" --domain antipattern')
            seen_domains.add("antipattern")
        elif section == "user_stories" and "user-story" not in seen_domains:
            suggestions.append(f'python3 search.py "user story acceptance criteria" --domain user-story')
            seen_domains.add("user-story")
        elif section == "success_metrics" and "metric" not in seen_domains:
            query = "mobile app retention engagement" if is_mobile else "saas activation conversion"
            suggestions.append(f'python3 search.py "{query}" --domain metric')
            seen_domains.add("metric")
        elif section in ("edge_cases", "launch_rollout") and "section" not in seen_domains:
            suggestions.append(f'python3 search.py "edge cases error handling" --domain section')
            seen_domains.add("section")

    return suggestions


# ──────────────────────────────────────────────
# Output renderers
# ──────────────────────────────────────────────

def render_scorecard(result: Dict, output_format: str = "ascii") -> str:
    if output_format == "markdown":
        return _render_scorecard_markdown(result)
    return _render_scorecard_ascii(result)


def _render_scorecard_ascii(r: Dict) -> str:
    w = 60
    out = []

    out.append("═" * w)
    out.append(f"  PRD REVIEW SCORECARD")
    out.append("═" * w)

    # Overall score
    score = r["score"]
    grade = r["grade"]
    bar_filled = round(score / 10)
    bar_empty = 10 - bar_filled
    bar = "■" * bar_filled + "░" * bar_empty

    out.append(f"\n  OVERALL SCORE:  {score}/100  [{grade}]")
    out.append(f"  {bar}")

    if r["is_mobile"]:
        out.append(f"  Mobile product detected: YES")

    # Section scores
    out.append(f"\n  SECTION SCORES:")
    out.append(f"  {'Section':<30} {'Score':>8}  Bar")
    out.append(f"  {'─' * 30} {'─' * 8}  {'─' * 12}")

    for sec_key, sec_data in r["section_scores"].items():
        if not sec_data["exists"] and sec_data["max"] == 0:
            continue
        label = sec_key.replace("_", " ").title()[:28]
        pct = sec_data["pct"]
        sec_bar_filled = round(pct / 10)
        sec_bar_empty = 10 - sec_bar_filled
        sec_bar = "■" * sec_bar_filled + "░" * sec_bar_empty

        score_str = f"{sec_data['score']:.0f}/{sec_data['max']:.0f}"
        status = ""
        if not sec_data["exists"]:
            status = " ← MISSING"
        elif pct < 40:
            status = " ← CRITICAL"
        elif pct < 60:
            status = " ← WEAK"

        out.append(f"  {label:<30} {score_str:>8}  {sec_bar}{status}")

    # Missing sections
    if r["sections_missing_critical"]:
        out.append(f"\n  MISSING CRITICAL SECTIONS:")
        for s in r["sections_missing_critical"]:
            out.append(f"    ✗ {s.replace('_', ' ').title()}")

    if r["sections_missing_high"]:
        out.append(f"\n  MISSING HIGH-PRIORITY SECTIONS:")
        for s in r["sections_missing_high"]:
            out.append(f"    ○ {s.replace('_', ' ').title()}")

    if r["sections_missing_mobile"]:
        out.append(f"\n  MISSING MOBILE SECTIONS:")
        for s in r["sections_missing_mobile"]:
            out.append(f"    ○ {s.replace('_', ' ').title()}")

    # Top issues
    if r["top_issues"]:
        out.append(f"\n  TOP ISSUES (by impact):")
        for i, issue in enumerate(r["top_issues"][:7], 1):
            sev = issue["severity"]
            section_label = issue["section"].replace("_", " ").title()
            out.append(f"\n  {i}. [{sev}] {issue['issue']}")
            out.append(f"     Section: {section_label}")
            out.append(f"     Fix: {issue['fix']}")

    # Fill-in required
    if r["fill_in_required"]:
        out.append(f"\n  {'═' * w}")
        out.append(f"  SECTIONS THAT NEED YOUR INPUT:")
        out.append(f"  {'═' * w}")
        for item in r["fill_in_required"]:
            out.append(f"\n  ▸ {item['section']}")
            for line in item["what_to_fill"].split("\n"):
                out.append(f"    {line}")

    # Suggestions
    if r["suggestions"]:
        out.append(f"\n  SUGGESTED COMMANDS:")
        for s in r["suggestions"]:
            out.append(f"  → {s}")

    out.append("\n" + "═" * w)
    return "\n".join(out)


def _render_scorecard_markdown(r: Dict) -> str:
    lines = []

    score = r["score"]
    grade = r["grade"]

    lines.append(f"# PRD Review Scorecard")
    lines.append(f"\n**Overall Score: {score}/100** — {grade}")

    if r["is_mobile"]:
        lines.append(f"**Mobile product detected:** Yes")

    # Section scores table
    lines.append(f"\n## Section Scores")
    lines.append("| Section | Score | Status |")
    lines.append("|---------|-------|--------|")

    for sec_key, sec_data in r["section_scores"].items():
        if not sec_data["exists"] and sec_data["max"] == 0:
            continue
        label = sec_key.replace("_", " ").title()
        pct = sec_data["pct"]

        if not sec_data["exists"]:
            status = "MISSING"
        elif pct >= 80:
            status = "Good"
        elif pct >= 60:
            status = "Needs Work"
        elif pct >= 40:
            status = "Weak"
        else:
            status = "Critical"

        lines.append(f"| {label} | {sec_data['score']:.0f}/{sec_data['max']:.0f} ({pct}%) | {status} |")

    # Missing sections
    if r["sections_missing_critical"]:
        lines.append(f"\n## Missing Critical Sections")
        for s in r["sections_missing_critical"]:
            lines.append(f"- **{s.replace('_', ' ').title()}**")

    # Top issues
    if r["top_issues"]:
        lines.append(f"\n## Top Issues")
        for i, issue in enumerate(r["top_issues"][:7], 1):
            lines.append(f"\n### {i}. [{issue['severity']}] {issue['issue']}")
            lines.append(f"**Section:** {issue['section'].replace('_', ' ').title()}")
            lines.append(f"**Fix:** {issue['fix']}")

    # Fill-in required
    if r["fill_in_required"]:
        lines.append(f"\n## Sections That Need Your Input")
        for item in r["fill_in_required"]:
            lines.append(f"\n### {item['section']}")
            lines.append(item["what_to_fill"])

    # Suggestions
    if r["suggestions"]:
        lines.append(f"\n## Suggested Commands")
        for s in r["suggestions"]:
            lines.append(f"```bash\n{s}\n```")

    return "\n".join(lines)
