from tools.audit.check_dual_mount import run_check
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dual_mounts_present():
    res = run_check()
    assert res["ok"], (
        "Missing dual mounts for base paths:\n"
        + "\n".join(f" - {k} (bare={v['bare']}, v1={v['v1']})" for k, v in res["missing_dual_mounts"].items())
    )
