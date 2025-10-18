#!/usr/bin/env python3
"""
Simple server for testing pathogen endpoints with Flutter app.
"""

import json
import sqlite3
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Engines.EngineShelob import apply_import, ingest_file


class PathogenAPIHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for testing pathogen API endpoints."""

    def __init__(self, *args, **kwargs):
        # Get database path
        try:
            from api.settings import get_db_path

            self.db_path = get_db_path()
        except Exception:
            # Use temp database if API settings fail
            self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
            self.db_path = self.temp_db.name
            self.temp_db.close()
            self._create_temp_schema()
        super().__init__(*args, **kwargs)

    def _create_temp_schema(self):
        """Create temporary database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pathogens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    classification TEXT,
                    nt TEXT,
                    pathogen_id TEXT,
                    pathogen_name TEXT NOT NULL,
                    vaccine TEXT,
                    toxin TEXT,
                    transmission TEXT,
                    ab_resistance TEXT,
                    host TEXT,
                    commensal TEXT,
                    disease TEXT,
                    incubation TEXT,
                    diagnosis TEXT,
                    treatment TEXT,
                    prevention TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS association_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pathogen_associations (
                    pathogen_id INTEGER NOT NULL,
                    association_type_id INTEGER NOT NULL,
                    value INTEGER NOT NULL CHECK(value IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    PRIMARY KEY (pathogen_id, association_type_id),
                    FOREIGN KEY (pathogen_id) REFERENCES pathogens(id) ON DELETE CASCADE,
                    FOREIGN KEY (association_type_id) REFERENCES association_types(id) ON DELETE CASCADE
                )
            """
            )
            conn.commit()

    def _send_json_response(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == "/api/v1/health":
            self._handle_health()
        elif path == "/api/v1/pathogens/":
            self._handle_list_pathogens(query)
        elif path.startswith("/api/v1/pathogens/") and path.endswith("/associations"):
            pathogen_id = int(path.split("/")[-2])
            self._handle_get_associations(pathogen_id)
        elif path == "/api/v1/pathogens/association-types/":
            self._handle_list_association_types()
        elif path == "/api/v1/pathogens/stats/summary":
            self._handle_get_stats()
        elif path.startswith("/api/v1/pathogens/"):
            try:
                pathogen_id = int(path.split("/")[-1])
                self._handle_get_pathogen(pathogen_id)
            except ValueError:
                self._send_json_response({"error": "Invalid pathogen ID"}, 400)
        else:
            self._send_json_response({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        if self.path == "/api/v1/pathogens/import":
            self._handle_import_pathogens()
        else:
            self._send_json_response({"error": "Not found"}, 404)

    def _handle_health(self):
        """Handle health check."""
        health_data = {
            "ok": True,
            "version": "1.0.0",
            "service": "Lorien API",
            "pathogen_engine": "EngineShelob",
            "database": "SQLite",
            "checked_at": "2025-01-27T15:00:00Z",
        }
        self._send_json_response(health_data)

    def _handle_list_pathogens(self, query):
        """List pathogens with optional search and pagination."""
        limit = int(query.get("limit", ["100"])[0])
        offset = int(query.get("offset", ["0"])[0])
        search = query.get("search", [None])[0]

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if search:
                cursor.execute(
                    "SELECT * FROM pathogens WHERE pathogen_name LIKE ? ORDER BY pathogen_name LIMIT ? OFFSET ?",
                    (f"%{search}%", limit, offset),
                )
            else:
                cursor.execute(
                    "SELECT * FROM pathogens ORDER BY pathogen_name LIMIT ? OFFSET ?",
                    (limit, offset),
                )

            rows = cursor.fetchall()
            pathogens = [dict(row) for row in rows]

        self._send_json_response(pathogens)

    def _handle_get_pathogen(self, pathogen_id):
        """Get a single pathogen with associations."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get pathogen
            cursor.execute("SELECT * FROM pathogens WHERE id = ?", (pathogen_id,))
            pathogen_row = cursor.fetchone()

            if not pathogen_row:
                self._send_json_response({"error": "Pathogen not found"}, 404)
                return

            # Get associations
            cursor.execute(
                """
                SELECT at.name as association_type, pa.value
                FROM pathogen_associations pa
                JOIN association_types at ON pa.association_type_id = at.id
                WHERE pa.pathogen_id = ?
            """,
                (pathogen_id,),
            )
            association_rows = cursor.fetchall()

            associations = [
                {"association_type": row["association_type"], "value": row["value"]}
                for row in association_rows
            ]

            pathogen_data = dict(pathogen_row)
            pathogen_data["associations"] = associations

            self._send_json_response(pathogen_data)

    def _handle_get_associations(self, pathogen_id):
        """Get associations for a specific pathogen."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Verify pathogen exists
            cursor.execute("SELECT id FROM pathogens WHERE id = ?", (pathogen_id,))
            if not cursor.fetchone():
                self._send_json_response({"error": "Pathogen not found"}, 404)
                return

            # Get associations
            cursor.execute(
                """
                SELECT at.name as association_type, pa.value
                FROM pathogen_associations pa
                JOIN association_types at ON pa.association_type_id = at.id
                WHERE pa.pathogen_id = ?
            """,
                (pathogen_id,),
            )
            rows = cursor.fetchall()

            associations = [
                {"association_type": row["association_type"], "value": row["value"]} for row in rows
            ]

            self._send_json_response(associations)

    def _handle_list_association_types(self):
        """List all association types."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM association_types ORDER BY name")
            rows = cursor.fetchall()
            types = [row[0] for row in rows]

        self._send_json_response(types)

    def _handle_get_stats(self):
        """Get pathogen statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get pathogen count
            cursor.execute("SELECT COUNT(*) FROM pathogens")
            pathogen_count = cursor.fetchone()[0]

            # Get association type count
            cursor.execute("SELECT COUNT(*) FROM association_types")
            association_type_count = cursor.fetchone()[0]

            # Get total associations count
            cursor.execute("SELECT COUNT(*) FROM pathogen_associations")
            total_associations = cursor.fetchone()[0]

            # Get pathogens with associations count
            cursor.execute("SELECT COUNT(DISTINCT pathogen_id) FROM pathogen_associations")
            pathogens_with_associations = cursor.fetchone()[0]

            stats = {
                "total_pathogens": pathogen_count,
                "total_association_types": association_type_count,
                "total_associations": total_associations,
                "pathogens_with_associations": pathogens_with_associations,
                "pathogens_without_associations": pathogen_count - pathogens_with_associations,
            }

        self._send_json_response(stats)

    def _handle_import_pathogens(self):
        """Import pathogen data from uploaded file."""
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)

        # Parse multipart form data (simplified)
        boundary = self.headers["Content-Type"].split("boundary=")[1]
        parts = post_data.split(f"--{boundary}".encode())

        file_content = None
        for part in parts:
            if b"filename=" in part:
                # Extract file content
                file_start = part.find(b"\r\n\r\n") + 4
                file_end = part.rfind(b"\r\n")
                file_content = part[file_start:file_end]
                break

        if not file_content:
            self._send_json_response({"error": "No file uploaded"}, 400)
            return

        try:
            # Ingest file
            ingested_data = ingest_file(file_content, "uploaded_file.csv")

            if not ingested_data["success"]:
                self._send_json_response(
                    {"success": False, "errors": ingested_data.get("errors", [])}, 400
                )
                return

            # Apply import
            result = apply_import(self.db_path, ingested_data)

            response = {
                "success": len(result.errors) == 0,
                "pathogens_processed": result.pathogens_processed,
                "pathogens_created": result.pathogens_created,
                "pathogens_updated": result.pathogens_updated,
                "associations_processed": result.associations_processed,
                "associations_created": result.associations_created,
                "errors": result.errors,
                "warnings": result.warnings,
            }

            self._send_json_response(response)

        except Exception as e:
            self._send_json_response({"error": f"Import failed: {str(e)}"}, 500)


def main():
    """Start the test server."""
    port = 8000
    server = HTTPServer(("localhost", port), PathogenAPIHandler)
    print(f"🚀 Lorien Pathogen API Server running on http://localhost:{port}")

    # Get database path for display
    try:
        from api.settings import get_db_path

        db_path = get_db_path()
    except Exception:
        db_path = "temporary database"
    print(f"📁 Database: {db_path}")

    print("\nAvailable endpoints:")
    print(f"  GET  http://localhost:{port}/api/v1/health")
    print(f"  GET  http://localhost:{port}/api/v1/pathogens/")
    print(f"  GET  http://localhost:{port}/api/v1/pathogens/1")
    print(f"  GET  http://localhost:{port}/api/v1/pathogens/1/associations")
    print(f"  GET  http://localhost:{port}/api/v1/pathogens/association-types/")
    print(f"  GET  http://localhost:{port}/api/v1/pathogens/stats/summary")
    print(f"  POST http://localhost:{port}/api/v1/pathogens/import")
    print(
        f"\n📄 Test with: curl -F 'file=@sample_pathogens.csv' http://localhost:{port}/api/v1/pathogens/import"
    )
    print("\nPress Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()


if __name__ == "__main__":
    main()
