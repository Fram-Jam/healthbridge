"""
HealthBridge - Unified Health Data Platform
Main Streamlit Application

Design System: Geist by Vercel
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Page config must be first Streamlit command
st.set_page_config(
    page_title="HealthBridge",
    page_icon="△",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:support@healthbridge.demo',
        'Report a bug': 'mailto:bugs@healthbridge.demo',
        'About': """
        ## HealthBridge
        **The unified platform for all your health data.**

        Connect your wearables, see your labs, get AI-powered insights.

        Demo Version 0.1.0
        """
    }
)

# =============================================================================
# GEIST DESIGN SYSTEM CSS
# Inspired by Vercel's Geist: vercel.com/geist
# Philosophy: Simplicity, minimalism, precision, clarity
# =============================================================================
st.markdown("""
<style>
    /* Geist Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@100;200;300;400;500;600;700;800;900&family=Geist+Mono:wght@400;500;600&display=swap');

    /* ===========================================
       GEIST COLOR SYSTEM
       High contrast, accessible, minimal
       =========================================== */
    :root {
        /* Backgrounds */
        --geist-background: #000000;
        --geist-background-secondary: #0a0a0a;

        /* Gray Scale (Geist 10-step) */
        --gray-100: #111111;
        --gray-200: #1a1a1a;
        --gray-300: #252525;
        --gray-400: #333333;
        --gray-500: #454545;
        --gray-600: #666666;
        --gray-700: #888888;
        --gray-800: #999999;
        --gray-900: #a1a1a1;
        --gray-1000: #ededed;

        /* Alpha variants */
        --gray-alpha-100: rgba(255, 255, 255, 0.04);
        --gray-alpha-200: rgba(255, 255, 255, 0.06);
        --gray-alpha-400: rgba(255, 255, 255, 0.1);

        /* Foreground */
        --geist-foreground: #fafafa;
        --geist-foreground-secondary: #a1a1a1;
        --geist-foreground-muted: #666666;

        /* Borders */
        --geist-border: #252525;
        --geist-border-hover: #333333;

        /* Semantic Colors */
        --geist-success: #0070f3;
        --geist-error: #ee0000;
        --geist-warning: #f5a623;
        --geist-cyan: #79ffe1;
        --geist-purple: #7928ca;
        --geist-violet: #8b5cf6;

        /* Accents */
        --accent-1: #111111;
        --accent-2: #1a1a1a;
        --accent-3: #252525;
        --accent-4: #333333;
        --accent-5: #666666;
        --accent-6: #888888;
        --accent-7: #a1a1a1;
        --accent-8: #ededed;
    }

    /* ===========================================
       BASE STYLES
       =========================================== */
    .stApp {
        font-family: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: var(--geist-background) !important;
        color: var(--geist-foreground);
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    .main .block-container {
        padding: 48px 64px;
        max-width: 1200px;
    }

    /* ===========================================
       TYPOGRAPHY (Geist Scale)
       =========================================== */

    /* Heading 48 */
    .geist-heading-48 {
        font-size: 48px;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.1;
        color: var(--geist-foreground);
        margin: 0;
    }

    /* Heading 32 */
    .geist-heading-32 {
        font-size: 32px;
        font-weight: 600;
        letter-spacing: -0.02em;
        line-height: 1.2;
        color: var(--geist-foreground);
        margin: 0;
    }

    /* Heading 24 */
    .geist-heading-24 {
        font-size: 24px;
        font-weight: 600;
        letter-spacing: -0.01em;
        line-height: 1.3;
        color: var(--geist-foreground);
        margin: 0;
    }

    /* Heading 20 */
    .geist-heading-20 {
        font-size: 20px;
        font-weight: 600;
        letter-spacing: -0.01em;
        line-height: 1.4;
        color: var(--geist-foreground);
        margin: 0;
    }

    /* Label 14 - Most common */
    .geist-label-14 {
        font-size: 14px;
        font-weight: 500;
        line-height: 1.5;
        color: var(--geist-foreground);
    }

    /* Label 13 */
    .geist-label-13 {
        font-size: 13px;
        font-weight: 400;
        line-height: 1.5;
        color: var(--geist-foreground-secondary);
    }

    /* Label 12 - Small */
    .geist-label-12 {
        font-size: 12px;
        font-weight: 500;
        line-height: 1.5;
        letter-spacing: 0.01em;
        color: var(--geist-foreground-muted);
    }

    /* Copy 14 */
    .geist-copy-14 {
        font-size: 14px;
        font-weight: 400;
        line-height: 1.7;
        color: var(--geist-foreground-secondary);
    }

    /* Mono */
    .geist-mono {
        font-family: 'Geist Mono', 'SF Mono', Monaco, 'Courier New', monospace;
    }

    /* ===========================================
       SIDEBAR
       =========================================== */
    section[data-testid="stSidebar"] {
        background: var(--geist-background) !important;
        border-right: 1px solid var(--geist-border);
    }

    section[data-testid="stSidebar"] > div {
        padding: 24px 20px;
    }

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 24px;
        border-bottom: 1px solid var(--geist-border);
        margin-bottom: 24px;
    }

    .sidebar-logo {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .sidebar-logo-text {
        font-size: 15px;
        font-weight: 600;
        color: var(--geist-foreground);
        letter-spacing: -0.01em;
    }

    .sidebar-section {
        margin-bottom: 24px;
    }

    .sidebar-section-title {
        font-size: 12px;
        font-weight: 500;
        color: var(--geist-foreground-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }

    .sidebar-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid var(--gray-alpha-100);
    }

    .sidebar-item:last-child {
        border-bottom: none;
    }

    .sidebar-item-label {
        font-size: 14px;
        color: var(--geist-foreground-secondary);
    }

    .sidebar-status {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--geist-success);
    }

    .status-dot.offline {
        background: var(--accent-5);
    }

    .sidebar-badge {
        padding: 16px;
        background: var(--gray-100);
        border: 1px solid var(--geist-border);
        border-radius: 8px;
        margin-top: 24px;
    }

    .sidebar-badge-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--geist-foreground-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .sidebar-badge-value {
        font-size: 13px;
        color: var(--geist-foreground-secondary);
        margin-top: 4px;
    }

    /* ===========================================
       METRIC CARDS (Geist Style)
       =========================================== */
    [data-testid="stMetric"] {
        background: var(--geist-background);
        border: 1px solid var(--geist-border);
        border-radius: 8px;
        padding: 20px;
        transition: border-color 0.15s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--geist-border-hover);
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Geist', sans-serif !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        color: var(--geist-foreground-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Geist', sans-serif !important;
        font-size: 28px !important;
        font-weight: 600 !important;
        color: var(--geist-foreground) !important;
        letter-spacing: -0.02em;
    }

    [data-testid="stMetricDelta"] {
        font-family: 'Geist Mono', monospace !important;
        font-size: 12px !important;
    }

    /* ===========================================
       FEATURE CARDS (Geist Minimal)
       =========================================== */
    .geist-card {
        background: var(--geist-background);
        border: 1px solid var(--geist-border);
        border-radius: 8px;
        padding: 24px;
        transition: all 0.15s ease;
        cursor: pointer;
        min-height: 140px;
    }

    .geist-card:hover {
        border-color: var(--geist-border-hover);
        background: var(--gray-alpha-100);
    }

    .geist-card-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--geist-foreground);
        margin: 0 0 8px 0;
        letter-spacing: -0.01em;
    }

    .geist-card-description {
        font-size: 14px;
        font-weight: 400;
        color: var(--geist-foreground-muted);
        line-height: 1.6;
        margin: 0;
    }

    .geist-card-icon {
        font-size: 20px;
        color: var(--geist-foreground-muted);
        margin-bottom: 16px;
        font-weight: 300;
    }

    /* ===========================================
       GRID & LAYOUT
       =========================================== */
    .geist-grid {
        display: grid;
        gap: 16px;
    }

    .geist-grid-3 {
        grid-template-columns: repeat(3, 1fr);
    }

    .geist-spacer-24 {
        height: 24px;
    }

    .geist-spacer-32 {
        height: 32px;
    }

    .geist-spacer-48 {
        height: 48px;
    }

    .geist-divider {
        height: 1px;
        background: var(--geist-border);
        margin: 32px 0;
    }

    /* ===========================================
       BUTTONS (Geist Style)
       =========================================== */
    .stButton > button {
        font-family: 'Geist', sans-serif !important;
        font-size: 14px;
        font-weight: 500;
        background: var(--geist-foreground) !important;
        color: var(--geist-background) !important;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        transition: opacity 0.15s ease;
    }

    .stButton > button:hover {
        opacity: 0.9;
    }

    /* Secondary button */
    .geist-button-secondary {
        background: transparent !important;
        color: var(--geist-foreground) !important;
        border: 1px solid var(--geist-border) !important;
    }

    .geist-button-secondary:hover {
        border-color: var(--geist-foreground) !important;
    }

    /* ===========================================
       NAVIGATION LINKS
       =========================================== */
    .geist-nav-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 6px;
        color: var(--geist-foreground-secondary);
        text-decoration: none;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.15s ease;
    }

    .geist-nav-item:hover {
        background: var(--gray-alpha-200);
        color: var(--geist-foreground);
    }

    .geist-nav-item.active {
        background: var(--gray-alpha-400);
        color: var(--geist-foreground);
    }

    /* ===========================================
       BADGES
       =========================================== */
    .geist-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        background: var(--gray-200);
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 500;
        color: var(--geist-foreground-secondary);
    }

    .geist-badge-success {
        background: rgba(0, 112, 243, 0.1);
        color: var(--geist-success);
    }

    .geist-badge-warning {
        background: rgba(245, 166, 35, 0.1);
        color: var(--geist-warning);
    }

    .geist-badge-error {
        background: rgba(238, 0, 0, 0.1);
        color: var(--geist-error);
    }

    /* ===========================================
       TABLES
       =========================================== */
    .stDataFrame {
        border: 1px solid var(--geist-border) !important;
        border-radius: 8px;
    }

    /* ===========================================
       INPUTS
       =========================================== */
    .stTextInput > div > div > input {
        font-family: 'Geist', sans-serif !important;
        background: var(--geist-background) !important;
        border: 1px solid var(--geist-border) !important;
        border-radius: 6px;
        color: var(--geist-foreground) !important;
        font-size: 14px;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--geist-foreground) !important;
        box-shadow: none !important;
    }

    /* ===========================================
       HERO SECTION
       =========================================== */
    .geist-hero {
        padding: 0 0 48px 0;
    }

    .geist-hero-title {
        font-size: 48px;
        font-weight: 700;
        letter-spacing: -0.03em;
        line-height: 1.1;
        color: var(--geist-foreground);
        margin: 0 0 12px 0;
    }

    .geist-hero-subtitle {
        font-size: 18px;
        font-weight: 400;
        color: var(--geist-foreground-muted);
        margin: 0;
        line-height: 1.5;
    }

    /* ===========================================
       SECTION HEADERS
       =========================================== */
    .geist-section-title {
        font-size: 12px;
        font-weight: 500;
        color: var(--geist-foreground-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 16px;
    }

    /* ===========================================
       ANIMATIONS
       =========================================== */
    @keyframes geist-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .geist-pulse {
        animation: geist-pulse 2s ease-in-out infinite;
    }

    /* ===========================================
       SCROLLBAR (Minimal)
       =========================================== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--accent-4);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-5);
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        'authenticated': True,
        'user_id': 'demo_user',
        'user_name': 'Demo User',
        'connected_devices': [],
        'health_data': None,
        'patient_profile': None,
        'lab_data': None,
        'demo_mode': True,
        'data_loaded': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_demo_data():
    """Load synthetic demo data."""
    if not st.session_state.data_loaded:
        from src.data.synthetic.patient_generator import generate_demo_data
        from src.data.synthetic.lab_generator import generate_lab_history

        with st.spinner(""):
            patient, health_data = generate_demo_data(days=90)
            st.session_state.patient_profile = patient
            st.session_state.health_data = health_data

            labs = generate_lab_history(
                patient.id, patient.health_conditions,
                patient.age, patient.sex, num_panels=4
            )
            st.session_state.lab_data = labs

            st.session_state.connected_devices = [
                {'name': 'Oura Ring Gen 3', 'type': 'ring', 'connected': True},
                {'name': 'Apple Watch Ultra', 'type': 'watch', 'connected': True},
                {'name': 'Dexcom G7', 'type': 'cgm', 'connected': True},
            ]
            st.session_state.data_loaded = True


def main():
    """Main application."""
    init_session_state()
    load_demo_data()

    # ==========================================================================
    # SIDEBAR
    # ==========================================================================
    with st.sidebar:
        # Brand
        st.markdown('''
        <div class="sidebar-brand">
            <div class="sidebar-logo">
                <span style="font-size: 20px; color: #fafafa;">△</span>
            </div>
            <span class="sidebar-logo-text">HealthBridge</span>
        </div>
        ''', unsafe_allow_html=True)

        # User profile
        if st.session_state.patient_profile:
            patient = st.session_state.patient_profile
            st.markdown(f'''
            <div class="sidebar-section">
                <div class="sidebar-section-title">Profile</div>
                <div class="sidebar-item">
                    <span class="sidebar-item-label">{patient.name}</span>
                </div>
                <div class="sidebar-item">
                    <span class="sidebar-item-label" style="color: var(--geist-foreground-muted);">{patient.age} years · {patient.activity_level.replace('_', ' ').title()}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        # Connected devices
        st.markdown('<div class="sidebar-section-title">Devices</div>', unsafe_allow_html=True)

        for device in st.session_state.connected_devices:
            status = "connected" if device['connected'] else "offline"
            st.markdown(f'''
            <div class="sidebar-item">
                <span class="sidebar-item-label">{device['name']}</span>
                <div class="sidebar-status">
                    <span class="status-dot {'offline' if not device['connected'] else ''}"></span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        # Demo badge
        if st.session_state.demo_mode:
            st.markdown('''
            <div class="sidebar-badge">
                <div class="sidebar-badge-label">Environment</div>
                <div class="sidebar-badge-value">Demo Mode · Synthetic Data</div>
            </div>
            ''', unsafe_allow_html=True)

    # ==========================================================================
    # MAIN CONTENT
    # ==========================================================================

    # Hero
    st.markdown('''
    <div class="geist-hero">
        <h1 class="geist-hero-title">Your health data,<br>unified.</h1>
        <p class="geist-hero-subtitle">Connect your wearables, view your labs, get AI-powered insights.</p>
    </div>
    ''', unsafe_allow_html=True)

    # Metrics
    if st.session_state.health_data:
        latest = st.session_state.health_data[-1]
        prev = st.session_state.health_data[-2] if len(st.session_state.health_data) > 1 else latest

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            delta = latest['sleep_score'] - prev['sleep_score']
            st.metric("Sleep", f"{latest['sleep_score']}", delta=f"{delta:+.0f}" if delta else None)

        with col2:
            delta = latest['hrv'] - prev['hrv']
            st.metric("HRV", f"{latest['hrv']:.0f}", delta=f"{delta:+.0f}" if delta else None)

        with col3:
            delta = latest['resting_hr'] - prev['resting_hr']
            st.metric("RHR", f"{latest['resting_hr']}", delta=f"{delta:+.0f}" if delta else None, delta_color="inverse")

        with col4:
            delta = latest['steps'] - prev['steps']
            st.metric("Steps", f"{latest['steps']:,}", delta=f"{delta:+,}" if delta else None)

        with col5:
            delta = latest['readiness_score'] - prev['readiness_score']
            st.metric("Ready", f"{latest['readiness_score']}", delta=f"{delta:+.0f}" if delta else None)

    # Spacer
    st.markdown('<div class="geist-spacer-48"></div>', unsafe_allow_html=True)

    # Section title
    st.markdown('<div class="geist-section-title">Features</div>', unsafe_allow_html=True)

    # Feature cards helper
    def geist_card(title: str, desc: str):
        return f'''
        <div class="geist-card">
            <div class="geist-card-title">{title}</div>
            <div class="geist-card-description">{desc}</div>
        </div>
        '''

    # Row 1
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(geist_card(
            "Dashboard",
            "Real-time metrics and trends from all your connected devices."
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(geist_card(
            "AI Insights",
            "Personalized recommendations powered by health AI."
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(geist_card(
            "Lab Results",
            "Clinical data, biomarkers, and trend analysis."
        ), unsafe_allow_html=True)

    st.markdown('<div class="geist-spacer-24"></div>', unsafe_allow_html=True)

    # Row 2
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(geist_card(
            "Weekly Report",
            "Health summaries with grades and actionable insights."
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(geist_card(
            "Sleep Analysis",
            "Sleep stages, patterns, and optimization strategies."
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(geist_card(
            "Goals",
            "Set targets, track streaks, and measure progress."
        ), unsafe_allow_html=True)

    st.markdown('<div class="geist-spacer-24"></div>', unsafe_allow_html=True)

    # Row 3
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(geist_card(
            "Workouts",
            "Exercise tracking, training load, and recovery."
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(geist_card(
            "Devices",
            "Connect Oura, Apple Watch, Whoop, Garmin, and more."
        ), unsafe_allow_html=True)

    with col3:
        st.markdown(geist_card(
            "Settings",
            "Configure preferences and manage your data."
        ), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
