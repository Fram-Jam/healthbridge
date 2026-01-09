"""
Main Health Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(page_title="Dashboard | HealthBridge", layout="wide", page_icon="🌉")


def safe_get(record, key, default=0):
    """Safely get a value from a record, returning default if None."""
    val = record.get(key)
    return val if val is not None else default


def has_data(data: list, key: str) -> bool:
    """Check if any records have non-None values for a key."""
    return any(d.get(key) is not None for d in data)


def create_sleep_chart(data: list) -> go.Figure:
    """Create sleep duration and quality chart."""
    # Filter to records with sleep data
    sleep_data = [d for d in data if d.get('sleep_duration') is not None]
    if not sleep_data:
        return None

    df = pd.DataFrame(sleep_data)
    df['date'] = pd.to_datetime(df['date'])
    df['sleep_duration'] = df['sleep_duration'].fillna(0)
    df['deep_sleep'] = df['deep_sleep'].fillna(0)
    df['rem_sleep'] = df['rem_sleep'].fillna(0)
    df['light_sleep'] = df['light_sleep'].fillna(0)

    # Check if we have sleep stage data
    has_stages = df['deep_sleep'].sum() > 0 or df['rem_sleep'].sum() > 0

    if has_stages:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=("Sleep Duration", "Sleep Stages"),
            row_heights=[0.4, 0.6]
        )
    else:
        fig = go.Figure()

    # Sleep duration line
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['sleep_duration'],
            mode='lines+markers',
            name='Total Sleep',
            line=dict(color='#6366F1', width=2),
            marker=dict(size=6)
        ),
        row=1 if has_stages else None,
        col=1 if has_stages else None
    )

    # Target sleep line
    if has_stages:
        fig.add_hline(y=7.5, line_dash="dash", line_color="gray",
                      annotation_text="Target: 7.5h", row=1, col=1)
    else:
        fig.add_hline(y=7.5, line_dash="dash", line_color="gray",
                      annotation_text="Target: 7.5h")

    # Sleep stages stacked bar (only if data available)
    if has_stages:
        fig.add_trace(
            go.Bar(x=df['date'], y=df['deep_sleep'], name='Deep', marker_color='#1E3A8A'),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=df['date'], y=df['rem_sleep'], name='REM', marker_color='#3B82F6'),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=df['date'], y=df['light_sleep'], name='Light', marker_color='#93C5FD'),
            row=2, col=1
        )

    fig.update_layout(
        barmode='stack',
        height=500 if has_stages else 300,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    if has_stages:
        fig.update_yaxes(title_text="Hours", row=1, col=1, gridcolor='#E2E8F0')
        fig.update_yaxes(title_text="Hours", row=2, col=1, gridcolor='#E2E8F0')
    else:
        fig.update_yaxes(title_text="Hours", gridcolor='#E2E8F0')
    fig.update_xaxes(gridcolor='#E2E8F0')

    return fig


def create_hrv_rhr_chart(data: list) -> go.Figure:
    """Create HRV and Resting HR chart."""
    # Check if we have any heart data
    has_hrv = has_data(data, 'hrv')
    has_rhr = has_data(data, 'resting_hr')

    if not has_hrv and not has_rhr:
        return None

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # HRV (if available)
    if has_hrv:
        hrv_data = df[df['hrv'].notna()]
        fig.add_trace(
            go.Scatter(
                x=hrv_data['date'],
                y=hrv_data['hrv'],
                mode='lines+markers',
                name='HRV (ms)',
                line=dict(color='#10B981', width=2),
                marker=dict(size=5)
            ),
            secondary_y=False
        )

    # RHR (if available)
    if has_rhr:
        rhr_data = df[df['resting_hr'].notna()]
        fig.add_trace(
            go.Scatter(
                x=rhr_data['date'],
                y=rhr_data['resting_hr'],
                mode='lines+markers',
                name='Resting HR (bpm)',
                line=dict(color='#EF4444', width=2),
                marker=dict(size=5)
            ),
            secondary_y=True
        )

    fig.update_layout(
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    if has_hrv:
        fig.update_yaxes(title_text="HRV (ms)", secondary_y=False, gridcolor='#E2E8F0')
    if has_rhr:
        fig.update_yaxes(title_text="RHR (bpm)", secondary_y=True, gridcolor='#E2E8F0')
    fig.update_xaxes(gridcolor='#E2E8F0')

    return fig


def create_activity_chart(data: list) -> go.Figure:
    """Create steps and activity chart."""
    if not has_data(data, 'steps'):
        return None

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['steps'] = df['steps'].fillna(0)

    fig = go.Figure()

    # Steps bar chart
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['steps'],
            name='Steps',
            marker_color='#8B5CF6'
        )
    )

    # 10k target line
    fig.add_hline(y=10000, line_dash="dash", line_color="gray",
                  annotation_text="Goal: 10,000")

    # 7-day moving average
    df['steps_ma'] = df['steps'].rolling(window=7, min_periods=1).mean()
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['steps_ma'],
            mode='lines',
            name='7-day avg',
            line=dict(color='#C4B5FD', width=3)
        )
    )

    fig.update_layout(
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_yaxes(gridcolor='#E2E8F0')
    fig.update_xaxes(gridcolor='#E2E8F0')

    return fig


def create_glucose_chart(data: list) -> go.Figure:
    """Create glucose chart if CGM data available."""
    # Check for glucose data in either format (nested or flat)
    glucose_days = []
    for d in data:
        if d.get('glucose'):  # Nested format
            glucose_days.append({
                'date': d['date'],
                'avg': d['glucose']['avg'],
                'min': d['glucose']['min'],
                'max': d['glucose']['max'],
                'tir': d['glucose'].get('time_in_range')
            })
        elif d.get('glucose_avg') is not None:  # Flat format
            glucose_days.append({
                'date': d['date'],
                'avg': d['glucose_avg'],
                'min': d.get('glucose_min'),
                'max': d.get('glucose_max'),
                'tir': d.get('time_in_range')
            })

    if not glucose_days:
        return None

    df = pd.DataFrame(glucose_days)
    df['date'] = pd.to_datetime(df['date'])

    fig = go.Figure()

    # Range band (min to max) if available
    if df['min'].notna().any() and df['max'].notna().any():
        valid_df = df[df['min'].notna() & df['max'].notna()]
        fig.add_trace(
            go.Scatter(
                x=pd.concat([valid_df['date'], valid_df['date'][::-1]]),
                y=pd.concat([valid_df['max'], valid_df['min'][::-1]]),
                fill='toself',
                fillcolor='rgba(99, 102, 241, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Range',
                showlegend=True
            )
        )

    # Average line
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['avg'],
            mode='lines+markers',
            name='Average',
            line=dict(color='#6366F1', width=2),
            marker=dict(size=6)
        )
    )

    # Target range
    fig.add_hrect(y0=70, y1=140, fillcolor="rgba(16, 185, 129, 0.1)",
                  line_width=0, annotation_text="Target Range")

    fig.update_layout(
        height=350,
        yaxis_title="Glucose (mg/dL)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_yaxes(gridcolor='#E2E8F0')
    fig.update_xaxes(gridcolor='#E2E8F0')

    return fig


def create_readiness_chart(data: list) -> go.Figure:
    """Create readiness/recovery score chart."""
    if not has_data(data, 'readiness_score'):
        return None

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['readiness_score'].notna()]

    if df.empty:
        return None

    fig = go.Figure()

    # Color based on score
    colors = ['#EF4444' if s < 60 else '#F59E0B' if s < 75 else '#10B981'
              for s in df['readiness_score']]

    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['readiness_score'],
            marker_color=colors,
            name='Readiness'
        )
    )

    fig.update_layout(
        height=300,
        yaxis_title="Score",
        yaxis_range=[0, 100],
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_yaxes(gridcolor='#E2E8F0')
    fig.update_xaxes(gridcolor='#E2E8F0')

    return fig


# Initialize session state using centralized storage
from src.data.storage import (
    init_storage, is_data_loaded, load_dataset_data,
    get_active_dataset, get_active_subject, is_synthetic_mode,
    SYNTHETIC_DATASET_ID
)

init_storage()

# Load data if needed
if not is_data_loaded():
    with st.spinner("Loading health data..."):
        dataset_id = get_active_dataset()
        subject_id = get_active_subject()
        load_dataset_data(dataset_id, subject_id)

        if is_synthetic_mode():
            st.session_state.connected_devices = [
                {'name': 'Oura Ring', 'type': 'oura', 'connected': True, 'last_sync': datetime.now()},
                {'name': 'Apple Watch', 'type': 'apple', 'connected': True, 'last_sync': datetime.now()},
                {'name': 'Dexcom G7', 'type': 'cgm', 'connected': True, 'last_sync': datetime.now()},
            ]

# Main dashboard
st.title("🏠 Health Dashboard")

# Date range selector
col1, col2, col3 = st.columns([2, 2, 6])
with col1:
    time_range = st.selectbox(
        "Time Range",
        ["Last 7 days", "Last 14 days", "Last 30 days", "Last 90 days"],
        index=2
    )
with col2:
    if st.button("🔄 Refresh Data"):
        st.session_state.data_loaded = False
        st.rerun()

# Filter data based on selection
days_map = {"Last 7 days": 7, "Last 14 days": 14, "Last 30 days": 30, "Last 90 days": 90}
days = days_map[time_range]

if st.session_state.health_data:
    data = st.session_state.health_data[-days:]

    # Today's summary
    st.markdown("### Today's Summary")
    today = data[-1]

    cols = st.columns(6)

    # Helper to format metric values safely
    def fmt_metric(val, fmt_str="{}", suffix=""):
        if val is None:
            return "N/A"
        return fmt_str.format(val) + suffix

    with cols[0]:
        sleep_dur = today.get('sleep_duration')
        st.metric("😴 Sleep", fmt_metric(sleep_dur, "{:.1f}", "h"))

    with cols[1]:
        hrv = today.get('hrv')
        st.metric("❤️ HRV", fmt_metric(hrv, "{:.0f}", " ms"))

    with cols[2]:
        rhr = today.get('resting_hr')
        st.metric("💓 RHR", fmt_metric(rhr, "{}", " bpm"))

    with cols[3]:
        steps = today.get('steps')
        st.metric("🚶 Steps", fmt_metric(steps, "{:,}"))

    with cols[4]:
        cals = today.get('active_calories') or today.get('calories_active')
        st.metric("🔥 Calories", fmt_metric(cals))

    with cols[5]:
        ready = today.get('readiness_score')
        st.metric("⚡ Readiness", fmt_metric(ready))

    st.markdown("---")

    # Charts grid - only show charts that have data
    charts_shown = 0

    # Sleep and Heart in first row
    col1, col2 = st.columns(2)

    sleep_chart = create_sleep_chart(data)
    hrv_chart = create_hrv_rhr_chart(data)

    with col1:
        if sleep_chart:
            st.markdown("### 😴 Sleep")
            st.plotly_chart(sleep_chart, use_container_width=True)
            charts_shown += 1
        elif hrv_chart:
            st.markdown("### ❤️ Heart Health")
            st.plotly_chart(hrv_chart, use_container_width=True)
            hrv_chart = None  # Already shown
            charts_shown += 1

    with col2:
        if hrv_chart:
            st.markdown("### ❤️ Heart Health")
            st.plotly_chart(hrv_chart, use_container_width=True)
            charts_shown += 1

    # Activity and Readiness in second row
    activity_chart = create_activity_chart(data)
    readiness_chart = create_readiness_chart(data)

    if activity_chart or readiness_chart:
        col1, col2 = st.columns(2)

        with col1:
            if activity_chart:
                st.markdown("### 🚶 Activity")
                st.plotly_chart(activity_chart, use_container_width=True)
                charts_shown += 1

        with col2:
            if readiness_chart:
                st.markdown("### ⚡ Readiness Score")
                st.plotly_chart(readiness_chart, use_container_width=True)
                charts_shown += 1

    # Glucose chart (if available)
    glucose_chart = create_glucose_chart(data)
    if glucose_chart:
        st.markdown("### 🩸 Glucose")
        st.plotly_chart(glucose_chart, use_container_width=True)
        charts_shown += 1

    # Show message if no charts available
    if charts_shown == 0:
        st.info("No chart data available for the selected time range.")

    # Data sources footer
    st.markdown("---")
    if st.session_state.get('connected_devices'):
        st.markdown("**Data Sources:** " + ", ".join([d['name'] for d in st.session_state.connected_devices]))
    else:
        dataset = get_active_dataset()
        st.markdown(f"**Data Source:** {dataset}")
else:
    st.warning("No health data available. Please connect your devices in Settings or select a dataset.")
