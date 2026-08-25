FROM node:22-alpine AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# Stage 1: Install dependencies
FROM base AS deps
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web-portal/package.json ./apps/web-portal/
RUN pnpm install --frozen-lockfile

# Stage 2: Build
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/web-portal/node_modules ./apps/web-portal/node_modules
COPY . .
RUN pnpm --filter @myolab-ai/web-portal run build

# Stage 3: Runner
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3100

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/apps/web-portal/node_modules ./apps/web-portal/node_modules
COPY --from=builder /app/apps/web-portal/.next ./apps/web-portal/.next
COPY --from=builder /app/apps/web-portal/public ./apps/web-portal/public
COPY --from=builder /app/apps/web-portal/package.json ./apps/web-portal/package.json
COPY --from=builder /app/package.json ./package.json

EXPOSE 3100

CMD ["node", "apps/web-portal/node_modules/next/dist/bin/next", "start", "apps/web-portal", "--port", "3100"]
