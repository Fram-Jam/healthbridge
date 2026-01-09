"""
OhioT1DM Dataset Adapter

Loads data from the Ohio T1DM Dataset for Blood Glucose Level Prediction.
Source: http://smarthealth.cs.ohio.edu/OhioT1DM-dataset.html

Contains CGM data from 12 Type 1 Diabetes patients:
- 8 weeks of continuous glucose monitoring (5-minute intervals)
- Insulin bolus and basal data
- Self-reported meal data
- Exercise and sleep annotations
"""

import csv
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from ..base import BaseDatasetAdapter, DatasetMetadata, Subject, DataCategory
from ..registry import registry


@registry.register
class OhioT1DMAdapter(BaseDatasetAdapter):
    """Adapter for OhioT1DM CGM Dataset."""

    @property
    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            id="ohio_t1dm",
            name="OhioT1DM (CGM)",
            description="12 Type 1 Diabetes patients with 8 weeks of continuous glucose monitoring at 5-minute intervals, plus insulin, meals, and activity data.",
            category=DataCategory.CGM,
            source_url="http://smarthealth.cs.ohio.edu/OhioT1DM-dataset.html",
            citation="Marling, C., & Bunescu, R. (2020). The OhioT1DM Dataset for Blood Glucose Level Prediction. KHD Workshop at IJCAI.",
            subject_count=12,
            date_range="8 weeks per subject",
            size_mb=50,
            available_fields=[
                "glucose_avg", "glucose_min", "glucose_max", "glucose_std",
                "time_in_range", "insulin_bolus", "insulin_basal",
                "carbs", "exercise_minutes"
            ],
            download_instructions="""
1. Visit http://smarthealth.cs.ohio.edu/OhioT1DM-dataset.html
2. Complete the data use agreement form
3. Download the dataset (2018 or 2020 version)
4. Extract XML files to data/datasets/ohio_t1dm/
            """.strip(),
            requires_auth=True,
            license="Research Use Only"
        )

    def is_available(self) -> bool:
        """Check if OhioT1DM data is downloaded."""
        data_path = self.dataset_path
        if not data_path.exists():
            return False

        # Check for XML files (OhioT1DM format)
        xml_files = list(data_path.glob("*.xml"))
        if xml_files:
            return True

        # Check for subdirectories with patient data
        patient_dirs = [d for d in data_path.iterdir() if d.is_dir() and d.name.isdigit()]
        return len(patient_dirs) > 0

    def list_subjects(self) -> List[Subject]:
        """List all subjects in the dataset."""
        if not self.is_available():
            return []

        subjects = []
        seen_ids = set()

        # Method 1: XML files in root
        for xml_file in self.dataset_path.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                # Get patient ID from filename or XML
                subj_id = xml_file.stem.split('-')[0] if '-' in xml_file.stem else xml_file.stem
                if subj_id in seen_ids:
                    continue
                seen_ids.add(subj_id)

                # Count glucose entries
                glucose_events = root.findall('.//glucose_level/event')
                record_count = len(glucose_events)

                # Get date range
                dates = []
                for event in glucose_events:
                    ts = event.get('ts')
                    if ts:
                        try:
                            dt = datetime.strptime(ts.split()[0], '%d-%m-%Y')
                            dates.append(dt.date())
                        except ValueError:
                            pass

                date_range = None
                if dates:
                    date_range = f"{min(dates)} to {max(dates)}"

                subjects.append(Subject(
                    id=subj_id,
                    display_name=f"Patient {subj_id}",
                    date_range=date_range,
                    record_count=record_count
                ))

            except ET.ParseError:
                continue

        # Method 2: Patient subdirectories
        for patient_dir in self.dataset_path.iterdir():
            if not patient_dir.is_dir():
                continue

            subj_id = patient_dir.name
            if not subj_id.isdigit() or subj_id in seen_ids:
                continue

            seen_ids.add(subj_id)

            # Look for data files in patient directory
            xml_files = list(patient_dir.glob("*.xml"))
            csv_files = list(patient_dir.glob("*.csv"))

            subjects.append(Subject(
                id=subj_id,
                display_name=f"Patient {subj_id}",
                date_range=None,
                record_count=len(xml_files) + len(csv_files)
            ))

        return sorted(subjects, key=lambda s: s.id)

    def load_health_data(self, subject_id: str) -> List[Dict]:
        """Load and normalize health data for a subject."""
        if not self.is_available():
            return []

        # Load glucose data
        glucose_by_day = self._load_glucose_data(subject_id)

        # Load insulin data
        insulin_by_day = self._load_insulin_data(subject_id)

        # Load meal data
        meals_by_day = self._load_meal_data(subject_id)

        # Get all unique dates
        all_dates = set(glucose_by_day.keys()) | set(insulin_by_day.keys()) | set(meals_by_day.keys())

        # Build daily records
        records = []
        for record_date in sorted(all_dates):
            record = self._create_empty_record(record_date)

            # Glucose metrics
            if record_date in glucose_by_day:
                glucose_values = glucose_by_day[record_date]
                if glucose_values:
                    record['glucose_avg'] = sum(glucose_values) / len(glucose_values)
                    record['glucose_min'] = min(glucose_values)
                    record['glucose_max'] = max(glucose_values)

                    # Standard deviation
                    mean = record['glucose_avg']
                    variance = sum((x - mean) ** 2 for x in glucose_values) / len(glucose_values)
                    record['glucose_std'] = variance ** 0.5

                    # Time in range (70-180 mg/dL)
                    in_range = sum(1 for x in glucose_values if 70 <= x <= 180)
                    record['time_in_range'] = (in_range / len(glucose_values)) * 100

            # Insulin totals (store in metadata-like fields)
            if record_date in insulin_by_day:
                ins = insulin_by_day[record_date]
                # Store as readiness_score placeholder (will need schema extension)
                record['readiness_score'] = None

            records.append(record)

        return records

    def _load_glucose_data(self, subject_id: str) -> Dict[date, List[float]]:
        """Load glucose readings grouped by day."""
        result = defaultdict(list)

        # Try XML file
        xml_file = self._find_patient_xml(subject_id)
        if xml_file:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                for event in root.findall('.//glucose_level/event'):
                    ts = event.get('ts')
                    value = event.get('value')

                    if not ts or not value:
                        continue

                    try:
                        # Format: "28-09-2018 00:04:00"
                        dt = datetime.strptime(ts, '%d-%m-%Y %H:%M:%S')
                        glucose = float(value)
                        result[dt.date()].append(glucose)
                    except ValueError:
                        continue

            except ET.ParseError:
                pass

        # Try CSV file
        csv_file = self._find_patient_csv(subject_id, 'glucose')
        if csv_file:
            try:
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        ts = row.get('timestamp') or row.get('ts') or row.get('time')
                        value = row.get('value') or row.get('glucose')

                        if not ts or not value:
                            continue

                        try:
                            dt = self._parse_timestamp(ts)
                            glucose = float(value)
                            result[dt.date()].append(glucose)
                        except (ValueError, TypeError):
                            continue
            except (IOError, csv.Error):
                pass

        return result

    def _load_insulin_data(self, subject_id: str) -> Dict[date, Dict]:
        """Load insulin data grouped by day."""
        result = defaultdict(lambda: {'bolus': 0, 'basal': 0})

        xml_file = self._find_patient_xml(subject_id)
        if xml_file:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                # Bolus insulin
                for event in root.findall('.//bolus/event'):
                    ts = event.get('ts')
                    value = event.get('dose')

                    if not ts or not value:
                        continue

                    try:
                        dt = datetime.strptime(ts, '%d-%m-%Y %H:%M:%S')
                        result[dt.date()]['bolus'] += float(value)
                    except ValueError:
                        continue

                # Basal insulin
                for event in root.findall('.//basal/event'):
                    ts = event.get('ts')
                    value = event.get('value')

                    if not ts or not value:
                        continue

                    try:
                        dt = datetime.strptime(ts, '%d-%m-%Y %H:%M:%S')
                        result[dt.date()]['basal'] += float(value)
                    except ValueError:
                        continue

            except ET.ParseError:
                pass

        return result

    def _load_meal_data(self, subject_id: str) -> Dict[date, Dict]:
        """Load meal/carb data grouped by day."""
        result = defaultdict(lambda: {'carbs': 0, 'meals': 0})

        xml_file = self._find_patient_xml(subject_id)
        if xml_file:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                for event in root.findall('.//meal/event'):
                    ts = event.get('ts')
                    carbs = event.get('carbs')

                    if not ts:
                        continue

                    try:
                        dt = datetime.strptime(ts, '%d-%m-%Y %H:%M:%S')
                        result[dt.date()]['meals'] += 1
                        if carbs:
                            result[dt.date()]['carbs'] += float(carbs)
                    except ValueError:
                        continue

            except ET.ParseError:
                pass

        return result

    def _find_patient_xml(self, subject_id: str) -> Optional[Path]:
        """Find XML file for a patient."""
        # Direct match
        xml_file = self.dataset_path / f"{subject_id}.xml"
        if xml_file.exists():
            return xml_file

        # With suffix
        for xml_file in self.dataset_path.glob(f"{subject_id}*.xml"):
            return xml_file

        # In subdirectory
        subdir = self.dataset_path / subject_id
        if subdir.exists():
            for xml_file in subdir.glob("*.xml"):
                return xml_file

        return None

    def _find_patient_csv(self, subject_id: str, data_type: str) -> Optional[Path]:
        """Find CSV file for a patient and data type."""
        patterns = [
            f"{subject_id}_{data_type}.csv",
            f"{subject_id}-{data_type}.csv",
            f"{data_type}.csv",
        ]

        for pattern in patterns:
            csv_file = self.dataset_path / pattern
            if csv_file.exists():
                return csv_file

            # In subdirectory
            csv_file = self.dataset_path / subject_id / pattern
            if csv_file.exists():
                return csv_file

        return None

    def _parse_timestamp(self, ts: str) -> datetime:
        """Parse timestamp in various formats."""
        formats = [
            '%d-%m-%Y %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(ts, fmt)
            except ValueError:
                continue

        raise ValueError(f"Cannot parse timestamp: {ts}")

    def get_subject_profile(self, subject_id: str) -> Optional[Dict]:
        """
        Get profile info for a subject.

        OhioT1DM doesn't include detailed demographics for privacy.
        """
        # All subjects are Type 1 Diabetes patients
        return {
            'condition': 'Type 1 Diabetes',
            'age': None,
            'sex': None,
            'height_cm': None,
            'weight_kg': None,
        }
