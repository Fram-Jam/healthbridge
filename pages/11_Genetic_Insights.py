"""
Genetic Insights Page - DNA Sequencing Results and Analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(page_title="Genetic Insights | HealthBridge", layout="wide", page_icon="△")

# =============================================================================
# GEIST DESIGN SYSTEM CSS
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@100;200;300;400;500;600;700;800;900&family=Geist+Mono:wght@400;500;600&display=swap');

    :root {
        --geist-background: #000000;
        --gray-100: #111111;
        --gray-200: #1a1a1a;
        --gray-300: #252525;
        --gray-400: #333333;
        --gray-600: #666666;
        --gray-900: #a1a1a1;
        --geist-foreground: #fafafa;
        --geist-foreground-muted: #666666;
        --geist-border: #252525;
        --geist-success: #0070f3;
        --geist-error: #ee0000;
        --geist-warning: #f5a623;
    }

    .stApp {
        font-family: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .geist-page-title {
        font-size: 32px;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--geist-foreground);
        margin-bottom: 8px;
    }

    .geist-page-subtitle {
        font-size: 16px;
        color: var(--geist-foreground-muted);
        margin-bottom: 32px;
    }

    .geist-section-title {
        font-size: 12px;
        font-weight: 500;
        color: var(--geist-foreground-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 16px;
        margin-top: 32px;
    }

    .risk-card {
        background: var(--gray-100);
        border: 1px solid var(--geist-border);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 12px;
    }

    .risk-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .risk-card-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--geist-foreground);
    }

    .risk-badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 500;
    }

    .risk-low { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
    .risk-average { background: rgba(100, 116, 139, 0.15); color: #94a3b8; }
    .risk-elevated { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .risk-high { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

    .risk-bar-container {
        height: 6px;
        background: var(--gray-300);
        border-radius: 3px;
        overflow: hidden;
        margin: 12px 0;
    }

    .risk-bar {
        height: 100%;
        border-radius: 3px;
        transition: width 0.3s ease;
    }

    .risk-description {
        font-size: 13px;
        color: var(--gray-900);
        line-height: 1.5;
    }

    .carrier-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 13px;
    }

    .carrier-negative { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
    .carrier-positive { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }

    .drug-card {
        background: var(--gray-100);
        border: 1px solid var(--geist-border);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 8px;
    }

    .drug-name {
        font-size: 14px;
        font-weight: 600;
        color: var(--geist-foreground);
    }

    .drug-class {
        font-size: 12px;
        color: var(--geist-foreground-muted);
        margin-bottom: 8px;
    }

    .metabolizer-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metabolizer-poor { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
    .metabolizer-intermediate { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .metabolizer-normal { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
    .metabolizer-rapid { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
    .metabolizer-ultra_rapid { background: rgba(139, 92, 246, 0.15); color: #8b5cf6; }

    .trait-card {
        background: var(--gray-100);
        border: 1px solid var(--geist-border);
        border-radius: 8px;
        padding: 16px;
    }

    .trait-name {
        font-size: 13px;
        color: var(--geist-foreground-muted);
        margin-bottom: 4px;
    }

    .trait-value {
        font-size: 15px;
        font-weight: 500;
        color: var(--geist-foreground);
    }

    .ancestry-bar {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0;
        border-bottom: 1px solid var(--geist-border);
    }

    .ancestry-bar:last-child {
        border-bottom: none;
    }

    .ancestry-region {
        width: 140px;
        font-size: 14px;
        color: var(--geist-foreground);
    }

    .ancestry-pct {
        width: 50px;
        font-size: 14px;
        font-weight: 600;
        color: var(--geist-foreground);
        text-align: right;
        font-family: 'Geist Mono', monospace;
    }

    .ancestry-bar-bg {
        flex: 1;
        height: 8px;
        background: var(--gray-300);
        border-radius: 4px;
        overflow: hidden;
    }

    .ancestry-bar-fill {
        height: 100%;
        border-radius: 4px;
    }

    .info-badge {
        background: var(--gray-200);
        border: 1px solid var(--geist-border);
        border-radius: 8px;
        padding: 16px;
        margin-top: 24px;
    }

    .info-badge-title {
        font-size: 11px;
        font-weight: 600;
        color: var(--geist-foreground-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }

    .info-badge-value {
        font-size: 13px;
        color: var(--gray-900);
    }

    [data-testid="stMetric"] {
        background: var(--gray-100);
        border: 1px solid var(--geist-border);
        border-radius: 8px;
        padding: 20px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        font-weight: 500 !important;
        color: var(--geist-foreground-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 600 !important;
        color: var(--geist-foreground) !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'genetic_data' not in st.session_state:
    st.session_state.genetic_data = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False


def load_genetic_data():
    """Load genetic data."""
    if st.session_state.genetic_data is None:
        from src.data.synthetic.genetic_generator import generate_genetic_profile
        from src.data.synthetic.patient_generator import generate_demo_data

        if st.session_state.get('patient_profile') is None:
            patient, health_data = generate_demo_data(days=90)
            st.session_state.patient_profile = patient
            st.session_state.health_data = health_data

        patient = st.session_state.patient_profile
        st.session_state.genetic_data = generate_genetic_profile(patient.id)


load_genetic_data()


# Page header
st.markdown('<h1 class="geist-page-title">Genetic Insights</h1>', unsafe_allow_html=True)
st.markdown('<p class="geist-page-subtitle">DNA analysis, disease risk, pharmacogenomics, and traits</p>', unsafe_allow_html=True)

genetic = st.session_state.genetic_data

if genetic:
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Variants Analyzed", f"{genetic.variants_analyzed:,}")

    with col2:
        high_risks = sum(1 for r in genetic.disease_risks if r.risk_level in ['elevated', 'high'])
        st.metric("Elevated Risks", high_risks)

    with col3:
        carriers = sum(1 for c in genetic.carrier_statuses if c.status == 'carrier')
        st.metric("Carrier Status", f"{carriers} conditions")

    with col4:
        actionable = sum(1 for d in genetic.drug_responses if d.clinical_significance == 'actionable' and d.metabolizer_status != 'normal')
        st.metric("Drug Alerts", actionable)

    # Tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Disease Risk", "Pharmacogenomics", "Carrier Status", "Traits", "Ancestry"])

    # ==========================================================================
    # TAB 1: Disease Risk
    # ==========================================================================
    with tab1:
        st.markdown('<div class="geist-section-title">Polygenic Risk Scores</div>', unsafe_allow_html=True)

        # Group by category
        categories = {}
        for risk in genetic.disease_risks:
            if risk.category not in categories:
                categories[risk.category] = []
            categories[risk.category].append(risk)

        category_labels = {
            'cardiovascular': 'Cardiovascular',
            'metabolic': 'Metabolic',
            'neurological': 'Neurological',
            'cancer': 'Cancer',
            'autoimmune': 'Autoimmune',
            'other': 'Other'
        }

        for cat_key, cat_label in category_labels.items():
            if cat_key in categories:
                with st.expander(f"**{cat_label}**", expanded=(cat_key in ['cardiovascular', 'metabolic'])):
                    for risk in categories[cat_key]:
                        risk_class = f"risk-{risk.risk_level}"
                        bar_color = {
                            'low': '#22c55e',
                            'average': '#64748b',
                            'elevated': '#f59e0b',
                            'high': '#ef4444'
                        }.get(risk.risk_level, '#64748b')

                        modifiable = " · Lifestyle modifiable" if risk.lifestyle_modifiable else ""

                        st.markdown(f'''
                        <div class="risk-card">
                            <div class="risk-card-header">
                                <span class="risk-card-title">{risk.condition}</span>
                                <span class="risk-badge {risk_class}">{risk.risk_level.title()} Risk</span>
                            </div>
                            <div class="risk-bar-container">
                                <div class="risk-bar" style="width: {risk.percentile}%; background: {bar_color};"></div>
                            </div>
                            <div class="risk-description">
                                {risk.percentile}th percentile · {risk.variants_analyzed} variants analyzed{modifiable}
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)

    # ==========================================================================
    # TAB 2: Pharmacogenomics
    # ==========================================================================
    with tab2:
        st.markdown('<div class="geist-section-title">Drug Response Predictions</div>', unsafe_allow_html=True)
        st.markdown("How your genetics may affect drug metabolism and efficacy.")

        # Actionable alerts first
        actionable_drugs = [d for d in genetic.drug_responses if d.clinical_significance == 'actionable' and d.metabolizer_status != 'normal']

        if actionable_drugs:
            st.warning(f"**{len(actionable_drugs)} Actionable Finding(s)** - Discuss with your healthcare provider")

        col1, col2 = st.columns(2)

        for i, drug in enumerate(genetic.drug_responses):
            with col1 if i % 2 == 0 else col2:
                status_class = f"metabolizer-{drug.metabolizer_status}"
                status_label = drug.metabolizer_status.replace('_', ' ').title()

                actionable_marker = ""
                if drug.clinical_significance == 'actionable' and drug.metabolizer_status != 'normal':
                    actionable_marker = '<span style="color: #f59e0b; margin-left: 8px;">●</span>'

                st.markdown(f'''
                <div class="drug-card">
                    <div class="drug-name">{drug.drug}{actionable_marker}</div>
                    <div class="drug-class">{drug.drug_class} · {drug.gene}</div>
                    <span class="metabolizer-badge {status_class}">{status_label}</span>
                    <div style="font-size: 12px; color: var(--gray-900); margin-top: 8px;">{drug.recommendation}</div>
                </div>
                ''', unsafe_allow_html=True)

    # ==========================================================================
    # TAB 3: Carrier Status
    # ==========================================================================
    with tab3:
        st.markdown('<div class="geist-section-title">Recessive Condition Carrier Status</div>', unsafe_allow_html=True)
        st.markdown("Carrier screening for inherited conditions. Important for family planning.")

        carriers_found = [c for c in genetic.carrier_statuses if c.status == 'carrier']
        not_carriers = [c for c in genetic.carrier_statuses if c.status == 'not_carrier']

        if carriers_found:
            st.markdown("### Carrier Detected")
            for carrier in carriers_found:
                st.markdown(f'''
                <div class="risk-card">
                    <div class="risk-card-header">
                        <span class="risk-card-title">{carrier.condition}</span>
                        <span class="carrier-status carrier-positive">Carrier</span>
                    </div>
                    <div class="risk-description">
                        <strong>Gene:</strong> {carrier.gene} · <strong>Inheritance:</strong> {carrier.inheritance.replace('_', ' ').title()}<br>
                        <strong>Population prevalence:</strong> {carrier.prevalence}<br>
                        {carrier.description}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            st.markdown("")

        st.markdown("### Not a Carrier")
        cols = st.columns(2)
        for i, nc in enumerate(not_carriers):
            with cols[i % 2]:
                st.markdown(f'''
                <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--geist-border);">
                    <span style="color: var(--geist-foreground);">{nc.condition}</span>
                    <span class="carrier-status carrier-negative">Not Carrier</span>
                </div>
                ''', unsafe_allow_html=True)

    # ==========================================================================
    # TAB 4: Traits
    # ==========================================================================
    with tab4:
        st.markdown('<div class="geist-section-title">Genetic Trait Predictions</div>', unsafe_allow_html=True)

        trait_categories = {}
        for trait in genetic.traits:
            if trait.category not in trait_categories:
                trait_categories[trait.category] = []
            trait_categories[trait.category].append(trait)

        category_titles = {
            'nutrition': 'Nutrition & Diet',
            'fitness': 'Fitness & Exercise',
            'sleep': 'Sleep',
            'sensory': 'Sensory',
            'appearance': 'Appearance'
        }

        for cat_key, cat_title in category_titles.items():
            if cat_key in trait_categories:
                st.markdown(f"### {cat_title}")
                cols = st.columns(3)
                for i, trait in enumerate(trait_categories[cat_key]):
                    with cols[i % 3]:
                        confidence_color = {'high': '#22c55e', 'moderate': '#f59e0b', 'low': '#64748b'}.get(trait.confidence, '#64748b')
                        st.markdown(f'''
                        <div class="trait-card">
                            <div class="trait-name">{trait.trait}</div>
                            <div class="trait-value">{trait.prediction}</div>
                            <div style="font-size: 11px; color: {confidence_color}; margin-top: 4px;">{trait.confidence.title()} confidence</div>
                        </div>
                        ''', unsafe_allow_html=True)
                st.markdown("")

    # ==========================================================================
    # TAB 5: Ancestry
    # ==========================================================================
    with tab5:
        st.markdown('<div class="geist-section-title">Ancestry Composition</div>', unsafe_allow_html=True)

        colors = ['#8b5cf6', '#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#06b6d4', '#84cc16']

        for i, anc in enumerate(genetic.ancestry):
            color = colors[i % len(colors)]
            st.markdown(f'''
            <div class="ancestry-bar">
                <span class="ancestry-region">{anc.region}</span>
                <div class="ancestry-bar-bg">
                    <div class="ancestry-bar-fill" style="width: {anc.percentage}%; background: {color};"></div>
                </div>
                <span class="ancestry-pct">{anc.percentage}%</span>
            </div>
            ''', unsafe_allow_html=True)

        # Pie chart
        st.markdown("")
        fig = go.Figure(data=[go.Pie(
            labels=[a.region for a in genetic.ancestry],
            values=[a.percentage for a in genetic.ancestry],
            hole=0.6,
            marker_colors=colors[:len(genetic.ancestry)],
            textinfo='percent',
            textfont_size=12,
            textfont_color='#fafafa'
        )])
        fig.update_layout(
            showlegend=True,
            legend=dict(font=dict(color='#a1a1a1', size=12)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=20, r=20),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    # Sequencing info
    st.markdown(f'''
    <div class="info-badge">
        <div class="info-badge-title">Sequencing Information</div>
        <div class="info-badge-value">
            <strong>Type:</strong> {genetic.sequencing_type.replace('_', ' ').title()} ·
            <strong>Date:</strong> {genetic.sequencing_date} ·
            <strong>Variants:</strong> {genetic.variants_analyzed:,}
        </div>
    </div>
    ''', unsafe_allow_html=True)

else:
    st.info("""
    **No genetic data available**

    Upload your DNA sequencing results to unlock:
    - Polygenic disease risk scores
    - Pharmacogenomic drug response predictions
    - Carrier status screening
    - Trait predictions
    - Ancestry composition

    Supported formats: 23andMe, AncestryDNA, WGS/WES VCF files
    """)

    uploaded = st.file_uploader("Upload genetic data", type=['txt', 'csv', 'vcf', 'zip'])
    if uploaded:
        st.success(f"File uploaded: {uploaded.name}")
        if st.button("Process Genetic Data"):
            with st.spinner("Analyzing genetic variants..."):
                import time
                time.sleep(3)
                st.success("Genetic data processed successfully!")
                st.rerun()

# Demo notice
st.markdown("---")
st.markdown('''
<div class="info-badge">
    <div class="info-badge-title">Demo Mode</div>
    <div class="info-badge-value">
        Genetic data shown is synthetic and generated for demonstration purposes.
        Real genetic analysis requires actual DNA sequencing data.
    </div>
</div>
''', unsafe_allow_html=True)
