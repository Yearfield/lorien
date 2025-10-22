import json

import pandas as pd

# Load disease probabilities
disease_df = pd.read_csv("C:/Harm Calc/P(Disease).csv", encoding="utf-8")
disease_df.columns = [str(col).strip().replace("\ufeff", "") for col in disease_df.columns]

# Load symptom probabilities
symptom_df = pd.read_csv("C:/Harm Calc/P(Symptom).csv", encoding="utf-8")
symptom_df.columns = [str(col).strip().replace("\ufeff", "") for col in symptom_df.columns]

# Load and reshape P(Symptom|Disease)
symptom_disease_wide = pd.read_csv("C:/Harm Calc/P(Symptom_Disease).csv", encoding="utf-8")
symptom_disease_wide.columns = [
    str(col).strip().replace("\ufeff", "") for col in symptom_disease_wide.columns
]
symptom_disease_long = symptom_disease_wide.melt(
    id_vars=["Symptom"], var_name="Disease", value_name="P(Symptom|Disease)"
)
symptom_disease_long = symptom_disease_long.dropna(
    subset=["Symptom", "Disease", "P(Symptom|Disease)"]
)

# Load symptoms from JSON file
json_path = "C:/Harm Calc/input_symptoms.json"  # Update this path as needed
try:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
        observed_symptoms = data.get("symptoms", [])
        if not observed_symptoms or len(observed_symptoms) > 5:
            raise ValueError("Please provide 1 to 5 symptoms in the JSON file.")
except Exception as e:
    print("❌ Error loading symptoms from JSON:", e)
    exit()

# Build lookup dictionaries
symptom_probs = {
    row["Symptom"].strip().lower(): row["P(symptom)"] for _, row in symptom_df.iterrows()
}
symptom_given_disease = {
    (row["Symptom"].strip().lower(), row["Disease"].strip()): row["P(Symptom|Disease)"]
    for _, row in symptom_disease_long.iterrows()
}

# Calculate unnormalized scores
scores = []
for _, row in disease_df.iterrows():
    VM = row["Disease"]
    Prob_VM = row["Estimated Lifetime Risk"]

    P_symptoms_given_VM = []
    missing_data = False
    for s in observed_symptoms:
        key = (s.strip().lower(), VM)
        prob = symptom_given_disease.get(key)
        if prob is not None:
            P_symptoms_given_VM.append(prob)
        else:
            missing_data = True
            break

    if missing_data:
        continue

    score = Prob_VM
    for p in P_symptoms_given_VM:
        score *= p

    scores.append((VM, score))

# Normalize and display top 5
total_score = sum(score for _, score in scores)
normalized_results = [(disease, score / total_score) for disease, score in scores]
top_diseases = sorted(normalized_results, key=lambda x: x[1], reverse=True)[:5]

print("\nTop 5 most likely diseases based on uploaded symptoms:")
for disease, prob in top_diseases:
    print(f"{disease}: P(Disease | Symptoms) = {prob:.6f}")
