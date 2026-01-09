"""
Fitbit Kaggle Dataset Adapter

Loads data from the Kaggle Fitbit Fitness Tracker Dataset.
Source: https://www.kaggle.com/datasets/arashnic/fitbit

Contains data from 30 Fitbit users including:
- Daily activity (steps, distance, calories)
- Heart rate (second-level)
- Sleep logs
- Weight logs
"""

import csv
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional

from ..base import BaseDatasetAdapter, DatasetMetadata, Subject, DataCategory
from ..registry import registry


@registry.register
class FitbitKaggleAdapter(BaseDatasetAdapter):
    """Adapter for Kaggle Fitbit Fitness Tracker Dataset."""

    @property
    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            id="fitbit_kaggle",
            name="Fitbit Fitness Tracker (Kaggle)",
            description="30 Fitbit users' daily activity, heart rate, and sleep data collected via Amazon Mechanical Turk survey (March-May 2016).",
            category=DataCategory.WEARABLES,
            source_url="https://www.kaggle.com/datasets/arashnic/fitbit",
            citation="Furberg, R., Brinton, J., Keating, M., & Ortiz, A. (2016). Crowd-sourced Fitbit datasets 03.12.2016-05.12.2016. Zenodo.",
            subject_count=30,
            date_range="2016-03-12 to 2016-05-12",
            size_mb=85,
            available_fields=[
                "steps", "distance_km", "active_calories", "total_calories",
                "active_minutes", "sedentary_minutes", "sleep_duration",
                "resting_hr", "hr_min", "hr_max"
            ],
            download_instructions="""
1. Install Kaggle CLI: pip install kaggle
2. Set up Kaggle API credentials (~/.kaggle/kaggle.json)
3. Run: kaggle datasets download -d arashnic/fitbit -p data/datasets/fitbit_kaggle --unzip
            """.strip(),
            requires_auth=True,
            license="CC0: Public Domain"
        )

    def is_available(self) -> bool:
        """Check if Fitbit data is downloaded."""
        # Look for key files in the dataset
        data_path = self.dataset_path
        if not data_path.exists():
            return False

        # Check for merged daily activity file (most important)
        possible_paths = [
            data_path / "Fitabase Data 4.12.16-5.12.16" / "dailyActivity_merged.csv",
            data_path / "dailyActivity_merged.csv",
            data_path / "mturkfitbit_export_4.12.16-5.12.16" / "Fitabase Data 4.12.16-5.12.16" / "dailyActivity_merged.csv",
        ]

        return any(p.exists() for p in possible_paths)

    def _find_file(self, filename: str) -> Optional[Path]:
        """Find a file in the dataset directory (handles nested structure)."""
        # Try common locations
        candidates = [
            self.dataset_path / filename,
            self.dataset_path / "Fitabase Data 4.12.16-5.12.16" / filename,
            self.dataset_path / "mturkfitbit_export_4.12.16-5.12.16" / "Fitabase Data 4.12.16-5.12.16" / filename,
        ]

        for path in candidates:
            if path.exists():
                return path

        # Recursive search as fallback
        for path in self.dataset_path.rglob(filename):
            return path

        return None

    def list_subjects(self) -> List[Subject]:
        """List all subjects in the dataset."""
        if not self.is_available():
            return []

        activity_file = self._find_file("dailyActivity_merged.csv")
        if not activity_file:
            return []

        subject_data = defaultdict(lambda: {"dates": set(), "records": 0})

        with open(activity_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                subj_id = row.get('Id', '')
                if subj_id:
                    subject_data[subj_id]["records"] += 1
                    date_str = row.get('ActivityDate', '')
                    if date_str:
                        subject_data[subj_id]["dates"].add(date_str)

        subjects = []
        for subj_id, data in sorted(subject_data.items()):
            dates = sorted(data["dates"])
            date_range = f"{dates[0]} to {dates[-1]}" if dates else None
            subjects.append(Subject(
                id=subj_id,
                display_name=f"Subject {subj_id[-4:]}",
                date_range=date_range,
                record_count=data["records"]
            ))

        return subjects

    def load_health_data(self, subject_id: str) -> List[Dict]:
        """Load and normalize health data for a subject."""
        if not self.is_available():
            return []

        # Gather data from all sources
        activity_data = self._load_activity_data(subject_id)
        sleep_data = self._load_sleep_data(subject_id)
        hr_data = self._load_heart_rate_data(subject_id)

        # Get all unique dates
        all_dates = set(activity_data.keys()) | set(sleep_data.keys()) | set(hr_data.keys())

        # Merge into unified records
        records = []
        for record_date in sorted(all_dates):
            record = self._create_empty_record(record_date)

            # Activity data
            if record_date in activity_data:
                act = activity_data[record_date]
                record['steps'] = act.get('steps')
                record['distance_km'] = act.get('distance_km')
                record['active_calories'] = act.get('active_calories')
                record['total_calories'] = act.get('total_calories')
                record['active_minutes'] = act.get('active_minutes')
                record['sedentary_minutes'] = act.get('sedentary_minutes')

            # Sleep data
            if record_date in sleep_data:
                slp = sleep_data[record_date]
                record['sleep_duration'] = slp.get('sleep_duration')
                record['sleep_score'] = slp.get('sleep_score')

            # Heart rate data
            if record_date in hr_data:
                hr = hr_data[record_date]
                record['resting_hr'] = hr.get('resting_hr')
                record['hr_min'] = hr.get('hr_min')
                record['hr_max'] = hr.get('hr_max')

            records.append(record)

        return records

    def _load_activity_data(self, subject_id: str) -> Dict[date, Dict]:
        """Load daily activity data for a subject."""
        result = {}
        activity_file = self._find_file("dailyActivity_merged.csv")

        if not activity_file:
            return result

        with open(activity_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Id') != subject_id:
                    continue

                try:
                    record_date = datetime.strptime(row['ActivityDate'], '%m/%d/%Y').date()
                except (ValueError, KeyError):
                    try:
                        record_date = datetime.strptime(row['ActivityDate'], '%Y-%m-%d').date()
                    except (ValueError, KeyError):
                        continue

                result[record_date] = {
                    'steps': self._safe_int(row.get('TotalSteps')),
                    'distance_km': self._safe_float(row.get('TotalDistance')),
                    'active_calories': self._safe_int(row.get('Calories')),
                    'total_calories': self._safe_int(row.get('Calories')),
                    'active_minutes': (
                        self._safe_int(row.get('VeryActiveMinutes', 0)) +
                        self._safe_int(row.get('FairlyActiveMinutes', 0)) +
                        self._safe_int(row.get('LightlyActiveMinutes', 0))
                    ),
                    'sedentary_minutes': self._safe_int(row.get('SedentaryMinutes')),
                }

        return result

    def _load_sleep_data(self, subject_id: str) -> Dict[date, Dict]:
        """Load sleep data for a subject."""
        result = {}
        sleep_file = self._find_file("sleepDay_merged.csv")

        if not sleep_file:
            return result

        with open(sleep_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Id') != subject_id:
                    continue

                try:
                    # Format: "4/12/2016 12:00:00 AM"
                    date_str = row['SleepDay'].split()[0]
                    record_date = datetime.strptime(date_str, '%m/%d/%Y').date()
                except (ValueError, KeyError):
                    continue

                total_minutes = self._safe_float(row.get('TotalMinutesAsleep'))
                sleep_hours = total_minutes / 60 if total_minutes else None

                # Estimate sleep score from efficiency
                sleep_score = None
                if total_minutes:
                    time_in_bed = self._safe_float(row.get('TotalTimeInBed'))
                    if time_in_bed and time_in_bed > 0:
                        efficiency = (total_minutes / time_in_bed) * 100
                        # Map efficiency to a 0-100 score
                        sleep_score = min(100, int(efficiency * 1.1))

                result[record_date] = {
                    'sleep_duration': sleep_hours,
                    'sleep_score': sleep_score,
                }

        return result

    def _load_heart_rate_data(self, subject_id: str) -> Dict[date, Dict]:
        """Load aggregated heart rate data for a subject."""
        result = {}
        hr_file = self._find_file("heartrate_seconds_merged.csv")

        if not hr_file:
            return result

        # Aggregate second-level data to daily
        daily_hr = defaultdict(list)

        with open(hr_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Id') != subject_id:
                    continue

                try:
                    # Format: "4/12/2016 7:21:00 AM"
                    date_str = row['Time'].split()[0]
                    record_date = datetime.strptime(date_str, '%m/%d/%Y').date()
                    hr_value = int(row['Value'])
                    daily_hr[record_date].append(hr_value)
                except (ValueError, KeyError):
                    continue

        # Calculate daily aggregates
        for record_date, hr_values in daily_hr.items():
            if hr_values:
                # Resting HR estimate: 10th percentile of readings
                sorted_hr = sorted(hr_values)
                resting_idx = max(0, int(len(sorted_hr) * 0.1))

                result[record_date] = {
                    'resting_hr': sorted_hr[resting_idx],
                    'hr_min': min(hr_values),
                    'hr_max': max(hr_values),
                }

        return result

    @staticmethod
    def _safe_int(value) -> Optional[int]:
        """Safely convert value to int."""
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
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
