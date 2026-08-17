# syntax=docker/dockerfile:1

# ---- builder: install the published package into a venv ----
FROM python:3.12-slim AS builder

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir secret-guard-scan

# ---- runtime: minimal image, non-root user ----
FROM python:3.12-slim AS runtime

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN groupadd --gid 1000 scanner \
    && useradd --uid 1000 --gid scanner --shell /usr/sbin/nologin --create-home scanner
USER scanner

WORKDIR /code

ENTRYPOINT ["secret-guard"]
CMD ["--version"]