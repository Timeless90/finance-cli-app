FROM node:24.20.0-bookworm-slim AS build
RUN npm install --global pnpm@10.15.1
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
ENV CFO_LOCAL_GATEWAY=true
RUN pnpm build --mode devlocal
FROM nginxinc/nginx-unprivileged:1.28-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
