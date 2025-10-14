"""
Dictionary sync service for maintaining consistency between dictionary entries and tree nodes.
"""

import json
import sqlite3
from typing import Any, Optional

import anyio

from ..exceptions import ConflictError


class DictionarySyncService:
    """Service for maintaining bidirectional sync between dictionary and tree nodes."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    async def sync_dictionary_metrics(self, term: str) -> dict[str, Any]:
        """
        Update dictionary metrics (avg_children_count, conflicts_count) for a term.
        This is called when tree nodes are modified.
        """
        # Calculate average children count
        children_count = await anyio.to_thread.run_sync(self._calculate_children_count, term)

        # Calculate conflicts count
        conflicts_count = await anyio.to_thread.run_sync(self._calculate_conflicts_count, term)

        # Update dictionary entry
        cursor = await anyio.to_thread.run_sync(
            self.conn.execute,
            """
            UPDATE medical_dictionary
            SET
                avg_children_count = ?,
                conflicts_count = ?,
                updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
            WHERE LOWER(TRIM(term)) = LOWER(?)
            """,
            (children_count, conflicts_count, term),
        )

        if cursor.rowcount == 0:
            # Create dictionary entry if it doesn't exist
            await anyio.to_thread.run_sync(
                self.conn.execute,
                """
                INSERT INTO medical_dictionary (
                    term, definition, synonyms, is_red_flag,
                    avg_children_count, conflicts_count,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                """,
                (term, None, json.dumps([]), 0, children_count, conflicts_count),
            )

        return {
            "term": term,
            "avg_children_count": children_count,
            "conflicts_count": conflicts_count,
        }

    def _calculate_children_count(self, term: str) -> int:
        """Calculate the number of children for all nodes with this term."""
        cursor = self.conn.execute(
            """
            SELECT COUNT(*) as child_count
            FROM nodes n1
            JOIN nodes n2 ON n2.parent_id = n1.id
            WHERE LOWER(TRIM(n1.label)) = LOWER(?)
            """,
            (term,),
        )
        result = cursor.fetchone()
        return result["child_count"] if result else 0

    def _calculate_conflicts_count(self, term: str) -> int:
        """Calculate the number of conflicts for this term."""
        cursor = self.conn.execute(
            """
            SELECT COUNT(*) as occurrences
            FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(?)
            """,
            (term,),
        )
        result = cursor.fetchone()
        occurrences = result["occurrences"] if result else 0
        return max(0, occurrences - 1)

    async def sync_nodes_from_dictionary(
        self,
        old_term: str,
        new_term: str,
        definition: Optional[str] = None,
        synonyms: Optional[list[str]] = None,
        is_red_flag: Optional[bool] = None,
    ) -> dict[str, Any]:
        """
        Update tree nodes when dictionary term is modified.
        This is called when dictionary entries are updated.
        """
        # Check if the term change would cause conflicts
        if old_term != new_term:
            conflicts = await self._check_term_conflicts(new_term)
            if conflicts > 0:
                raise ConflictError(
                    f"Term '{new_term}' already exists in {conflicts} other nodes. "
                    "This would create additional conflicts."
                )

        # Update all nodes with the old term
        cursor = await anyio.to_thread.run_sync(
            self.conn.execute,
            """
            UPDATE nodes
            SET
                label = ?,
                updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
            WHERE LOWER(TRIM(label)) = LOWER(?)
            """,
            (new_term, old_term),
        )

        updated_nodes = cursor.rowcount

        # Sync red flag status if provided
        if is_red_flag is not None:
            await self._sync_red_flags(new_term, is_red_flag)

        return {
            "old_term": old_term,
            "new_term": new_term,
            "updated_nodes": updated_nodes,
            "synced_red_flags": is_red_flag is not None,
        }

    def _check_term_conflicts(self, term: str) -> int:
        """Check how many existing nodes would conflict with this term."""
        cursor = self.conn.execute(
            """
            SELECT COUNT(*) as conflicts
            FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(?)
            """,
            (term,),
        )
        result = cursor.fetchone()
        return result["conflicts"] if result else 0

    async def _sync_red_flags(self, term: str, is_red_flag: bool):
        """Sync red flag status between dictionary and tree nodes."""
        # Get all nodes with this term
        cursor = await anyio.to_thread.run_sync(
            self.conn.execute,
            """
            SELECT id FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(?)
            """,
            (term,),
        )
        node_ids = [row["id"] for row in cursor.fetchall()]

        if not node_ids:
            return

        # Note: The nodes table doesn't have an is_red_flag column
        # Red flags are managed through the edge_meta table

        # Also update edge_meta table for VM Builder compatibility
        for node_id in node_ids:
            # Get all parent-child relationships for this node
            cursor = await anyio.to_thread.run_sync(
                self.conn.execute,
                """
                SELECT parent_id FROM nodes WHERE id = ?
                """,
                (node_id,),
            )
            parent_row = await anyio.to_thread.run_sync(cursor.fetchone)

            if parent_row and parent_row[0]:
                parent_id = parent_row[0]

                # Update or insert edge_meta entry
                await anyio.to_thread.run_sync(
                    self.conn.execute,
                    """
                    INSERT INTO edge_meta(parent_id, child_id, red_flag)
                    VALUES(?, ?, ?)
                    ON CONFLICT(parent_id, child_id) DO UPDATE SET red_flag = excluded.red_flag
                    """,
                    (parent_id, node_id, 1 if is_red_flag else 0),
                )

        if is_red_flag:
            # Create or get red flag for this term
            cursor = await anyio.to_thread.run_sync(
                self.conn.execute,
                """
                INSERT OR IGNORE INTO red_flags (name, description, severity)
                VALUES (?, ?, ?)
                """,
                (
                    f"Dictionary Term: {term}",
                    f"Medical term flagged in dictionary: {term}",
                    "medium",
                ),
            )

            # Get the red flag ID
            cursor = await anyio.to_thread.run_sync(
                self.conn.execute,
                """
                SELECT id FROM red_flags
                WHERE name = ?
                """,
                (f"Dictionary Term: {term}",),
            )
            red_flag_row = cursor.fetchone()

            if red_flag_row:
                red_flag_id = red_flag_row["id"]

                # Add red flag associations
                for node_id in node_ids:
                    await anyio.to_thread.run_sync(
                        self.conn.execute,
                        """
                        INSERT OR IGNORE INTO node_red_flags (node_id, red_flag_id)
                        VALUES (?, ?)
                        """,
                        (node_id, red_flag_id),
                    )
        else:
            # Remove red flag associations for this term
            await anyio.to_thread.run_sync(
                self.conn.execute,
                """
                DELETE FROM node_red_flags
                WHERE node_id IN ({})
                AND red_flag_id IN (
                    SELECT id FROM red_flags
                    WHERE name = ?
                )
                """.format(",".join("?" * len(node_ids))),
                node_ids + [f"Dictionary Term: {term}"],
            )

    async def validate_dictionary_update(
        self,
        term_id: int,
        new_term: str,
        old_term: str,
    ) -> dict[str, Any]:
        """
        Validate that a dictionary update won't cause conflicts or issues.
        Returns validation results and warnings.
        """
        warnings = []
        errors = []

        # Check for term conflicts if term name is changing
        if old_term != new_term:
            conflicts = await self._check_term_conflicts(new_term)
            if conflicts > 0:
                errors.append(
                    f"Term '{new_term}' already exists in {conflicts} tree nodes. "
                    "This will create conflicts."
                )

        # Check if term exists in tree
        cursor = await anyio.to_thread.run_sync(
            self.conn.execute,
            """
            SELECT COUNT(*) as node_count
            FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(?)
            """,
            (old_term,),
        )
        result = cursor.fetchone()
        node_count = result["node_count"] if result else 0

        if node_count == 0:
            warnings.append(
                f"Term '{old_term}' is not currently used in the decision tree. "
                "Updating it will not affect any tree nodes."
            )
        else:
            warnings.append(
                f"Term '{old_term}' is used in {node_count} tree nodes. "
                "Updating it will affect all these nodes."
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "affected_nodes": node_count,
        }

    async def get_sync_status(self, term: str) -> dict[str, Any]:
        """
        Get the current sync status between dictionary and tree nodes for a term.
        """
        # Get dictionary entry
        cursor = await anyio.to_thread.run_sync(
            self.conn.execute,
            """
            SELECT * FROM medical_dictionary
            WHERE LOWER(TRIM(term)) = LOWER(?)
            """,
            (term,),
        )
        dict_row = cursor.fetchone()

        # Get tree nodes
        cursor = await anyio.to_thread.run_sync(
            self.conn.execute,
            """
            SELECT id, depth, slot, created_at, updated_at
            FROM nodes
            WHERE LOWER(TRIM(label)) = LOWER(?)
            ORDER BY depth, id
            """,
            (term,),
        )
        node_rows = cursor.fetchall()

        # Get red flag associations
        cursor = await anyio.to_thread.run_sync(
            self.conn.execute,
            """
            SELECT rf.name, rf.severity
            FROM node_red_flags nrf
            JOIN red_flags rf ON rf.id = nrf.red_flag_id
            WHERE nrf.node_id IN (
                SELECT id FROM nodes
                WHERE LOWER(TRIM(label)) = LOWER(?)
            )
            """,
            (term,),
        )
        red_flag_rows = cursor.fetchall()

        return {
            "term": term,
            "dictionary_exists": dict_row is not None,
            "dictionary_data": dict(dict_row) if dict_row else None,
            "tree_nodes": [dict(row) for row in node_rows],
            "red_flags": [dict(row) for row in red_flag_rows],
            "sync_status": {
                "in_dictionary": dict_row is not None,
                "in_tree": len(node_rows) > 0,
                "has_red_flags": len(red_flag_rows) > 0,
                "node_count": len(node_rows),
                "red_flag_count": len(red_flag_rows),
            },
        }
