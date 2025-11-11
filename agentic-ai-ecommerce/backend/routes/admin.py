from fastapi import APIRouter

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/dashboard")
async def dashboard():
    # Minimal: in real life, load from DB and analytics utils
    return {
        "analytics": {
            "total_users": 1,
            "total_orders": 1,
            "total_revenue": 0,
            "orders_this_week": 0
        },
        "message": "Admin dashboard (stub). Replace with real stats."
    }
