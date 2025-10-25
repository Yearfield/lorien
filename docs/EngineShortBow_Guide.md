# EngineShortBow - Interactive Symptom Navigator Guide

## Overview

EngineShortBow is an interactive symptom navigator based on conditional probabilities that mimics aspects of differential diagnosis systems like those used in symptom checkers. It provides a guided navigation experience through related symptoms using a probability matrix.

## Purpose

EngineShortBow provides:

- **Interactive Symptom Navigation**: Guided navigation through related symptoms using probability matrices
- **Symptom Co-occurrence Analysis**: Uses probability matrices to find symptoms that commonly occur together
- **Calculation History**: Saves and tracks navigation sessions for reference
- **Data Import/Export**: Supports Excel file formats for symptom matrix data
- **Top Symptom Discovery**: Identifies symptoms with highest average linkage for starting navigation

## Data Format Requirements

### Symptom Matrix Excel File

The engine expects an Excel file containing a square matrix where:

- **Rows and Columns**: Symptom names
- **Cell Values**: Probabilities (0-1) representing linkage/co-occurrence between symptoms
- **Diagonal**: Should be 0 (no self-linkage) or will be ignored
- **Matrix Type**: Can be non-symmetric; uses row for current symptom to find linked ones

**Example Excel Structure:**

|         | fever | cough | headache | fatigue | nausea |
|---------|-------|-------|----------|---------|--------|
| fever   | 0     | 0.8   | 0.6      | 0.7     | 0.3    |
| cough   | 0.7   | 0     | 0.4      | 0.5     | 0.2    |
| headache| 0.6   | 0.4   | 0        | 0.8     | 0.4    |
| fatigue | 0.7   | 0.5   | 0.8      | 0       | 0.6    |
| nausea  | 0.3   | 0.2   | 0.4      | 0.6     | 0      |

## API Usage

### Import Symptom Matrix

```bash
curl -X POST "http://localhost:8000/api/v1/shortbow/import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@symptom_matrix.xlsx"
```

### Navigate Symptoms

```bash
curl -X POST "http://localhost:8000/api/v1/shortbow/navigate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_symptom": "fever",
    "exclude": ["cough", "headache"]
  }'
```

**Response:**

```json
{
  "current_symptom": "fever",
  "top_linked": [
    {
      "from_symptom": "fever",
      "to_symptom": "fatigue",
      "probability": 0.7
    },
    {
      "from_symptom": "fever",
      "to_symptom": "cough",
      "probability": 0.8
    }
  ],
  "excluded_symptoms": ["cough", "headache"],
  "total_available": 12
}
```

### Get Top Symptoms

```bash
curl "http://localhost:8000/api/v1/shortbow/top-symptoms?limit=6"
```

### Get Statistics

```bash
curl "http://localhost:8000/api/v1/shortbow/stats/summary"
```

**Response:**

```json
{
  "total_symptoms": 15,
  "total_links": 210,
  "total_calculations": 25,
  "saved_calculations": 10
}
```

### Save Calculation

```bash
curl -X POST "http://localhost:8000/api/v1/shortbow/calculations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_symptom": "fever",
    "selected_symptoms": ["fever", "fatigue", "cough", "headache", "nausea"]
  }'
```

### List Calculations

```bash
curl "http://localhost:8000/api/v1/shortbow/calculations?limit=20"
```

## Flutter UI Workflow

### 1. Access ShortBow Navigator

1. Navigate to the **VM Builder** pane
2. Click the **navigation icon** (🧭) in the app bar
3. This opens the ShortBow Navigator screen

### 2. Import Data

1. In the ShortBow Navigator, select the **"Import Data"** tab
2. Click **"Choose Excel File"** to upload your symptom matrix
3. Review the import results and statistics
4. The system will show:
   - Number of symptoms processed
   - Number of links created
   - Any errors or warnings

### 3. Navigate Symptoms

1. Switch to the **"Navigate"** tab
2. Use the dropdown to select a starting symptom
3. The system will show the top 5 linked symptoms with probabilities
4. Click the **"+"** button next to symptoms to add them to your selection
5. Selected symptoms appear as chips that can be removed
6. Continue navigating through related symptoms (up to 5 total)

### 4. Save Navigation Session

1. Once you have selected symptoms, click **"Save Calculation"**
2. The navigation session will be saved to your history
3. You can view recent calculations in the history section

### 5. View History

- Recent calculations are displayed at the bottom of the Navigate tab
- Each calculation shows the initial symptom and selected symptoms
- Click the bookmark icon to save important calculations
- Saved calculations are marked with a blue bookmark

## Database Schema

### Tables

#### `shortbow_symptoms`

- `id`: Primary key
- `symptom_name`: Symptom name (unique)
- `created_at`, `updated_at`: Timestamps

#### `shortbow_symptom_links`

- `id`: Primary key
- `symptom_from_id`: Foreign key to symptoms (source)
- `symptom_to_id`: Foreign key to symptoms (target)
- `probability`: Linkage probability (0.0-1.0)
- `created_at`, `updated_at`: Timestamps

#### `shortbow_calculations`

- `id`: Primary key
- `calculation_date`: When navigation was performed
- `initial_symptom`: Starting symptom name
- `selected_symptoms`: JSON array of selected symptoms
- `saved`: Boolean flag for saved calculations
- `created_at`: Timestamp

