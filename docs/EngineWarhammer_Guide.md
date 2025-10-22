# EngineWarhammer - Bayesian Disease Probability Calculator Guide

## Overview

EngineWarhammer is a specialized Bayesian inference engine for calculating disease probabilities based on observed symptoms. It implements the same mathematical approach as the original Warhammer_v3.py script but integrates seamlessly into the Lorien decision tree platform with advanced features for clinical decision support.

## Purpose

EngineWarhammer provides:

- **Bayesian Disease Probability Calculations**: Uses P(Disease), P(Symptom), and P(Symptom|Disease) to calculate P(Disease|Symptoms)
- **Clinical Decision Support**: Helps identify the most likely diseases given a set of observed symptoms
- **Data Import/Export**: Supports CSV and Excel file formats for easy data management
- **Calculation History**: Saves and tracks past calculations for reference
- **Decision Tree Integration**: Sources symptoms directly from VM Builder decision tree structure
- **Synonym Management**: Maps decision tree symptoms to Warhammer database symptoms
- **Confidence Visualization**: Visual confidence meters and detailed calculation explanations
- **Symptom Comparison**: Compare decision tree symptoms with Warhammer database coverage

## Data Format Requirements

### 1. Diseases Data (P(Disease).csv)

Contains disease names and their estimated lifetime risks.

**Required Columns:**

- `Disease` or `disease_name`: Disease name
- `Estimated Lifetime Risk` or `estimated_lifetime_risk`: Probability value (0.0 to 1.0)

**Example:**

```csv
Disease,Estimated Lifetime Risk
"Common Cold",0.15
"Flu",0.05
"Pneumonia",0.02
```

### 2. Symptoms Data (P(Symptom).csv)

Contains symptom names and their base probabilities.

**Required Columns:**

- `Symptom` or `symptom_name`: Symptom name
- `P(symptom)` or `probability`: Base probability value (0.0 to 1.0)

**Example:**

```csv
Symptom,P(symptom)
"fever",0.20
"cough",0.30
"headache",0.25
```

### 3. Conditional Probabilities (P(Symptom|Disease).csv)

Contains conditional probabilities for symptoms given diseases.

**Required Columns:**

- `Symptom` or `symptom_name`: Symptom name
- `Disease` or `disease_name`: Disease name
- `P(Symptom|Disease)` or `conditional_probability`: Conditional probability (0.0 to 1.0)

**Example:**

```csv
Symptom,Disease,P(Symptom|Disease)
"fever","Common Cold",0.40
"cough","Common Cold",0.80
"fever","Flu",0.90
"cough","Flu",0.60
```

## API Usage

### Import Data

#### Import Diseases

```bash
curl -X POST "http://localhost:8000/api/v1/warhammer/import/diseases" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@diseases.csv"
```

#### Import Symptoms

```bash
curl -X POST "http://localhost:8000/api/v1/warhammer/import/symptoms" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@symptoms.csv"
```

#### Import Conditionals

```bash
curl -X POST "http://localhost:8000/api/v1/warhammer/import/conditionals" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@conditionals.csv"
```

### Calculate Disease Probabilities

```bash
curl -X POST "http://localhost:8000/api/v1/warhammer/calculate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough", "headache"]
  }'
```

**Response:**

```json
{
  "calculation_id": null,
  "input_symptoms": ["fever", "cough", "headache"],
  "results": [
    {
      "disease": "Flu",
      "probability": 0.456
    },
    {
      "disease": "Common Cold",
      "probability": 0.321
    },
    {
      "disease": "Pneumonia",
      "probability": 0.223
    }
  ],
  "timestamp": "2025-01-27T10:30:00.000Z",
  "errors": [],
  "synonym_resolutions": [
    {
      "original": "Fever",
      "resolved": "fever"
    }
  ],
  "explanations": [
    {
      "disease": "Flu",
      "prior": 0.05,
      "factors": [
        {"symptom": "fever", "p_symptom_given_disease": 0.9},
        {"symptom": "cough", "p_symptom_given_disease": 0.6},
        {"symptom": "headache", "p_symptom_given_disease": 0.7}
      ]
    }
  ]
}
```

### List Available Symptoms

```bash
curl "http://localhost:8000/api/v1/warhammer/symptoms?limit=50"
```

### Get Statistics

```bash
curl "http://localhost:8000/api/v1/warhammer/stats/summary"
```

**Response:**

```json
{
  "total_diseases": 150,
  "total_symptoms": 75,
  "total_conditionals": 300,
  "total_calculations": 25,
  "saved_calculations": 10
}
```

### Save Calculations

