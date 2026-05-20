# 監視・ログ設計書

関連: [要件定義書](requirements.md) / [技術スタック](tech-stack.md)

---

## 1. 概要

本ドキュメントは FitLog バックエンド（FastAPI）の **ログ設計・監視設計・障害対応設計** を定義する。

### 基本方針

| 項目 | 方針 |
|------|------|
| ログ形式 | JSON 構造化ログ（行単位の NDJSON） |
| 収集先 | 標準出力 → コンテナランタイム（ECS）経由で CloudWatch Logs |
| 将来連携 | Datadog Agent / Datadog Forwarder 経由でダッシュボード化（フィールドは準備済み） |
| ログ保持 | CloudWatch Logs: 90日 ／ Datadog: 15日（インデックス） |

---

## 2. ログ設計

### 2.1 フィールド定義

すべてのログ行は以下フィールドを含む JSON オブジェクト（1行）として出力する。

| フィールド | 型 | 説明 | 例 |
|---|---|---|---|
| `timestamp` | string (ISO 8601) | UTC タイムスタンプ | `"2026-05-20T10:00:00.123Z"` |
| `level` | string | ログレベル | `"INFO"` |
| `logger` | string | ロガー名 | `"fitlog.request"` |
| `message` | string | ログメッセージ | `"request completed"` |
| `service` | string | サービス名（固定） | `"fitlog-api"` |
| `env` | string | 実行環境 | `"production"` |
| `version` | string | アプリバージョン | `"0.1.0"` |
| `request_id` | string (UUID v4) | リクエスト単位の追跡 ID | `"a1b2c3d4-..."` |
| `method` | string | HTTP メソッド | `"POST"` |
| `path` | string | リクエストパス | `"/workouts"` |
| `status_code` | integer | HTTP ステータスコード | `201` |
| `duration_ms` | float | 処理時間（ミリ秒） | `45.3` |
| `user_id` | integer \| null | 認証済みユーザー ID | `123` |
| `error` | string \| null | 例外メッセージ（ERROR 時） | `"IntegrityError: ..."` |
| `dd.trace_id` | string | Datadog 分散トレーシング ID（スタブ） | `"0"` |
| `dd.span_id` | string | Datadog スパン ID（スタブ） | `"0"` |
| `dd.service` | string | Datadog サービス名 | `"fitlog-api"` |
| `dd.env` | string | Datadog 環境名 | `"production"` |
| `dd.version` | string | Datadog バージョン | `"0.1.0"` |

> **Datadog 連携時の手順**  
> 1. `ddtrace` パッケージをインストールして `dd-trace` コマンド経由で起動  
> 2. `dd.trace_id` / `dd.span_id` を `ddtrace.tracer.current_span()` から取得するよう差し替え  
> 3. Datadog Agent の `logs_config.container_collect_all: true` を有効化

### 2.2 ログレベル定義

| レベル | 用途 | 例 |
|--------|------|----|
| `DEBUG` | 開発時の詳細情報。本番では無効 | SQL クエリ、認証トークン検証ステップ |
| `INFO` | 通常のリクエスト完了、主要操作の記録 | `GET /workouts` 200、ログイン成功 |
| `WARNING` | 異常ではないが注意が必要な状態 | 認証失敗、レートリミット近接 |
| `ERROR` | 処理が失敗した例外 | DB 接続エラー、S3 アップロード失敗 |
| `CRITICAL` | サービス全体に影響する致命的障害 | DB 接続不可、起動失敗 |

### 2.3 ログ出力対象と方針

| カテゴリ | ロガー名 | 内容 |
|----------|----------|------|
| リクエスト | `fitlog.request` | 全リクエスト（INFO） + 5xx（ERROR） |
| 認証 | `fitlog.auth` | ログイン成功・失敗、トークン検証失敗（WARNING） |
| DB | `fitlog.db` | 接続エラー（ERROR）、スロークエリ（WARNING） |
| S3 | `fitlog.storage` | アップロード成功（INFO）、失敗（ERROR） |
| アプリ | `fitlog.app` | 起動・シャットダウン（INFO） |

#### 出力しないもの（PII・セキュリティ）

- パスワード / パスワードハッシュ
- JWT トークン全体
- リクエスト / レスポンスボディ（ただしエラー時のバリデーション詳細は除く）
- メールアドレス（ユーザー ID のみ記録）

### 2.4 ログ出力例

**通常リクエスト（INFO）**

```json
{
  "timestamp": "2026-05-20T10:00:00.123Z",
  "level": "INFO",
  "logger": "fitlog.request",
  "message": "request completed",
  "service": "fitlog-api",
  "env": "production",
  "version": "0.1.0",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/workouts",
  "status_code": 201,
  "duration_ms": 45.3,
  "user_id": 123,
  "dd.trace_id": "0",
  "dd.span_id": "0",
  "dd.service": "fitlog-api",
  "dd.env": "production",
  "dd.version": "0.1.0"
}
```

**サーバーエラー（ERROR）**

```json
{
  "timestamp": "2026-05-20T10:01:00.456Z",
  "level": "ERROR",
  "logger": "fitlog.request",
  "message": "unhandled exception",
  "service": "fitlog-api",
  "env": "production",
  "version": "0.1.0",
  "request_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "method": "POST",
  "path": "/workouts",
  "status_code": 500,
  "duration_ms": 12.1,
  "user_id": 123,
  "error": "IntegrityError: duplicate key value violates unique constraint",
  "dd.trace_id": "0",
  "dd.span_id": "0",
  "dd.service": "fitlog-api",
  "dd.env": "production",
  "dd.version": "0.1.0"
}
```

---

## 3. 監視設計

### 3.1 ヘルスチェック

