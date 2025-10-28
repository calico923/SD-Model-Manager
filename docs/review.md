# docs リビューまとめ

## ドキュメントレビュー概要
- 対象ファイル: `docs/mvp_specification.md`, `docs/requirements.md`
- レビュー目的: MVP 仕様と要件定義の整合性確認、および保守性向上に向けた改善提案

## 主な指摘事項
- Python バージョン要件の不一致  
  - `docs/mvp_specification.md:247` と `docs/requirements.md:141` で Python 3.9+ と記載されており、リポジトリ方針 (Python 3.11+) と矛盾。
- ディレクトリ構造方針の相違  
  - `docs/mvp_specification.md:259-284`, `docs/requirements.md:151-169` の構造案が「`src/sd_model_manager/` 配下に runtime コードを置く」ガイドラインに沿っていない。
- MVP スコープの齟齬  
  - `docs/mvp_specification.md:552-554` は LoRA/Checkpoint/VAE/Embedding すべて対応とする一方、`docs/requirements.md:222-226` では LoRA のみを対象と明記。
- SQLite 採用タイミングの混在  
  - `docs/mvp_specification.md:231` では非実装扱いだが、`docs/mvp_specification.md:253` で Phase 2 オプションとして列挙。
- デバイス対応の矛盾  
  - `docs/mvp_specification.md:417` でタブレット以下後回しとしつつ、`docs/mvp_specification.md:559-561` では MVP 成功基準にモバイル・タブレット対応を含めている。
- フロントエンド技術選定の不一致  
  - `docs/mvp_specification.md:242-252` は React + shadcn/ui を想定するが、`docs/requirements.md:143` では CDN ベースの軽量 UI を想定。

## 推奨技術スタック
- バックエンド: Python 3.11, FastAPI, Pydantic v2, httpx
- フロントエンド: TypeScript, React, Vite, Tailwind/shadcn.ui  
  - 最小構成を優先する場合は FastAPI + HTMX/Alpine.js も候補だが、進捗表示や将来のドラッグ&ドロップ UI を考慮すると React/TypeScript が無難。

## 推奨ディレクトリ構造 (抜粋)
```
src/sd_model_manager/
├── __main__.py
├── config.py
├── logging.py
├── lib/
│   └── filesystem.py
├── registry/
│   ├── scanners.py
│   ├── repositories.py
│   └── models.py
├── download/
│   ├── clients.py
│   ├── services.py
│   └── history.py
├── sync/
├── ui/
│   ├── api/
│   ├── frontend/
│   └── templates/
├── cli/
│   ├── commands.py
│   └── formatters.py
└── infrastructure/
    ├── storage.py
    ├── http.py
    └── scheduler.py
```
- `lib/` に共通ユーティリティを集約して循環依存を回避。
- サービス層 (`download/services.py` など) を共有し、UI/CLI/将来の自動同期から再利用可能にする。
- React プロジェクトを同居させる場合は `ui/frontend/` に配置し、ビルド成果物を `ui/templates/` 配下で FastAPI から配信する運用を推奨。
