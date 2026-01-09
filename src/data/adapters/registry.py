"""
Dataset Registry

Central registry for discovering and managing dataset adapters.
"""

from pathlib import Path
from typing import Dict, List, Optional, Type
from .base import BaseDatasetAdapter, DataCategory, DatasetMetadata


class DatasetRegistry:
    """
    Registry for dataset adapters.

    Provides discovery and instantiation of adapters.
    """

    def __init__(self):
        self._adapters: Dict[str, Type[BaseDatasetAdapter]] = {}
        self._instances: Dict[str, BaseDatasetAdapter] = {}
        self._data_dir: Optional[Path] = None

    def set_data_dir(self, data_dir: Path):
        """Set the root data directory for all adapters."""
        self._data_dir = data_dir
        self._instances.clear()

    @property
    def data_dir(self) -> Path:
        """Get the data directory, defaulting to ./data/datasets."""
        if self._data_dir is None:
            self._data_dir = Path(__file__).parent.parent.parent.parent / "data" / "datasets"
        return self._data_dir

    def register(self, adapter_class: Type[BaseDatasetAdapter]) -> Type[BaseDatasetAdapter]:
        """
        Register an adapter class.

        Can be used as a decorator:
            @registry.register
            class MyAdapter(BaseDatasetAdapter):
                ...
        """
        temp_instance = adapter_class(self.data_dir)
        dataset_id = temp_instance.metadata.id
        self._adapters[dataset_id] = adapter_class
        return adapter_class

    def get(self, dataset_id: str) -> Optional[BaseDatasetAdapter]:
        """
        Get an adapter instance by dataset ID.

        Args:
            dataset_id: The unique dataset identifier

        Returns:
            Adapter instance or None if not found
        """
        if dataset_id not in self._adapters:
            return None

        if dataset_id not in self._instances:
            self._instances[dataset_id] = self._adapters[dataset_id](self.data_dir)

        return self._instances[dataset_id]

    def list_all(self) -> List[DatasetMetadata]:
        """List metadata for all registered datasets."""
        result = []
        for dataset_id, adapter_class in self._adapters.items():
            adapter = self.get(dataset_id)
            if adapter:
                result.append(adapter.metadata)
        return result

    def list_by_category(self, category: DataCategory) -> List[DatasetMetadata]:
        """List datasets filtered by category."""
        return [m for m in self.list_all() if m.category == category]

    def list_available(self) -> List[DatasetMetadata]:
        """List only datasets that are downloaded and available."""
        result = []
        for dataset_id in self._adapters:
            adapter = self.get(dataset_id)
            if adapter and adapter.is_available():
                result.append(adapter.metadata)
        return result

    def get_available_ids(self) -> List[str]:
        """Get IDs of all available (downloaded) datasets."""
        return [m.id for m in self.list_available()]


# Global registry instance
registry = DatasetRegistry()


def register_all_adapters():
    """Import all adapter modules to trigger registration."""
    try:
        from . import wearables
    except ImportError:
        pass

    try:
        from . import clinical
    except ImportError:
        pass

    try:
        from . import genetics
    except ImportError:
        pass

    try:
        from . import sleep
    except ImportError:
        pass

    try:
        from . import cgm
    except ImportError:
        pass
