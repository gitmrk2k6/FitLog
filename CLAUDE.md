# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## FitLog — Claude Code ルール

## 命名規則（Conventional Commits ベース）

すべての命名で以下の `type` を統一して使う。

| type | 用途 |
|------|------|
| `feat` | 新機能追加 |
| `fix` | バグ修正 |
| `docs` | ドキュメント更新 |
| `refactor` | リファクタリング |
| `chore` | 設定変更・依存関係更新 |
| `test` | テスト追加・修正 |

### イシュータイトル

```
<type>: <作業の概要>
```

### ブランチ名

```
<type>/issue-<番号>-<短い説明（英語）>
```

例: `feat/issue-3-f01-auth` / `docs/issue-1-requirements`

### コミットメッセージ

```
<type>: <変更内容の概要>
```

### プルリクエストタイトル

```
<type>: <作業の概要> (#<イシュー番号>)
```

---

## GitHub ワークフロー（必ず守ること）

### 1. 作業開始前に必ずイシューを作る

```bash
gh issue create --title "<type>: <作業の概要>" --body "<詳細説明>"
```

- **イシューなしで作業を開始してはならない**

### 2. ブランチを作る

```bash
git checkout -b <type>/issue-<番号>-<説明>
```

### 3. main への直接プッシュ禁止

- `main` への直接コミット・プッシュは禁止
- 作業は必ずフィーチャーブランチで行い、プルリクエスト経由でマージする

### 4. プルリクエストのルール

- PR 本文に `Closes #<イシュー番号>` を必ず記載する
- PR のマージはユーザーが行う。Claude は PR を作成して URL を報告するまでが役割

### 5. ブランチの掃除（自動化方針）

- **リモート**: マージ後の head ブランチは GitHub 設定で自動削除（`delete-branch-on-merge` 有効）
- **ローカル**: 作業開始前に必ず以下で掃除してから新ブランチを切る

```bash
git cleanup   # main へ切替→pull --prune→マージ済み(gone)ローカルブランチを削除
```

- リポジトリには `fetch.prune = true` と `alias.cleanup` を設定済み
- 新しい作業を始めるとき・PR がマージされた後は、ブランチ作成前に `git cleanup` を実行する

### 6. 作業の流れまとめ

```
1. git cleanup で不要ローカルブランチを掃除
2. gh issue create でイシュー作成
3. git checkout -b <type>/issue-<番号>-<説明> でブランチ作成
4. 作業・コミット（Conventional Commits 形式）
5. gh pr create でプルリクエスト作成・URL を報告
6. マージはユーザー。マージ後リモートブランチは自動削除
```

---

## テスト方針（必ず守ること）

- **機能の実装とテストコードは必ずセットで作成する**（実装＋テストで1機能の完了とする）
- 後追いでの一括テスト作成はしない
- バックエンド: pytest ／ フロントエンド: Vitest

---

## サーバー起動ルール（必ず守ること）

### 指定ポート

| サーバー | ポート |
| ------- | ------ |
| フロントエンド（Vue 3 / Vite） | `3000` |
| バックエンド（FastAPI / Uvicorn） | `8000` |
| データベース（PostgreSQL） | `5432` |

### ポート競合時の対処

一時的に別ポートで起動することは禁止。競合時は競合プロセスを停止し、必ず指定ポートで起動し直す。

```bash
kill $(lsof -ti:<ポート番号>)
```

### 起動順序

```bash
docker compose up -d                 # 1. PostgreSQL
cd backend && uvicorn app.main:app --reload --port 8000   # 2. バックエンド
cd frontend && npm run dev           # 3. フロントエンド（port 3000）
```

---

## 技術スタック方針

| レイヤー | 主要技術 |
| ------- | ------- |
| フロントエンド | Vue 3（Composition API）+ Vite + TypeScript |
| バックエンド | FastAPI（Python）+ SQLAlchemy |
| データベース | PostgreSQL（Docker） |
| 認証 | JWT（python-jose / passlib[bcrypt]） |
| 画像ストレージ | AWS S3 |
| インフラ | AWS ECS Fargate + RDS + ALB + CloudFront + S3（RaiseTimeLine と同構成を流用） |

- バージョンを変更したら `docs/tech-stack.md` も同時に更新する

---

## プロジェクト概要

- **コース**: RaiseTech AIエンジニアコース 中級編 最終課題
- **テーマ**: 筋トレ・運動記録アプリ（複数ユーザーが双方向にやり取りするサービス）
- **機能**: F-01〜F-10（認証・記録・一覧・ナイストレ・アドバイス・フォロー・目標/達成率・ストリーク・自己ベスト・写真）
- **ドキュメント**: `docs/` ディレクトリ参照
