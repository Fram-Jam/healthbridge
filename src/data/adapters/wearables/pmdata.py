"""
PMData Dataset Adapter

Loads data from the PMData dataset from Simula Research Laboratory.
Source: https://datasets.simula.no/pmdata/

Contains data from 16 participants over 5 months including:
- 20M+ heart rate readings
- 1,836 sleep score assessments
- Activity and step data
"""

import json
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional

from ..base import BaseDatasetAdapter, DatasetMetadata, Subject, DataCategory
from ..registry import registry


@registry.register
class PMDataAdapter(BaseDatasetAdapter):
    """Adapter for PMData Wearables Dataset."""

    @property
    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            id="pmdata",
            name="PMData (Simula)",
            description="16 participants over 5 months with 20M+ heart rate readings, sleep scores, and activity data from Fitbit devices.",
            category=DataCategory.WEARABLES,
            source_url="https://datasets.simula.no/pmdata/",
            citation="Thambawita, V., et al. (2020). PMData: A Sports Logging Dataset. MMSys '20.",
            subject_count=16,
            date_range="~5 months per subject",
            size_mb=500,
            available_fields=[
                "steps", "resting_hr", "hrv", "sleep_duration", "sleep_score",
                "deep_sleep", "rem_sleep", "light_sleep", "active_calories"
            ],
            download_instructions="""
1. Visit https://datasets.simula.no/pmdata/
2. Download the dataset (requires acceptance of terms)
3. Extract to data/datasets/pmdata/
            """.strip(),
            requires_auth=False,
            license="CC BY 4.0"
        )

    def is_available(self) -> bool:
        """Check if PMData is downloaded."""
        data_path = self.dataset_path
        if not data_path.exists():
            return False

        # Check for participant directories
        participant_dirs = list(data_path.glob("p[0-9]*"))
        return len(participant_dirs) > 0

    def list_subjects(self) -> List[Subject]:
        """List all subjects in the dataset."""
        if not self.is_available():
            return []

        subjects = []
        for p_dir in sorted(self.dataset_path.glob("p[0-9]*")):
            if not p_dir.is_dir():
                continue

            subj_id = p_dir.name
            record_count = 0
            dates = set()

            # Count sleep records
            sleep_file = p_dir / "fitbit" / "sleep.json"
            if sleep_file.exists():
                try:
                    with open(sleep_file, 'r') as f:
                        sleep_data = json.load(f)
                        record_count += len(sleep_data)
                        for record in sleep_data:
                            if 'dateOfSleep' in record:
                                dates.add(record['dateOfSleep'])
                except (json.JSONDecodeError, IOError):
                    pass

            date_range = None
            if dates:
                sorted_dates = sorted(dates)
                date_range = f"{sorted_dates[0]} to {sorted_dates[-1]}"

            subjects.append(Subject(
                id=subj_id,
                display_name=f"Participant {subj_id.upper()}",
                date_range=date_range,
                record_count=record_count
            ))

        return subjects

    def load_health_data(self, subject_id: str) -> List[Dict]:
        """Load and normalize health data for a subject."""
        if not self.is_available():
            return []

        subj_path = self.dataset_path / subject_id / "fitbit"
        if not subj_path.exists():
            return []

        # Load data from various sources
        sleep_data = self._load_sleep_data(subj_path)
        hr_data = self._load_hr_data(subj_path)
        activity_data = self._load_activity_data(subj_path)

        # Get all unique dates
        all_dates = set(sleep_data.keys()) | set(hr_data.keys()) | set(activity_data.keys())

        # Merge into unified records
        records = []
        for record_date in sorted(all_dates):
            record = self._create_empty_record(record_date)

            # Sleep data
            if record_date in sleep_data:
                slp = sleep_data[record_date]
                record['sleep_duration'] = slp.get('sleep_duration')
                record['sleep_score'] = slp.get('sleep_score')
                record['deep_sleep'] = slp.get('deep_sleep')
                record['rem_sleep'] = slp.get('rem_sleep')
                record['light_sleep'] = slp.get('light_sleep')
                record['awake_time'] = slp.get('awake_time')

            # Heart rate data
            if record_date in hr_data:
                hr = hr_data[record_date]
                record['resting_hr'] = hr.get('resting_hr')
                record['hrv'] = hr.get('hrv')
                record['hr_min'] = hr.get('hr_min')
                record['hr_max'] = hr.get('hr_max')

            # Activity data
            if record_date in activity_data:
                act = activity_data[record_date]
                record['steps'] = act.get('steps')
                record['active_calories'] = act.get('active_calories')
                record['active_minutes'] = act.get('active_minutes')

            records.append(record)

        return records

    def _load_sleep_data(self, subj_path: Path) -> Dict[date, Dict]:
        """Load sleep data from JSON files."""
        result = {}
        sleep_file = subj_path / "sleep.json"

        if not sleep_file.exists():
            return result

        try:
            with open(sleep_file, 'r') as f:
                sleep_records = json.load(f)
        except (json.JSONDecodeError, IOError):
            return result

        for record in sleep_records:
            try:
                record_date = datetime.strptime(record['dateOfSleep'], '%Y-%m-%d').date()
            except (ValueError, KeyError):
                continue

            # Extract sleep stages if available
            stages = record.get('levels', {}).get('summary', {})

            result[record_date] = {
                'sleep_duration': record.get('minutesAsleep', 0) / 60 if record.get('minutesAsleep') else None,
                'sleep_score': record.get('efficiency'),
                'deep_sleep': stages.get('deep', {}).get('minutes', 0) / 60 if stages.get('deep') else None,
                'rem_sleep': stages.get('rem', {}).get('minutes', 0) / 60 if stages.get('rem') else None,
                'light_sleep': stages.get('light', {}).get('minutes', 0) / 60 if stages.get('light') else None,
                'awake_time': stages.get('wake', {}).get('minutes', 0) / 60 if stages.get('wake') else None,
            }

        return result

    def _load_hr_data(self, subj_path: Path) -> Dict[date, Dict]:
        """Load heart rate data from JSON files."""
        result = {}

        # PMData stores HR in daily files
        hr_dir = subj_path / "heart_rate"
        if not hr_dir.exists():
            return result

        for hr_file in hr_dir.glob("*.json"):
            try:
                # Extract date from filename (heart_rate-YYYY-MM-DD.json)
                date_str = hr_file.stem.replace("heart_rate-", "")
                record_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                continue

            try:
                with open(hr_file, 'r') as f:
                    hr_records = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            if not hr_records:
                continue

            # Extract HR values
            hr_values = []
            for record in hr_records:
                if 'value' in record:
                    if isinstance(record['value'], dict):
                        hr_values.append(record['value'].get('bpm', 0))
                    else:
                        hr_values.append(record['value'])

            if hr_values:
                sorted_hr = sorted(hr_values)
                resting_idx = max(0, int(len(sorted_hr) * 0.1))

                result[record_date] = {
                    'resting_hr': sorted_hr[resting_idx],
                    'hr_min': min(hr_values),
                    'hr_max': max(hr_values),
                    'hrv': None,  # HRV not directly available in basic HR data
                }

        return result

    def _load_activity_data(self, subj_path: Path) -> Dict[date, Dict]:
        """Load activity data from JSON files."""
        result = {}

        # Check for steps data
        steps_file = subj_path / "steps.json"
        if steps_file.exists():
            try:
                with open(steps_file, 'r') as f:
                    steps_records = json.load(f)

                for record in steps_records:
                    try:
                        record_date = datetime.strptime(record['dateTime'], '%Y-%m-%d').date()
                        result[record_date] = {
                            'steps': int(record.get('value', 0)),
                            'active_calories': None,
                            'active_minutes': None,
                        }
                    except (ValueError, KeyError):
                        continue
            except (json.JSONDecodeError, IOError):
                pass

        # Check for calories data
        calories_file = subj_path / "calories.json"
        if calories_file.exists():
            try:
                with open(calories_file, 'r') as f:
                    cal_records = json.load(f)

                for record in cal_records:
                    try:
                        record_date = datetime.strptime(record['dateTime'], '%Y-%m-%d').date()
                        if record_date not in result:
                            result[record_date] = {'steps': None, 'active_calories': None, 'active_minutes': None}
                        result[record_date]['active_calories'] = int(record.get('value', 0))
                    except (ValueError, KeyError):
                        continue
            except (json.JSONDecodeError, IOError):
                pass

        return result
