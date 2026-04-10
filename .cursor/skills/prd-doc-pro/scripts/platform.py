#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Doc Pro Platform Intelligence — iOS/Android-aware PRD enrichment.

Automatically appends platform-specific sections, checklists, and compliance
requirements based on the target platform and product type.
"""

from typing import Dict, List, Optional, Set
from core import search_domain


# ──────────────────────────────────────────────
# Platform configuration
# ──────────────────────────────────────────────

PLATFORM_CONFIG = {
    "ios": {
        "name": "iOS",
        "guidelines": "Apple Human Interface Guidelines (HIG)",
        "store": "App Store",
        "store_review": "App Store Review Guidelines",
        "navigation": "Bottom Tab Bar (UITabBarController), Navigation Controller (push/pop)",
        "back_navigation": "Edge swipe gesture + nav bar back button",
        "permissions_api": "Info.plist usage descriptions + runtime prompts",
        "push_service": "APNs via Firebase Cloud Messaging",
        "biometric_api": "LocalAuthentication (Face ID / Touch ID)",
        "secure_storage": "Keychain Services",
        "deep_links": "Universal Links (apple-app-site-association)",
        "analytics": "Firebase Analytics, Amplitude, Mixpanel",
        "crash_reporting": "Firebase Crashlytics, Sentry",
        "widget_framework": "WidgetKit (SwiftUI only)",
        "min_version_note": "Support current and N-2 iOS versions (currently iOS 15+)",
        "required_features": [
            "Sign in with Apple (if offering any social login)",
            "App Tracking Transparency (ATT) prompt for tracking",
            "Privacy Nutrition Label",
            "Dynamic Type support",
            "VoiceOver accessibility",
        ],
        "store_commission": "30% (15% for Small Business Program <$1M/yr)",
        "review_time": "24-48 hours (average), up to 7 days for complex apps",
    },
    "android": {
        "name": "Android",
        "guidelines": "Google Material Design 3",
        "store": "Google Play Store",
        "store_review": "Google Play Developer Policy",
        "navigation": "Bottom Navigation Bar, Navigation Drawer, Navigation Component",
        "back_navigation": "System back button/gesture (predictive back on Android 14+)",
        "permissions_api": "AndroidManifest.xml + runtime permissions (API 23+)",
        "push_service": "Firebase Cloud Messaging (FCM)",
        "biometric_api": "BiometricPrompt API",
        "secure_storage": "Android Keystore",
        "deep_links": "Android App Links (assetlinks.json)",
        "analytics": "Firebase Analytics, Amplitude, Mixpanel",
        "crash_reporting": "Firebase Crashlytics, Sentry",
        "widget_framework": "App Widgets (RemoteViews) / Glance (Jetpack Compose)",
        "min_version_note": "Support API 26+ (Android 8.0) covers 95%+ of active devices",
        "required_features": [
            "Android App Bundle (AAB) format for Play Store",
            "POST_NOTIFICATIONS permission (API 33+)",
            "Data Safety Section",
            "Predictive back gesture support (Android 14+)",
            "TalkBack accessibility",
        ],
        "store_commission": "15% for first $1M/yr, 30% after",
        "review_time": "Hours to 3 days (usually <24 hours)",
    },
}


# ──────────────────────────────────────────────
# Feature-specific platform requirements
# ──────────────────────────────────────────────

FEATURE_PLATFORM_REQUIREMENTS = {
    "push_notification": {
        "ios": [
            "APNs push certificate configured in App Store Connect",
            "Provisional authorization available (quiet notifications without prompt)",
            "Notification Service Extension for rich media (images, custom UI)",
            "Notification Content Extension for interactive notifications",
            "Critical Alerts entitlement required for health/safety apps",
        ],
        "android": [
            "FCM server key configured in Firebase Console",
            "POST_NOTIFICATIONS runtime permission required (API 33+)",
            "Notification channels required (API 26+) — one channel per category",
            "Foreground service notification required for background work",
            "Big picture / big text notification styles for rich content",
        ],
    },
    "biometric_auth": {
        "ios": [
            "Face ID: NSFaceIDUsageDescription in Info.plist",
            "Touch ID: handled automatically by LocalAuthentication",
            "Keychain with kSecAttrAccessibleWhenUnlockedThisDeviceOnly",
            "Fallback to device passcode (not custom PIN) via LAContext",
        ],
        "android": [
            "BiometricPrompt with BIOMETRIC_STRONG or BIOMETRIC_WEAK",
            "AndroidKeystore for cryptographic key storage",
            "Fallback to device credential (PIN/pattern/password)",
            "Handle BiometricManager.canAuthenticate() for capability check",
        ],
    },
    "camera": {
        "ios": [
            "NSCameraUsageDescription in Info.plist (required)",
            "NSPhotoLibraryUsageDescription for saving to camera roll",
            "AVCaptureSession for custom camera UI",
            "PHPickerViewController for photo library selection (no permission needed)",
        ],
        "android": [
            "CAMERA permission in manifest + runtime request",
            "READ_MEDIA_IMAGES (API 33+) or READ_EXTERNAL_STORAGE (older)",
            "CameraX API (Jetpack) recommended over Camera2",
            "Photo picker (API 33+) for gallery selection (no permission needed)",
        ],
    },
    "location": {
        "ios": [
            "NSLocationWhenInUseUsageDescription in Info.plist",
            "NSLocationAlwaysAndWhenInUseUsageDescription for background",
            "Core Location with desired accuracy levels",
            "Significant Location Changes for battery-efficient background tracking",
        ],
        "android": [
            "ACCESS_FINE_LOCATION + ACCESS_COARSE_LOCATION permissions",
            "ACCESS_BACKGROUND_LOCATION requires separate prompt (API 29+)",
            "Fused Location Provider (Google Play Services) recommended",
            "Geofencing API for region monitoring",
        ],
    },
    "payment": {
        "ios": [
            "StoreKit 2 for in-app purchases and subscriptions",
            "Apple Pay (PassKit) for physical goods/services",
            "Server-side receipt validation (AppStoreServerAPI)",
            "'Restore Purchases' button required on paywall screen",
        ],
        "android": [
            "Google Play Billing Library v6+ for digital goods",
            "Google Pay API for physical goods/services",
            "Server-side purchase verification (Google Play Developer API)",
            "Pending purchases handling for slow network scenarios",
        ],
    },
    "offline": {
        "ios": [
            "Core Data or SwiftData for local persistence",
            "Network.framework NWPathMonitor for connectivity detection",
            "Background App Refresh for periodic sync",
            "NSUbiquitousKeyValueStore for lightweight cross-device sync",
        ],
        "android": [
            "Room database for local persistence",
            "ConnectivityManager for network state",
            "WorkManager for reliable background sync",
            "DataStore for key-value preferences",
        ],
    },
}


# ──────────────────────────────────────────────
# Mobile checklist generator
# ──────────────────────────────────────────────

def generate_mobile_checklist(
    platforms: List[str],
    features: Optional[List[str]] = None,
    product_type: str = "",
) -> str:
    """Generate a platform-specific checklist for a mobile PRD."""
    lines = []
    lines.append("## Mobile Platform Checklist")
    lines.append("")

    target_platforms = [p.lower().strip() for p in platforms if p.lower().strip() in PLATFORM_CONFIG]
    if not target_platforms:
        target_platforms = ["ios", "android"]

    # Universal mobile checklist
    lines.append("### Universal Mobile Requirements")
    lines.append("- [ ] Offline behavior defined for every network-dependent feature")
    lines.append("- [ ] Loading states (skeleton/shimmer) for every data-loading screen")
    lines.append("- [ ] Empty states designed for every list/feed/dashboard")
    lines.append("- [ ] Error states with retry for every API call")
    lines.append("- [ ] Pull-to-refresh on all dynamic content screens")
    lines.append("- [ ] Touch targets minimum 44x44pt (iOS) / 48x48dp (Android)")
    lines.append("- [ ] Performance budget: cold start <2s, 60fps scrolling")
    lines.append("- [ ] App download size target: <50MB")
    lines.append("- [ ] Dark mode support")
    lines.append("- [ ] Accessibility: screen reader labels, Dynamic Type, color contrast 4.5:1")
    lines.append("- [ ] Deep link handling for all shareable content")
    lines.append("- [ ] Feature flags for server-side feature control")
    lines.append("- [ ] Phased rollout plan with rollback criteria")
    lines.append("- [ ] Analytics events defined for all key user actions")
    lines.append("- [ ] Crash reporting configured (Crashlytics/Sentry)")
    lines.append("")

    # Platform-specific checklist
    for platform in target_platforms:
        config = PLATFORM_CONFIG[platform]
        lines.append(f"### {config['name']}-Specific Requirements")
        for feature in config["required_features"]:
            lines.append(f"- [ ] {feature}")
        lines.append(f"- [ ] Navigation: {config['navigation']}")
        lines.append(f"- [ ] Back navigation: {config['back_navigation']}")
        lines.append(f"- [ ] Secure storage: {config['secure_storage']}")
        lines.append(f"- [ ] Deep links: {config['deep_links']}")
        lines.append(f"- [ ] Minimum version: {config['min_version_note']}")
        lines.append(f"- [ ] Store commission: {config['store_commission']}")
        lines.append(f"- [ ] Review timeline: {config['review_time']}")
        lines.append("")

    # Feature-specific platform requirements
    if features:
        detected_features = _detect_features(features, product_type)
        if detected_features:
            lines.append("### Feature-Specific Platform Requirements")
            for feature_key in detected_features:
                if feature_key in FEATURE_PLATFORM_REQUIREMENTS:
                    feature_name = feature_key.replace("_", " ").title()
                    lines.append(f"\n**{feature_name}:**")
                    for platform in target_platforms:
                        if platform in FEATURE_PLATFORM_REQUIREMENTS[feature_key]:
                            lines.append(f"\n_{PLATFORM_CONFIG[platform]['name']}:_")
                            for req in FEATURE_PLATFORM_REQUIREMENTS[feature_key][platform]:
                                lines.append(f"- [ ] {req}")
            lines.append("")

    # App Store compliance checklist
    lines.append("### App Store Compliance")
    lines.append("- [ ] Privacy policy URL configured in store listing")
    if "ios" in target_platforms:
        lines.append("- [ ] iOS: Privacy Nutrition Label completed in App Store Connect")
        lines.append("- [ ] iOS: App Tracking Transparency prompt (if tracking)")
        lines.append("- [ ] iOS: Sign in with Apple (if any social login offered)")
        lines.append("- [ ] iOS: In-App Purchase for digital goods (StoreKit)")
        lines.append("- [ ] iOS: Demo account credentials prepared for App Review")
        lines.append("- [ ] iOS: Review notes explaining new features")
    if "android" in target_platforms:
        lines.append("- [ ] Android: Data Safety Section completed in Play Console")
        lines.append("- [ ] Android: Android App Bundle (AAB) format")
        lines.append("- [ ] Android: Target API level meets Play Store requirements")
        lines.append("- [ ] Android: Content rating questionnaire completed")
    lines.append("")

    return "\n".join(lines)


def _detect_features(feature_hints: List[str], product_type: str) -> Set[str]:
    """Detect which platform features are relevant based on hints and product type."""
    combined = " ".join(feature_hints).lower() + " " + product_type.lower()
    detected = set()

    feature_keywords = {
        "push_notification": ["push", "notification", "alert", "remind", "engage"],
        "biometric_auth": ["biometric", "face id", "touch id", "fingerprint", "secure", "banking", "fintech"],
        "camera": ["camera", "photo", "scan", "qr", "image", "video", "ar"],
        "location": ["location", "map", "gps", "nearby", "geofence", "delivery", "ride"],
        "payment": ["payment", "purchase", "subscription", "billing", "iap", "paywall", "fintech", "commerce"],
        "offline": ["offline", "sync", "cache", "field", "remote", "rural"],
    }

    for feature_key, keywords in feature_keywords.items():
        for kw in keywords:
            if kw in combined:
                detected.add(feature_key)
                break

    return detected


def generate_platform_differences(platforms: List[str]) -> str:
    """Generate a platform differences table for cross-platform PRDs."""
    if len(platforms) < 2:
        return ""

    lines = []
    lines.append("## Platform Differences")
    lines.append("")
    lines.append("| Aspect | iOS | Android |")
    lines.append("|--------|-----|---------|")

    ios = PLATFORM_CONFIG.get("ios", {})
    android = PLATFORM_CONFIG.get("android", {})

    rows = [
        ("Design System", ios.get("guidelines", ""), android.get("guidelines", "")),
        ("Navigation", "Bottom Tab Bar", "Bottom Navigation / Drawer"),
        ("Back Navigation", "Edge swipe + nav bar button", "System back button/gesture"),
        ("Push Service", "APNs (via FCM)", "FCM direct"),
        ("Biometric API", "LocalAuthentication", "BiometricPrompt"),
        ("Secure Storage", "Keychain", "Keystore"),
        ("Deep Links", "Universal Links", "App Links"),
        ("Widget Framework", "WidgetKit", "App Widgets / Glance"),
        ("Store Commission", ios.get("store_commission", ""), android.get("store_commission", "")),
        ("Review Time", ios.get("review_time", ""), android.get("review_time", "")),
        ("Permission Model", "Info.plist + runtime", "Manifest + runtime"),
        ("Share Mechanism", "UIActivityViewController", "Share Intent"),
        ("Haptic Feedback", "UIFeedbackGenerator", "HapticFeedbackConstants"),
    ]

    for aspect, ios_val, android_val in rows:
        lines.append(f"| {aspect} | {ios_val} | {android_val} |")

    lines.append("")
    return "\n".join(lines)


def get_platform_context(platforms: List[str], product_type: str = "") -> Dict:
    """Get full platform context for the generator to use."""
    target = [p.lower().strip() for p in platforms if p.lower().strip() in PLATFORM_CONFIG]
    if not target:
        target = ["ios", "android"]

    context = {
        "platforms": target,
        "is_cross_platform": len(target) > 1,
        "configs": {p: PLATFORM_CONFIG[p] for p in target},
    }

    # Get relevant platform rules from knowledge base
    query = product_type + " " + " ".join(target) + " mobile app store compliance"
    rules_result = search_domain(query, "platform-rules", max_results=5)
    context["relevant_rules"] = rules_result.get("results", [])

    # Get relevant mobile UX patterns
    ux_result = search_domain(product_type + " mobile navigation interaction", "mobile-ux", max_results=5)
    context["relevant_ux_patterns"] = ux_result.get("results", [])

    return context
