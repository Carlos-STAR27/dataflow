# Start Now: Deploy Dataflow Digram with Netlify + Railway + TiDB

Target stack:
- Frontend: Netlify
- Backend: Railway (Docker)
- Database: TiDB Cloud

## 1) Prepare Git source

1. Push this project to GitHub.
2. Keep branch `main` as deploy branch.

## 2) Deploy backend on Railway

1. Railway -> New Project -> Deploy from GitHub Repo.
2. Select this repository.
3. Railway auto-detects root `Dockerfile`.
4. Set service env vars:

Quick option: copy from `RAILWAY_ENV_PRODUCTION.md`.

```bash
DB_HOST=<tidb_host>
DB_PORT=4000
DB_USER=<tidb_user>
DB_PASSWORD=<tidb_password>
DB_NAME=dataflow_digram

DB_SSL_CA=/etc/ssl/certs/ca-certificates.crt
DB_SSL_DISABLED=false
DB_SSL_VERIFY_CERT=true
DB_SSL_VERIFY_IDENTITY=true

DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=<strong_password>

AUTH_COOKIE_NAME=df_session
AUTH_COOKIE_SECURE=true
AUTH_COOKIE_SAMESITE=none
AUTH_COOKIE_DOMAIN=

# Fill after Netlify URL is ready
CORS_ALLOW_ORIGINS=
CORS_ALLOW_ORIGIN_REGEX=
```

5. Deploy and copy backend URL, e.g. `https://dataflow-api-production.up.railway.app`.

## 3) Deploy frontend on Netlify

1. Netlify -> Add new site -> Import an existing project.
2. Select the same GitHub repository.
3. `netlify.toml` will be picked automatically:
   - Build command: empty
   - Publish directory: `frontend-prototype`
4. Deploy and copy site URL, e.g. `https://dataflow-digram.netlify.app`.

## 4) Backfill cross-origin and API base

1. In Railway, set:

```bash
CORS_ALLOW_ORIGINS=https://dataflow-digram.netlify.app
```

2. Edit `frontend-prototype/runtime-config.js`:

```js
window.__DATAFLOW_API_BASE__ = "https://dataflow-api-production.up.railway.app";
```

3. Commit and push. Netlify will redeploy automatically.

## 5) Verify

1. Open Netlify URL.
2. Login with admin account.
3. Confirm API calls return 200 and include cookie.
4. Check backend docs URL: `https://<railway-domain>/docs`.

## 6) Typical failure checks

1. 401 after login:
   - `AUTH_COOKIE_SECURE=true`
   - `AUTH_COOKIE_SAMESITE=none`
   - exact `CORS_ALLOW_ORIGINS`
2. CORS blocked:
   - frontend origin not matching exactly.
3. DB connect error:
   - TiDB host/port/user/password or TLS flags mismatch.
