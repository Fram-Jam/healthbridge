"""
NSRR MESA Dataset Adapter

Loads data from the National Sleep Research Resource MESA study.
Source: https://sleepdata.org/datasets/mesa

Contains sleep data from 2,237 participants including:
- Polysomnography (PSG) recordings
- 7-day actigraphy
- Sleep questionnaires
"""

import csv
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from ..base import BaseDatasetAdapter, DatasetMetadata, Subject, DataCategory
from ..registry import registry


@registry.register
class NSRRMesaAdapter(BaseDatasetAdapter):
    """Adapter for NSRR MESA Sleep Dataset."""

    @property
    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            id="nsrr_mesa",
            name="NSRR MESA Sleep Study",
            description="2,237 participants with polysomnography recordings and 7-day actigraphy from the Multi-Ethnic Study of Atherosclerosis.",
            category=DataCategory.SLEEP,
            source_url="https://sleepdata.org/datasets/mesa",
            citation="Chen, X., et al. (2015). Racial/Ethnic Differences in Sleep Disturbances. Sleep, 38(6).",
            subject_count=2237,
            date_range="2010-2013",
            size_mb=500,
            available_fields=[
                "sleep_duration", "sleep_efficiency", "deep_sleep", "rem_sleep",
                "light_sleep", "awake_time", "sleep_latency", "waso",
                "ahi", "oxygen_saturation"
            ],
            download_instructions="""
1. Register at https://sleepdata.org/
2. Request access to MESA dataset
3. Download: mesa-sleep-dataset-*.csv, mesa-actigraphy-*.csv
4. Place files in data/datasets/nsrr_mesa/
Note: Requires data use agreement approval (~1-2 weeks)
            """.strip(),
            requires_auth=True,
            license="Data Use Agreement Required"
        )

    def is_available(self) -> bool:
        """Check if NSRR MESA data is downloaded."""
        data_path = self.dataset_path
        if not data_path.exists():
            return False

        # Check for main data files
        sleep_files = (
            list(data_path.glob("*sleep*.csv")) +
            list(data_path.glob("*psg*.csv")) +
            list(data_path.glob("*polysom*.csv"))
        )

        return len(sleep_files) > 0

    def _find_file(self, pattern: str) -> Optional[Path]:
        """Find a file matching a pattern."""
        for p in [f"*{pattern}*.csv", f"*{pattern.lower()}*.csv"]:
            matches = list(self.dataset_path.glob(p))
            if matches:
                return matches[0]
        return None

    def list_subjects(self) -> List[Subject]:
        """List all subjects in the dataset."""
        if not self.is_available():
            return []

        # Find main sleep data file
        sleep_file = self._find_file("sleep") or self._find_file("psg")
        if not sleep_file:
            return []

        subjects = []
        seen_ids = set()

        try:
            with open(sleep_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # MESA uses 'mesaid' as subject ID
                    subj_id = (
                        row.get('mesaid') or
                        row.get('nsrrid') or
                        row.get('id') or
                        ''
                    )

                    if not subj_id or subj_id in seen_ids:
                        continue

                    seen_ids.add(subj_id)

                    subjects.append(Subject(
                        id=subj_id,
                        display_name=f"MESA-{subj_id}",
                        date_range=None,
                        record_count=1,
                        metadata={
                            'study': 'MESA',
                        }
                    ))
        except (IOError, csv.Error):
            pass

        return subjects[:200]  # Limit for performance

    def load_health_data(self, subject_id: str) -> List[Dict]:
        """
        Load health data for a subject.

        MESA has PSG (single night) and actigraphy (7 days).
        """
        if not self.is_available():
            return []

        records = []

        # Load PSG data (single night)
        psg_data = self._load_psg_data(subject_id)
        if psg_data:
            records.append(psg_data)

        # Load actigraphy data (multiple days)
        actigraphy_data = self._load_actigraphy_data(subject_id)
        records.extend(actigraphy_data)

        return sorted(records, key=lambda x: x['date'])

    def _load_psg_data(self, subject_id: str) -> Optional[Dict]:
        """Load polysomnography data for a subject."""
        sleep_file = self._find_file("sleep") or self._find_file("psg")
        if not sleep_file:
            return None

        try:
            with open(sleep_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subj_id = row.get('mesaid') or row.get('nsrrid') or ''
                    if subj_id != subject_id:
                        continue

                    # Use a reference date since MESA doesn't have specific dates
                    record_date = date(2012, 1, 1)

                    record = self._create_empty_record(record_date)

                    # Total sleep time (minutes -> hours)
                    tst = self._safe_float(row.get('slpprdp'))  # Sleep period
                    if tst:
                        record['sleep_duration'] = tst / 60

                    # Sleep efficiency
                    eff = self._safe_float(row.get('slpeffp'))
                    if eff:
                        record['sleep_score'] = int(min(100, eff))

                    # Sleep stages (minutes -> hours)
                    # N3 = deep sleep
                    n3 = self._safe_float(row.get('timest3p'))
                    if n3:
                        record['deep_sleep'] = n3 / 60

                    # REM sleep
                    rem = self._safe_float(row.get('timeremp'))
                    if rem:
                        record['rem_sleep'] = rem / 60

                    # N1 + N2 = light sleep
                    n1 = self._safe_float(row.get('timest1p')) or 0
                    n2 = self._safe_float(row.get('timest2p')) or 0
                    if n1 or n2:
                        record['light_sleep'] = (n1 + n2) / 60

                    # Wake after sleep onset
                    waso = self._safe_float(row.get('waso'))
                    if waso:
                        record['awake_time'] = waso / 60

                    return record

        except (IOError, csv.Error):
            pass

        return None

    def _load_actigraphy_data(self, subject_id: str) -> List[Dict]:
        """Load actigraphy data for a subject."""
        result = []

        acti_file = self._find_file("actigraphy") or self._find_file("acti")
        if not acti_file:
            return result

        try:
            with open(acti_file, 'r') as f:
                reader = csv.DictReader(f)
                day_num = 0
                for row in reader:
                    subj_id = row.get('mesaid') or row.get('nsrrid') or ''
                    if subj_id != subject_id:
                        continue

                    # Generate sequential dates
                    record_date = date(2012, 1, 1) + timedelta(days=day_num)
                    day_num += 1

                    record = self._create_empty_record(record_date)

                    # Actigraphy sleep duration
                    sleep_min = self._safe_float(row.get('sleepmain') or row.get('sleeptime'))
                    if sleep_min:
                        record['sleep_duration'] = sleep_min / 60

                    # Sleep efficiency from actigraphy
                    eff = self._safe_float(row.get('efficiency') or row.get('slpeff'))
                    if eff:
                        record['sleep_score'] = int(min(100, eff))

                    # Activity/steps if available
                    activity = self._safe_int(row.get('activity') or row.get('actcount'))
                    if activity:
                        # Convert activity counts to approximate steps
                        record['steps'] = activity

                    result.append(record)

        except (IOError, csv.Error):
            pass

        return result

    def get_subject_profile(self, subject_id: str) -> Optional[Dict]:
        """Get demographic/profile info for a subject."""
        # Try to find demographics file
        demo_file = self._find_file("demo") or self._find_file("baseline")
        if not demo_file:
            # Try the main sleep file which may have demographics
            demo_file = self._find_file("sleep")

        if not demo_file:
            return None

        try:
            with open(demo_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    subj_id = row.get('mesaid') or row.get('nsrrid') or ''
                    if subj_id != subject_id:
                        continue

                    return {
                        'age': self._safe_int(row.get('sleepage5c') or row.get('age')),
                        'sex': self._parse_sex(row.get('gender') or row.get('gender1')),
                        'height_cm': self._safe_float(row.get('htcm')),
                        'weight_kg': self._safe_float(row.get('wtkg')),
                    }

        except (IOError, csv.Error):
            pass

        return None

    @staticmethod
    def _parse_sex(value) -> Optional[str]:
        """Parse sex/gender value."""
        if not value:
            return None
        value = str(value).lower()
        if value in ['1', 'male', 'm']:
            return 'male'
        elif value in ['2', 'female', 'f']:
            return 'female'
        return None

    @staticmethod
    def _safe_float(value) -> Optional[float]:
        """Safely convert value to float."""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(value) -> Optional[int]:
        """Safely convert value to int."""
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
