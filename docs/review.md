# docs/review.md

## レビュー対象
- `docs/mvp_specification.md`
- `docs/requirements.md`

## 指摘事項と調整提案
- **Python バージョン表記の不一致**  
  - `docs/mvp_specification.md:247` および `docs/requirements.md:141` に Python 3.9+ とあるが、リポジトリ方針は 3.11+。現行方針に合わせて修正する。
- **ディレクトリ構造ガイドとの乖離**  
  - `docs/mvp_specification.md:259-284`, `docs/requirements.md:151-169` の構成案が「`src/sd_model_manager/` に runtime コード集約」という規約に沿っていない。新構成案へ差し替え推奨（後述）。
- **MVP スコープの矛盾**  
  - `docs/mvp_specification.md:552-554` は LoRA/Checkpoint/VAE/Embedding 全対応を前提としている一方、`docs/requirements.md:222-226` は LoRA 限定。MVP では LoRA に絞り、残りは後続フェーズへ。
- **SQLite 採用タイミングの混乱**  
  - `docs/mvp_specification.md:231` では「非実装」、`docs/mvp_specification.md:253` では Phase 2 オプション。バックログ側に寄せる等、記載を整理する。
- **デバイス対応の矛盾**  
  - `docs/mvp_specification.md:417` でモバイル後回しとしながら、`docs/mvp_specification.md:559-561` で MVP 成功条件にモバイル対応を含めている。デスクトップ優先へ統一。
- **フロントエンド技術選定の揺れ**  
  - `docs/mvp_specification.md:242-252` で React + shadcn/ui を想定する一方、`docs/requirements.md:143` では CDN ベースの軽量 UI を推奨。MVP では軽量構成を採り、需要に応じて React/Vite へ移行する段階アプローチが現実的。

## 推奨技術スタック
- **バックエンド / ドメインロジック**: Python 3.12, FastAPI, Pydantic v2, httpx  
  - Python 3.12 は 3.11 より GC/パフォーマンスが向上し、主要ライブラリも対応済み。3.13 はリリース直後で安定性リスクあり。
- **フロントエンド (MVP)**: FastAPI + Jinja + HTMX/Alpine.js 等の軽量構成  
  - 初期実装を素早く行い、将来ドラッグ&ドロップや複雑 UI が必要になった段階で React/Vite + TypeScript へ移行。
- **CLI / 自動化タスク**: Python (Typer など) で API とロジックを共有。

## 他スタックを選ばない理由
- **Rust / Go**: 高性能だがモデル管理領域のライブラリが乏しく、学習コストが高い。UI・CLI を別言語に分ける必要があり保守が複雑化。
- **Node.js/TypeScript バックエンド**: フロントと統一できるが、モデルファイル操作や ML 関連ライブラリの充実度で Python に劣る。
- **Kotlin/Java**: 大規模向けで MVP の開発速度が低下。マルチ言語管理が前提となり小規模チームには過剰。
- **Elixir/Phoenix, Deno/Bun, 新興言語**: エコシステムが未成熟で、モデル管理ドメインに必要な資産・情報が不足。
- **Electron/Tauri 先行採用**: 初期コストが高く、Web UI を安定させてから段階的にデスクトップ化する方が現実的。

## UI に関するライセンス注意
- ComfyUI-Lora-Manager (GPL-3.0) のコードやスタイルは直接流用しない。UX のみ参考にし、実装は MIT 系の shadcn/ui 等を用いて独自に構築する。

## 推奨ディレクトリ構造（抜粋）
```
src/sd_model_manager/
├── __main__.py            # CLI エントリ
├── config.py
├── logging.py
├── lib/                   # 汎用ユーティリティ
│   └── filesystem.py
├── registry/              # モデルスキャン・登録ドメイン
│   ├── scanners.py
│   ├── repositories.py
│   └── models.py
├── download/
│   ├── clients.py         # Civitai API クライアント
│   ├── services.py        # ダウンロード処理
│   └── history.py
├── sync/                  # 将来拡張（ポーリング等）
├── ui/
│   ├── api/               # FastAPI ルータ
│   ├── frontend/          # React/Vite を導入する場合
│   └── templates/         # 軽量 UI 用 HTML
├── cli/
│   ├── commands.py
│   └── formatters.py
└── infrastructure/
    ├── storage.py
    ├── http.py
    └── scheduler.py
```
- ドメイン単位でモジュールを整理し、UI・CLI から共通サービスを利用できる構造とする。
- 将来的に React を導入する場合、ビルド成果物は `ui/templates/` に配置し FastAPI 側で提供。

## スコープ調整案（MVP）
1. **対象モデル**: LoRA のみに絞る。他タイプは Phase 2+ に追加。
2. **UI 機能**: 「ダウンロード」「履歴」の基本画面と進捗表示に集中し、フォルダツリーやドラッグ&ドロップは後続フェーズ。
3. **デバイス対応**: MVP 成功基準からモバイル対応を外し、デスクトップ向けに最適化。
4. **技術スタック**: 初期は軽量 UI、ニーズ増大に応じて React/Vite へ段階移行。

## 今後のタスク例
- ドキュメント内のバージョン・構成・スコープ表記を現行方針に合わせて修正。
- Python 3.12 仮想環境で主要依存の動作検証。
- MVP 実装ロードマップの再整理（必須機能と後続機能の線引き）。
