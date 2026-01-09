"""
Dataset Adapters for HealthBridge

Provides a unified interface for loading health data from various public datasets.
"""

from .base import (
    DataCategory,
    DatasetMetadata,
    Subject,
    BaseDatasetAdapter,
)
from .registry import DatasetRegistry, registry

__all__ = [
    'DataCategory',
    'DatasetMetadata',
    'Subject',
    'BaseDatasetAdapter',
    'DatasetRegistry',
    'registry',
]
