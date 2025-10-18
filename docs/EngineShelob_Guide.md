# EngineShelob - Pathogen Data Import Guide

## Overview

EngineShelob is a specialized import engine for pathogen data that reads spreadsheets containing pathogen properties and binary associations, storing them in isolated database tables separate from the decision tree structure.

## Data Format

### Spreadsheet Structure

EngineShelob expects spreadsheets with two distinct zones:

#### Zone A: Pathogen Properties (Columns A-AJ)

Descriptive or categorical attributes of pathogens:

| Column | Property | Example |
|--------|----------|---------|
| A | classification | "xd" |
| B | nt | "Actinobacteria" |
| C | pathogen_id | "2205725" |
| D | pathogen_name | "BACTERIA Actinobacteria Actinomycetales..." |
| E | vaccine | "No" |
| F | toxin | "No" |
| G | transmission | "Dental work, trauma, surgery, aspiration..." |
| H | ab_resistance | "" |
| I | host | "Ubiquitous soil commensal human and animal" |
| J | commensal | "Normal commensal flora oral respiratory tract..." |
| K | disease | "Lump Jaw Actinomycosis is a chronic..." |
| L | incubation | "days to years" |
| M | diagnosis | "Oral Periodontal Infection post dental work..." |
| N | treatment | "" |
| O | prevention | "" |
| P | notes | "oral-cervicofacial disease..." |

#### Zone B: Binary Associations (Columns AK+)

0/1 indicators showing presence of symptoms, diseases, risks, etc.:

| Column | Association Type | Example Values |
|--------|------------------|----------------|
| AK | meningitis | 0, 1 |
| AL | fever | 0, 1 |
| AM | cough | 0, 1 |
| ... | ... | ... |

### Supported File Formats

- **CSV** (.csv)
- **Excel** (.xlsx, .xls)

## API Usage

### Import Pathogen Data

```bash
curl -X POST "http://localhost:8000/api/v1/pathogens/import" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@pathogens.xlsx" \
  -F "strategy=upsert"
```

**Response:**

```json
{
  "success": true,
  "pathogens_processed": 150,
  "pathogens_created": 120,
  "pathogens_updated": 30,
  "associations_processed": 450,
  "associations_created": 300,
  "errors": [],
  "warnings": []
}
```

### List Pathogens

```bash
curl "http://localhost:8000/api/v1/pathogens/?limit=10&search=actinomyces"
```

**Response:**

```json
[
  {
    "id": 1,
    "classification": "xd",
    "nt": "Actinobacteria",
    "pathogen_id": "2205725",
    "pathogen_name": "Actinomyces gravenitzii",
    "vaccine": "No",
    "toxin": "No",
    "transmission": "Dental work, trauma, surgery, aspiration",
    "ab_resistance": "",
    "host": "Ubiquitous soil commensal human and animal",
    "commensal": "Normal commensal flora oral respiratory tract",
    "disease": "Lump Jaw Actinomycosis is a chronic suppurative",
    "incubation": "days to years",
    "diagnosis": "Oral Periodontal Infection post dental work",
    "treatment": "Immunocompromised",
    "prevention": "No",
    "notes": "oral-cervicofacial disease",
    "created_at": "2025-01-27T10:30:00.000Z",
    "updated_at": "2025-01-27T10:30:00.000Z"
  }
]
```

### Get Pathogen with Associations

```bash
curl "http://localhost:8000/api/v1/pathogens/1"
```

**Response:**

```json
{
  "id": 1,
  "classification": "xd",
  "nt": "Actinobacteria",
  "pathogen_id": "2205725",
  "pathogen_name": "Actinomyces gravenitzii",
  "vaccine": "No",
  "toxin": "No",
  "transmission": "Dental work, trauma, surgery, aspiration",
  "ab_resistance": "",
  "host": "Ubiquitous soil commensal human and animal",
  "commensal": "Normal commensal flora oral respiratory tract",
  "disease": "Lump Jaw Actinomycosis is a chronic suppurative",
  "incubation": "days to years",
  "diagnosis": "Oral Periodontal Infection post dental work",
  "treatment": "Immunocompromised",
  "prevention": "No",
  "notes": "oral-cervicofacial disease",
  "created_at": "2025-01-27T10:30:00.000Z",
  "updated_at": "2025-01-27T10:30:00.000Z",
  "associations": [
    {
      "association_type": "meningitis",
      "value": 1
    },
    {
      "association_type": "cough",
      "value": 1
    }
  ]
}
```

### Get Association Types

```bash
curl "http://localhost:8000/api/v1/pathogens/association-types/"
```

**Response:**

```json
[
  "cough",
  "diarrhea",
  "fever",
  "meningitis",
  "pneumonia"
]
```

### Get Statistics

```bash
curl "http://localhost:8000/api/v1/pathogens/stats/summary"
```

**Response:**

```json
{
  "total_pathogens": 150,
  "total_association_types": 25,
  "total_associations": 300,
  "pathogens_with_associations": 120,
  "pathogens_without_associations": 30
}
```

## Database Schema

### Tables

#### `pathogens`

Stores pathogen properties and descriptive attributes.

#### `association_types`

Stores unique association names from column headers.

#### `pathogen_associations`

Junction table linking pathogens to associations with binary values.

### Key Features

- **Isolation**: Completely separate from decision tree data
- **Idempotency**: Re-importing same data is safe
- **Efficiency**: Only stores positive associations (1s) to keep database light
- **Flexibility**: Dynamic association types from column headers

## Error Handling

### Common Issues

1. **Missing Pathogen Name**: Rows without a pathogen_name are skipped
2. **Invalid File Format**: Only CSV and Excel files are supported
3. **File Size Limit**: Maximum 10MB file size
4. **Binary Value Normalization**: Various formats (yes/no, true/false, 1/0) are supported

### Error Response Format

```json
{
  "success": false,
  "pathogens_processed": 0,
  "pathogens_created": 0,
  "pathogens_updated": 0,
  "associations_processed": 0,
  "associations_created": 0,
  "errors": [
    "Error processing pathogen 'Unknown': Pathogen name is required"
  ],
  "warnings": []
}
```

## Best Practices

1. **Column Headers**: Use clear, descriptive column names
2. **Data Consistency**: Ensure pathogen names are consistent across imports
3. **Binary Values**: Use 0/1, yes/no, or true/false for associations
4. **File Size**: Keep files under 10MB for optimal performance
5. **Backup**: Always backup your database before large imports

## Migration

To add the pathogen tables to your database, run:

```bash
python storage/migrate.py
```

This will apply the `010_add_pathogen_tables.sql` migration.
