FROM node:24-alpine AS dependencies
WORKDIR /app
RUN corepack enable
COPY apps/web/package.json apps/web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM node:24-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN corepack enable
COPY --from=dependencies /app/node_modules ./node_modules
COPY apps/web ./
RUN pnpm build

EXPOSE 3000
CMD ["pnpm", "start"]
