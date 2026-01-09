"""
Data Sources Page

Manage and explore available health datasets.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Data Sources | HealthBridge",
    page_icon="△",
    layout="wide"
)

from src.data.storage import (
    init_storage, get_active_dataset, set_active_dataset,
    set_active_subject, SYNTHETIC_DATASET_ID, SYNTHETIC_DATASET_NAME
)
from src.data.adapters.registry import registry, register_all_adapters
from src.data.adapters.base import DataCategory

# Initialize
init_storage()
register_all_adapters()

# Page CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #000000 !important;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .page-title {
        font-size: 32px;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: #fafafa;
        margin-bottom: 8px;
    }

    .page-subtitle {
        font-size: 14px;
        color: #666666;
        margin-bottom: 32px;
    }

    .dataset-card {
        background: #000000;
        border: 1px solid #252525;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        transition: border-color 0.15s ease;
    }

    .dataset-card:hover {
        border-color: #333333;
    }

    .dataset-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }

    .dataset-name {
        font-size: 16px;
        font-weight: 600;
        color: #fafafa;
        margin: 0;
    }

    .dataset-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 500;
    }

    .status-available {
        background: rgba(0, 112, 243, 0.1);
        color: #0070f3;
    }

    .status-missing {
        background: rgba(102, 102, 102, 0.1);
        color: #666666;
    }

    .dataset-description {
        font-size: 14px;
        color: #888888;
        line-height: 1.5;
        margin-bottom: 16px;
    }

    .dataset-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 16px;
    }

    .meta-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .meta-label {
        font-size: 11px;
        font-weight: 500;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .meta-value {
        font-size: 13px;
        color: #a1a1a1;
    }

    .dataset-fields {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 16px;
    }

    .field-tag {
        padding: 4px 8px;
        background: #1a1a1a;
        border-radius: 4px;
        font-size: 11px;
        color: #888888;
        font-family: 'Geist Mono', monospace;
    }

    .dataset-instructions {
        background: #0a0a0a;
        border: 1px solid #1a1a1a;
        border-radius: 6px;
        padding: 12px;
        font-size: 12px;
        color: #666666;
        font-family: 'Geist Mono', monospace;
        white-space: pre-wrap;
        margin-bottom: 16px;
    }

    .section-title {
        font-size: 12px;
        font-weight: 500;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 32px 0 16px 0;
    }

    .category-badge {
        display: inline-flex;
        padding: 2px 8px;
        background: #1a1a1a;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 500;
        color: #888888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown('<h1 class="page-title">Data Sources</h1>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Browse and connect to public health datasets. Download datasets locally, then select them from the sidebar.</p>', unsafe_allow_html=True)

# Category tabs
categories = ["All"] + [c.value.title() for c in DataCategory]
selected_category = st.tabs(categories)

def render_dataset_card(metadata, is_available: bool):
    """Render a dataset card."""
    status_class = "status-available" if is_available else "status-missing"
    status_text = "Available" if is_available else "Not Downloaded"
    status_icon = "✓" if is_available else "○"

    fields_html = "".join([f'<span class="field-tag">{f}</span>' for f in metadata.available_fields[:8]])
    if len(metadata.available_fields) > 8:
        fields_html += f'<span class="field-tag">+{len(metadata.available_fields) - 8} more</span>'

    st.markdown(f'''
    <div class="dataset-card">
        <div class="dataset-header">
            <h3 class="dataset-name">
                {metadata.name}
                <span class="category-badge">{metadata.category.value}</span>
            </h3>
            <span class="dataset-status {status_class}">{status_icon} {status_text}</span>
        </div>
        <p class="dataset-description">{metadata.description}</p>
        <div class="dataset-meta">
            <div class="meta-item">
                <span class="meta-label">Subjects</span>
                <span class="meta-value">{metadata.subject_count:,}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Size</span>
                <span class="meta-value">{metadata.size_mb or 'Unknown'} MB</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Date Range</span>
                <span class="meta-value">{metadata.date_range or 'N/A'}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">License</span>
                <span class="meta-value">{metadata.license}</span>
            </div>
        </div>
        <div class="dataset-fields">{fields_html}</div>
    </div>
    ''', unsafe_allow_html=True)

    # Expandable instructions
    with st.expander("Download Instructions"):
        st.code(metadata.download_instructions, language="bash")
        st.markdown(f"**Source:** [{metadata.source_url}]({metadata.source_url})")
        st.markdown(f"**Citation:** {metadata.citation}")

    # Use this dataset button
    if is_available:
        if st.button(f"Use {metadata.name}", key=f"use_{metadata.id}"):
            set_active_dataset(metadata.id)
            set_active_subject(None)
            st.success(f"Switched to {metadata.name}")
            st.rerun()


# Render tabs
for i, category_name in enumerate(categories):
    with selected_category[i]:
        if category_name == "All":
            datasets = registry.list_all()
        else:
            category_enum = DataCategory(category_name.lower())
            datasets = registry.list_by_category(category_enum)

        if not datasets:
            st.info("No datasets registered for this category yet.")
        else:
            for metadata in datasets:
                adapter = registry.get(metadata.id)
                is_available = adapter.is_available() if adapter else False
                render_dataset_card(metadata, is_available)

# Summary section
st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)

all_datasets = registry.list_all()
available = sum(1 for m in all_datasets if registry.get(m.id) and registry.get(m.id).is_available())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Datasets", len(all_datasets))

with col2:
    st.metric("Downloaded", available)

with col3:
    total_subjects = sum(m.subject_count for m in all_datasets)
    st.metric("Total Subjects", f"{total_subjects:,}")

with col4:
    current = get_active_dataset()
    current_name = SYNTHETIC_DATASET_NAME if current == SYNTHETIC_DATASET_ID else current
    st.metric("Active", current_name[:15] + "..." if len(current_name) > 15 else current_name)
