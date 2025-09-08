from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/tree/conflicts", name="conflicts_root")
def conflicts_root():
    """
    Lightweight anchor route so clients/tests have a stable 'conflicts' base.
    Returns a minimal capability summary; detailed lists live under /tree/conflicts/*.
    """
    return JSONResponse({
        "ok": True,
        "endpoints": [
            "/tree/conflicts/group",
            "/tree/conflicts/group/resolve",
            "/tree/conflicts/duplicate-labels",
            "/tree/conflicts/depth-anomalies",
            "/tree/conflicts/orphans"
        ]
    })
