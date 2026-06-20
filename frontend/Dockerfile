FROM oven/bun:1.1.29 AS builder

WORKDIR /app

COPY package.json /app/
RUN bun install

COPY . /app
RUN bun run build

FROM oven/bun:1.1.29 AS runner

WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app /app
ENV HOST=0.0.0.0
ENV PORT=3000

EXPOSE 3000
CMD ["bun", "./build/index.js"]
