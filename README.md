# LOC Data Analysis

A Python tool for analyzing OFLC (Office of Foreign Labor Certification) wage data to identify locations where your hourly wage qualifies for specific wage levels (L1-L4) based on SOC (Standard Occupational Classification) codes.

## Overview

This tool helps you determine which locations in the United States meet wage eligibility requirements for Labor Condition Applications (LCA). It analyzes OFLC wage data and identifies areas where your hourly wage meets or exceeds the specified wage level for your occupation.

## Features

- **Configurable wage levels**: Choose between L1 (Entry), L2 (Qualified), L3 (Experienced), or L4 (Fully Competent)
- **Flexible hourly wage**: Set your hourly wage in the configuration file
- **Multi-year support**: Analyze data from different fiscal years
- **SOC code filtering**: Filter by specific occupation codes
- **Automatic data loading**: Handles encoding issues and data cleaning
- **Multiple output formats**: Export to Excel or CSV
- **Detailed statistics**: View wage distributions and eligibility counts

## Project Structure

```
loc-data-analysis/
├── config.yaml              # Configuration file (edit this!)
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── data/                   # Input data files
│   ├── OFLC_Wages_2023-24/
│   │   ├── ALC_Export.csv
│   │   └── Geography.csv
│   ├── OFLC_Wages_2024-25/
│   │   ├── ALC_Export.csv
│   │   └── Geography.csv
│   └── OFLC_Wages_2025-26_Updated/
│       ├── ALC_Export.csv
│       └── Geography.csv
├── output/                 # Generated results (not tracked in git)
│   └── OFLC_Wages_*_eligible_locations.xlsx
└── src/                    # Source code
    └── analyze_locations.py
```

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install pandas PyYAML openpyxl xlsxwriter
   ```

3. **Ensure your data files are in the `data/` folder**

## Configuration

All settings are controlled through `config.yaml`. Edit this file to customize your analysis:

### Key Configuration Options

```yaml
# Your hourly wage (in USD)
hourly_wage: 80.0

# Wage level to compare against (L1, L2, L3, or L4)
# L1 = Entry Level
# L2 = Qualified Level
# L3 = Experienced Level
# L4 = Fully Competent Level
wage_level: "L4"

# Which year's data to use
data_year: "2024-25"  # Options: "2023-24", "2024-25", "2025-26_Updated"

# SOC code for your occupation
soc_code: "15-1299"  # Example: Computer Occupations, All Other
```

### Understanding Wage Levels

The OFLC provides four wage levels for each occupation and location:

- **L1 (Level 1)**: Entry level - for workers with basic understanding
- **L2 (Level 2)**: Qualified level - for workers with limited experience
- **L3 (Level 3)**: Experienced level - for workers with significant experience
- **L4 (Level 4)**: Fully competent level - for workers with full proficiency

**Important**: The tool finds locations where your hourly wage **meets or exceeds** the selected level. For example, if you set `wage_level: "L4"` and `hourly_wage: 80.0`, you'll get all locations where L4 wage is ≤ $80.00/hour.

## Usage

### Basic Usage

1. **Edit `config.yaml`** with your parameters:
   ```yaml
   hourly_wage: 75.0      # Your hourly wage
   wage_level: "L3"       # Level you want to qualify for
   data_year: "2024-25"   # Data year
   soc_code: "15-1252"    # Your SOC code
   ```

2. **Run the analysis**:
   ```bash
   python src/analyze_locations.py
   ```

3. **Find your results** in the `output/` folder:
   ```
   output/OFLC_Wages_2025-26_Updated_eligible_locations.xlsx
   ```

### Advanced Usage

#### Using a custom configuration file:
```bash
python src/analyze_locations.py --config my_config.yaml
```

#### Finding your SOC code:
Visit the [O*NET Online](https://www.onetonline.org/) or [BLS SOC page](https://www.bls.gov/soc/) to find your occupation's SOC code.

Common tech SOC codes:
- `15-1252`: Software Developers
- `15-1299`: Computer Occupations, All Other
- `15-1244`: Network and Computer Systems Administrators
- `15-1211`: Computer Systems Analysts

#### Changing comparison logic:
In `config.yaml`, under `advanced` section:
```yaml
advanced:
  # Use ">" for strictly greater than, ">=" for greater or equal, etc.
  comparison_operator: ">="
```

## Output

The tool generates an Excel or CSV file with the following columns:

| Column | Description |
|--------|-------------|
| Area | OFLC area code |
| AreaName | Name of the area/MSA |
| StateAb | State abbreviation (e.g., CA, NY) |
| State | Full state name |
| CountyTownName | County or town name |
| SocCode | SOC code |
| Level1-Level4 | Hourly wage for each level |
| Average | Average wage |
| Label | Additional label information |

Results are automatically sorted by state and area name.

## Example Output

```
======================================================================
LOC ELIGIBILITY ANALYSIS
======================================================================
✓ Configuration loaded from config.yaml
✓ Configuration validated
  - Hourly wage: $80.0
  - Wage level: L4
  - SOC code: 15-1299
  - Data year: 2025-26_Updated
✓ Data files located:
  - ALC: /path/to/data/OFLC_Wages_2025-26_Updated/ALC_Export.csv
  - Geography: /path/to/data/OFLC_Wages_2025-26_Updated/Geography.csv

Loading data files...
✓ Loaded ALC data: 449,440 rows, 9 columns
✓ Loaded Geography data
  Geography data: 3,275 rows, 5 columns

Filtering data...
✓ Found 530 locations with SOC code '15-1299'
✓ Found 392 locations where $80.0 >= Level4

Level4 wage statistics for SOC 15-1299:
  Min:  $29.95
  25th: $49.08
  Median: $54.64
  75th: $60.70
  Max:  $107.28
  Your wage ($80.0) is at the 95.3rd percentile

Merging with geography data...
✓ Merged data: 2,505 rows

Exporting results...
✓ Exported to Excel: output/OFLC_Wages_2025-26_Updated_eligible_locations.xlsx

======================================================================
ANALYSIS COMPLETE
======================================================================
Total eligible locations: 2,505
SOC Code: 15-1299
Hourly Wage: $80.0
Wage Level: L4
Output file: output/OFLC_Wages_2025-26_Updated_eligible_locations.xlsx
======================================================================
```

## Jupyter Notebook

The original Jupyter notebook (`loc_eligibility_analysis.ipynb`) is still available for interactive exploration, but the Python script is recommended for regular use.

## Troubleshooting

### No eligible locations found
- Check that your SOC code exists in the data
- Try a lower wage level (e.g., L3 instead of L4)
- Verify your hourly wage is reasonable for your occupation

### File encoding errors
The tool automatically tries multiple encodings for CSV files. If you still have issues, check the `advanced.csv_encodings` setting in `config.yaml`.

### Missing data files
Ensure your data folders follow this structure:
```
data/OFLC_Wages_{year}/
├── ALC_Export.csv
└── Geography.csv
```

## Data Sources

OFLC wage data is available from the [U.S. Department of Labor](https://www.dol.gov/agencies/eta/foreign-labor/wages/prevailing-wage-calculator).

## License

This tool is provided as-is for analysis of public OFLC wage data.

## Contributing

Feel free to submit issues or pull requests for improvements.

---

**Note**: This tool is for informational purposes only. Always verify wage requirements with official OFLC sources and consult with immigration professionals for LCA filings.