```bash
curl -X POST "http://localhost:8000/api/v1/warhammer/calculations/123/save" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Saved Calculations

```bash
curl "http://localhost:8000/api/v1/warhammer/calculations?limit=20"
```

## Flutter UI Workflow

### 1. Import Data

1. Navigate to the **Outcomes** pane
2. Select **Warhammer** engine from the dropdown
3. If no data is available, click **"Import Data"**
4. Upload the three required CSV files:
   - Diseases data (P(Disease).csv)
   - Symptoms data (P(Symptom).csv)
   - Conditional probabilities (P(Symptom|Disease).csv)
5. Review import results and statistics

### 2. Calculate Disease Probabilities

1. In the **Outcomes** pane with **Warhammer** selected
2. Use the hierarchical symptom dropdown to select 1-5 symptoms:
   - Start at decision tree roots
   - Navigate through the tree structure
   - Select symptoms as you go
3. The system auto-calculates when 5 symptoms are selected
4. Click **"Auto-calculated! Click to recalculate"** to manually recalculate
5. Optionally save the calculation for future reference

### 3. View Results

Results are displayed with:

- **Top disease highlighted** in blue with larger text
- **Probability percentages** for each disease
- **Confidence meters** showing visual probability bars
- **Warnings** if any data is missing
- **Save button** to persist the calculation
- **"Why these results?"** expandable section showing calculation details

### 4. Manage Symptoms and Synonyms

1. Click **"Compare Symptoms"** to see coverage analysis
2. View missing symptoms from decision tree vs Warhammer database
3. Create synonym mappings for "extra" Warhammer symptoms
4. Use **"Scan VM Builder"** to refresh decision tree data after changes

### 5. Refresh Decision Tree Data

The **"Scan VM Builder"** button is essential for keeping EngineWarhammer synchronized with your decision tree:

**When to Use:**

- After importing new decision trees through VM Builder
- After creating new Vital Measurements in the Editor
- After making structural changes to existing decision trees
- When symptom dropdown doesn't show expected options

**How It Works:**

1. Click the **"Scan VM Builder"** button (green button with refresh icon)
2. The system fetches the latest decision tree roots from the API
3. Updates the symptom selection dropdown with new available options
4. Resets navigation to root level to show all available trees
5. Any previously selected symptoms remain selected

**Technical Details:**

- Calls `/api/v1/tree/roots` endpoint to fetch current decision tree structure
- Updates internal state with new root nodes and available options
- Maintains user's symptom selections while refreshing available choices
- Provides loading indicator during refresh operation

## Database Schema

### Tables

#### `diseases`

- `id`: Primary key
- `disease_name`: Disease name (unique)
- `estimated_lifetime_risk`: Lifetime risk probability
- `created_at`, `updated_at`: Timestamps

#### `symptoms`

- `id`: Primary key
- `symptom_name`: Symptom name (unique)
- `probability`: Base symptom probability
- `created_at`, `updated_at`: Timestamps

#### `symptom_disease_conditionals`

- `id`: Primary key
- `symptom_id`: Foreign key to symptoms
- `disease_id`: Foreign key to diseases
- `conditional_probability`: P(Symptom|Disease)
- `created_at`, `updated_at`: Timestamps

#### `warhammer_calculations`

- `id`: Primary key
- `calculation_date`: When calculation was performed
- `input_symptoms`: JSON array of symptom names
- `results`: JSON array of disease results
- `saved`: Boolean flag for saved calculations
- `created_at`: Timestamp

#### `symptom_synonyms`

- `id`: Primary key
- `warhammer_symptom`: Symptom name in Warhammer database
- `decision_tree_symptom`: Corresponding symptom name in decision tree
- `created_at`, `updated_at`: Timestamps

## Mathematical Foundation

EngineWarhammer uses Bayesian inference to calculate:

**P(Disease|Symptoms) = P(Disease) × P(Symptom1|Disease) × P(Symptom2|Disease) × ... / P(Symptoms)**

Where:

- **P(Disease)**: Prior probability from diseases table
- **P(Symptom|Disease)**: Conditional probabilities from conditionals table
- **P(Symptoms)**: Normalization factor (sum of all disease scores)

The engine:

1. Calculates unnormalized scores for each disease
2. Normalizes scores to probabilities (sum = 1.0)
3. Returns top 5 diseases sorted by probability

## Error Handling

### Common Issues

1. **Missing Data**: Diseases without conditional probabilities are excluded
2. **Invalid Probabilities**: Values outside 0.0-1.0 range are rejected
3. **File Format**: Only CSV and Excel files are supported
4. **Symptom Limits**: Must provide 1-5 symptoms for calculation

### Error Response Format

```json
{
  "success": false,
  "errors": [
    "Missing conditional probability data for 5 diseases",
    "Invalid probability value for symptom 'fever' and disease 'Unknown'"
  ],
  "warnings": []
}
```

## Best Practices

### Data Preparation

1. **Consistent Naming**: Use consistent disease and symptom names across files
2. **Probability Validation**: Ensure all probabilities are between 0.0 and 1.0
3. **Complete Data**: Include conditional probabilities for all disease-symptom combinations
4. **File Size**: Keep files under 50MB for optimal performance

### Usage Guidelines

1. **Symptom Selection**: Choose 1-5 most relevant symptoms
2. **Data Quality**: Regularly validate and update probability data
3. **Calculation History**: Save important calculations for reference
4. **Backup**: Always backup your database before large imports

## Advanced Features

### Decision Tree Integration

EngineWarhammer sources symptoms directly from the VM Builder decision tree:

- **Hierarchical Navigation**: Start at roots and navigate through tree structure
- **Manual Sync**: Use "Scan VM Builder" to refresh symptom choices when decision tree changes
- **Consistent Naming**: Symptoms match exactly with decision tree labels
- **State Management**: Maintains user selections while updating available options

### Synonym Management

Map decision tree symptoms to Warhammer database symptoms:

- **Symptom Comparison**: View coverage between decision tree and Warhammer
- **Synonym Creation**: Map "extra" Warhammer symptoms to decision tree equivalents
- **Automatic Resolution**: Calculator uses synonyms when symptoms aren't found directly
- **Validation**: Prevents case-only differences from being treated as synonyms

### Confidence Visualization

Enhanced result display with:

- **Visual Meters**: Linear progress bars showing relative probabilities
- **Calculation Details**: Expandable "Why these results?" section
- **Prior Values**: Shows P(Disease) for each result
- **Conditional Factors**: Displays P(Symptom|Disease) for each selected symptom

## Integration with Lorien

EngineWarhammer integrates with the Lorien platform through:

- **Outcomes Pane**: Main UI for calculations and data management
- **Engine Selector**: Extensible design for future engines
- **API Endpoints**: RESTful API for programmatic access
- **Database Integration**: Shared SQLite database with other Lorien features
- **VM Builder Integration**: Direct symptom sourcing from decision tree
- **Security**: Follows Lorien's authentication and rate limiting policies

## Migration

To add Warhammer tables to your database:

```bash
python storage/migrate.py
```

This applies the `011_add_warhammer_tables.sql` migration automatically.

## Troubleshooting

### Import Issues

- Check file format (CSV/Excel only)
- Verify required columns are present
- Ensure probability values are valid (0.0-1.0)

### Calculation Issues

- Verify all three data types are imported
- Check for missing conditional probabilities
- Ensure symptom names match exactly

### UI Issues

- Refresh the page if data doesn't appear
- Check browser console for JavaScript errors
- Verify API server is running and accessible

## API Endpoints Reference

### Synonym Management

#### List Synonyms

```bash
curl "http://localhost:8000/api/v1/warhammer/synonyms"
```

#### Create Synonym

```bash
curl -X POST "http://localhost:8000/api/v1/warhammer/synonyms" \
  -H "Content-Type: application/json" \
  -d '{
    "warhammer_symptom": "muscle pain",
    "decision_tree_symptom": "Myalgia"
  }'
```

#### Delete Synonym

```bash
curl -X DELETE "http://localhost:8000/api/v1/warhammer/synonyms/123"
```

### Symptom Comparison

#### Compare Decision Tree vs Warhammer Symptoms

```bash
curl "http://localhost:8000/api/v1/warhammer/symptoms/comparison"
```

**Response:**

```json
{
  "decision_tree_symptoms": ["Fever", "Cough", "Headache"],
  "warhammer_symptoms": ["fever", "cough", "headache", "muscle pain"],
  "matching_symptoms": ["Fever", "Cough", "Headache"],
  "missing_from_warhammer": [],
  "extra_in_warhammer": ["muscle pain"],
  "total_decision_tree": 3,
  "total_warhammer": 4,
  "match_count": 3,
  "normalized_matches": [
    {
      "decision_tree": "Fever",
      "warhammer": "fever",
      "normalized": "fever"
    }
  ]
}
```

## Future Enhancements

Planned improvements include:

- **Advanced Filtering**: Filter diseases by category or severity
- **Export Results**: Export calculations to CSV/PDF
- **Batch Calculations**: Calculate probabilities for multiple symptom sets
- **Confidence Intervals**: Statistical confidence measures for results
- **Machine Learning**: Improve probability estimates based on usage patterns
