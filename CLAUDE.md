# Line Draw

A physics-based image-to-drawing tool that transforms images into line art by simulating a ball rolling on a 3D surface.

## How It Works

The algorithm treats an image as a 3D height map (grayscale values = elevation). A simulated ball rolls down this surface following physics rules, and its trajectory produces the line drawing.

Key physics:
- Gravity constant: `G = -1e-6`
- Image is inverted (dark areas become peaks)
- Gaussian blur smooths the surface
- A paraboloid gradient filter prevents dead zones
- Ball bounces off boundaries

## Project Structure

```
line-draw/
├── experiments/          # Original Jupyter notebooks and utils
├── frontend/             # React + Vite + TypeScript + Tailwind
│   └── src/
│       ├── components/   # ImageUploader, ParameterControls, ProcessingView, ResultDisplay
│       ├── hooks/        # useWebSocket for real-time progress
│       └── lib/          # API client
├── backend/              # FastAPI + uv
│   └── app/
│       ├── api/          # REST routes + WebSocket
│       ├── core/         # simulation.py (physics), drawing.py (rendering)
│       ├── models/       # Pydantic schemas
│       └── services/     # job_manager.py
```

## Running the App

**Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Frontend runs on http://localhost:5173, proxies `/api` to backend.

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/images/upload` | POST | Upload image, returns `job_id` |
| `/api/jobs/{id}/start` | POST | Start processing with params |
| `/api/jobs/{id}` | GET | Get job status and progress |
| `/api/jobs/{id}/result` | GET | Download result PNG |
| `/api/ws/jobs/{id}` | WS | Real-time progress updates |

## Key Parameters

- `blur_sigma` (1-20): Higher = smoother, more abstract lines
- `iterations` (100K-3M): More = more detail, takes longer
- `start_x`, `start_y` (0-1): Ball starting position

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Framer Motion, react-dropzone
- **Backend**: FastAPI, uvicorn, Pillow, NumPy
- **Package Management**: npm (frontend), uv (backend)

## Key Files

- `backend/app/core/simulation.py` - Physics engine, `PhysicsSimulator` class
- `backend/app/services/job_manager.py` - Job lifecycle, async processing
- `frontend/src/hooks/useWebSocket.ts` - WebSocket connection for progress
- `frontend/src/App.tsx` - Main app state machine (upload → configure → processing → result)
