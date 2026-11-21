# vm1 deployment (CI/CD + systemd)

```
GitHub Actions (.github/workflows/ci-cd.yml)
  changes ── deploy (main only):
               rsync repo ──> deploy@vm1:/opt/mezon/src
               ssh deploy@vm1 sudo mezon-deploy --sha <sha> <backend|frontend|all>   (health check + auto rollback)
  No test jobs in CI (team decision for deploy speed). Run them locally before pushing:
  frontend: pnpm i18n && pnpm typecheck && pnpm build    backend: make test
vm1
  /usr/local/sbin/mezon-deploy   build image on the host, keep :previous, systemctl restart, health check, rollback
  systemd: mezon-db.service (Postgres) ─┐
           mezon-mongo.service (history) ┴> mezon-backend.service (127.0.0.1:8000)    mezon-frontend.service (127.0.0.1:3000)
  docker compose: /opt/mezon/storage (RustFS S3, container mezon-storage, 127.0.0.1:9000 API / :9001 console)
  nginx:   https://mezon.modeus.cc  /api/* -> :8000, /audio/*.mp3 -> bucket mezon-audio, everything else -> :3000
```

Only the parts that changed are deployed: `frontend/**` → frontend, `backend/**`, `scenarios/**` and `legal_data/**` → backend, `deploy/**` → both.
To deploy by hand: Actions → **CI/CD** → **Run workflow**, then pick all, frontend or backend.

## Files

| Path | Where it goes on vm1 |
|---|---|
| `systemd/mezon-{db,mongo,backend,frontend}.service` | `/etc/systemd/system/` |
| `mezon-deploy` | `/usr/local/sbin/mezon-deploy` (root-owned; the `deploy` user may only `sudo` this) |
| `env/backend.env.example` | appended to `/etc/mezon/backend.env` (secrets, `chmod 600`, never in git) |
| `env/frontend.build.env.example` | `/etc/mezon/frontend.build.env` (`NEXT_PUBLIC_API_MODE=mock\|live`, `NEXT_PUBLIC_GOOGLE_AUTH`); missing keys are appended |
| `nginx/mezon.modeus.cc.conf` | reference for `/etc/nginx/sites-available/mezon.modeus.cc` (certbot adds TLS) |
| `storage/docker-compose.yml`, `storage/mezon-audio.policy.json` | `/opt/mezon/storage/` (RustFS; root credentials in `/etc/mezon/storage.env`). Official MinIO images are no longer published, RustFS is S3-compatible |
| `bootstrap.sh` | one-time setup, idempotent |

CI only syncs source code. **Changes to units or `mezon-deploy` need a root re-run of `bootstrap.sh`** on vm1. That is on purpose: CI can't change what runs as root.

## One-time setup (already done on vm1, 2026-11-20)

```bash
# on your machine: a dedicated deploy key
ssh-keygen -t ed25519 -N '' -C mezon-ci-deploy -f mezon_ci
scp -r deploy/vm1 root@vm1.modeus.cc:/root/mezon-bootstrap
ssh root@vm1.modeus.cc "bash /root/mezon-bootstrap/bootstrap.sh '$(cat mezon_ci.pub)'"

# GitHub (repo → Settings → Secrets and variables → Actions): secret VM1_SSH_KEY, variable VM1_KNOWN_HOSTS
gh secret set VM1_SSH_KEY -R Jasurito/mezon < mezon_ci
ssh-keyscan -t ed25519,ecdsa,rsa vm1.modeus.cc 2>/dev/null | gh variable set VM1_KNOWN_HOSTS -R Jasurito/mezon
rm mezon_ci
```

Without the key or the known hosts the deploy job is skipped with a warning (CI still runs). The host (`vm1.modeus.cc`) and the user (`deploy`) are set in the workflow.

## Operations

```bash
systemctl status mezon-db mezon-mongo mezon-backend mezon-frontend
journalctl -u mezon-backend -f                      # logs (container stdout goes to journald)
sudo mezon-deploy all                               # rebuild + restart from /opt/mezon/src
sudo nano /etc/mezon/backend.env && sudo systemctl restart mezon-backend   # e.g. set ANTHROPIC_API_KEY
docker exec -it mezon-db psql -U mezon mezon         # Postgres shell
docker exec -it mezon-mongo mongosh -u mezon -p "$(sudo sed -n 's/^MONGO_INITDB_ROOT_PASSWORD=//p' /etc/mezon/mongo.env)"   # Mongo shell
```

