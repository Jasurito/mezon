# Mezon frontend (Next.js standalone). Build: docker compose build frontend
FROM node:24-alpine AS base
RUN corepack enable
WORKDIR /app

FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# mock = in-browser demo backend; live = real FastAPI under /api on the same origin
ARG NEXT_PUBLIC_API_MODE=mock
ARG NEXT_PUBLIC_SHOW_SKETCHES=true
# live mode only: show "Continue with Google" (true once GOOGLE_CLIENT_ID/SECRET are set in the backend env)
ARG NEXT_PUBLIC_GOOGLE_AUTH=false
ENV NEXT_PUBLIC_API_MODE=$NEXT_PUBLIC_API_MODE NEXT_PUBLIC_SHOW_SKETCHES=$NEXT_PUBLIC_SHOW_SKETCHES \
    NEXT_PUBLIC_GOOGLE_AUTH=$NEXT_PUBLIC_GOOGLE_AUTH NEXT_TELEMETRY_DISABLED=1
RUN pnpm build

FROM node:24-alpine AS run
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0 NEXT_TELEMETRY_DISABLED=1
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:3000/uz >/dev/null || exit 1
CMD ["node", "server.js"]
