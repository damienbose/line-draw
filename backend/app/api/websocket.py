"""
WebSocket handler for real-time progress updates.
"""

import asyncio
import logging
import queue
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.job_manager import job_manager
from app.models.schemas import JobStatus

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/jobs/{job_id}")
async def websocket_job_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job progress updates."""
    await websocket.accept()
    logger.info(f"WebSocket connected for job {job_id}")

    job = job_manager.get_job(job_id)
    if not job:
        logger.warning(f"WebSocket: job {job_id} not found")
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

        # Listen for updates from the job queue (thread-safe queue.Queue)
        heartbeat_counter = 0
        while True:
            # Try to get messages from queue (non-blocking)
            try:
                message = job.websocket_queue.get_nowait()
                await websocket.send_json(message)
                logger.debug(f"WebSocket sent message type={message.get('type')} for job {job_id}")

                # If job is complete or failed, close connection
                if message.get("type") in ("complete", "error"):
                    logger.info(f"WebSocket closing for job {job_id}: {message.get('type')}")
                    break

            except queue.Empty:
                # No message available, check job status and send heartbeat
                heartbeat_counter += 1

                if job.status == JobStatus.COMPLETED:
                    base64_image = job_manager.get_result_image_base64(job_id)
                    await websocket.send_json({
                        "type": "complete",
                        "status": "completed",
                        "image_base64": base64_image
                    })
                    logger.info(f"WebSocket: job {job_id} completed (status check)")
                    break
                elif job.status == JobStatus.FAILED:
                    await websocket.send_json({
                        "type": "error",
                        "error": job.error or "Unknown error"
                    })
                    logger.info(f"WebSocket: job {job_id} failed (status check)")
                    break

                # Send heartbeat every ~5 iterations (500ms)
                if heartbeat_counter >= 5:
                    await websocket.send_json({
                        "type": "heartbeat",
                        "status": job.status.value,
                        "progress": job.progress
                    })
                    heartbeat_counter = 0

                # Small sleep to avoid busy-waiting
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job {job_id}")
    finally:
        await websocket.close()
