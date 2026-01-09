#!/usr/bin/env python3
"""
Dataset Download Script for HealthBridge

Downloads and sets up public health datasets for use with HealthBridge.

Usage:
    python scripts/download_datasets.py --list           # List all datasets
    python scripts/download_datasets.py --all            # Download all datasets
    python scripts/download_datasets.py fitbit_kaggle    # Download specific dataset
    python scripts/download_datasets.py --status         # Check download status
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.adapters.registry import registry, register_all_adapters
from src.data.adapters.base import DataCategory

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BOLD}{text}{Colors.END}")
    print("=" * len(text))


def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")


def print_warning(text):
    print(f"{Colors.YELLOW}○{Colors.END} {text}")


def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")


def print_info(text):
    print(f"{Colors.BLUE}→{Colors.END} {text}")


def get_data_dir() -> Path:
    """Get the datasets directory."""
    return Path(__file__).parent.parent / "data" / "datasets"


def ensure_manifest(data_dir: Path) -> dict:
    """Load or create manifest file."""
    manifest_path = data_dir / "manifest.json"

    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            return json.load(f)

    return {
        "created": datetime.now().isoformat(),
        "datasets": {}
    }


def save_manifest(data_dir: Path, manifest: dict):
    """Save manifest file."""
    manifest_path = data_dir / "manifest.json"
    manifest["updated"] = datetime.now().isoformat()

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)


def list_datasets():
    """List all available datasets."""
    print_header("Available Datasets")

    register_all_adapters()
    datasets = registry.list_all()

    if not datasets:
        print_warning("No datasets registered.")
        return

    # Group by category
    by_category = {}
    for metadata in datasets:
        cat = metadata.category.value
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(metadata)

    for category, items in sorted(by_category.items()):
        print(f"\n{Colors.BOLD}{category.upper()}{Colors.END}")

        for metadata in items:
            adapter = registry.get(metadata.id)
            is_available = adapter.is_available() if adapter else False
            status = f"{Colors.GREEN}✓{Colors.END}" if is_available else f"{Colors.YELLOW}○{Colors.END}"
            auth = " (auth required)" if metadata.requires_auth else ""

            print(f"  {status} {metadata.id:<20} {metadata.name}{auth}")
            print(f"      Subjects: {metadata.subject_count:,} | Size: {metadata.size_mb or '?'} MB")


def check_status():
    """Check download status of all datasets."""
    print_header("Dataset Status")

    register_all_adapters()
    datasets = registry.list_all()

    data_dir = get_data_dir()
    manifest = ensure_manifest(data_dir)

    available = 0
    missing = 0

    for metadata in datasets:
        adapter = registry.get(metadata.id)
        is_available = adapter.is_available() if adapter else False

        if is_available:
            available += 1
            print_success(f"{metadata.name}")
        else:
            missing += 1
            print_warning(f"{metadata.name} - not downloaded")

    print(f"\n{Colors.BOLD}Summary:{Colors.END} {available} available, {missing} missing")


def download_dataset(dataset_id: str) -> bool:
    """Download a specific dataset."""
    register_all_adapters()
    adapter = registry.get(dataset_id)

    if adapter is None:
        print_error(f"Unknown dataset: {dataset_id}")
        return False

    metadata = adapter.metadata

    print_header(f"Downloading: {metadata.name}")
    print_info(f"Source: {metadata.source_url}")
    print_info(f"Size: {metadata.size_mb or 'Unknown'} MB")

    if metadata.requires_auth:
        print_warning("This dataset requires authentication/data agreement")

    # Create dataset directory
    data_dir = get_data_dir()
    dataset_dir = data_dir / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    # Dataset-specific download logic
    if dataset_id == "fitbit_kaggle":
        return download_fitbit_kaggle(dataset_dir)
    elif dataset_id == "nhanes":
        return download_nhanes(dataset_dir)
    elif dataset_id == "thousand_genomes":
        return download_thousand_genomes(dataset_dir)
    else:
        print_info("Manual download required:")
        print(f"\n{metadata.download_instructions}\n")
        print_info(f"Place downloaded files in: {dataset_dir}")
        return False


def download_fitbit_kaggle(dataset_dir: Path) -> bool:
    """Download Fitbit Kaggle dataset."""
    print_info("Checking for Kaggle CLI...")

    # Check if kaggle is installed
    try:
        result = subprocess.run(
            ["kaggle", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print_warning("Kaggle CLI not found. Install with: pip install kaggle")
            return False
    except FileNotFoundError:
        print_warning("Kaggle CLI not found. Install with: pip install kaggle")
        print_info("Also configure ~/.kaggle/kaggle.json with your API credentials")
        return False

    print_info("Downloading Fitbit dataset from Kaggle...")

    try:
        result = subprocess.run(
            [
                "kaggle", "datasets", "download",
                "-d", "arashnic/fitbit",
                "-p", str(dataset_dir),
                "--unzip"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print_success("Fitbit dataset downloaded successfully!")
            return True
        else:
            print_error(f"Download failed: {result.stderr}")
            return False

    except Exception as e:
        print_error(f"Download failed: {e}")
        return False


def download_nhanes(dataset_dir: Path) -> bool:
    """Download NHANES dataset files."""
    print_info("NHANES data requires manual download from CDC website")
    print()
    print("Steps:")
    print("1. Visit: https://wwwn.cdc.gov/nchs/nhanes/")
    print("2. Select survey cycle (e.g., 2017-2020)")
    print("3. Download:")
    print("   - Demographics (DEMO_J.XPT)")
    print("   - Plasma Fasting Glucose (GLU_J.XPT)")
    print("   - Standard Biochemistry Profile (BIOPRO_J.XPT)")
    print("   - Complete Blood Count (CBC_J.XPT)")
    print()
    print("4. Convert XPT to CSV using pyreadstat:")
    print("   pip install pyreadstat")
    print("   python -c \"import pyreadstat; df, meta = pyreadstat.read_xport('DEMO_J.XPT'); df.to_csv('DEMO_J.csv', index=False)\"")
    print()
    print(f"5. Place CSV files in: {dataset_dir}")

    return False


def download_thousand_genomes(dataset_dir: Path) -> bool:
    """Download 1000 Genomes sample metadata."""
    import urllib.request

    print_info("Downloading 1000 Genomes sample metadata...")

    url = "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel"
    output_file = dataset_dir / "samples.panel"

    try:
        urllib.request.urlretrieve(url, output_file)
        print_success(f"Downloaded sample panel to {output_file}")
        return True
    except Exception as e:
        print_error(f"Download failed: {e}")
        print_info("You can manually download from:")
        print(f"  {url}")
        return False


def download_all():
    """Download all datasets (where possible)."""
    print_header("Downloading All Datasets")

    register_all_adapters()
    datasets = registry.list_all()

    successes = 0
    failures = 0

    for metadata in datasets:
        if download_dataset(metadata.id):
            successes += 1
        else:
            failures += 1

    print(f"\n{Colors.BOLD}Complete:{Colors.END} {successes} downloaded, {failures} require manual download")


def main():
    parser = argparse.ArgumentParser(
        description="Download health datasets for HealthBridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_datasets.py --list              List all available datasets
  python download_datasets.py --status            Check download status
  python download_datasets.py fitbit_kaggle       Download Fitbit dataset
  python download_datasets.py --all               Download all datasets
        """
    )

    parser.add_argument(
        "dataset",
        nargs="?",
        help="Dataset ID to download"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available datasets"
    )
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Check download status"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Download all datasets"
    )

    args = parser.parse_args()

    # Ensure data directory exists
    data_dir = get_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)

    if args.list:
        list_datasets()
    elif args.status:
        check_status()
    elif args.all:
        download_all()
    elif args.dataset:
        download_dataset(args.dataset)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
