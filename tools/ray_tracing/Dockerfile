# tools/ray_tracing/Dockerfile
# PR #42 — Disposable Deterministic Render Container
#
# Self-contained execution environment for the Deterministic Light Transport
# Layer.  No GPU drivers, no NVIDIA libs, no vendor lock-in.
#
# Build:
#   docker build -t dltl:pr42 tools/ray_tracing/
#
# Run a single frame:
#   docker run --rm dltl:pr42 python -c "
#     from transport.path_tracer import trace_path_deterministic
#     from geometry.intersect import Ray, Scene, Sphere, Material
#     scene = Scene(spheres=[Sphere((0,0,-2), 0.5, Material(emission=1.0))])
#     ray = Ray((0,0,0), (0,0,-1))
#     r = trace_path_deterministic(ray, 0, b'\x00'*32, scene)
#     print(f'radiance={r:.6f}')
#   "
#
# Standard: Yeshua
# GRACE: public domain base image, zero proprietary components

FROM python:3.11-slim

LABEL org.opencontainers.image.title="Deterministic Light Transport Layer"
LABEL org.opencontainers.image.description="PR #42 — Yeshua DLTL render container"
LABEL org.opencontainers.image.version="1.0.0"
LABEL standard="Yeshua"
LABEL pr="42"

# Reproducible builds: pin SOURCE_DATE_EPOCH and PYTHONHASHSEED
ENV PYTHONHASHSEED=42 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=UTC \
    SOURCE_DATE_EPOCH=1700000000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /opt/dltl

# Copy only the ray_tracing package (no external dependencies)
COPY . /opt/dltl/tools/ray_tracing/

# Verify: no randomness in source
RUN grep -r "import random" /opt/dltl/tools/ray_tracing/ && exit 1 || echo "GRACE: no randomness found"
RUN grep -r "np\.random" /opt/dltl/tools/ray_tracing/ && exit 1 || echo "GRACE: no numpy randomness found"

# Smoke test: Sobol' sequence is deterministic
RUN python - <<'EOF'
import sys
sys.path.insert(0, '/opt/dltl')
from tools.ray_tracing.samplers.sobol import sobol_sequence
seed = b'\x00' * 32
a = sobol_sequence(5, 16, seed)
b = sobol_sequence(5, 16, seed)
assert a == b, "LOGOS violation: Sobol sequence not deterministic"
print("LOGOS: Sobol determinism verified")
EOF

# Smoke test: path trace is deterministic
RUN python - <<'EOF'
import sys
sys.path.insert(0, '/opt/dltl')
from tools.ray_tracing.geometry.intersect import Ray, Scene, Sphere, Material
from tools.ray_tracing.transport.path_tracer import trace_path_deterministic
scene = Scene(
    spheres=[Sphere(center=(0,0,-2), radius=0.5, material=Material(emission=1.0))]
)
ray = Ray(origin=(0,0,0), direction=(0,0,-1))
r1 = trace_path_deterministic(ray, 0, b'\x00'*32, scene)
r2 = trace_path_deterministic(ray, 0, b'\x00'*32, scene)
assert r1 == r2, "LOGOS violation: path trace not deterministic"
print(f"LOGOS: path trace verified — radiance={r1:.6f}")
EOF

CMD ["python", "-c", "from tools.ray_tracing import __version__; print(f'DLTL v{__version__} — ready')"]
