#!/usr/bin/env python3
"""
LOC Eligibility Analysis Script

This script analyzes OFLC wage data to identify locations where a given
hourly wage meets or exceeds the specified wage level (L1-L4) for a
particular SOC code.

Usage:
    python src/analyze_locations.py [--config CONFIG_FILE]

Configuration is read from config.yaml by default.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml


class LOCAnalyzer:
    """Analyzes OFLC wage data to find eligible locations."""

    def __init__(self, config_path="config.yaml"):
        """Initialize analyzer with configuration."""
        self.config = self._load_config(config_path)
        self.project_root = Path(__file__).parent.parent
        self._validate_config()

    def _load_config(self, config_path):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✓ Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            print(f"✗ Error: Configuration file '{config_path}' not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"✗ Error parsing YAML configuration: {e}")
            sys.exit(1)

    def _validate_config(self):
        """Validate configuration parameters."""
        # Validate wage level
        wage_level = self.config.get('wage_level', '').upper()
        if wage_level not in ['L1', 'L2', 'L3', 'L4']:
            print(f"✗ Error: wage_level must be one of L1, L2, L3, L4 (got '{wage_level}')")
            sys.exit(1)

        # Validate hourly wage
        hourly_wage = self.config.get('hourly_wage')
        if not isinstance(hourly_wage, (int, float)) or hourly_wage <= 0:
            print(f"✗ Error: hourly_wage must be a positive number (got '{hourly_wage}')")
            sys.exit(1)

        # Validate data year
        data_year = self.config.get('data_year')
        if not data_year:
            print("✗ Error: data_year must be specified in config")
            sys.exit(1)

        print(f"✓ Configuration validated")
        print(f"  - Hourly wage: ${hourly_wage}")
        print(f"  - Wage level: {wage_level} (compares against {wage_level.replace('L', 'Level')} column)")
        print(f"  - SOC code: {self.config.get('soc_code')}")
        print(f"  - Data year: {data_year}")

    def _get_data_paths(self):
        """Construct paths to data files based on configuration."""
        data_year = self.config['data_year']
        data_dir = self.config.get('paths', {}).get('data_dir', 'data')

        # Construct folder name
        data_folder = f"OFLC_Wages_{data_year}"
        data_folder_path = self.project_root / data_dir / data_folder

        if not data_folder_path.exists():
            print(f"✗ Error: Data folder not found: {data_folder_path}")
            sys.exit(1)

        # Get file names from config or use defaults
        alc_file = self.config.get('paths', {}).get('alc_file', 'ALC_Export.csv')
        geography_file = self.config.get('paths', {}).get('geography_file', 'Geography.csv')

        alc_path = data_folder_path / alc_file
        geography_path = data_folder_path / geography_file

        if not alc_path.exists():
            print(f"✗ Error: ALC file not found: {alc_path}")
            sys.exit(1)

        if not geography_path.exists():
            print(f"✗ Error: Geography file not found: {geography_path}")
            sys.exit(1)

        print(f"✓ Data files located:")
        print(f"  - ALC: {alc_path}")
        print(f"  - Geography: {geography_path}")

        return str(alc_path), str(geography_path)

    def _load_data(self, alc_path, geography_path):
        """Load and preprocess data files."""
        print("\nLoading data files...")

        # Load ALC Export data
        try:
            alc_data = pd.read_csv(alc_path, low_memory=False)
            print(f"✓ Loaded ALC data: {alc_data.shape[0]:,} rows, {alc_data.shape[1]} columns")
        except Exception as e:
            print(f"✗ Error loading ALC file: {e}")
            sys.exit(1)

        # Load Geography data with encoding fallback
        encodings = self.config.get('advanced', {}).get('csv_encodings',
            ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252'])

        geography_data = None
        for encoding in encodings:
            try:
                geography_data = pd.read_csv(geography_path, encoding=encoding)
                if encoding != 'utf-8':
                    print(f"✓ Loaded Geography data with {encoding} encoding")
                else:
                    print(f"✓ Loaded Geography data")
                break
            except (UnicodeDecodeError, LookupError):
                continue

        if geography_data is None:
            print("✗ Error: Could not read Geography file with any encoding")
            sys.exit(1)

        print(f"  Geography data: {geography_data.shape[0]:,} rows, {geography_data.shape[1]} columns")

        return alc_data, geography_data

    def _clean_wage_columns(self, df):
        """Clean and convert wage columns to numeric."""
        wage_columns = ["Level1", "Level2", "Level3", "Level4", "Average"]

        for col in wage_columns:
            if col in df.columns:
                # Remove currency symbols, commas, and convert to numeric
                cleaned = (
                    df[col]
                    .astype(str)
                    .str.replace(r"[^0-9.\-]", "", regex=True)
                    .replace({"": pd.NA})
                )
                df[col] = pd.to_numeric(cleaned, errors="coerce")

        return df

    def _filter_data(self, alc_data):
        """Filter data based on SOC code and wage level."""
        print("\nFiltering data...")

        # Get parameters
        soc_code = self.config['soc_code']
        wage_level = self.config['wage_level'].upper()
        hourly_wage = self.config['hourly_wage']
        operator = self.config.get('advanced', {}).get('comparison_operator', '>=')

        # Map wage level to column name
        level_column = f"Level{wage_level[1]}"  # L1 -> Level1, L2 -> Level2, etc.

        if level_column not in alc_data.columns:
            print(f"✗ Error: Column '{level_column}' not found in data")
            sys.exit(1)

        # Filter by SOC code
        if 'SocCode' not in alc_data.columns:
            print("✗ Error: 'SocCode' column not found in ALC data")
            sys.exit(1)

        soc_mask = alc_data['SocCode'] == soc_code
        soc_count = soc_mask.sum()

        if soc_count == 0:
            print(f"✗ Warning: No records found for SOC code '{soc_code}'")
            print(f"  Available SOC codes (sample): {sorted(alc_data['SocCode'].unique())[:10]}")
            return pd.DataFrame()

        print(f"✓ Found {soc_count:,} locations with SOC code '{soc_code}'")

        # Apply wage filter
        if operator == '>=':
            wage_mask = alc_data[level_column] <= hourly_wage
        elif operator == '>':
            wage_mask = alc_data[level_column] < hourly_wage
        elif operator == '<=':
            wage_mask = alc_data[level_column] >= hourly_wage
        elif operator == '<':
            wage_mask = alc_data[level_column] > hourly_wage
        else:
            print(f"✗ Error: Invalid comparison operator '{operator}'")
            sys.exit(1)

        # Combine filters
        combined_mask = soc_mask & wage_mask
        filtered_data = alc_data[combined_mask].copy()

        print(f"✓ Found {len(filtered_data):,} locations where ${hourly_wage} {operator} {level_column}")
        print(f"  (Using wage level: {wage_level} → {level_column})")

        # Print statistics
        if len(filtered_data) > 0:
            level_stats = alc_data.loc[soc_mask, level_column].describe()
            print(f"\n{level_column} wage statistics for SOC {soc_code}:")
            print(f"  Min:  ${level_stats['min']:.2f}")
            print(f"  25th: ${level_stats['25%']:.2f}")
            print(f"  Median: ${level_stats['50%']:.2f}")
            print(f"  75th: ${level_stats['75%']:.2f}")
            print(f"  Max:  ${level_stats['max']:.2f}")
            print(f"  Your wage (${hourly_wage}) is at the {((alc_data.loc[soc_mask, level_column] <= hourly_wage).sum() / soc_count * 100):.1f}th percentile")

        return filtered_data

    def _merge_geography(self, filtered_data, geography_data):
        """Merge filtered data with geography information."""
        print("\nMerging with geography data...")

        merged = filtered_data.merge(geography_data, on="Area", how="left")
        print(f"✓ Merged data: {len(merged):,} rows")

        # Check for missing geography info
        missing_geo = merged['AreaName'].isna().sum()
        if missing_geo > 0:
            print(f"  Warning: {missing_geo} locations missing geography information")

        return merged

    def _prepare_output(self, merged_data):
        """Prepare final output with selected columns."""
        # Get columns to include
        columns_config = self.config.get('output', {}).get('columns')

        if columns_config is None:
            # Use all available columns in a sensible order
            preferred_order = [
                "Area", "AreaName", "StateAb", "State", "CountyTownName",
                "SocCode", "Level1", "Level2", "Level3", "Level4",
                "Average", "Label"
            ]
            columns = [col for col in preferred_order if col in merged_data.columns]
        else:
            columns = [col for col in columns_config if col in merged_data.columns]

        final_data = merged_data[columns].copy()

        # Sort by state and area name
        sort_columns = [col for col in ["StateAb", "AreaName"] if col in final_data.columns]
        if sort_columns:
            final_data = final_data.sort_values(sort_columns, na_position="last")

        return final_data

    def _export_results(self, final_data):
        """Export results to file."""
        print("\nExporting results...")

        # Get output configuration
        output_config = self.config.get('output', {})
        output_format = output_config.get('format', 'excel')
        include_timestamp = output_config.get('include_timestamp', False)
        output_dir = self.config.get('paths', {}).get('output_dir', 'output')

        # Construct output filename
        data_year = self.config['data_year']
        base_name = f"OFLC_Wages_{data_year}_eligible_locations"

        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"{base_name}_{timestamp}"

        output_path = self.project_root / output_dir

        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Export based on format
        if output_format.lower() == 'excel':
            output_file = output_path / f"{base_name}.xlsx"
            try:
                final_data.to_excel(output_file, index=False, engine='openpyxl')
                print(f"✓ Exported to Excel: {output_file}")
            except ImportError:
                print("  Warning: openpyxl not installed, trying xlsxwriter...")
                try:
                    final_data.to_excel(output_file, index=False, engine='xlsxwriter')
                    print(f"✓ Exported to Excel: {output_file}")
                except ImportError:
                    print("  Error: No Excel engine available, falling back to CSV")
                    output_file = output_path / f"{base_name}.csv"
                    final_data.to_csv(output_file, index=False)
                    print(f"✓ Exported to CSV: {output_file}")
        else:
            output_file = output_path / f"{base_name}.csv"
            final_data.to_csv(output_file, index=False)
            print(f"✓ Exported to CSV: {output_file}")

        return output_file

    def run(self):
        """Run the complete analysis pipeline."""
        print("=" * 70)
        print("LOC ELIGIBILITY ANALYSIS")
        print("=" * 70)

        # Get data paths
        alc_path, geography_path = self._get_data_paths()

        # Load data
        alc_data, geography_data = self._load_data(alc_path, geography_path)

        # Clean wage columns
        alc_data = self._clean_wage_columns(alc_data)

        # Filter data
        filtered_data = self._filter_data(alc_data)

        if len(filtered_data) == 0:
            print("\n" + "=" * 70)
            print("No eligible locations found. Please check your configuration.")
            print("=" * 70)
            return None

        # Merge with geography
        merged_data = self._merge_geography(filtered_data, geography_data)

        # Prepare output
        final_data = self._prepare_output(merged_data)

        # Export results
        output_file = self._export_results(final_data)

        # Print summary
        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"Total eligible locations: {len(final_data):,}")
        print(f"SOC Code: {self.config['soc_code']}")
        print(f"Hourly Wage: ${self.config['hourly_wage']}")
        print(f"Wage Level: {self.config['wage_level']}")
        print(f"Output file: {output_file}")
        print("=" * 70)

        return final_data


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Analyze OFLC wage data to find eligible locations'
    )
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    args = parser.parse_args()

    try:
        analyzer = LOCAnalyzer(config_path=args.config)
        analyzer.run()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
