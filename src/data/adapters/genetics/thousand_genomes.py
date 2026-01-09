"""
1000 Genomes Project Adapter

Loads data from the 1000 Genomes Project.
Source: https://www.internationalgenome.org/

Contains genomic data from 3,202 individuals across 26 populations:
- Whole genome sequencing data
- Population ancestry information
- Sample metadata
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional
import random

from ..base import BaseDatasetAdapter, DatasetMetadata, Subject, DataCategory
from ..registry import registry


@registry.register
class ThousandGenomesAdapter(BaseDatasetAdapter):
    """Adapter for 1000 Genomes Project Dataset."""

    # Population code to ancestry mapping
    POPULATION_ANCESTRY = {
        # African
        'YRI': ('Yoruba in Ibadan, Nigeria', 'African'),
        'LWK': ('Luhya in Webuye, Kenya', 'African'),
        'GWD': ('Gambian in Western Divisions', 'African'),
        'MSL': ('Mende in Sierra Leone', 'African'),
        'ESN': ('Esan in Nigeria', 'African'),
        'ASW': ('African Ancestry in SW USA', 'African'),
        'ACB': ('African Caribbean in Barbados', 'African'),
        # European
        'CEU': ('Utah residents, N/W European', 'European'),
        'TSI': ('Toscani in Italia', 'European'),
        'FIN': ('Finnish in Finland', 'European'),
        'GBR': ('British in England/Scotland', 'European'),
        'IBS': ('Iberian Population in Spain', 'European'),
        # East Asian
        'CHB': ('Han Chinese in Beijing', 'East Asian'),
        'JPT': ('Japanese in Tokyo', 'East Asian'),
        'CHS': ('Southern Han Chinese', 'East Asian'),
        'CDX': ('Chinese Dai in Xishuangbanna', 'East Asian'),
        'KHV': ('Kinh in Ho Chi Minh City', 'East Asian'),
        # South Asian
        'GIH': ('Gujarati Indians in Houston', 'South Asian'),
        'PJL': ('Punjabi from Lahore, Pakistan', 'South Asian'),
        'BEB': ('Bengali from Bangladesh', 'South Asian'),
        'STU': ('Sri Lankan Tamil from UK', 'South Asian'),
        'ITU': ('Indian Telugu from UK', 'South Asian'),
        # Americas
        'MXL': ('Mexican Ancestry in LA', 'Americas'),
        'PUR': ('Puerto Ricans from PR', 'Americas'),
        'CLM': ('Colombians from Medellin', 'Americas'),
        'PEL': ('Peruvians from Lima', 'Americas'),
    }

    @property
    def metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            id="thousand_genomes",
            name="1000 Genomes Project",
            description="3,202 individuals from 26 global populations with whole genome sequencing, ancestry, and sample metadata.",
            category=DataCategory.GENETICS,
            source_url="https://www.internationalgenome.org/data/",
            citation="The 1000 Genomes Project Consortium. Nature 526, 68-74 (2015).",
            subject_count=3202,
            date_range="Phase 3 (2015)",
            size_mb=50,  # Just metadata, not full VCF
            available_fields=[
                "ancestry", "population", "super_population", "sex"
            ],
            download_instructions="""
1. Download sample metadata from:
   ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/
2. Get igsr_samples.tsv from:
   https://www.internationalgenome.org/data-portal/sample
