"""
Base Dataset Adapter

Abstract base class for all dataset adapters. Each adapter normalizes
a specific dataset format to HealthBridge's common schema.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import date


class DataCategory(Enum):
    """Categories of health datasets."""
    WEARABLES = "wearables"
    CLINICAL = "clinical"
    GENETICS = "genetics"
    SLEEP = "sleep"
    CGM = "cgm"


@dataclass
class DatasetMetadata:
    """Metadata about a dataset."""
    id: str
    name: str
    description: str
    category: DataCategory
    source_url: str
    citation: str
    subject_count: int
    date_range: Optional[str] = None
    size_mb: Optional[float] = None
    available_fields: List[str] = field(default_factory=list)
    download_instructions: str = ""
    requires_auth: bool = False
    license: str = "Unknown"


@dataclass
class Subject:
    """A participant/subject in a dataset."""
    id: str
    display_name: str
    date_range: Optional[str] = None
    record_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseDatasetAdapter(ABC):
    """
    Abstract base class for dataset adapters.

    Each adapter must implement methods to:
    - Check data availability
    - List subjects
    - Load normalized health data
    """

    def __init__(self, data_dir: Path):
        """
        Initialize adapter with data directory.

        Args:
            data_dir: Root directory where datasets are stored
        """
        self.data_dir = data_dir
        self._dataset_path: Optional[Path] = None

    @property
    @abstractmethod
    def metadata(self) -> DatasetMetadata:
        """Return dataset metadata."""
        pass

    @property
    def dataset_path(self) -> Path:
        """Path to this dataset's directory."""
        if self._dataset_path is None:
            self._dataset_path = self.data_dir / self.metadata.id
        return self._dataset_path

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if dataset is downloaded and available locally.

        Returns:
            True if dataset files exist and are valid
        """
        pass

    @abstractmethod
    def list_subjects(self) -> List[Subject]:
        """
        List all available subjects in the dataset.

        Returns:
            List of Subject objects
        """
        pass

    @abstractmethod
    def load_health_data(self, subject_id: str) -> List[Dict]:
        """
        Load health data for a specific subject.

        Args:
            subject_id: ID of the subject to load

        Returns:
            List of daily health records in HealthBridge schema:
            {
                'date': date,
                'sleep_duration': float or None,
                'sleep_score': int or None,
                'deep_sleep': float or None,
                'rem_sleep': float or None,
                'light_sleep': float or None,
                'awake_time': float or None,
                'resting_hr': int or None,
                'hrv': int or None,
                'hr_min': int or None,
                'hr_max': int or None,
                'steps': int or None,
                'active_calories': int or None,
                'total_calories': int or None,
                'distance_km': float or None,
                'floors_climbed': int or None,
                'active_minutes': int or None,
                'sedentary_minutes': int or None,
                'glucose_avg': float or None,
                'glucose_min': float or None,
                'glucose_max': float or None,
                'glucose_std': float or None,
                'time_in_range': float or None,
                'readiness_score': int or None,
                'stress_score': int or None,
                'recovery_score': int or None,
            }
        """
        pass

    def load_lab_data(self, subject_id: str) -> Optional[List[Dict]]:
        """
        Load lab/biomarker data for a subject if available.

        Args:
            subject_id: ID of the subject to load

        Returns:
            List of lab records or None if not available
        """
        return None

    def load_genetic_data(self, subject_id: str) -> Optional[Dict]:
        """
        Load genetic data for a subject if available.

        Args:
            subject_id: ID of the subject to load

        Returns:
            Genetic data dict or None if not available
        """
        return None

    def load_workouts(self, subject_id: str) -> Optional[List[Dict]]:
        """
        Load workout data for a subject if available.

        Args:
            subject_id: ID of the subject to load

        Returns:
            List of workout records or None if not available
        """
        return None

    def get_subject_profile(self, subject_id: str) -> Optional[Dict]:
        """
        Get demographic/profile info for a subject if available.

        Args:
            subject_id: ID of the subject

        Returns:
            Profile dict with keys like 'age', 'sex', 'height_cm', 'weight_kg'
            or None if not available
        """
        return None

    def _create_empty_record(self, record_date: date) -> Dict:
        """Create an empty health record with all fields set to None."""
        return {
            'date': record_date,
            'sleep_duration': None,
            'sleep_score': None,
            'deep_sleep': None,
            'rem_sleep': None,
            'light_sleep': None,
            'awake_time': None,
            'resting_hr': None,
            'hrv': None,
            'hr_min': None,
            'hr_max': None,
            'steps': None,
            'active_calories': None,
            'total_calories': None,
            'distance_km': None,
            'floors_climbed': None,
            'active_minutes': None,
            'sedentary_minutes': None,
            'glucose_avg': None,
            'glucose_min': None,
            'glucose_max': None,
            'glucose_std': None,
            'time_in_range': None,
            'readiness_score': None,
            'stress_score': None,
            'recovery_score': None,
        }
