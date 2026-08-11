# CIVIC EYE

Autonomous, offline-first civic issue monitoring for vehicle cameras. CIVIC EYE continuously observes the road, runs a local YOLO-compatible vision model, confirms detections across frames, captures its own evidence, attaches GPS/time/vehicle metadata, and consolidates observations into real-world issues. There is no citizen complaint or manual photo workflow.

## End-to-end workflow

```text
Camera / RTSP / video → local inference → temporal gate → best frame
  → SQLite offline queue → FastAPI → geo/time issue matching → operations UI
  → assigned → in progress → pending verification
  → independent vehicle pass → verified resolved OR reopened
```

The repository contains:

- `edge/`: OpenCV capture, local Ultralytics model adapter, mock detector, evidence capture, GPS abstraction, temporal gate, and SQLite uploader queue.
- `backend/`: FastAPI, SQLAlchemy domain model, lifecycle and verification rules, local media, and PostgreSQL-ready configuration.
- `app/`: responsive Flutter/Riverpod operations client for mobile and web.
- `docker-compose.yml`: PostGIS database and API service.

## Quick demo (Windows PowerShell)

### 1. Backend, immediate SQLite mode

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

Open `http://localhost:8002/docs` or `http://localhost:8002/health`.

For PostgreSQL/PostGIS instead:

```powershell
docker compose up -d db
Copy-Item backend\.env.example backend\.env
# Set DATABASE_URL=postgresql+psycopg://civic_eye:civic_eye_dev@localhost:5432/civic_eye
cd backend
uvicorn app.main:app --reload --port 8002
```

`docker compose up --build` runs both database and API. Development credentials are compose-only defaults; change them outside a local demo.

### 2. Flutter operations client

```powershell
cd app
flutter pub get
flutter run -d chrome --dart-define=API_URL=http://localhost:8002
```

For Android emulator use `--dart-define=API_URL=http://10.0.2.2:8002`. The client polls every five seconds, so new autonomous detections appear without refresh.

### 3. Edge camera

```powershell
cd edge
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.main
```

Mock detection is enabled in the example configuration. It generates a temporally confirmed pothole observation from the live camera, automatically saves the best frame, and uploads it. There is no capture button. Change `CAMERA_SOURCE` to a USB index, RTSP URL, or MP4 path, or run:

```powershell
python -m app.main --source test_data\test.mp4
```

Press `q` only to stop the technical preview.

## Production checkpoint

Place a trained YOLO-compatible checkpoint at `edge/models/civic_detector.pt`, set `MOCK_DETECTION=false`, and ensure its labels map to `waste`/`garbage`/`trash`, `pothole`, or `waterlogging`/`flooded`. The app never downloads a model. All inference remains local and requires no external AI API key.

Important edge settings live in one `.env`: confidence threshold, per-class minimum frames, cooldown, source, model, vehicle, backend, mock GPS, and preview. Offline events remain in `edge/data/offline_queue.db` and retry in the background.

## API overview

- `GET /health`
- `POST /api/v1/detections` (multipart evidence + metadata)
- `GET /api/v1/issues`, `/issues/{id}`, `/issues/map`
- `PATCH /api/v1/issues/{id}`
- `GET /api/v1/issues/verification-targets`
- `POST /api/v1/issues/{id}/verify`
- `GET /api/v1/dashboard/stats`
- `GET /api/v1/vehicles`, `POST /api/v1/vehicles/heartbeat`
- `GET /media/{generated-filename}`

Evidence filenames are server-generated. Upload type/size and coordinate/confidence values are validated. CORS and credentials are environment-driven; the service boundary is ready for OIDC/JWT middleware later.

## Lifecycle demo

1. Let mock/local inference create an issue and open it from the dashboard.
2. Use the issue action to assign it, start work, then mark work complete.
3. The system enters `PENDING_VERIFICATION`, never directly resolved.
4. Submit a vehicle result to `/api/v1/issues/{id}/verify` with `ISSUE_NOT_PRESENT` to reach `VERIFIED_RESOLVED`, or `ISSUE_PRESENT` to reach `REOPENED`.

## Tests

```powershell
cd backend; pytest
cd ..\edge; pytest
```

The backend defaults to SQLite for a zero-setup demo. PostgreSQL is supported through `DATABASE_URL`; the matching service deliberately uses portable Haversine distance in this MVP so behavior is identical in local tests. A production migration can replace the query boundary with `ST_DWithin` while retaining the same domain logic.
