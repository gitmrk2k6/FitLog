# FitLog

筋トレ・運動記録アプリ。RaiseTech AIエンジニアコース **中級編 最終課題**。

トレーニング記録（種目・セット・重量・回数・写真）を蓄積し、週間/月間で集計・可視化することで
**「続けられる」体験**を提供する。複数ユーザーが互いの記録に対し双方向にやり取り（ナイストレ/アドバイス/フォロー）できる。

## 継続の工夫

- 目標設定＋達成率グラフ（週間/月間）
- ストリーク＋カレンダーヒートマップ
- 自己ベスト(PR)自動検出

## 技術スタック

教材 RaiseTimeLine（Spring Boot/Java + Next.js + MyBatis）から変更。

| レイヤー | 採用 |
| --- | --- |
| バックエンド | FastAPI (Python) + SQLAlchemy |
| フロントエンド | Vue 3 + Vite + TypeScript |
| データベース | PostgreSQL |
| 認証 | JWT |
| インフラ | AWS（RaiseTimeLine と同構成を流用） |

選定理由は [docs/tech-stack.md](docs/tech-stack.md) を参照。

## ドキュメント

| ドキュメント | 内容 |
| --- | --- |
| [要件定義書](docs/requirements.md) | 概要・想定ユーザー・機能/非機能要件・スコープ |
| [機能要件書](docs/functional-requirements.md) | 機能定義（F-01〜F-10）・バリデーション・ユースケース |
| [データベース設計書](docs/database-design.md) | ER図・テーブル定義・インデックス・制約 |
| [技術スタック](docs/tech-stack.md) | 採用技術・選定理由（教材との差分の「なぜ」） |

## 開発方針

- 機能実装はテストコードとセットで完了とする（FastAPI: pytest / Vue: Vitest）
- 作業はイシュー → ブランチ → プルリクエストの流れで進める（Conventional Commits）
