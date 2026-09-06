FROM ghcr.io/jdx/mise:2026.8.2
RUN apt-get update && apt-get install -y --no-install-recommends libnspr4 libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libdbus-1-3 libcups2t64 libxkbcommon0 libasound2t64 libgbm1 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libatspi2.0-0t64 fonts-liberation
RUN useradd --create-home --uid 1000 --shell /bin/bash vscode
ENV MISE_DATA_DIR=/home/vscode/.local/share/mise
ENV MISE_CONFIG_DIR=/home/vscode/.config/mise
ENV MISE_CACHE_DIR=/home/vscode/.cache/mise
ENV PATH="/home/vscode/.local/share/mise/shims:$PATH"
RUN mkdir -p /workspaces/template/backend/.venv /workspaces/template/frontend/node_modules && chown -R vscode:vscode /workspaces/template
USER vscode
ENTRYPOINT []
CMD ["sleep", "infinity"]
