from typing import Optional, Iterable, List, Any, Set
from dataclasses import dataclass
import io, csv, sqlite3
from fastapi import Response

@dataclass
class ExportOptions:
    fmt: str = "csv"
    max_depth: Optional[int] = None
    root_ids: Optional[Set[int]] = None
    root_labels: Optional[Set[str]] = None
    only_red: bool = False
    include_meta: bool = False
    filename: Optional[str] = None

class ExportEngine:
    """
    Class-based exporter for decision tree data.
    Keeps legacy defaults if options are not provided.
    """
    def __init__(self, conn: sqlite3.Connection, options: ExportOptions):
        self.conn = conn
        self.opt = options

    def export(self) -> Response:
        root_ids = self._resolve_root_ids()
        rows_iter = self._iter_rows(root_ids)
        if self.opt.fmt == "csv":
            return self._write_csv(rows_iter)
        elif self.opt.fmt == "xlsx":
            try:
                import xlsxwriter  # noqa: F401
            except Exception:
                # fallback to CSV if Excel writer isn't available
                self.opt.fmt = "csv"
                return self._write_csv(rows_iter)
            return self._write_xlsx(rows_iter)
        raise ValueError(f"Unsupported format: {self.opt.fmt}")

    # ---------- internals ----------
    def _resolve_root_ids(self) -> Set[int]:
        root_ids = set(self.opt.root_ids or [])
        if self.opt.root_labels:
            qmarks = ",".join("?" for _ in self.opt.root_labels)
            labels = [lbl.lower().strip() for lbl in self.opt.root_labels]
            for row in self.conn.execute(
                f"SELECT id FROM nodes WHERE depth=0 AND LOWER(TRIM(label)) IN ({qmarks})", labels
            ):
                root_ids.add(row[0])
        if not root_ids:
            rows = self.conn.execute("SELECT id FROM nodes WHERE depth=0").fetchall()
            root_ids = {r[0] for r in rows}
        return root_ids

    def _has_red_flags(self) -> bool:
        try:
            t = self.conn.execute(
                "SELECT 1 FROM sqlite_master WHERE (type='table' OR type='view') AND name='node_red_flags'"
            ).fetchone()
            return bool(t)
        except Exception:
            return False

    def _children_of(self, pid: int):
        if self.opt.only_red and self._has_red_flags():
            q = """
            SELECT c.id, c.parent_id, c.depth, c.slot, c.label, c.created_at, c.updated_at
            FROM nodes c
            JOIN node_red_flags nrf ON nrf.node_id = c.id
            WHERE c.parent_id = ?
            ORDER BY c.slot ASC
            """
            return self.conn.execute(q, (pid,)).fetchall()
        else:
            q = """
            SELECT id, parent_id, depth, slot, label, created_at, updated_at
            FROM nodes
            WHERE parent_id = ?
            ORDER BY slot ASC
            """
            return self.conn.execute(q, (pid,)).fetchall()

    def _iter_rows(self, root_ids: Set[int]) -> Iterable[List[Any]]:
        # fetch full root rows
        if not root_ids:
            return []
        q = f"""
        SELECT id, parent_id, depth, slot, label, created_at, updated_at
        FROM nodes
        WHERE id IN ({','.join('?' for _ in root_ids)})
        """
        roots = self.conn.execute(q, tuple(root_ids)).fetchall()
        from collections import deque
        for root in roots:
            queue = deque()
            queue.append((root, [None]*7))
            while queue:
                node, path = queue.popleft()
                nid, ppid, depth, slot, label, created, updated = node
                # place label in correct Dk
                if 0 <= depth <= 6:
                    path = path.copy()
                    path[depth] = label
                # stop by max_depth?
                if self.opt.max_depth is not None and depth >= self.opt.max_depth:
                    row = path + [""]
                    if self.opt.include_meta:
                        row += [nid, ppid, depth, slot, created, updated]
                    yield row
                    continue
                kids = self._children_of(nid)
                if not kids:
                    row = [(value or "") for value in path]
                    meta_row = self.conn.execute(
                        "SELECT d6, notes FROM path_meta WHERE leaf_id = ?",
                        (nid,),
                    ).fetchone()
                    notes_value = ""
                    if meta_row:
                        d6_value = meta_row[0] or ""
                        notes_value = meta_row[1] or ""
                        row[6] = d6_value or row[6]
                    row.append(notes_value)
                    if self.opt.include_meta:
                        row += [nid, ppid, depth, slot, created, updated]
                    yield row
                else:
                    for child in kids:
                        queue.append((child, path))

    def _csv_header(self) -> List[str]:
        header = ["D0","D1","D2","D3","D4","D5","D6","Notes"]
        if self.opt.include_meta:
            header += ["node_id","parent_id","depth","slot","created_at","updated_at"]
        return header

    def _write_csv(self, rows_iter: Iterable[List[Any]]) -> Response:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(self._csv_header())
        for row in rows_iter:
            writer.writerow(row)
        content = buf.getvalue().encode("utf-8")
        resp = Response(content, media_type="text/csv; charset=utf-8")
        fname = self.opt.filename or "lorien_export.csv"
        resp.headers["Content-Disposition"] = f'attachment; filename="{fname}"'
        return resp

    def _write_xlsx(self, rows_iter: Iterable[List[Any]]) -> Response:
        """
        Produce a *real* Excel workbook using xlsxwriter.
        - Bold header
        - Freeze header row
        - Auto-filter on header row
        - Reasonable column widths (best-effort, no heavy measurement)
        """
        import xlsxwriter
        buf = io.BytesIO()
        wb = xlsxwriter.Workbook(buf, {"in_memory": True})
        ws = wb.add_worksheet("Export")

        header = self._csv_header()

        # Formats
        fmt_header = wb.add_format({"bold": True})
        fmt_wrap = wb.add_format({"text_wrap": True})

        # Write header
        for c, name in enumerate(header):
            ws.write(0, c, name, fmt_header)

        # Data rows
        r = 1
        max_len = [len(h) for h in header]  # track rough widths
        for row in rows_iter:
            for c, val in enumerate(row):
                ws.write(r, c, val if val is not None else "", fmt_wrap if c >= 7 else None)
                ln = len(str(val)) if val is not None else 0
                if ln > max_len[c]:
                    max_len[c] = ln
            r += 1

        # Basic UX: freeze header, auto-filter
        ws.freeze_panes(1, 0)
        ws.autofilter(0, 0, max(0, r - 1), len(header) - 1)

        # Column widths: 1 char ~ 1 unit; cap to avoid huge columns
        for c, ln in enumerate(max_len):
            width = min(max(8, ln + 2), 60)
            ws.set_column(c, c, width)

        wb.close()
        buf.seek(0)
        content = buf.read()

        resp = Response(
            content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        fname = self.opt.filename or "lorien_export.xlsx"
        if not fname.lower().endswith(".xlsx"):
            fname = f"{fname}.xlsx"
        resp.headers["Content-Disposition"] = f'attachment; filename="{fname}"'
        return resp
