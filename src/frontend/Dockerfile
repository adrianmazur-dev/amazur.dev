FROM node:24-alpine AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci


FROM deps AS builder

COPY . .
RUN npm run build && npm prune --omit=dev


FROM node:24-alpine AS runtime

WORKDIR /app

COPY --from=builder --chown=node:node /app/dist ./dist
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/package.json ./package.json

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=4321

USER node

EXPOSE 4321

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:4321/ || exit 1

CMD ["node", "./dist/server/entry.mjs"]