## Mathematical Foundation

EngineShortBow uses probability matrices to calculate symptom linkages:

**Navigation Logic:**

1. For a given current symptom, find all outgoing links
2. Exclude previously selected symptoms
3. Sort by probability descending
4. Return top 5 linked symptoms

**Top Symptoms Calculation:**

1. Calculate average linkage for each symptom to all others
2. Sort by average probability descending
3. Return top N symptoms for starting navigation

## Error Handling

### Common Issues

1. **Invalid File Format**: Only Excel files (.xlsx, .xls) are supported
2. **Invalid Probabilities**: Values outside 0.0-1.0 range are rejected
3. **Missing Data**: Symptoms without links are excluded from navigation
4. **Navigation Limits**: Maximum 5 symptoms can be selected

### Error Response Format

```json
{
  "success": false,
  "errors": [
    "Invalid probability value for symptom 'fever' and 'cough'"
  ],
  "warnings": [
    "Symptom 'unknown' has no outgoing links"
  ]
}
```

## Best Practices

### Data Preparation

1. **Consistent Naming**: Use consistent symptom names across the matrix
2. **Probability Validation**: Ensure all probabilities are between 0.0 and 1.0
3. **Complete Data**: Include probabilities for all relevant symptom pairs
4. **File Size**: Keep files under 50MB for optimal performance

### Usage Guidelines

1. **Symptom Selection**: Choose 1-5 most relevant symptoms for navigation
2. **Data Quality**: Regularly validate and update probability data
3. **Calculation History**: Save important navigation sessions for reference
4. **Backup**: Always backup your database before large imports

## Advanced Features

### Top Symptom Discovery

The engine automatically identifies symptoms with the highest average linkage to help users start navigation:

- **Calculation**: Average of all outgoing probabilities for each symptom
- **Ranking**: Sorted by average probability descending
- **Usage**: Displayed as starting options in the UI

### Navigation History

Track and manage navigation sessions:

- **Automatic Saving**: All navigation sessions are recorded
- **Manual Saving**: Mark important sessions for easy retrieval
- **History View**: Browse and reload previous navigation sessions

### Probability Visualization

Enhanced result display with:

- **Probability Percentages**: Clear display of linkage strengths
- **Visual Indicators**: Icons and colors for easy identification
- **Interactive Selection**: Easy addition/removal of symptoms

## Integration with Lorien

EngineShortBow integrates with the Lorien platform through:

- **VM Builder Access**: Available via navigation button in VM Builder
- **API Endpoints**: RESTful API for programmatic access
- **Database Integration**: Shared SQLite database with other Lorien features
- **Security**: Follows Lorien's authentication and rate limiting policies

## Sample Data Generation

To generate sample data for testing:

```bash
cd /home/jharm/Lorien
python3 Engines/EngineShortBow/sample_generator.py
```

This creates `sample_symptom_matrix.xlsx` with 15 symptoms and random probabilities.

## Migration

To add ShortBow tables to your database:

```bash
python storage/migrate.py
```

This applies the `012_add_shortbow_tables.sql` migration automatically.

## Troubleshooting

### Import Issues

- Check file format (Excel only)
- Verify probability values are valid (0.0-1.0)
- Ensure matrix has consistent row/column names

### Navigation Issues

- Verify symptoms exist in the database
- Check for missing probability data
- Ensure symptom names match exactly

### UI Issues

- Refresh the page if data doesn't appear
- Check browser console for JavaScript errors
- Verify API server is running and accessible

## API Endpoints Reference

### Core Navigation

#### Navigate Symptoms

```bash
curl -X POST "http://localhost:8000/api/v1/shortbow/navigate" \
  -H "Content-Type: application/json" \
  -d '{
    "current_symptom": "fever",
    "exclude": ["cough"]
  }'
```

#### Get Top Symptoms

```bash
curl "http://localhost:8000/api/v1/shortbow/top-symptoms?limit=6"
```

### Data Management

#### Import Matrix

```bash
curl -X POST "http://localhost:8000/api/v1/shortbow/import" \
  -F "file=@matrix.xlsx"
```

#### List Symptoms

```bash
curl "http://localhost:8000/api/v1/shortbow/symptoms?limit=50"
```

### Calculations

#### Create Calculation

```bash
curl -X POST "http://localhost:8000/api/v1/shortbow/calculations" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_symptom": "fever",
    "selected_symptoms": ["fever", "fatigue", "cough"]
  }'
```

#### Save Calculation

```bash
curl -X POST "http://localhost:8000/api/v1/shortbow/calculations/123/save"
```

#### List Calculations

```bash
curl "http://localhost:8000/api/v1/shortbow/calculations?limit=20"
```

## Future Enhancements

Planned improvements include:

- **Advanced Filtering**: Filter symptoms by category or severity
- **Export Results**: Export navigation sessions to CSV/PDF
- **Batch Navigation**: Navigate multiple symptom sets simultaneously
- **Confidence Intervals**: Statistical confidence measures for linkages
- **Machine Learning**: Improve probability estimates based on usage patterns
- **Integration**: Connect with decision tree symptoms for hybrid navigation
