# 技術スタック

関連: [要件定義書](requirements.md)

## 1. 方針 — なぜ教材と変えるのか

本課題（中級編 最終課題）の評価ポイントは「**教材 RaiseTimeLine と異なるスタックを自分で選び、その理由を説明できること**」。
そのため「何を選ぶか」より「**なぜそれを選んだか**」を重視する。

選定の軸は **アプリの本質との整合**。

- RaiseTimeLine の山場 = リアルタイムSNSフィード（SSE・カーソルページネーション）
- FitLog の山場 = **時系列データの集計・可視化と継続支援**（週間/月間集計、達成率、ストリーク、ヒートマップ、自己ベスト）

性質が「SNS」から「パーソナル分析・習慣化アプリ」へ変わるため、集計・分析に強いスタックを選ぶ。

---

## 2. 採用技術と選定理由

| レイヤー | 教材（RaiseTimeLine） | FitLog 採用 | 選定理由（なぜ） |
| --- | --- | --- | --- |
| バックエンド言語/FW | Java 21 / Spring Boot 3 | **Python / FastAPI** | AIエンジニアコースの中核言語と一致。集計・分析処理と相性が良く、`pydantic` による型安全な入出力・依存性注入が学べる。言語・パラダイムが教材から明確に変化 |
| ORM/DB アクセス | MyBatis（XMLマッパー） | **SQLAlchemy（＋必要に応じ生SQL）** | MyBatis の「SQLを明示」とは別アプローチの ORM を経験。集計の複雑クエリは SQLAlchemy Core / 生SQL で書き分け |
| API ドキュメント | SpringDoc OpenAPI | **FastAPI 標準（OpenAPI/Swagger 自動生成）** | SpringDoc 相当を標準機能で代替できることを示す |
| フロントエンド | Next.js 14 / React | **Vue 3（Composition API）+ Vite + TypeScript** | 教材の React/Next.js から別系統のフレームワークへ。ダッシュボード/グラフ中心のSPAと相性。Vite で高速開発 |
| フォーム/型 | React Hook Form + Zod | **VeeValidate + Zod（または Valibot）** | Vue エコシステムでの型安全フォームバリデーション |
| データDB | PostgreSQL 17 | **PostgreSQL（継続採用）** | 集計に強く意図的に流用。`date_trunc` / ウィンドウ関数 / `generate_series` が週月集計・ヒートマップ・ストリーク算出に直結。教材資産（RDS構成）も流用可 |
| 認証 | Spring Security + JJWT | **JWT（python-jose / passlib[bcrypt]）** | 認証方式（JWT）の知見は流用しつつ実装言語を刷新 |
| テスト | JUnit / Vitest | **pytest（バックエンド）/ Vitest（フロント）** | 機能実装と同時にテストを書く方針（教材では後追い一括だった反省） |
| インフラ | AWS ECS Fargate + CloudFront + S3 + RDS + ALB + Terraform | **同構成を流用** | 課題はアプリ層の刷新が趣旨。AWS は教材と同じ構成でよく、IaC 資産を再利用して工数を集計・継続機能に集中 |

---

## 3. プロジェクト構成（予定）

```text
FitLog/
  docs/                 # 要件定義・設計ドキュメント
  backend/              # FastAPI（router / service / repository 層構成）
    app/
      routers/
      services/
      repositories/
      models/           # SQLAlchemy モデル
      schemas/          # pydantic スキーマ
    tests/              # pytest（機能と同時に作成）
  frontend/             # Vue 3 + Vite + TS
    src/
      views/
      components/
      composables/
    tests/              # Vitest
  docker-compose.yml    # PostgreSQL（ローカル）
```

---

## 4. ローカル開発（予定ポート）

| サーバー | ポート |
| --- | --- |
| フロントエンド（Vite） | 3000 |
| バックエンド（FastAPI / Uvicorn） | 8000 |
| データベース（PostgreSQL / Docker） | 5432 |

起動順序: PostgreSQL（docker compose）→ FastAPI（uvicorn）→ Vue（vite dev）。

---

## 5. バージョン管理メモ

- バージョンを更新したら本ファイルを同時に更新する
- 主要ライブラリの確定バージョンは実装着手時に追記

### バックエンド確定バージョン（Increment 1 / F-01 着手時）

| ライブラリ | バージョン |
| --- | --- |
| fastapi | 0.115.6 |
| uvicorn[standard] | 0.34.0 |
| sqlalchemy | 2.0.36 |
| alembic | 1.14.0 |
| psycopg[binary] | 3.2.3 |
| pydantic | 2.10.4 |
| pydantic-settings | 2.7.0 |
| python-jose[cryptography] | 3.3.0 |
| passlib[bcrypt] | 1.7.4 |
| bcrypt | 4.1.3 |
| email-validator | 2.2.0 |
| python-multipart | 0.0.20 |
| pytest (dev) | 8.3.4 |
| httpx (dev) | 0.28.1 |

- DB: PostgreSQL 17（docker compose、ポート5432）
