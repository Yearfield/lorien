"""
Generate sample symptom matrix Excel file for EngineShortBow.
"""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_sample_matrix(
    num_symptoms: int = 15, output_path: str = "sample_symptom_matrix.xlsx"
) -> str:
    """
    Generate a sample symptom probability matrix.

    Args:
        num_symptoms: Number of symptoms to generate
        output_path: Output file path

    Returns:
        Path to generated file
    """
    # Sample symptoms (medical and general)
    base_symptoms = [
        "fever",
        "cough",
        "headache",
        "fatigue",
        "nausea",
        "diarrhea",
        "sore_throat",
        "rash",
        "chest_pain",
        "shortness_of_breath",
        "muscle_ache",
        "chills",
        "sweating",
        "dizziness",
        "abdominal_pain",
        "vomiting",
        "constipation",
        "joint_pain",
        "back_pain",
        "eye_pain",
    ]

    # Use first num_symptoms
    symptoms = base_symptoms[:num_symptoms]

    # Generate random probability matrix
    np.random.seed(42)  # For reproducibility
    prob_matrix = np.random.uniform(0, 0.8, (len(symptoms), len(symptoms)))

    # Make symmetric
    prob_matrix = (prob_matrix + prob_matrix.T) / 2

    # Set diagonal to 0 (no self-linkage)
    np.fill_diagonal(prob_matrix, 0)

    # Create DataFrame
    df = pd.DataFrame(prob_matrix, index=symptoms, columns=symptoms)

    # Round to 3 decimal places
    df = df.round(3)

    # Save to Excel
    output_file = Path(output_path)
    df.to_excel(output_file)

    print(f"Sample Excel sheet generated: {output_file}")
    print(f"Matrix size: {len(symptoms)}x{len(symptoms)}")
    print(f"Non-zero probabilities: {(df > 0).sum().sum()}")
    print(f"Average probability: {df.values[df.values > 0].mean():.3f}")

    return str(output_file)


if __name__ == "__main__":
    # Generate sample file in project root
    project_root = Path(__file__).parent.parent.parent
    output_path = project_root / "sample_symptom_matrix.xlsx"

    generate_sample_matrix(num_symptoms=15, output_path=str(output_path))
