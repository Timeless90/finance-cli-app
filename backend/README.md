# Finance backend

Python 3.13 / uv / FastAPI with the retained finance-cli entrypoint.
Run `mise exec -- make install` from the repository root.
From this directory: `uv run cfo-api`, `uv run finance-cli --help`,
`uv run pytest`, `uv run pyright`. Root Make targets run the complete checks.
Application modules live under `app/`; CLI modules under `finance_cli/`.
The existing repository interfaces and storage formats remain supported.
