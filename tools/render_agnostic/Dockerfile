# tools/render_agnostic/Dockerfile — PR #41 Disposable Render Environment
#
# Stateless, reproducible container for the Render Agnostic Output Layer.
# The CPU reference path requires no additional dependencies beyond Python 3.
#
# Standard: Yeshua
# PR: #41
# Version: 1.0.0

FROM python:3.11-slim

LABEL org.opencontainers.image.title="RAOL CPU Reference Renderer"
LABEL org.opencontainers.image.description="PR #41 Render Agnostic Output Layer — stateless, reproducible render environment"
LABEL org.opencontainers.image.version="1.0.0"

# Reproducible environment
ENV PYTHONHASHSEED=41
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=UTC

WORKDIR /app

# Copy only the render_agnostic package and tests
COPY tools/render_agnostic/ tools/render_agnostic/
COPY tests/test_pr41_render_agnostic.py tests/

# No external dependencies required for the CPU reference path.
# pytest is the only install needed for the test suite.
RUN pip install --no-cache-dir pytest==8.3.5

# Default: run the test suite
CMD ["python", "-m", "pytest", "tests/test_pr41_render_agnostic.py", "-v"]
