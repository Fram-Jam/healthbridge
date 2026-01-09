"""
Session State Management for Health Data

Handles data persistence within Streamlit sessions.
"""

import streamlit as st
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

# Dataset constants
SYNTHETIC_DATASET_ID = "synthetic"
SYNTHETIC_DATASET_NAME = "Synthetic (Demo)"


def init_storage():
    """Initialize all session state variables."""
    defaults = {
        'authenticated': True,
        'user_id': 'demo_user',
        'user_name': 'Demo User',
        'connected_devices': [],
        'health_data': None,
        'patient_profile': None,
        'lab_data': None,
        'genetic_data': None,
        'workouts': None,
        'demo_mode': True,
        'data_loaded': False,
        # Dataset selection
        'active_dataset': SYNTHETIC_DATASET_ID,
        'active_subject': None,
        'settings': {
            'weight_unit': 'kg',
            'height_unit': 'cm',
            'temp_unit': 'celsius',
            'date_format': 'YYYY-MM-DD',
            'time_format': '12h',
            'default_time_range': 30,
            'show_targets': True,
            'show_averages': True,
        }
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_health_data() -> Optional[List[Dict]]:
    """Get health data from session state."""
    return st.session_state.get('health_data')


def set_health_data(data: List[Dict]):
    """Set health data in session state."""
    st.session_state.health_data = data


def get_patient_profile() -> Optional[Any]:
    """Get patient profile from session state."""
    return st.session_state.get('patient_profile')


def set_patient_profile(profile: Any):
    """Set patient profile in session state."""
    st.session_state.patient_profile = profile


def get_lab_data() -> Optional[List]:
    """Get lab data from session state."""
    return st.session_state.get('lab_data')


def set_lab_data(data: List):
    """Set lab data in session state."""
    st.session_state.lab_data = data


def get_connected_devices() -> List[Dict]:
    """Get list of connected devices."""
    return st.session_state.get('connected_devices', [])


def add_device(device: Dict):
    """Add a connected device."""
    devices = get_connected_devices()
    if not any(d['type'] == device['type'] for d in devices):
        devices.append(device)
        st.session_state.connected_devices = devices


def remove_device(device_type: str):
    """Remove a connected device by type."""
    devices = get_connected_devices()
    st.session_state.connected_devices = [
        d for d in devices if d['type'] != device_type
    ]


def is_device_connected(device_type: str) -> bool:
    """Check if a device type is connected."""
    return any(d['type'] == device_type for d in get_connected_devices())


def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting value."""
    settings = st.session_state.get('settings', {})
    return settings.get(key, default)


def set_setting(key: str, value: Any):
    """Set a setting value."""
    if 'settings' not in st.session_state:
        st.session_state.settings = {}
    st.session_state.settings[key] = value


def clear_all_data():
    """Clear all health data from session."""
    st.session_state.health_data = None
    st.session_state.lab_data = None
    st.session_state.patient_profile = None
    st.session_state.data_loaded = False


def mark_data_loaded():
    """Mark data as loaded."""
    st.session_state.data_loaded = True


def is_data_loaded() -> bool:
    """Check if data has been loaded."""
    return st.session_state.get('data_loaded', False)


# Dataset selection functions

def get_active_dataset() -> str:
    """Get the currently active dataset ID."""
    return st.session_state.get('active_dataset', SYNTHETIC_DATASET_ID)


def set_active_dataset(dataset_id: str):
    """Set the active dataset."""
    st.session_state.active_dataset = dataset_id
    # Clear loaded data when switching datasets
    clear_all_data()


def get_active_subject() -> Optional[str]:
    """Get the currently active subject ID."""
    return st.session_state.get('active_subject')


def set_active_subject(subject_id: Optional[str]):
    """Set the active subject."""
    st.session_state.active_subject = subject_id
    # Clear loaded data when switching subjects
    clear_all_data()


def is_synthetic_mode() -> bool:
    """Check if using synthetic (demo) data."""
    return get_active_dataset() == SYNTHETIC_DATASET_ID


def get_genetic_data() -> Optional[Dict]:
    """Get genetic data from session state."""
    return st.session_state.get('genetic_data')


def set_genetic_data(data: Dict):
    """Set genetic data in session state."""
    st.session_state.genetic_data = data


def get_workouts() -> Optional[List[Dict]]:
    """Get workout data from session state."""
    return st.session_state.get('workouts')


def set_workouts(data: List[Dict]):
    """Set workout data in session state."""
    st.session_state.workouts = data


def load_dataset_data(dataset_id: str, subject_id: Optional[str] = None) -> bool:
    """
    Load data from a specific dataset and subject.

    Args:
        dataset_id: The dataset to load from
        subject_id: Optional subject ID (required for multi-subject datasets)

    Returns:
        True if data was loaded successfully
    """
    if dataset_id == SYNTHETIC_DATASET_ID:
        # Use synthetic data generator
        return _load_synthetic_data()

    # Import here to avoid circular imports
    from .adapters.registry import registry, register_all_adapters

    # Ensure adapters are registered
    register_all_adapters()

    adapter = registry.get(dataset_id)
    if adapter is None:
        return False

    if not adapter.is_available():
        return False

    if subject_id is None:
        subjects = adapter.list_subjects()
        if not subjects:
            return False
        subject_id = subjects[0].id

    # Load health data
    health_data = adapter.load_health_data(subject_id)
    if health_data:
        set_health_data(health_data)

    # Load optional data types
    lab_data = adapter.load_lab_data(subject_id)
    if lab_data:
        set_lab_data(lab_data)

    genetic_data = adapter.load_genetic_data(subject_id)
    if genetic_data:
        set_genetic_data(genetic_data)

    workouts = adapter.load_workouts(subject_id)
    if workouts:
        set_workouts(workouts)

    profile = adapter.get_subject_profile(subject_id)
    if profile:
        set_patient_profile(profile)

    mark_data_loaded()
    return True


def _load_synthetic_data() -> bool:
    """Load synthetic demo data."""
    from .synthetic.patient_generator import generate_synthetic_patient

    patient = generate_synthetic_patient()
    set_patient_profile(patient)
    set_health_data(patient.health_data)
    set_lab_data(patient.lab_data)

    # Generate genetic data
    from .synthetic.genetic_generator import generate_genetic_profile
    genetic_profile = generate_genetic_profile()
    set_genetic_data({
        'disease_risks': [vars(r) for r in genetic_profile.disease_risks],
        'carrier_status': [vars(c) for c in genetic_profile.carrier_status],
        'drug_responses': [vars(d) for d in genetic_profile.drug_responses],
        'traits': [vars(t) for t in genetic_profile.traits],
        'ancestry': vars(genetic_profile.ancestry),
        'last_updated': genetic_profile.last_updated.isoformat(),
    })

    set_workouts(patient.workouts)
    mark_data_loaded()
    return True
