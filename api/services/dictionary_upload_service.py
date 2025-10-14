"""
Dictionary upload service for processing medical dictionary files.
Handles CSV/XLSX uploads, term matching, definition filling, and spelling error detection.
"""

import json
import sqlite3
from difflib import SequenceMatcher
from typing import Any, Optional

import anyio
from fastapi import HTTPException, status


class DictionaryUploadService:
    """Service for processing medical dictionary file uploads."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.similarity_threshold = 0.8  # Minimum similarity for spelling suggestions

    async def process_dictionary_upload(
        self,
        file_content: bytes,
        filename: str,
        update_existing: bool = True,
        create_new_terms: bool = True,
        min_similarity: float = 0.8,
    ) -> dict[str, Any]:
        """
        Process a medical dictionary file upload.

        Args:
            file_content: Raw file bytes
            filename: Original filename
            update_existing: Whether to update existing dictionary terms
            create_new_terms: Whether to create new terms not in dictionary
            min_similarity: Minimum similarity threshold for spelling suggestions

        Returns:
            Processing results with matches, updates, and spelling suggestions
        """
        try:
            import time

            start_time = time.time()

            # Parse the uploaded file
            parse_start = time.time()
            rows = await self._parse_dictionary_file(file_content, filename)
            parse_duration = time.time() - parse_start

            # Analyze the file structure
            analysis_start = time.time()
            analysis = await self._analyze_dictionary_structure(rows)
            analysis_duration = time.time() - analysis_start

            # Process each term in the file
            processing_start = time.time()
            results = await self._process_dictionary_terms(
                rows,
                update_existing=update_existing,
                create_new_terms=create_new_terms,
                min_similarity=min_similarity,
            )
            processing_duration = time.time() - processing_start

            total_duration = time.time() - start_time

            return {
                "success": True,
                "filename": filename,
                "file_analysis": analysis,
                "processing_results": results,
                "summary": self._generate_summary(results),
                "performance_metrics": {
                    "total_duration_ms": round(total_duration * 1000, 2),
                    "parse_duration_ms": round(parse_duration * 1000, 2),
                    "analysis_duration_ms": round(analysis_duration * 1000, 2),
                    "processing_duration_ms": round(processing_duration * 1000, 2),
                    "terms_per_second": round(len(rows) / total_duration, 2)
                    if total_duration > 0
                    else 0,
                    "file_size_bytes": len(file_content),
                },
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Dictionary upload processing failed: {str(e)}",
            )

    async def _parse_dictionary_file(
        self, file_content: bytes, filename: str
    ) -> list[dict[str, Any]]:
        """Parse CSV or XLSX dictionary file."""
        # Use the existing file parsing functionality
        from ..routers.helpers import parse_csv_or_xlsx

        try:
            _, rows = parse_csv_or_xlsx(file_content, filename)
            return rows
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not parse dictionary file: {str(e)}",
            )

    async def _analyze_dictionary_structure(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze the structure of the uploaded dictionary file."""
        if not rows:
            return {"error": "No data found in file"}

        # Detect columns
        sample_row = rows[0]
        detected_columns = list(sample_row.keys())

        # Try to identify term and definition columns
        term_column = self._detect_column(
            detected_columns, ["term", "symptom", "condition", "diagnosis", "name"]
        )
        definition_column = self._detect_column(
            detected_columns, ["definition", "description", "meaning", "explanation"]
        )
        synonyms_column = self._detect_column(
            detected_columns, ["synonyms", "alternatives", "aliases", "other_names"]
        )
        red_flag_column = self._detect_column(
            detected_columns, ["red_flag", "urgent", "critical", "emergency"]
        )

        return {
            "total_rows": len(rows),
            "detected_columns": detected_columns,
            "mapped_columns": {
                "term": term_column,
                "definition": definition_column,
                "synonyms": synonyms_column,
                "red_flag": red_flag_column,
            },
            "file_structure_valid": bool(term_column),
        }

    def _detect_column(self, columns: list[str], possible_names: list[str]) -> Optional[str]:
        """Detect the most likely column name from a list of possibilities."""
        columns_lower = [col.lower().strip() for col in columns]

        for possible in possible_names:
            for col in columns_lower:
                if possible.lower() in col or col in possible.lower():
                    return columns[columns_lower.index(col)]

        return None

    async def _process_dictionary_terms(
        self,
        rows: list[dict[str, Any]],
        update_existing: bool = True,
        create_new_terms: bool = True,
        min_similarity: float = 0.8,
    ) -> dict[str, Any]:
        """Process each term in the dictionary file."""
        results = {
            "matches_found": 0,
            "updates_applied": 0,
            "new_terms_created": 0,
            "spelling_suggestions": [],
            "errors": [],
            "processed_terms": [],
        }

        # Get all existing dictionary terms for matching
        existing_terms = await self._get_existing_dictionary_terms()
        existing_terms_lower = {term.lower(): term for term in existing_terms}

        for row_idx, row in enumerate(rows, 1):
            try:
                term_result = await self._process_single_term(
                    row,
                    row_idx,
                    existing_terms_lower,
                    update_existing=update_existing,
                    create_new_terms=create_new_terms,
                    min_similarity=min_similarity,
                )

                results["processed_terms"].append(term_result)

                if term_result["match_type"] == "exact_match":
                    results["matches_found"] += 1
                    if term_result["updated"]:
                        results["updates_applied"] += 1
                elif term_result["match_type"] == "new_term":
                    results["new_terms_created"] += 1
                elif term_result["match_type"] == "spelling_suggestion":
                    results["spelling_suggestions"].append(term_result)

            except Exception as e:
                error_msg = f"Row {row_idx}: {str(e)}"
                results["errors"].append(error_msg)

        return results

    async def _get_existing_dictionary_terms(self) -> list[str]:
        """Get all existing dictionary terms."""
        cursor = await anyio.to_thread.run_sync(
            self.conn.execute, "SELECT term FROM medical_dictionary ORDER BY term"
        )
        rows = await anyio.to_thread.run_sync(cursor.fetchall)
        return [row["term"] for row in rows]

    async def _process_single_term(
        self,
        row: dict[str, Any],
        row_idx: int,
        existing_terms_lower: dict[str, str],
        update_existing: bool = True,
        create_new_terms: bool = True,
        min_similarity: float = 0.8,
    ) -> dict[str, Any]:
        """Process a single term from the dictionary file."""
        # Extract term information
        term_info = self._extract_term_info(row)

        if not term_info["term"]:
            return {
                "row": row_idx,
                "term": "",
                "match_type": "error",
                "error": "No term found in row",
                "updated": False,
            }

        term = term_info["term"]
        term_lower = term.lower().strip()

        # Check for exact match
        if term_lower in existing_terms_lower:
            existing_term = existing_terms_lower[term_lower]
            return await self._handle_exact_match(existing_term, term_info, update_existing)

        # Check for spelling suggestions
        spelling_suggestions = self._find_spelling_suggestions(
            term_lower, existing_terms_lower, min_similarity
        )

        if spelling_suggestions:
            return {
                "row": row_idx,
                "term": term,
                "match_type": "spelling_suggestion",
                "spelling_suggestions": spelling_suggestions,
                "definition": term_info["definition"],
                "updated": False,
            }

        # Create new term if allowed
        if create_new_terms:
            return await self._create_new_term(term_info, row_idx)
        else:
            return {
                "row": row_idx,
                "term": term,
                "match_type": "no_match",
                "error": "Term not found and new term creation disabled",
                "updated": False,
            }

    def _extract_term_info(self, row: dict[str, Any]) -> dict[str, Any]:
        """Extract term information from a row."""
        # Try to find term in various possible column names
        term = None
        for key in row.keys():
            if key.lower() in ["term", "symptom", "condition", "diagnosis", "name"]:
                term = row[key]
                break

        # If no specific term column, use the first non-empty column
        if not term:
            for key, value in row.items():
                if value and str(value).strip():
                    term = value
                    break

        # Try to find definition
        definition = None
        for key in row.keys():
            if key.lower() in ["definition", "description", "meaning", "explanation"]:
                definition = row[key]
                break

        # Try to find synonyms
        synonyms = []
        for key in row.keys():
            if key.lower() in ["synonyms", "alternatives", "aliases", "other_names"]:
                synonyms_str = row[key]
                if synonyms_str:
                    # Parse synonyms (comma-separated)
                    synonyms = [s.strip() for s in str(synonyms_str).split(",") if s.strip()]
                break

        # Try to find red flag status
        is_red_flag = False
        for key in row.keys():
            if key.lower() in ["red_flag", "urgent", "critical", "emergency"]:
                red_flag_value = row[key]
                if red_flag_value:
                    # Check for various true values
                    red_flag_str = str(red_flag_value).lower().strip()
                    is_red_flag = red_flag_str in ["true", "1", "yes", "y", "urgent", "critical"]
                break

        return {
            "term": str(term).strip() if term else "",
            "definition": str(definition).strip() if definition else None,
            "synonyms": synonyms,
            "is_red_flag": is_red_flag,
        }

    async def _handle_exact_match(
        self, existing_term: str, term_info: dict[str, Any], update_existing: bool
    ) -> dict[str, Any]:
        """Handle exact match with existing dictionary term."""
        if not update_existing:
            return {
                "term": existing_term,
                "match_type": "exact_match",
                "updated": False,
                "message": "Update disabled - term already exists",
            }

        # Check if update is needed
        cursor = await anyio.to_thread.run_sync(
            self.conn.execute,
            "SELECT definition, synonyms, is_red_flag FROM medical_dictionary WHERE term = ?",
            (existing_term,),
        )
        existing_data = await anyio.to_thread.run_sync(cursor.fetchone)

        if not existing_data:
            return {
                "term": existing_term,
                "match_type": "exact_match",
                "updated": False,
                "error": "Term found in matching but not in database",
            }

        # Check what needs updating
        updates = []
        params = []

        if term_info["definition"] and existing_data["definition"] != term_info["definition"]:
            updates.append("definition = ?")
            params.append(term_info["definition"])

        if term_info["synonyms"]:
            existing_synonyms = (
                json.loads(existing_data["synonyms"]) if existing_data["synonyms"] else []
            )
            if set(term_info["synonyms"]) != set(existing_synonyms):
                updates.append("synonyms = ?")
                params.append(json.dumps(term_info["synonyms"]))

        if term_info["is_red_flag"] != bool(existing_data["is_red_flag"]):
            updates.append("is_red_flag = ?")
            params.append(int(term_info["is_red_flag"]))

        if updates:
            params.append(existing_term)
            update_query = f"UPDATE medical_dictionary SET {', '.join(updates)}, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE term = ?"

            await anyio.to_thread.run_sync(self.conn.execute, update_query, params)

            return {
                "term": existing_term,
                "match_type": "exact_match",
                "updated": True,
                "updates_applied": updates,
                "definition": term_info["definition"],
                "synonyms": term_info["synonyms"],
                "is_red_flag": term_info["is_red_flag"],
            }
        else:
            return {
                "term": existing_term,
                "match_type": "exact_match",
                "updated": False,
                "message": "No updates needed",
            }

    def _find_spelling_suggestions(
        self, term: str, existing_terms_lower: dict[str, str], min_similarity: float
    ) -> list[dict[str, Any]]:
        """Find spelling suggestions for a term."""
        suggestions = []

        for existing_term_lower, existing_term in existing_terms_lower.items():
            similarity = SequenceMatcher(None, term, existing_term_lower).ratio()

            if similarity >= min_similarity:
                suggestions.append(
                    {
                        "suggested_term": existing_term,
                        "similarity": round(similarity, 3),
                        "confidence": "high"
                        if similarity >= 0.9
                        else "medium"
                        if similarity >= 0.8
                        else "low",
                    }
                )

        # Sort by similarity (highest first)
        suggestions.sort(key=lambda x: x["similarity"], reverse=True)

        return suggestions[:5]  # Return top 5 suggestions

    async def _create_new_term(self, term_info: dict[str, Any], row_idx: int) -> dict[str, Any]:
        """Create a new dictionary term."""
        try:
            # Insert new term
            await anyio.to_thread.run_sync(
                self.conn.execute,
                """
                INSERT INTO medical_dictionary (
                    term, definition, synonyms, is_red_flag,
                    avg_children_count, conflicts_count,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, 0, 0, strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                """,
                (
                    term_info["term"],
                    term_info["definition"],
                    json.dumps(term_info["synonyms"]),
                    int(term_info["is_red_flag"]),
                ),
            )

            return {
                "row": row_idx,
                "term": term_info["term"],
                "match_type": "new_term",
                "updated": True,
                "definition": term_info["definition"],
                "synonyms": term_info["synonyms"],
                "is_red_flag": term_info["is_red_flag"],
            }

        except sqlite3.IntegrityError:
            return {
                "row": row_idx,
                "term": term_info["term"],
                "match_type": "error",
                "error": "Term already exists (race condition)",
                "updated": False,
            }

    def _generate_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate a summary of the processing results."""
        total_processed = len(results["processed_terms"])
        errors = len(results["errors"])

        return {
            "total_terms_processed": total_processed,
            "exact_matches_found": results["matches_found"],
            "updates_applied": results["updates_applied"],
            "new_terms_created": results["new_terms_created"],
            "spelling_suggestions_found": len(results["spelling_suggestions"]),
            "errors_encountered": errors,
            "success_rate": round((total_processed - errors) / total_processed * 100, 1)
            if total_processed > 0
            else 0,
        }

    async def validate_dictionary_file(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """Validate a dictionary file before processing."""
        try:
            rows = await self._parse_dictionary_file(file_content, filename)
            analysis = await self._analyze_dictionary_structure(rows)

            validation_result = {
                "valid": analysis["file_structure_valid"],
                "analysis": analysis,
                "warnings": [],
                "errors": [],
            }

            if not analysis["file_structure_valid"]:
                validation_result["errors"].append("No term column detected in file")

            if analysis["total_rows"] == 0:
                validation_result["errors"].append("File contains no data")

            if analysis["total_rows"] > 10000:
                validation_result["warnings"].append(
                    "Large file detected - processing may take time"
                )

            return validation_result

        except Exception as e:
            return {"valid": False, "errors": [f"File validation failed: {str(e)}"], "warnings": []}
