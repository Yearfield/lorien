"""
Constants and column mappings for EngineWarhammer.
Defines the expected structure of CSV files for disease and symptom data.
"""

# Column mappings for P(Disease).csv
DISEASE_COLUMNS = {
    "disease_name": ["Disease", "disease", "DISEASE"],
    "estimated_lifetime_risk": [
        "Estimated Lifetime Risk",
        "estimated_lifetime_risk",
        "ESTIMATED_LIFETIME_RISK",
        "probability",
        "prob",
    ],
}

# Column mappings for P(Symptom).csv
SYMPTOM_COLUMNS = {
    "symptom_name": ["Symptom", "symptom", "SYMPTOM"],
    "probability": ["P(symptom)", "P(symptom)", "probability", "prob", "P_symptom"],
}

# Column mappings for P(Symptom_Disease).csv
CONDITIONAL_COLUMNS = {
    "symptom_name": ["Symptom", "symptom", "SYMPTOM", "symptom_name"],
    "disease_name": ["Disease", "disease", "DISEASE", "disease_name"],
    "conditional_probability": [
        "P(Symptom|Disease)",
        "P(Symptom | Disease)",
        "P(Symptom_given_Disease)",
        "P(S|D)",
        "P(Symptom_Disease)",
        "conditional_probability",
        "Conditional Probability",
        "Likelihood",
        "prob",
        "probability",
    ],
}

# File type validation
SUPPORTED_FILE_EXTENSIONS = [".csv", ".xlsx", ".xls"]

# Calculation constraints
MIN_SYMPTOMS = 1
MAX_SYMPTOMS = 5
TOP_RESULTS_LIMIT = 5

# Database table names
DISEASES_TABLE = "diseases"
SYMPTOMS_TABLE = "symptoms"
SYMPTOM_DISEASE_CONDITIONALS_TABLE = "symptom_disease_conditionals"
WARHAMMER_CALCULATIONS_TABLE = "warhammer_calculations"
