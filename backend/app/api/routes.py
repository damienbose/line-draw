"""
API routes for the line-draw application.
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

logger = logging.getLogger(__name__)
from fastapi.responses import StreamingResponse
from PIL import Image
from io import BytesIO

from app.models.schemas import (
    UploadResponse,
    StartJobRequest,
    StartJobResponse,
    JobStatusResponse,
    JobStatus,
)
from app.services.job_manager import job_manager
from app.core.drawing import image_to_bytes

router = APIRouter()


@router.post("/images/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload an image for processing."""
    logger.info(f"Received image upload: {file.filename}, content_type={file.content_type}")

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        logger.info(f"Image opened: size={image.size}, mode={image.mode}")

        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')

        # Create job
        job_id = job_manager.create_job(image)
        logger.info(f"Job created: {job_id}")

        return UploadResponse(job_id=job_id)

    except Exception as e:
        logger.exception("Failed to process uploaded image")
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")


@router.post("/jobs/{job_id}/start", response_model=StartJobResponse)
async def start_job(job_id: str, request: StartJobRequest, background_tasks: BackgroundTasks):
    """Start processing a job with given parameters."""
    logger.info(f"Start job request: job_id={job_id}, params={request.params}")
    job = job_manager.get_job(job_id)

    if not job:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == JobStatus.PROCESSING:
        raise HTTPException(status_code=400, detail="Job is already processing")

    if job.status == JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is already completed")

    # Start processing in background
    logger.info(f"Adding run_job to background tasks for job {job_id}")
    background_tasks.add_task(job_manager.run_job, job_id, request.params)

    return StartJobResponse(status=JobStatus.PROCESSING)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a job."""
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result_url = f"/api/jobs/{job_id}/result" if job.status == JobStatus.COMPLETED else None

    return JobStatusResponse(
        job_id=job_id,
        status=job.status,
        progress=job.progress,
        result_url=result_url,
        error=job.error,
    )


@router.get("/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    """Get the result image for a completed job."""
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is not completed")

    if not job.result_image:
        raise HTTPException(status_code=404, detail="Result image not found")

    image_bytes = image_to_bytes(job.result_image)

    return StreamingResponse(
        BytesIO(image_bytes),
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=line-drawing-{job_id[:8]}.png"}
    )


@router.get("/jobs/{job_id}/result/base64")
async def get_job_result_base64(job_id: str):
    """Get the result image as base64."""
    job = job_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is not completed")

    base64_image = job_manager.get_result_image_base64(job_id)

    if not base64_image:
        raise HTTPException(status_code=404, detail="Result image not found")

    return {"image_base64": base64_image}


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job."""
    if job_manager.delete_job(job_id):
        return {"message": "Job deleted successfully"}
    raise HTTPException(status_code=404, detail="Job not found")
