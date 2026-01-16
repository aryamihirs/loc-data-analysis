# Quick Start Guide

Get up and running in 3 simple steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or if you're using a virtual environment:
```bash
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows

pip install -r requirements.txt
```

## Step 2: Configure Your Analysis

Edit `config.yaml`:

```yaml
# Set your hourly wage
hourly_wage: 64.9

# Choose wage level: L1, L2, L3, or L4
wage_level: "L4"

# Choose data year
data_year: "2024-25"

# Set your SOC code
soc_code: "15-1299"
```

## Step 3: Run the Analysis

```bash
python src/analyze_locations.py
```

Or with virtual environment:
```bash
source .venv/bin/activate && python src/analyze_locations.py
```

## Results

Your results will be in:
```
output/OFLC_Wages_{data_year}_eligible_locations.xlsx
```

## Examples

### Example 1: Entry Level Developer ($50/hr, L1)
```yaml
hourly_wage: 50.0
wage_level: "L1"
data_year: "2024-25"
soc_code: "15-1252"  # Software Developers
```

### Example 2: Experienced Developer ($85/hr, L3)
```yaml
hourly_wage: 85.0
wage_level: "L3"
data_year: "2024-25"
soc_code: "15-1252"
```

### Example 3: Senior Developer ($100/hr, L4)
```yaml
hourly_wage: 100.0
wage_level: "L4"
data_year: "2025-26_Updated"
soc_code: "15-1252"
```

## Common Issues

**No module named 'pandas'**
→ Run: `pip install -r requirements.txt`

**No eligible locations found**
→ Try a lower wage level or higher hourly wage

**File not found error**
→ Check that your data files are in `data/OFLC_Wages_{year}/`

---

For more details, see [README.md](README.md)
