# ── Stage 1: builder ──────────────────────────────────────────

FROM python:3.12-slim AS builder

WORKDIR /app

# Copy only requirements first — Docker layer cache trick
# If requirements.txt hasn't changed, this layer is reused

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime ──────────────────────────────────────────

FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed packages from builder, not pip cache

COPY --from=builder /install /usr/local

# Copy application code

COPY app.py .

# Don't run as root — security best practice
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Expose port

EXPOSE 5000

# Gunicorn: 2 workers, bind to all interfaces on port 5000
CMD ["gunicorn", "--workers=2", "--bind=0.0.0.0:5000", "app:app"]