3. Place files in data/datasets/thousand_genomes/
4. For full VCF analysis, additional downloads needed (~1TB)
            """.strip(),
            requires_auth=False,
            license="Fort Lauderdale Agreement (Open Access)"
        )

    def is_available(self) -> bool:
        """Check if 1000 Genomes data is downloaded."""
        data_path = self.dataset_path
        if not data_path.exists():
            return False

        # Check for sample metadata file
        sample_files = (
            list(data_path.glob("*samples*.tsv")) +
            list(data_path.glob("*samples*.csv")) +
            list(data_path.glob("*.panel"))
        )

        return len(sample_files) > 0

    def _find_sample_file(self) -> Optional[Path]:
        """Find the sample metadata file."""
        for pattern in ["*samples*.tsv", "*samples*.csv", "*.panel"]:
            matches = list(self.dataset_path.glob(pattern))
            if matches:
                return matches[0]
        return None

    def list_subjects(self) -> List[Subject]:
        """List all subjects in the dataset."""
        if not self.is_available():
            return []

        sample_file = self._find_sample_file()
        if not sample_file:
            return []

        subjects = []
        delimiter = '\t' if sample_file.suffix in ['.tsv', '.panel'] else ','

        try:
            with open(sample_file, 'r') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    # Handle different column naming conventions
                    sample_id = (
                        row.get('Sample name') or
                        row.get('sample') or
                        row.get('Sample') or
                        row.get('SAMPLE') or
                        ''
                    )

                    if not sample_id:
                        continue

                    pop = (
                        row.get('Population code') or
                        row.get('pop') or
                        row.get('population') or
                        ''
                    )

                    sex = (
                        row.get('Sex') or
                        row.get('sex') or
                        row.get('gender') or
                        ''
                    )

                    pop_name = self.POPULATION_ANCESTRY.get(pop, (pop, 'Unknown'))[0]

                    subjects.append(Subject(
                        id=sample_id,
                        display_name=sample_id,
                        date_range=None,
                        record_count=1,
                        metadata={
                            'population': pop,
                            'population_name': pop_name,
                            'sex': sex.lower() if sex else None,
                        }
                    ))
        except (IOError, csv.Error):
            pass

        return subjects[:200]  # Limit for UI performance

    def load_health_data(self, subject_id: str) -> List[Dict]:
        """1000 Genomes doesn't have health/wearable data."""
        return []

    def load_genetic_data(self, subject_id: str) -> Optional[Dict]:
        """Load genetic/ancestry data for a subject."""
        if not self.is_available():
            return None

        sample_file = self._find_sample_file()
        if not sample_file:
            return None

        delimiter = '\t' if sample_file.suffix in ['.tsv', '.panel'] else ','

        try:
            with open(sample_file, 'r') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    sample_id = (
                        row.get('Sample name') or
                        row.get('sample') or
                        row.get('Sample') or
                        ''
                    )

                    if sample_id != subject_id:
                        continue

                    pop = (
                        row.get('Population code') or
                        row.get('pop') or
                        ''
                    )

                    super_pop = (
                        row.get('Superpopulation code') or
                        row.get('super_pop') or
                        ''
                    )

                    if pop in self.POPULATION_ANCESTRY:
                        _, ancestry_region = self.POPULATION_ANCESTRY[pop]
                    else:
                        ancestry_region = super_pop or 'Unknown'

                    # Generate ancestry composition based on population
                    ancestry = self._generate_ancestry_composition(pop, super_pop)

                    return {
                        'population': pop,
                        'super_population': super_pop,
                        'ancestry': ancestry,
                        'disease_risks': [],  # Would need VCF analysis
                        'carrier_status': [],
                        'drug_responses': [],
                        'traits': [],
                    }

        except (IOError, csv.Error):
            pass

        return None

    def _generate_ancestry_composition(self, pop: str, super_pop: str) -> Dict:
        """
        Generate ancestry composition based on population.

        Note: Real ancestry would require actual genomic analysis.
        This provides a reasonable estimate based on population.
        """
        # Base compositions by super-population
        base_compositions = {
            'AFR': {'African': 0.85, 'European': 0.10, 'Other': 0.05},
            'EUR': {'European': 0.90, 'Middle Eastern': 0.05, 'Other': 0.05},
            'EAS': {'East Asian': 0.90, 'Southeast Asian': 0.07, 'Other': 0.03},
            'SAS': {'South Asian': 0.85, 'Central Asian': 0.10, 'Other': 0.05},
            'AMR': {'Indigenous American': 0.40, 'European': 0.35, 'African': 0.20, 'Other': 0.05},
        }

        # Use population-specific if available, else super-population
        if super_pop in base_compositions:
            composition = base_compositions[super_pop].copy()
        else:
            # Default mixed
            composition = {'Unknown': 1.0}

        # Add some random variation (±5%)
        random.seed(hash(pop))
        varied = {}
        total = 0
        for region, pct in composition.items():
            varied_pct = max(0, pct + random.uniform(-0.05, 0.05))
            varied[region] = varied_pct
            total += varied_pct

        # Normalize to 100%
        return {region: round(pct / total * 100, 1) for region, pct in varied.items()}

    def get_subject_profile(self, subject_id: str) -> Optional[Dict]:
        """Get basic profile info for a subject."""
        if not self.is_available():
            return None

        sample_file = self._find_sample_file()
        if not sample_file:
            return None

        delimiter = '\t' if sample_file.suffix in ['.tsv', '.panel'] else ','

        try:
            with open(sample_file, 'r') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    sample_id = (
                        row.get('Sample name') or
                        row.get('sample') or
                        ''
                    )

                    if sample_id != subject_id:
                        continue

                    sex = (
                        row.get('Sex') or
                        row.get('sex') or
                        ''
                    )

                    return {
                        'sex': sex.lower() if sex else None,
                        'age': None,  # Not available in 1000 Genomes
                        'height_cm': None,
                        'weight_kg': None,
                    }

        except (IOError, csv.Error):
            pass

        return None
