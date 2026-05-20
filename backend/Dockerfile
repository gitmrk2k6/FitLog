# ── Stage 1: 依存パッケージのインストール ─────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# venv に隔離してインストール（runtime ステージに clean copy を渡す）
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: 実行イメージ ────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

WORKDIR /app

# curl は ECS ヘルスチェックコマンドで使用
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
  && rm -rf /var/lib/apt/lists/*

# 非 root ユーザー
RUN useradd --uid 1000 --no-create-home --shell /bin/bash appuser

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
