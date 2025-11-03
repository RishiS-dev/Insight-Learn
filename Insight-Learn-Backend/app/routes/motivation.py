from fastapi import APIRouter, Depends, HTTPException
from app.services.motivation_service import get_today_quote
try:
    # If your project protects dashboard routes, keep auth; otherwise remove this import and the Depends.
    from app.utils.auth_dependency import get_current_user
    AuthDep = get_current_user
except Exception:
    # Fallback to no-auth if your project doesn’t use it here
    def AuthDep():
        return {"id": 0}

router = APIRouter(prefix="/motivation", tags=["Motivation"])

@router.get("/today")
def motivation_today(user = Depends(AuthDep)):
    try:
        q = get_today_quote()
        return {"quote": q}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))