"""
NHANES Dataset Adapter

Loads data from the CDC National Health and Nutrition Examination Survey.
Source: https://www.cdc.gov/nchs/nhanes/

Contains comprehensive health data including:
- Demographics
- Laboratory results (19+ biomarkers)
- Physical examination data
- Dietary intake
"""

import csv
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional

from ..base import BaseDatasetAdapter, DatasetMetadata, Subject, DataCategory
from ..registry import registry


@registry.register
class NHANESAdapter(BaseDatasetAdapter):
    """Adapter for CDC NHANES Dataset."""

    # Mapping of NHANES variable codes to our schema
    LAB_MAPPINGS = {
        'LBXGLU': ('glucose', 'mg/dL', (70, 100)),
        'LBXGH': ('hba1c', '%', (4.0, 5.6)),
        'LBXTC': ('total_cholesterol', 'mg/dL', (125, 200)),
        'LBDHDL': ('hdl', 'mg/dL', (40, 60)),
        'LBDLDL': ('ldl', 'mg/dL', (0, 100)),
        'LBXTR': ('triglycerides', 'mg/dL', (0, 150)),
        'LBXCR': ('creatinine', 'mg/dL', (0.7, 1.3)),
        'LBXSBU': ('bun', 'mg/dL', (7, 20)),
        'LBXSUA': ('uric_acid', 'mg/dL', (3.5, 7.2)),
        'LBXSTP': ('total_protein', 'g/dL', (6.0, 8.3)),
        'LBXSAL': ('albumin', 'g/dL', (3.5, 5.0)),
        'LBXSTB': ('total_bilirubin', 'mg/dL', (0.1, 1.2)),
        'LBXSASSI': ('ast', 'U/L', (10, 40)),
        'LBXSATSI': ('alt', 'U/L', (7, 56)),
        'LBXSAPSI': ('alp', 'U/L', (44, 147)),
        'LBXWBCSI': ('wbc', '10^3/uL', (4.5, 11.0)),
        'LBXRBCSI': ('rbc', '10^6/uL', (4.5, 5.5)),
        'LBXHGB': ('hemoglobin', 'g/dL', (12.0, 17.5)),
        'LBXHCT': ('hematocrit', '%', (36, 50)),
    }

    @property
    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            id="nhanes",
            name="NHANES (CDC)",
            description="National Health and Nutrition Examination Survey with comprehensive lab results, physical exams, and demographic data for 10,000+ participants per cycle.",
            category=DataCategory.CLINICAL,
            source_url="https://www.cdc.gov/nchs/nhanes/",
            citation="CDC/NCHS. National Health and Nutrition Examination Survey Data.",
            subject_count=10000,
            date_range="Multiple survey cycles (2017-2020 recommended)",
            size_mb=200,
            available_fields=[
                "glucose", "hba1c", "total_cholesterol", "hdl", "ldl",
                "triglycerides", "creatinine", "bun", "uric_acid",
                "ast", "alt", "alp", "wbc", "rbc", "hemoglobin", "hematocrit"
            ],
            download_instructions="""
1. Visit https://wwwn.cdc.gov/nchs/nhanes/
2. Select survey cycle (e.g., 2017-2020)
3. Download: Demographics (DEMO), Lab (GLU, BIOPRO, CBC) XPT files
4. Convert XPT to CSV using: pip install pyreadstat
5. Place files in data/datasets/nhanes/
            """.strip(),
            requires_auth=False,
            license="Public Domain"
        )

    def is_available(self) -> bool:
        """Check if NHANES data is downloaded."""
        data_path = self.dataset_path
        if not data_path.exists():
            return False

        # Check for key files (demographics and at least one lab file)
        demo_files = list(data_path.glob("*DEMO*.csv")) + list(data_path.glob("*demo*.csv"))
        lab_files = list(data_path.glob("*GLU*.csv")) + list(data_path.glob("*BIOPRO*.csv"))

        return len(demo_files) > 0 and len(lab_files) > 0

    def _find_file(self, pattern: str) -> Optional[Path]:
        """Find a file matching a pattern."""
        matches = list(self.dataset_path.glob(f"*{pattern}*.csv"))
        if matches:
            return matches[0]
        # Try case-insensitive
        matches = list(self.dataset_path.glob(f"*{pattern.lower()}*.csv"))
        return matches[0] if matches else None

    def list_subjects(self) -> List[Subject]:
        """List all subjects in the dataset."""
        if not self.is_available():
            return []

        demo_file = self._find_file("DEMO")
        if not demo_file:
            return []

        subjects = []
        with open(demo_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                seqn = row.get('SEQN', '')
                if not seqn:
                    continue

                # Extract demographic info
                age = row.get('RIDAGEYR', '')
                gender_code = row.get('RIAGENDR', '')
                gender = 'Male' if gender_code == '1' else 'Female' if gender_code == '2' else 'Unknown'

                subjects.append(Subject(
                    id=seqn,
                    display_name=f"Subject {seqn}",
                    date_range=None,
                    record_count=1,
                    metadata={
                        'age': int(age) if age.isdigit() else None,
                        'gender': gender,
                    }
                ))

        return subjects[:100]  # Limit to first 100 for performance

    def load_health_data(self, subject_id: str) -> List[Dict]:
        """
        Load health data for a subject.

        NHANES is cross-sectional, so we return a single "day" of data.
        """
        # NHANES doesn't have daily health data like wearables
        # Return empty - the lab data is the main value
        return []

    def load_lab_data(self, subject_id: str) -> Optional[List[Dict]]:
        """Load lab/biomarker data for a subject."""
        if not self.is_available():
            return None

        # Collect lab values from multiple files
        lab_values = {}

        # Load glucose data
        glu_file = self._find_file("GLU")
        if glu_file:
            lab_values.update(self._load_lab_file(glu_file, subject_id))

        # Load biochemistry profile
        biopro_file = self._find_file("BIOPRO")
        if biopro_file:
            lab_values.update(self._load_lab_file(biopro_file, subject_id))

        # Load CBC data
        cbc_file = self._find_file("CBC")
        if cbc_file:
            lab_values.update(self._load_lab_file(cbc_file, subject_id))

        if not lab_values:
            return None

        # Convert to our lab data format
        lab_records = []
        for nhanes_code, value in lab_values.items():
            if nhanes_code not in self.LAB_MAPPINGS:
                continue

            name, unit, ref_range = self.LAB_MAPPINGS[nhanes_code]
            ref_low, ref_high = ref_range

            try:
                numeric_value = float(value)
            except (ValueError, TypeError):
                continue

            # Determine flag
            flag = 'normal'
            if numeric_value < ref_low:
                flag = 'low'
            elif numeric_value > ref_high:
                flag = 'high'

            lab_records.append({
                'name': name,
                'value': numeric_value,
                'unit': unit,
                'reference_range': f"{ref_low}-{ref_high}",
                'flag': flag,
                'date': date.today().isoformat(),  # NHANES doesn't have specific dates
            })

        return lab_records if lab_records else None

    def _load_lab_file(self, file_path: Path, subject_id: str) -> Dict[str, str]:
        """Load lab values for a subject from a specific file."""
        result = {}

        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('SEQN') != subject_id:
                        continue

                    # Extract all lab values from this row
                    for col, value in row.items():
                        if col.startswith('LBX') and value:
                            result[col] = value

                    break  # Found our subject
        except (IOError, csv.Error):
            pass

        return result

    def get_subject_profile(self, subject_id: str) -> Optional[Dict]:
        """Get demographic/profile info for a subject."""
        if not self.is_available():
            return None

        demo_file = self._find_file("DEMO")
        if not demo_file:
            return None

        try:
            with open(demo_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('SEQN') != subject_id:
                        continue

                    age = row.get('RIDAGEYR', '')
                    gender_code = row.get('RIAGENDR', '')

                    return {
                        'age': int(age) if age.isdigit() else None,
                        'sex': 'male' if gender_code == '1' else 'female' if gender_code == '2' else None,
                        'height_cm': self._safe_float(row.get('BMXHT')),
                        'weight_kg': self._safe_float(row.get('BMXWT')),
                    }
        except (IOError, csv.Error):
            pass

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
