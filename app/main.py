import time
import uvicorn
from app.api import user, candidate, report
from fastapi import FastAPI, HTTPException, Depends


app = FastAPI()
start_time = time.time()


@app.get("/health")
def check_health():
    """Endpoint to check api health
    Args:
        None
    Returns:
        dict: Dictionary with api status,uptime in seconds and message description
    """
    uptime = round(time.time() - start_time, 2)
    return {
        "status": "ok",
        "uptime": f"{uptime} seconds",
        "message": "API is running healthy",
    }


app.include_router(user.router)
app.include_router(candidate.router)
app.include_router(report.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
