# Railway Production Environment Variables

Use this file as a copy-paste checklist when creating the Railway service.

## 1) Required variables

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
DEFAULT_ADMIN_PASSWORD=<strong_admin_password>

AUTH_COOKIE_NAME=df_session
AUTH_COOKIE_SECURE=true
AUTH_COOKIE_SAMESITE=none
AUTH_COOKIE_DOMAIN=
```

## 2) Set after Netlify first deploy

```bash
CORS_ALLOW_ORIGINS=https://<your-netlify-site>.netlify.app
CORS_ALLOW_ORIGIN_REGEX=
```

If you need Netlify preview domains, use regex:

```bash
CORS_ALLOW_ORIGIN_REGEX=https://.*--<your-netlify-site>\.netlify\.app
```

## 3) Minimal verification

1. Open `https://<your-railway-domain>/docs` and confirm FastAPI docs page loads.
2. Login from Netlify frontend and check API requests are 200 with cookies.
3. Confirm browser response headers include:
   - `Access-Control-Allow-Origin` exact Netlify origin
   - `Access-Control-Allow-Credentials: true`
