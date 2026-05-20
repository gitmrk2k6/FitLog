# FitLog — 筋トレ・運動記録アプリ

RaiseTech AIエンジニアコース **中級編 最終課題**

---

## デモ動画

> デプロイ後に追加予定

---

## アプリ概要

筋トレ・運動の記録を蓄積し、目標達成率・ストリーク・自己ベスト更新で **継続できる** 体験を提供するアプリ。
複数ユーザーが互いの記録に「ナイストレ」「アドバイス」を送り合い、フォローしてフィードで応援し合える。

**課題要件「複数ユーザーが双方向にデータをやり取りするサービス」** をフィットネス特化で実現した。

---

## 機能一覧

| 機能 | 概要 |
|------|------|
| ユーザー認証 | 新規登録・ログイン・ログアウト（JWT） |
| トレーニング記録 | 実施日・種目・セット（重量×回数）・メモ・写真を記録/編集/削除 |
| 記録一覧/詳細 | 自分の記録を日別一覧で確認、総ボリュームを自動計算 |
| ナイストレーニング | 他ユーザーの記録に「いいね」相当のリアクションを送る |
| アドバイス・応援 | 他ユーザーの記録へコメントを送る |
| フォロー/フィード | 仲間をフォローしてフィードで記録を追う |
| 目標設定＋達成率 | 週間/月間のトレーニング目標を設定し、達成率グラフで進捗確認 |
| ストリーク＋ヒートマップ | 連続記録日数とカレンダーヒートマップで習慣を可視化 |
| 自己ベスト(PR)自動検出 | 記録時に最大重量・推定1RM・総ボリュームの自己ベスト超過を自動判定して通知 |
| 写真アップロード | トレーニング写真を AWS S3 に保存 |

---

## 技術スタック

教材「RaiseTimeLine」（Java/Spring Boot + Next.js/React + MyBatis）からスタックを変更した。

| レイヤー | 採用技術 | 教材からの変更 |
|----------|----------|---------------|
| バックエンド | Python / FastAPI | Java / Spring Boot → Python / FastAPI |
| ORM | SQLAlchemy | MyBatis → SQLAlchemy |
| フロントエンド | Vue 3 + Vite + TypeScript | Next.js / React → Vue 3 |
| データベース | PostgreSQL 17 | 同じ（継続採用） |
| 認証 | JWT（python-jose / passlib） | Spring Security → python-jose |
| 画像ストレージ | AWS S3 | 同じ（教材構成を流用） |
| インフラ | AWS ECS Fargate + RDS + ALB + CloudFront | 同じ（教材 IaC を流用） |
| テスト | pytest / Vitest / Playwright / k6 | 実装と同時にテストを書く方針に変更 |
| CI | GitHub Actions | 新規追加 |

### なぜこのスタックを選んだか

FitLog の本質は **時系列データの集計・可視化と継続支援**（週月集計・達成率・ストリーク・ヒートマップ・自己ベスト）であり、教材 RaiseTimeLine の山場（リアルタイム SNS フィード）とは性質が異なる。

- **Python / FastAPI** — AI/ML 分野の標準言語である Python を選ぶことで、将来の AI 機能追加（データ分析・推薦等）に備えられる。FastAPI は Pydantic による型安全な入出力と OpenAPI 自動生成を備えた現代的なフレームワークであり、Java/Spring Boot とは異なる設計思想を経験できる
- **SQLAlchemy + PostgreSQL** — `date_trunc` / `generate_series` / ウィンドウ関数が週月集計・ヒートマップ・ストリーク算出に直結。MyBatis と異なるアプローチの ORM を経験
- **Vue 3** — React/Next.js と別系統のフレームワーク。ダッシュボード/グラフ中心の SPA と相性がよく Vite で高速開発

詳細は [docs/tech-stack.md](docs/tech-stack.md) を参照。

---

## インフラ構成

> デプロイ後に構成図を追加予定

```
インターネット
    │
CloudFront ──── S3（静的ファイル配信 / 写真ストレージ）
    │
ALB（Application Load Balancer）
    │
ECS Fargate
  ├── バックエンド（FastAPI）
  └── フロントエンド（Vue 3 / Nginx）
    │
RDS（PostgreSQL 17）
```

教材 RaiseTimeLine の AWS 構成（ECS Fargate + RDS + ALB + CloudFront + S3）を流用し、アプリ層の実装に注力した。

---

## テスト

| 種別 | ツール | 件数 |
|------|--------|------|
| バックエンド単体・結合 | pytest | 154件 |
| フロントエンド単体 | Vitest | 59件 |
| E2E | Playwright | 全機能シナリオ |
| パフォーマンス | k6 | 主要エンドポイント |
| CI | GitHub Actions | push / PR 時に自動実行 |

---

## ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| [要件定義書](docs/requirements.md) | 概要・想定ユーザー・機能/非機能要件・スコープ |
| [機能要件書](docs/functional-requirements.md) | 機能定義（全10機能）・バリデーション・ユースケース |
| [データベース設計書](docs/database-design.md) | ER図・テーブル定義・インデックス・制約 |
| [画面設計書](docs/screen-design.md) | 画面一覧・遷移図・ワイヤーフレーム |
| [技術スタック](docs/tech-stack.md) | 採用技術・選定理由（教材との差分の「なぜ」） |
| [監視・ログ設計](docs/monitoring-logging.md) | ログ設計・監視設計・Datadog 連携方針 |