| チェック種別 | エンドポイント | 判定条件 |
|---|---|---|
| 死活監視（Liveness） | `GET /health` | HTTP 200 が返ること |
| 準備確認（Readiness） | `GET /health/ready` | DB 接続確認 + 200 |

`/health/ready` は ECS タスクの ALB ターゲットグループのヘルスチェックパスとして使用する。

### 3.2 監視メトリクス（CloudWatch）

ECS / ALB が自動収集するメトリクスを Datadog に転送して可視化する。

| メトリクス | 警告閾値 | 重大閾値 | 対応 |
|---|---|---|---|
| ALB `HTTPCode_Target_5XX_Count` | 5件/分 | 20件/分 | 障害対応 P2→P1 |
| ALB `TargetResponseTime` | p99 > 1s | p99 > 3s | パフォーマンス調査 |
| ECS `CPUUtilization` | 70% | 90% | スケールアウト検討 |
| ECS `MemoryUtilization` | 70% | 90% | メモリリーク調査 |
| RDS `DatabaseConnections` | 80件 | 150件 | コネクションプール確認 |
| RDS `FreeStorageSpace` | < 5GB | < 1GB | ストレージ拡張 |

### 3.3 ログベースアラート（CloudWatch Logs Insights）

| アラート名 | 検索クエリ | 閾値 |
|---|---|---|
| 5xx エラー急増 | `filter level = "ERROR" and status_code >= 500` | 10件/5分 |
| 認証失敗急増 | `filter logger = "fitlog.auth" and level = "WARNING"` | 30件/5分 |
| レスポンス遅延 | `filter duration_ms > 3000` | 5件/分 |
| DB エラー | `filter logger = "fitlog.db" and level = "ERROR"` | 1件/分 |

---

## 4. 障害対応設計

### 4.1 障害レベル定義

| レベル | 定義 | SLO 目標 | 対応時間 |
|--------|------|----------|----------|
| P1（重大） | サービス全体停止 / 認証不能 | 99.5% 稼働 | 即時（15分以内に初動） |
| P2（高） | 特定機能が使えない（写真 / アドバイス等） | — | 1時間以内に初動 |
| P3（中） | パフォーマンス劣化 / 警告レベル | — | 翌営業日対応 |
| P4（低） | 軽微な表示ズレ・UX 課題 | — | バックログ積み |

### 4.2 障害対応フロー

```
アラート発火（CloudWatch → SNS → メール）
    │
    ▼
1. 状況確認（5分以内）
   - CloudWatch Logs で直近 5 分の ERROR ログを確認
   - ALB / ECS / RDS ダッシュボードで異常メトリクスを確認
   - git log / デプロイ履歴との照合
    │
    ▼
2. 切り分け（10分以内）
   ┌─ DB 問題？ → RDS コンソール / pg_stat_activity 確認
   ├─ アプリ問題？ → ECS タスクログ確認 / タスク再起動
   ├─ デプロイ起因？ → 直前の ECS タスク定義にロールバック
   └─ インフラ問題？ → AWS Status / Route 53 / ALB 確認
    │
    ▼
3. 応急処置
   - ECS タスクの再起動: aws ecs update-service --force-new-deployment
   - ロールバック: 旧タスク定義を指定して update-service
   - DB 接続過多: コネクションプールの最大値を一時縮小
    │
    ▼
4. 恒久対応
   - 根本原因の特定とコード/設定修正
   - テスト追加（再発防止）
   - ポストモーテム作成（P1/P2 必須）
```

### 4.3 ポストモーテムテンプレート

```markdown
## ポストモーテム — <障害タイトル>

**発生日時**: YYYY-MM-DD HH:MM UTC  
**解消日時**: YYYY-MM-DD HH:MM UTC  
**障害レベル**: P1 / P2  
**影響範囲**: （ユーザー数・機能・時間）

### タイムライン
- HH:MM — アラート発火
- HH:MM — 調査開始
- HH:MM — 原因特定
- HH:MM — 応急処置完了
- HH:MM — サービス復旧

### 根本原因
（技術的な原因を記述）

### 対応内容
（実施した応急処置・恒久対応）

### 再発防止策
| アクション | 担当 | 期日 |
|---|---|---|
| | | |
```

---

## 5. Datadog 連携準備

実連携は不要だが、以下のステップで即時連携できる状態を維持する。

### 5.1 現在の準備状態

| 項目 | 状態 |
|------|------|
| JSON 構造化ログ出力 | ✅ 実装済み |
| `dd.*` フィールドのスタブ | ✅ 実装済み（値は `"0"`） |
| `service` / `env` / `version` タグ | ✅ 実装済み |
| `ddtrace` ライブラリ | 未インストール（連携時に追加） |

### 5.2 連携手順（将来）

```bash
# 1. ddtrace インストール
pip install ddtrace

# 2. 起動コマンド変更
ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. core/logging.py の dd.* フィールドを実値に変更
#    dd.trace_id: ddtrace.tracer.current_span().trace_id
#    dd.span_id:  ddtrace.tracer.current_span().span_id

# 4. ECS タスク定義に Datadog Agent サイドカーを追加
#    image: public.ecr.aws/datadog/agent:latest
#    environment: DD_API_KEY, DD_LOGS_ENABLED=true
```

### 5.3 Datadog ダッシュボード設計（連携後）

| ウィジェット | 指標 |
|---|---|
| エラー率時系列 | `status_code >= 500` 件数 / 全リクエスト数 |
| レイテンシ分布 | `duration_ms` の p50 / p95 / p99 |
| ユーザー別エラー | `user_id` × `status_code` のヒートマップ |
| パス別リクエスト数 | `path` × `method` の時系列 |
| DB エラー件数 | `logger = "fitlog.db" AND level = "ERROR"` |
