# Use Debian/glibc rather than Alpine/musl: Next.js and its native dependency
# tree are more reliable there during container builds.
FROM node:22-bookworm-slim AS dependencies
WORKDIR /app
RUN corepack enable
COPY apps/web/package.json apps/web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM node:22-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN corepack enable
COPY --from=dependencies /app/node_modules ./node_modules
COPY apps/web ./
RUN pnpm build

EXPOSE 3000
CMD ["pnpm", "start"]
