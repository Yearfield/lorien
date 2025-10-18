"""
Constants and column mappings for EngineShelob pathogen import.
"""

# Property columns (A-AJ) - descriptive attributes of pathogens
PROPERTY_COLUMNS = [
    "classification",  # Column A - e.g., "xd"
    "nt",  # Column B - e.g., "Actinobacteria"
    "pathogen_id",  # Column C - e.g., "2205725"
    "pathogen_name",  # Column D - e.g., "BACTERIA Actinobacteria Actinomycetales..."
    "vaccine",  # Column E - e.g., "No"
    "toxin",  # Column F - e.g., "No"
    "transmission",  # Column G - e.g., "Dental work, trauma, surgery, aspiration..."
    "ab_resistance",  # Column H - e.g., ""
    "host",  # Column I - e.g., "Ubiquitous soil commensal human and animal"
    "commensal",  # Column J - e.g., "Normal commensal flora oral respiratory tract..."
    "disease",  # Column K - e.g., "Lump Jaw Actinomycosis is a chronic..."
    "incubation",  # Column L - e.g., "days to years"
    "diagnosis",  # Column M - e.g., "Oral Periodontal Infection post dental work..."
    "treatment",  # Column N - e.g., ""
    "prevention",  # Column O - e.g., ""
    "notes",  # Column P - e.g., "oral-cervicofacial disease..."
]

# Patterns to detect association columns (AK+)
ASSOCIATION_DETECTION_PATTERNS = [
    # Binary value patterns
    r"^[01]$",
    r"^(yes|no)$",
    r"^(true|false)$",
    r"^(present|absent)$",
]

# Column names that indicate association columns
ASSOCIATION_INDICATORS = [
    "meningitis",
    "headache",
    "photophobia",
    "pneumonia",
    "fever",
    "cough",
    "diarrhea",
    "rodent",
    "asia",
    "europe",
    "africa",
    "america",
    "symptom",
    "disease",
    "syndrome",
    "risk",
    "factor",
    "complication",
    "outcome",
]

# Maximum number of property columns (should match PROPERTY_COLUMNS length)
MAX_PROPERTY_COLUMNS = len(PROPERTY_COLUMNS)

# File format support
SUPPORTED_FORMATS = [".csv", ".xlsx", ".xls"]
