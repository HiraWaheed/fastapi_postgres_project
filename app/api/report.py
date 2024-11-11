import csv
from io import StringIO
import logging
from celery import Celery
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import app.models.candidate as CandidateModel
from app.database import SessionLocal

router = APIRouter()
celery = Celery(
    "tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)


@celery.task
def generate_report_task():
    """
    Function to generate report as a celery task
    """
    with SessionLocal() as db:

        try:
            logging.info("Generating report task started")
            candidates = db.query(CandidateModel.Candidate).all()
            if not candidates:
                return "No candidate profiles found."

            # Generate CSV content
            buffer = StringIO()
            writer = csv.writer(buffer)
            writer.writerow(["ID", "First Name", "Last Name", "Experience"])

            for candidate in candidates:
                writer.writerow(
                    [
                        candidate.id,
                        candidate.first_name,
                        candidate.last_name,
                        candidate.experience,
                    ]
                )

            # Save buffer content to a file
            report_path = "/tmp/candidates_report.csv"
            with open(report_path, "w") as file:
                file.write(buffer.getvalue())

            logging.info("Generating report task completed")
            return report_path

        finally:
            db.close()


@router.get("/generate-report")
def generate_report():
    """
    Endpoint to generate report
    Args:
        None
    Returns:
        dict: Dictionary with task id and a message
    """
    # Trigger the Celery task
    try:
        task = generate_report_task.delay()
        return {"task_id": task.id, "message": "Report generation started."}
    except Exception as e:
        logging.error(f"Error occurred at generate_report{e}")
        return "Something went wrong while generating report"


@router.get("/download-report/{task_id}")
def download_report(task_id: str):
    """
    Endpoint to download report
    Args:
        task_id (str)
    Returns:
        FileResponse: FileResponse of generated report
    """
    try:
        task_result = AsyncResult(task_id, app=celery)
        if task_result.status != "SUCCESS":
            raise HTTPException(status_code=404, detail="Report is not yet ready.")

        report_path = task_result.result
        return FileResponse(
            path=report_path, filename="candidates_report.csv", media_type="text/csv"
        )
    except Exception as e:
        logging.error(f"Error occurred at download_report{e}")
        return "Something went wrong while downloading report"
