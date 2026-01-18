"""
WebSocket handler for real-time progress updates.
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.job_manager import job_manager
from app.models.schemas import JobStatus

router = APIRouter()


@router.websocket("/ws/jobs/{job_id}")
async def websocket_job_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job progress updates."""
    await websocket.accept()

    job = job_manager.get_job(job_id)
    if not job:
        await websocket.send_json({"type": "error", "error": "Job not found"})
        await websocket.close()
        return

    try:
        # Send initial status
        await websocket.send_json({
            "type": "status",
            "status": job.status.value,
            "progress": job.progress
        })

        # If job is already completed, send result and close
        if job.status == JobStatus.COMPLETED:
            base64_image = job_manager.get_result_image_base64(job_id)
            await websocket.send_json({
                "type": "complete",
                "status": "completed",
                "image_base64": base64_image
            })
            await websocket.close()
            return

        # If job failed, send error and close
        if job.status == JobStatus.FAILED:
            await websocket.send_json({
                "type": "error",
                "error": job.error or "Unknown error"
            })
            await websocket.close()
            return

        # Listen for updates from the job queue
        while True:
            try:
                # Wait for message from job with timeout
                message = await asyncio.wait_for(
                    job.websocket_queue.get(),
                    timeout=1.0
                )

                await websocket.send_json(message)

                # If job is complete or failed, close connection
                if message.get("type") in ("complete", "error"):
                    break

            except asyncio.TimeoutError:
                # Check if job status changed
                if job.status == JobStatus.COMPLETED:
                    base64_image = job_manager.get_result_image_base64(job_id)
                    await websocket.send_json({
                        "type": "complete",
                        "status": "completed",
                        "image_base64": base64_image
                    })
                    break
                elif job.status == JobStatus.FAILED:
                    await websocket.send_json({
                        "type": "error",
                        "error": job.error or "Unknown error"
                    })
                    break

                # Send heartbeat to keep connection alive
                await websocket.send_json({
                    "type": "heartbeat",
                    "status": job.status.value,
                    "progress": job.progress
                })

    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
