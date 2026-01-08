"""
Synthetic Genetic Data Generator

Generates realistic genetic/genomic data for demo purposes.
Includes disease risk scores, carrier status, pharmacogenomics, and traits.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date
from faker import Faker

fake = Faker()


@dataclass
class GeneticVariant:
    """A genetic variant (SNP)."""
    rsid: str
    gene: str
    genotype: str
    effect: str
    significance: str  # 'beneficial', 'neutral', 'risk', 'pathogenic'


@dataclass
class DiseaseRisk:
    """Disease risk assessment based on genetic variants."""
    condition: str
    category: str  # 'cardiovascular', 'metabolic', 'neurological', 'cancer', 'autoimmune'
    risk_score: float  # 0.0 to 1.0, where 0.5 is average population risk
    risk_level: str  # 'low', 'average', 'elevated', 'high'
    percentile: int  # 1-100
    variants_analyzed: int
    key_variants: List[GeneticVariant]
    lifestyle_modifiable: bool
    description: str


@dataclass
class CarrierStatus:
    """Carrier status for recessive genetic conditions."""
    condition: str
    status: str  # 'not_carrier', 'carrier', 'affected'
    gene: str
    inheritance: str  # 'autosomal_recessive', 'x_linked'
    prevalence: str  # e.g., "1 in 25"
    description: str


@dataclass
class DrugResponse:
    """Pharmacogenomic drug response prediction."""
    drug: str
    drug_class: str
    gene: str
    metabolizer_status: str  # 'poor', 'intermediate', 'normal', 'rapid', 'ultra_rapid'
    recommendation: str
    clinical_significance: str  # 'actionable', 'informative'


@dataclass
class GeneticTrait:
    """Genetic trait prediction."""
    trait: str
    category: str  # 'nutrition', 'fitness', 'sleep', 'appearance', 'sensory'
    prediction: str
    confidence: str  # 'high', 'moderate', 'low'
    description: str


@dataclass
class AncestryComposition:
    """Ancestry breakdown."""
    region: str
    percentage: float
    subregions: Dict[str, float] = field(default_factory=dict)


@dataclass
class GeneticProfile:
    """Complete genetic profile for a user."""
    id: str
    sequencing_date: date
    sequencing_type: str  # 'whole_genome', 'whole_exome', 'genotyping_array'
    variants_analyzed: int
    disease_risks: List[DiseaseRisk]
    carrier_statuses: List[CarrierStatus]
    drug_responses: List[DrugResponse]
    traits: List[GeneticTrait]
    ancestry: List[AncestryComposition]
    raw_data_available: bool = True


def generate_disease_risks() -> List[DiseaseRisk]:
    """Generate disease risk assessments."""

    conditions = [
        # Cardiovascular
        {
            'condition': 'Coronary Artery Disease',
            'category': 'cardiovascular',
            'lifestyle_modifiable': True,
            'desc': 'Risk of plaque buildup in heart arteries'
        },
        {
            'condition': 'Atrial Fibrillation',
            'category': 'cardiovascular',
            'lifestyle_modifiable': True,
            'desc': 'Risk of irregular heart rhythm'
        },
        {
            'condition': 'Venous Thromboembolism',
            'category': 'cardiovascular',
            'lifestyle_modifiable': True,
            'desc': 'Risk of blood clots in veins'
        },
        # Metabolic
        {
            'condition': 'Type 2 Diabetes',
            'category': 'metabolic',
            'lifestyle_modifiable': True,
            'desc': 'Risk of insulin resistance and high blood sugar'
        },
        {
            'condition': 'Obesity',
            'category': 'metabolic',
            'lifestyle_modifiable': True,
            'desc': 'Genetic predisposition to weight gain'
        },
        # Neurological
        {
            'condition': "Alzheimer's Disease",
            'category': 'neurological',
            'lifestyle_modifiable': True,
            'desc': 'Risk of late-onset cognitive decline'
        },
        {
            'condition': "Parkinson's Disease",
            'category': 'neurological',
            'lifestyle_modifiable': False,
            'desc': 'Risk of movement disorder'
        },
        # Cancer
        {
            'condition': 'Breast Cancer',
            'category': 'cancer',
            'lifestyle_modifiable': True,
            'desc': 'Polygenic risk for breast cancer'
        },
        {
            'condition': 'Prostate Cancer',
            'category': 'cancer',
            'lifestyle_modifiable': True,
            'desc': 'Polygenic risk for prostate cancer'
        },
        {
            'condition': 'Colorectal Cancer',
            'category': 'cancer',
            'lifestyle_modifiable': True,
            'desc': 'Risk of colon or rectal cancer'
        },
        # Autoimmune
        {
            'condition': 'Celiac Disease',
            'category': 'autoimmune',
            'lifestyle_modifiable': True,
            'desc': 'Risk of gluten sensitivity'
        },
        {
            'condition': 'Rheumatoid Arthritis',
            'category': 'autoimmune',
            'lifestyle_modifiable': False,
            'desc': 'Risk of inflammatory joint disease'
        },
        # Other
        {
            'condition': 'Age-Related Macular Degeneration',
            'category': 'other',
            'lifestyle_modifiable': True,
            'desc': 'Risk of vision loss with age'
        },
        {
            'condition': 'Osteoporosis',
            'category': 'other',
            'lifestyle_modifiable': True,
            'desc': 'Risk of bone density loss'
        },
    ]

    risks = []
    for cond in conditions:
        # Generate risk score with slight bias toward average
        risk_score = max(0.05, min(0.95, random.gauss(0.5, 0.2)))
        percentile = int(risk_score * 100)

        if risk_score < 0.3:
            risk_level = 'low'
        elif risk_score < 0.6:
            risk_level = 'average'
        elif risk_score < 0.8:
            risk_level = 'elevated'
        else:
            risk_level = 'high'

        # Generate key variants
        num_variants = random.randint(2, 5)
        key_variants = []
        for _ in range(num_variants):
            significance = random.choices(
                ['beneficial', 'neutral', 'risk'],
                weights=[0.2, 0.5, 0.3]
            )[0]
            key_variants.append(GeneticVariant(
                rsid=f"rs{random.randint(1000000, 99999999)}",
                gene=random.choice(['APOE', 'MTHFR', 'FTO', 'TCF7L2', 'BRCA1', 'LDLR', 'ACE', 'COMT']),
                genotype=random.choice(['A/A', 'A/G', 'G/G', 'C/C', 'C/T', 'T/T']),
                effect=random.choice(['increased risk', 'decreased risk', 'typical']),
                significance=significance
            ))

        risks.append(DiseaseRisk(
            condition=cond['condition'],
            category=cond['category'],
            risk_score=round(risk_score, 3),
            risk_level=risk_level,
            percentile=percentile,
            variants_analyzed=random.randint(50, 500),
            key_variants=key_variants,
            lifestyle_modifiable=cond['lifestyle_modifiable'],
            description=cond['desc']
        ))

    return risks


def generate_carrier_statuses() -> List[CarrierStatus]:
    """Generate carrier status for recessive conditions."""

    conditions = [
        {
            'condition': 'Cystic Fibrosis',
            'gene': 'CFTR',
            'inheritance': 'autosomal_recessive',
            'prevalence': '1 in 25',
            'desc': 'Affects lungs and digestive system'
        },
        {
            'condition': 'Sickle Cell Anemia',
            'gene': 'HBB',
            'inheritance': 'autosomal_recessive',
            'prevalence': '1 in 12 (African ancestry)',
            'desc': 'Affects red blood cell shape'
        },
        {
            'condition': 'Tay-Sachs Disease',
            'gene': 'HEXA',
            'inheritance': 'autosomal_recessive',
            'prevalence': '1 in 30 (Ashkenazi Jewish)',
            'desc': 'Progressive neurological disorder'
        },
        {
            'condition': 'Phenylketonuria (PKU)',
            'gene': 'PAH',
            'inheritance': 'autosomal_recessive',
            'prevalence': '1 in 50',
            'desc': 'Inability to metabolize phenylalanine'
        },
        {
            'condition': 'Hereditary Hemochromatosis',
            'gene': 'HFE',
            'inheritance': 'autosomal_recessive',
            'prevalence': '1 in 10',
            'desc': 'Iron overload disorder'
        },
        {
            'condition': 'Alpha-1 Antitrypsin Deficiency',
            'gene': 'SERPINA1',
            'inheritance': 'autosomal_recessive',
            'prevalence': '1 in 25',
            'desc': 'Affects lungs and liver'
        },
        {
            'condition': 'Spinal Muscular Atrophy',
            'gene': 'SMN1',
            'inheritance': 'autosomal_recessive',
            'prevalence': '1 in 50',
            'desc': 'Progressive muscle weakness'
        },
        {
            'condition': 'MCAD Deficiency',
            'gene': 'ACADM',
            'inheritance': 'autosomal_recessive',
            'prevalence': '1 in 50',
            'desc': 'Fatty acid oxidation disorder'
        },
    ]

    statuses = []
    for cond in conditions:
        # Most people are not carriers; small chance of being a carrier
        status = random.choices(
            ['not_carrier', 'carrier'],
            weights=[0.92, 0.08]
        )[0]

        statuses.append(CarrierStatus(
            condition=cond['condition'],
            status=status,
            gene=cond['gene'],
            inheritance=cond['inheritance'],
            prevalence=cond['prevalence'],
            description=cond['desc']
        ))

    return statuses


def generate_drug_responses() -> List[DrugResponse]:
    """Generate pharmacogenomic drug response predictions."""

    drugs = [
        # Pain/Anesthesia
        {
            'drug': 'Codeine',
            'class': 'Opioid Analgesic',
            'gene': 'CYP2D6',
            'significance': 'actionable'
        },
        {
            'drug': 'Tramadol',
            'class': 'Opioid Analgesic',
            'gene': 'CYP2D6',
            'significance': 'actionable'
        },
        # Cardiovascular
        {
            'drug': 'Clopidogrel (Plavix)',
            'class': 'Antiplatelet',
            'gene': 'CYP2C19',
            'significance': 'actionable'
        },
        {
            'drug': 'Warfarin',
            'class': 'Anticoagulant',
            'gene': 'CYP2C9/VKORC1',
            'significance': 'actionable'
        },
        {
            'drug': 'Simvastatin',
            'class': 'Statin',
            'gene': 'SLCO1B1',
            'significance': 'actionable'
        },
        # Psychiatric
        {
            'drug': 'Citalopram (Celexa)',
            'class': 'SSRI Antidepressant',
            'gene': 'CYP2C19',
            'significance': 'actionable'
        },
        {
            'drug': 'Sertraline (Zoloft)',
            'class': 'SSRI Antidepressant',
            'gene': 'CYP2C19',
            'significance': 'informative'
        },
        # Other
        {
            'drug': 'Omeprazole (Prilosec)',
            'class': 'Proton Pump Inhibitor',
            'gene': 'CYP2C19',
            'significance': 'informative'
        },
        {
            'drug': 'Caffeine',
            'class': 'Stimulant',
            'gene': 'CYP1A2',
            'significance': 'informative'
        },
        {
            'drug': 'Metformin',
            'class': 'Antidiabetic',
            'gene': 'SLC22A1',
            'significance': 'informative'
        },
    ]

    metabolizer_types = ['poor', 'intermediate', 'normal', 'rapid', 'ultra_rapid']
    metabolizer_weights = [0.05, 0.15, 0.55, 0.15, 0.10]

    recommendations = {
        'poor': 'Consider alternative medication or reduced dose',
        'intermediate': 'Standard dose may need adjustment',
        'normal': 'Standard dosing expected to be effective',
        'rapid': 'May require higher dose for therapeutic effect',
        'ultra_rapid': 'Increased risk of side effects; consider alternative'
    }

    responses = []
    for drug in drugs:
        status = random.choices(metabolizer_types, weights=metabolizer_weights)[0]

        responses.append(DrugResponse(
            drug=drug['drug'],
            drug_class=drug['class'],
            gene=drug['gene'],
            metabolizer_status=status,
            recommendation=recommendations[status],
            clinical_significance=drug['significance']
        ))

    return responses


def generate_traits() -> List[GeneticTrait]:
    """Generate genetic trait predictions."""

    trait_definitions = [
        # Nutrition
        {
            'trait': 'Caffeine Metabolism',
            'category': 'nutrition',
            'options': ['Fast metabolizer', 'Slow metabolizer'],
            'descriptions': ['Can consume caffeine later in day without sleep impact', 'Caffeine stays in system longer; avoid after noon']
        },
        {
            'trait': 'Lactose Tolerance',
            'category': 'nutrition',
            'options': ['Likely tolerant', 'Likely intolerant'],
            'descriptions': ['Can digest dairy products normally', 'May experience digestive issues with dairy']
        },
        {
            'trait': 'Alcohol Flush Reaction',
            'category': 'nutrition',
            'options': ['Normal metabolism', 'Flush reaction likely'],
            'descriptions': ['Metabolizes alcohol normally', 'May experience facial flushing after alcohol']
        },
        {
            'trait': 'Bitter Taste Perception',
            'category': 'sensory',
            'options': ['Taster', 'Non-taster'],
            'descriptions': ['Sensitive to bitter compounds like in broccoli', 'Less sensitive to bitter tastes']
        },
        {
            'trait': 'Saturated Fat Response',
            'category': 'nutrition',
            'options': ['Normal response', 'Elevated LDL response'],
            'descriptions': ['Standard dietary fat guidelines apply', 'May need to limit saturated fat more strictly']
        },
        # Fitness
        {
            'trait': 'Muscle Fiber Composition',
            'category': 'fitness',
            'options': ['Endurance-oriented', 'Power-oriented', 'Mixed'],
            'descriptions': ['More slow-twitch fibers; suits endurance sports', 'More fast-twitch fibers; suits power sports', 'Balanced fiber composition']
        },
        {
            'trait': 'VO2 Max Trainability',
            'category': 'fitness',
            'options': ['High responder', 'Normal responder', 'Low responder'],
            'descriptions': ['Cardiovascular fitness improves quickly with training', 'Standard improvement with training', 'May need more training for cardiovascular gains']
        },
        {
            'trait': 'Injury Risk (Achilles)',
            'category': 'fitness',
            'options': ['Lower risk', 'Average risk', 'Higher risk'],
            'descriptions': ['Standard injury precautions', 'Standard injury precautions', 'Extra attention to tendon health recommended']
        },
        # Sleep
        {
            'trait': 'Chronotype',
            'category': 'sleep',
            'options': ['Morning person', 'Evening person', 'Intermediate'],
            'descriptions': ['Natural tendency to wake early', 'Natural tendency toward later schedule', 'Flexible sleep schedule']
        },
        {
            'trait': 'Sleep Depth',
            'category': 'sleep',
            'options': ['Deep sleeper', 'Light sleeper'],
            'descriptions': ['Less likely to be disturbed during sleep', 'More sensitive to disturbances during sleep']
        },
        {
            'trait': 'Sleep Duration Need',
            'category': 'sleep',
            'options': ['Short sleeper', 'Average', 'Long sleeper'],
            'descriptions': ['May function well on less sleep', 'Typical 7-9 hour need', 'May need more than average sleep']
        },
        # Appearance
        {
            'trait': 'Male Pattern Baldness',
            'category': 'appearance',
            'options': ['Lower likelihood', 'Average likelihood', 'Higher likelihood'],
            'descriptions': ['Less genetic predisposition', 'Average genetic predisposition', 'Higher genetic predisposition']
        },
        {
            'trait': 'Freckling',
            'category': 'appearance',
            'options': ['Likely to freckle', 'Unlikely to freckle'],
            'descriptions': ['Genetic tendency toward freckling', 'Less likely to develop freckles']
        },
    ]

    traits = []
    for td in trait_definitions:
        idx = random.randint(0, len(td['options']) - 1)
        confidence = random.choice(['high', 'moderate', 'moderate', 'high'])

        traits.append(GeneticTrait(
            trait=td['trait'],
            category=td['category'],
            prediction=td['options'][idx],
            confidence=confidence,
            description=td['descriptions'][idx]
        ))

    return traits


def generate_ancestry() -> List[AncestryComposition]:
    """Generate ancestry composition."""

    # Generate a plausible ancestry mix
    templates = [
        # European-dominant
        {'European': 0.85, 'East Asian': 0.05, 'African': 0.03, 'Native American': 0.02, 'Middle Eastern': 0.03, 'South Asian': 0.02},
        # Mixed European/Latino
        {'European': 0.55, 'Native American': 0.25, 'African': 0.10, 'East Asian': 0.05, 'Middle Eastern': 0.03, 'South Asian': 0.02},
        # African American
        {'African': 0.75, 'European': 0.20, 'Native American': 0.03, 'East Asian': 0.01, 'Middle Eastern': 0.01},
        # East Asian
        {'East Asian': 0.90, 'Southeast Asian': 0.05, 'European': 0.03, 'South Asian': 0.02},
        # South Asian
        {'South Asian': 0.88, 'Middle Eastern': 0.05, 'Central Asian': 0.04, 'European': 0.03},
        # Mixed
        {'European': 0.40, 'African': 0.30, 'East Asian': 0.15, 'Native American': 0.10, 'Middle Eastern': 0.05},
    ]

    template = random.choice(templates)

    # Add some random variation
    total = 0
    ancestry = []
    regions = list(template.keys())

    for i, (region, pct) in enumerate(template.items()):
        if i == len(template) - 1:
            # Last one gets the remainder
            final_pct = round(1.0 - total, 3)
        else:
            # Add some variation
            variation = random.uniform(-0.03, 0.03)
            final_pct = max(0, min(1, pct + variation))
            final_pct = round(final_pct, 3)

        total += final_pct

        if final_pct > 0.01:  # Only include if > 1%
            ancestry.append(AncestryComposition(
                region=region,
                percentage=round(final_pct * 100, 1)
            ))

    # Sort by percentage descending
    ancestry.sort(key=lambda x: x.percentage, reverse=True)

    return ancestry


def generate_genetic_profile(patient_id: str) -> GeneticProfile:
    """Generate a complete genetic profile for a patient."""

    sequencing_type = random.choice(['whole_genome', 'whole_exome', 'genotyping_array'])
    variants_by_type = {
        'whole_genome': random.randint(4000000, 5000000),
        'whole_exome': random.randint(50000, 80000),
        'genotyping_array': random.randint(500000, 700000)
    }

    return GeneticProfile(
        id=patient_id,
        sequencing_date=date.today().replace(day=1),  # First of current month
        sequencing_type=sequencing_type,
        variants_analyzed=variants_by_type[sequencing_type],
        disease_risks=generate_disease_risks(),
        carrier_statuses=generate_carrier_statuses(),
        drug_responses=generate_drug_responses(),
        traits=generate_traits(),
        ancestry=generate_ancestry(),
        raw_data_available=True
    )
