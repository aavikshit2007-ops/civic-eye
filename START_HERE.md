# CIVIC EYE — Start Here

This package contains an autonomous civic monitoring demo. It runs camera inference locally and does not require an external AI API key.

## Requirements

- Windows 10 or 11
- Python 3.11 or newer
- A webcam
- Google Chrome or Microsoft Edge
- Internet access only for the initial Python package installation

Flutter is not required to run the included compiled web dashboard.

## First-time setup

Open PowerShell in the extracted `civic-eye` folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
pip install -r edge\requirements.txt
```

If PowerShell blocks activation, run this once in that terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Start the application

Use three separate PowerShell windows. Do not close them while using the app.

### Window 1 — API backend

```powershell
cd "PATH\TO\civic-eye"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8002
```

Wait for `Application startup complete`.

### Window 2 — Operations dashboard

```powershell
cd "PATH\TO\civic-eye"
.\.venv\Scripts\python.exe -m http.server 8080 --bind 127.0.0.1 --directory app\build\web
```

Open <http://127.0.0.1:8080>.

### Window 3 — Real camera AI

```powershell
cd "PATH\TO\civic-eye\edge"
$env:BACKEND_URL="http://127.0.0.1:8002"
$env:CAMERA_SOURCE="0"
$env:MOCK_DETECTION="false"
$env:SHOW_PREVIEW="true"
..\.venv\Scripts\python.exe -m app.main
```

The first model load can take one or two minutes on a CPU. A window named **CIVIC EYE - Autonomous Monitoring** will appear. Press `q` inside the camera window to stop it.

## Included local models

- `edge/models/civic_detector.pt` — pothole and garbage
- `edge/models/waterlogging_detector.pt` — flooded/waterlogged areas

Inference stays on the computer. Mock mode is disabled by default.

## Useful links

- Dashboard: <http://127.0.0.1:8080>
- API documentation: <http://127.0.0.1:8002/docs>
- Health check: <http://127.0.0.1:8002/health>

## Troubleshooting

- `Could not import module app.main`: use `--app-dir backend` or run Uvicorn from the `backend` directory.
- Camera unavailable: close Camera, Teams, Zoom, or browser tabs using the webcam.
- Wrong camera: change `$env:CAMERA_SOURCE="0"` to `"1"` or `"2"`.
- Dashboard says backend unavailable: confirm Window 1 is still running on port `8002`.
- Stop a server with `Ctrl+C`. Stop the camera by focusing its preview and pressing `q`.

