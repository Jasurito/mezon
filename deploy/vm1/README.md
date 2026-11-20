# vm1 deployment (CI/CD + systemd)

```
GitHub Actions (.github/workflows/ci-cd.yml)
  changes ─┬─ frontend: pnpm i18n check, typecheck, lint, build
           ├─ backend:  pytest (Postgres 16 + pgvector service), docker build
           └─ deploy (main only, after green checks):
                rsync repo ──> deploy@vm1:/opt/mezon/src
                ssh deploy@vm1 sudo mezon-deploy --sha <sha> <backend|frontend|all>
vm1
  /usr/local/sbin/mezon-deploy   build image on the host, keep :previous, systemctl restart, health check, rollback
  systemd: mezon-db.service (Postgres) ─┐
           mezon-mongo.service (history) ┴> mezon-backend.service (127.0.0.1:8000)    mezon-frontend.service (127.0.0.1:3000)
  nginx:   https://mezon.modeus.cc  /api/* -> :8000, everything else -> :3000
```

Only the parts that changed are deployed: `frontend/**` → frontend, `backend/**`, `scenarios/**` and `legal_data/**` → backend, `deploy/**` → both.
To deploy by hand: Actions → **CI/CD** → **Run workflow**, then pick all, frontend or backend.

## Files

| Path | Where it goes on vm1 |
|---|---|
| `systemd/mezon-{db,mongo,backend,frontend}.service` | `/etc/systemd/system/` |
| `mezon-deploy` | `/usr/local/sbin/mezon-deploy` (root-owned; the `deploy` user may only `sudo` this) |
| `env/backend.env.example` | appended to `/etc/mezon/backend.env` (secrets, `chmod 600`, never in git) |
| `env/frontend.build.env.example` | `/etc/mezon/frontend.build.env` (`NEXT_PUBLIC_API_MODE=mock\|live`) |
| `nginx/mezon.modeus.cc.conf` | reference for `/etc/nginx/sites-available/mezon.modeus.cc` (certbot adds TLS) |
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

**Frontend → real backend.** Set `NEXT_PUBLIC_API_MODE=live` in `/etc/mezon/frontend.build.env`, then run `sudo mezon-deploy frontend` (the value is baked in at build time).
