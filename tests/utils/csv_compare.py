from __future__ import annotations
import csv
from typing import List


def _read_csv(path: str) -> List[List[str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        return [row for row in reader]


def assert_csv_equal(
    got_path: str,
    expected_path: str,
    *,
    ignore_row_order: bool = False,
    message: str | None = None,
) -> None:
    """
    Compares two CSV files.
    - Headers must match EXACTLY.
    - Body rows compared in-order by default; set ignore_row_order=True to sort.
    """
    got = _read_csv(got_path)
    exp = _read_csv(expected_path)
    assert got, f"{got_path} is empty"
    assert exp, f"{expected_path} is empty"

    got_header, exp_header = got[0], exp[0]
    assert got_header == exp_header, (
        message or f"CSV header mismatch:\n  got: {got_header}\n  exp: {exp_header}"
    )

    got_body, exp_body = got[1:], exp[1:]
    if ignore_row_order:
        assert sorted(got_body) == sorted(exp_body), (
            message or f"CSV body mismatch (order-insensitive)"
        )
    else:
        assert got_body == exp_body, (
            message or f"CSV body mismatch (order-sensitive)"
        )