**Rollback.** Every deploy tags the running image as `:previous` first. If the new one fails its health check (`/uz` for the frontend, `/api/health` for the backend), `mezon-deploy` switches back automatically. To roll back by hand:
`docker tag mezon-backend:previous mezon-backend:latest && systemctl restart mezon-backend`.

**Data.** Postgres data is in the docker volume `mezon-pgdata` and MongoDB data in `mezon-mongodata`. Both survive container restarts, redeploys and reboots, but a volume is not a backup:
`docker exec mezon-db pg_dump -U mezon mezon | gzip > pg-$(date +%F).sql.gz` and `docker exec mezon-mongo mongodump -u mezon -p … --authenticationDatabase admin --archive --gzip > mongo-$(date +%F).gz`.

**Accounts.** The backend owns sign-in (`/api/auth/*`, cookie `mezon_session`). Production values live in
`/etc/mezon/backend.env` (the template lists them all):

| Setting | Value on vm1 | Why |
|---|---|---|
| `PUBLIC_BASE_URL` | `https://mezon.modeus.cc` | redirect after sign-in, Google redirect URI, and the CSRF check: POSTs from any other `Origin` get 403 `CSRF_FAILED` |
| `COOKIE_SECURE` | `true` | session cookie only over https |
| `TRUST_PROXY_HEADERS` | `true` | the backend listens on 127.0.0.1 behind nginx, which appends the client IP to `X-Forwarded-For`; without it every client is "127.0.0.1" for the rate limits |
| `AUTH_IP_MAX_REQUESTS` | `120` per 15 min | above the code default (30): the jury and the venue share one Wi-Fi address |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | empty | Google sign-in is off (503) until set |

To turn on Google sign-in: create a Web OAuth client in Google Cloud with the redirect URI
`https://mezon.modeus.cc/api/auth/google/callback`, put the id and secret in `/etc/mezon/backend.env`,
`systemctl restart mezon-backend`, then set `NEXT_PUBLIC_GOOGLE_AUTH=true` in `/etc/mezon/frontend.build.env` and run
`sudo mezon-deploy frontend` (the button is hidden until then). Failed Google sign-ins come back to `/?auth_error=google`
and the site explains what happened.

**AI (LLM on the GPU server).** Ollama (`gemma3:27b` + `bge-m3`) runs on a vast.ai RTX 3090 and listens only on
`127.0.0.1:11434` there. `mezon-llm-tunnel.service` keeps an SSH tunnel to it and exposes it on the docker0 address
of vm1 (`172.17.0.1:11435`), so the backend uses `OLLAMA_URL=http://host.docker.internal:11435`; nothing is public.

| File | Role |
|---|---|
| `/etc/mezon/llm-tunnel.key` | key used only for the tunnel; on the GPU server it is restricted (`restrict,port-forwarding,permitopen="127.0.0.1:11434",command=...`: no shell) |
| `/etc/mezon/llm-tunnel.known_hosts` | pinned ED25519 host key of the GPU server (check the fingerprint before writing it) |
| `/etc/mezon/llm-tunnel.env` | `GPU_HOST`, `GPU_PORT`, `GPU_USER`, `TUNNEL_BIND` (docker0), `TUNNEL_PORT` (template: `env/llm-tunnel.env.example`) |

Backend settings for it: `LLM_PROVIDER=ollama`, `OLLAMA_URL=http://host.docker.internal:11435`,
`OLLAMA_MODEL=gemma3:27b`, `EMBEDDER=ollama-bge-m3`; `/api/health` then shows `llm_configured: true` and the embedder.
Check: `systemctl status mezon-llm-tunnel`, `curl -s http://172.17.0.1:11435/api/version`.

**When vast.ai recreates the instance** (new IP/port): update `/etc/mezon/llm-tunnel.env`, rescan and verify the host
key (`ssh-keyscan -p <port> <ip> | grep ssh-ed25519 > /etc/mezon/llm-tunnel.known_hosts; ssh-keygen -lf …`), add
`/etc/mezon/llm-tunnel.key.pub` with the restriction above to `~/.ssh/authorized_keys` on the new instance, then
`systemctl restart mezon-llm-tunnel`. While the tunnel is down the site keeps working without AI (mentor shows sources,
NPCs use scripted lines).

**Frontend → real backend.** Set `NEXT_PUBLIC_API_MODE=live` in `/etc/mezon/frontend.build.env`, then run `sudo mezon-deploy frontend` (the value is baked in at build time).
