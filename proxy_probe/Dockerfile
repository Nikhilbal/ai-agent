# Temporary, read-only network diagnostic; standalone from other applications.
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir "fastapi>=0.115,<1" "uvicorn>=0.30,<1"
COPY proxy_probe/probe.py /app/probe.py
EXPOSE 10000
CMD ["sh", "-c", "exec python -m uvicorn probe:app --host 0.0.0.0 --port ${PORT:-10000} --no-proxy-headers --no-access-log"]
