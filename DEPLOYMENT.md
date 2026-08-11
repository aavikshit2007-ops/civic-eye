# CIVIC EYE deployment

The backend deploys as a Render Blueprint from `render.yaml`. The compiled Flutter dashboard deploys as a static Vercel project. The camera remains on the vehicle/laptop and uploads to the public backend URL.

## Render backend

1. Push this repository to GitHub.
2. In Render, select **New → Blueprint** and connect the repository.
3. Apply the detected `render.yaml` Blueprint.
4. Record the resulting backend URL and verify `https://<render-host>/health`.

The Blueprint initially allows all CORS origins so the dashboard can be deployed afterward. Replace `CORS_ORIGINS` with the exact Vercel origin once it is known.

## Flutter web build

```powershell
cd app
C:\dev\flutter\bin\flutter.bat build web --release --no-wasm-dry-run --dart-define=API_URL=https://YOUR-RENDER-HOST.onrender.com
Copy-Item web\vercel.json build\web\vercel.json
```

## Vercel dashboard

Deploy `app/build/web` as the Vercel project root. With the CLI:

```powershell
cd app\build\web
npx vercel --prod
```

After deployment, set Render `CORS_ORIGINS` to the exact Vercel URL without a trailing slash and redeploy.

## Edge camera

```powershell
cd edge
$env:BACKEND_URL="https://YOUR-RENDER-HOST.onrender.com"
$env:CAMERA_SOURCE="0"
$env:MOCK_DETECTION="false"
$env:SHOW_PREVIEW="true"
..\.venv\Scripts\python.exe -m app.main
```

Before a demonstration, check `/health`, load the dashboard, confirm it does not show “Backend unavailable,” and submit one real camera observation.
