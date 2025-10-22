"""
Data ingestion for EngineWarhammer.
Reads and parses CSV/XLSX files containing disease and symptom data.
"""

import io
import logging
import re
from typing import Any, Optional

import pandas as pd

from .consts import CONDITIONAL_COLUMNS, DISEASE_COLUMNS, SYMPTOM_COLUMNS
from .utils import normalize_disease_name, normalize_probability, normalize_symptom_name

logger = logging.getLogger(__name__)


def _normalize_header(name: str) -> str:
    s = str(name or "")
    s = s.strip().lower()
    # remove non-alphanumeric characters
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def find_column(df: pd.DataFrame, possible_names: list[str]) -> Optional[str]:
    """
    Find a column in DataFrame by trying multiple possible names.
    Matches are case/space/punctuation-insensitive.
    """
    normalized_to_original = {_normalize_header(col): col for col in df.columns}
    for name in possible_names:
        key = _normalize_header(name)
        if key in normalized_to_original:
            return normalized_to_original[key]
    return None


def read_file(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Read CSV or Excel file from bytes content.

    Args:
        file_content: File content as bytes
        filename: Original filename for format detection

    Returns:
        DataFrame with file contents

    Raises:
        ValueError: If file format is not supported
    """
    file_ext = filename.lower().split(".")[-1]

    if file_ext not in ["csv", "xlsx", "xls"]:
        raise ValueError(f"Unsupported file format: .{file_ext}")

    try:
        if file_ext == "csv":
            # Try different encodings for CSV
            for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
                try:
                    df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode CSV file with any supported encoding")
        else:
            # Excel file - read all sheets if present and concatenate
            try:
                all_sheets = pd.read_excel(io.BytesIO(file_content), sheet_name=None)
                if isinstance(all_sheets, dict) and all_sheets:
                    df = pd.concat(all_sheets.values(), ignore_index=True)
                else:
                    # Fallback to single-sheet read
                    df = pd.read_excel(io.BytesIO(file_content))
            except Exception:
                # Fallback to single-sheet read if multi-sheet parsing fails
                df = pd.read_excel(io.BytesIO(file_content))

        # Clean column names
        df.columns = [str(col).strip().replace("\ufeff", "") for col in df.columns]

        return df

    except Exception as e:
        logger.error(f"Error reading file {filename}: {str(e)}")
        raise ValueError(f"Error reading file: {str(e)}")


def extract_disease_data(file_content: bytes, filename: str) -> dict[str, Any]:
    """
    Extract disease data from CSV/XLSX file.

    Args:
        file_content: File content as bytes
        filename: Original filename

    Returns:
        Dictionary with extracted disease data
    """
    try:
        df = read_file(file_content, filename)

        # Find required columns
        disease_col = find_column(df, DISEASE_COLUMNS["disease_name"])
        risk_col = find_column(df, DISEASE_COLUMNS["estimated_lifetime_risk"])

        if not disease_col:
            return {
                "success": False,
                "errors": ["Required column 'Disease' not found in file"],
                "data": [],
            }

        if not risk_col:
            return {
                "success": False,
                "errors": ["Required column 'Estimated Lifetime Risk' not found in file"],
                "data": [],
            }

        diseases = []
        errors = []

        for idx, row in df.iterrows():
            try:
                disease_name = normalize_disease_name(row[disease_col])
                if not disease_name:
                    errors.append(f"Row {idx + 2}: Invalid disease name")
                    continue

                risk = normalize_probability(row[risk_col])
                if risk is None:
                    errors.append(f"Row {idx + 2}: Invalid risk value for disease '{disease_name}'")
                    continue

                diseases.append({"disease_name": disease_name, "estimated_lifetime_risk": risk})

            except Exception as e:
                errors.append(f"Row {idx + 2}: Error processing disease data - {str(e)}")

        return {"success": len(errors) == 0, "errors": errors, "data": diseases}

    except Exception as e:
        return {
            "success": False,
            "errors": [f"Error processing disease file: {str(e)}"],
            "data": [],
        }


def extract_symptom_data(file_content: bytes, filename: str) -> dict[str, Any]:
    """
    Extract symptom data from CSV/XLSX file.

    Args:
        file_content: File content as bytes
        filename: Original filename

    Returns:
        Dictionary with extracted symptom data
    """
    try:
        df = read_file(file_content, filename)

        # Find required columns
        symptom_col = find_column(df, SYMPTOM_COLUMNS["symptom_name"])
        prob_col = find_column(df, SYMPTOM_COLUMNS["probability"])

        if not symptom_col:
            return {
                "success": False,
                "errors": ["Required column 'Symptom' not found in file"],
                "data": [],
            }

        if not prob_col:
            return {
                "success": False,
                "errors": ["Required column 'P(symptom)' not found in file"],
                "data": [],
            }

        symptoms = []
        errors = []

        for idx, row in df.iterrows():
            try:
                symptom_name = normalize_symptom_name(row[symptom_col])
                if not symptom_name:
                    errors.append(f"Row {idx + 2}: Invalid symptom name")
                    continue

                prob = normalize_probability(row[prob_col])
                if prob is None:
                    errors.append(
                        f"Row {idx + 2}: Invalid probability value for symptom '{symptom_name}'"
                    )
                    continue

                symptoms.append({"symptom_name": symptom_name, "probability": prob})

            except Exception as e:
                errors.append(f"Row {idx + 2}: Error processing symptom data - {str(e)}")

        return {"success": len(errors) == 0, "errors": errors, "data": symptoms}

    except Exception as e:
        return {
            "success": False,
            "errors": [f"Error processing symptom file: {str(e)}"],
            "data": [],
        }


def extract_conditional_data(file_content: bytes, filename: str) -> dict[str, Any]:
    """
    Extract conditional probability data from CSV/XLSX file.

    Args:
        file_content: File content as bytes
        filename: Original filename

    Returns:
        Dictionary with extracted conditional data
    """
    try:
        df = read_file(file_content, filename)

        # Find required columns (long format)
        symptom_col = find_column(df, CONDITIONAL_COLUMNS["symptom_name"])
        disease_col = find_column(df, CONDITIONAL_COLUMNS["disease_name"])
        prob_col = find_column(df, CONDITIONAL_COLUMNS["conditional_probability"])

        # If not in long format, attempt to detect wide format and melt
        if symptom_col and (not disease_col or not prob_col):
            # Consider wide format if many non-symptom columns are numeric or look like diseases
            non_symptom_cols = [c for c in df.columns if c != symptom_col]
            numeric_like = [c for c in non_symptom_cols if pd.api.types.is_numeric_dtype(df[c])]
            if len(non_symptom_cols) >= 2 and (len(numeric_like) >= 1 or len(non_symptom_cols) > 5):
                melted = df.melt(
                    id_vars=[symptom_col], var_name="Disease", value_name="P(Symptom|Disease)"
                )
                # Drop rows with missing key fields
                melted = melted.dropna(subset=[symptom_col, "Disease", "P(Symptom|Disease)"])
                df = melted
                # Re-run detection against long-format names
                disease_col = find_column(df, CONDITIONAL_COLUMNS["disease_name"]) or "Disease"
                prob_col = (
                    find_column(df, CONDITIONAL_COLUMNS["conditional_probability"])
                    or "P(Symptom|Disease)"
                )

        # Fallback: if probability column still not found, try to auto-detect a numeric column
        if not prob_col:
            numeric_candidates = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            if len(numeric_candidates) == 1:
                prob_col = numeric_candidates[0]

        if not symptom_col:
            return {
                "success": False,
                "errors": ["Required column 'Symptom' not found in file"],
                "data": [],
            }

        if not disease_col:
            return {
                "success": False,
                "errors": ["Required column 'Disease' not found in file"],
                "data": [],
            }

        if not prob_col:
            return {
                "success": False,
                "errors": ["Required column 'P(Symptom|Disease)' not found in file"],
                "data": [],
            }

        conditionals = []
        errors = []

        for idx, row in df.iterrows():
            try:
                symptom_name = normalize_symptom_name(row[symptom_col])
                if not symptom_name:
                    errors.append(f"Row {idx + 2}: Invalid symptom name")
                    continue

                disease_name = normalize_disease_name(row[disease_col])
                if not disease_name:
                    errors.append(f"Row {idx + 2}: Invalid disease name")
                    continue

                prob = normalize_probability(row[prob_col])
                if prob is None:
                    errors.append(
                        f"Row {idx + 2}: Invalid probability value for symptom '{symptom_name}' and disease '{disease_name}'"
                    )
                    continue

                conditionals.append(
                    {
                        "symptom_name": symptom_name,
                        "disease_name": disease_name,
                        "conditional_probability": prob,
                    }
                )

            except Exception as e:
                errors.append(f"Row {idx + 2}: Error processing conditional data - {str(e)}")

        return {"success": len(errors) == 0, "errors": errors, "data": conditionals}

    except Exception:
        return {
            "success": False,
            "errors": ["Error processing conditional file: {str(e)}"],
            "data": [],
        }


def ingest_file(file_content: bytes, filename: str, file_type: str) -> dict[str, Any]:
    """
    Ingest file based on type (diseases, symptoms, or conditionals).

    Args:
        file_content: File content as bytes
        filename: Original filename
        file_type: Type of file ('diseases', 'symptoms', or 'conditionals')

    Returns:
        Dictionary with ingestion results
    """
    if file_type == "diseases":
        return extract_disease_data(file_content, filename)
    elif file_type == "symptoms":
        return extract_symptom_data(file_content, filename)
    elif file_type == "conditionals":
        return extract_conditional_data(file_content, filename)
    else:
        return {"success": False, "errors": [f"Unknown file type: {file_type}"], "data": []}
