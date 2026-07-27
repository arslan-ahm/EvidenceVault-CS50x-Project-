FROM oven/bun:1.1.29 AS builder

WORKDIR /app

COPY package.json /app/
RUN bun install

COPY . /app
RUN bun run build

FROM oven/bun:1.1.29 AS runner

WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/build /app/build
RUN bun add serve

EXPOSE 3000
CMD ["bunx", "serve", "build", "-l", "3000"]
