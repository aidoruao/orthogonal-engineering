# tools/discord_witness/Dockerfile
# Disposable witness container — no persistent state, no volumes.
# The bot reads from GitHub and posts to Discord, then exits.
# If banned, deleted, or corrupted: redeploy from this Dockerfile.
# No secrets baked in. Pass DISCORD_WEBHOOK_URL at runtime.

FROM python:3.11-slim

LABEL maintainer="Orthogonal Engineering"
LABEL description="PR #40 Discord Derivative Witness Bot — stateless, disposable"
LABEL standard="Yeshua"

# No additional packages needed: stdlib only
WORKDIR /app

# Copy only the tools we need
COPY tools/discord_witness/ ./tools/discord_witness/
COPY tools/state_witness/ ./tools/state_witness/
COPY AGENT_FEED.md ./AGENT_FEED.md

ENV PYTHONHASHSEED=40
ENV PYTHONIOENCODING=utf-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Entrypoint: run the witness bot, exit when done.
# Pass DISCORD_WEBHOOK_URL as an environment variable.
# Use --dry-run for smoke-testing the container without posting.
ENTRYPOINT ["python", "tools/discord_witness/bot.py"]
CMD []
