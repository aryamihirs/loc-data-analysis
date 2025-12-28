# LOC Data Analysis

A Python notebook for filtering and analyzing location eligibility data based on salary and SOC (Standard Occupational Classification) codes.

## Overview

This notebook helps identify eligible locations where a given salary qualifies for Level4 wage levels for a specific SOC code, using data from OFLC (Office of Foreign Labor Certification) wage data.

## Features

- Loads wage data (ALC_Export.csv) and geography data (Geography.csv)
- Filters locations by:
  - SOC Code (e.g., "15-1299")
  - Salary threshold (must be >= Level4 wage)
- Exports results to Excel with dynamic filename based on data folder name
- Handles encoding issues for CSV files

## Usage

1. Update the parameters in Cell 0:
   - `SALARY`: Your salary amount (e.g., 64.9)
   - `SOCCODE_FILTER`: The SOC code to filter (e.g., "15-1299")
   - `TABLE1_PATH`: Path to ALC_Export.csv
   - `TABLE2_PATH`: Path to Geography.csv

2. Run Cell 0 to load data and filter eligible locations

3. Run Cell 2 to export results to Excel

## Output

The notebook generates an Excel file named `{parent_folder}_eligible_locations.xlsx` containing all eligible locations with:
- Area information
- Location details (AreaName, StateAb, State, CountyTownName)
- Wage levels (Level1, Level2, Level3, Level4, Average)
- SOC Code and Label

## Requirements

- pandas
- openpyxl (for Excel export)

Install dependencies:
```bash
pip install pandas openpyxl
```

## Data Sources

Uses OFLC wage data files:
- ALC_Export.csv: Contains wage levels by Area and SOC Code
- Geography.csv: Contains location details by Area

