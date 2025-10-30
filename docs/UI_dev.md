# UI 開発メモ（LoRA ダウンロード履歴ビュー）

## 目的
- MVP で「ダウンロード済みモデルを一覧で確認できる UI」を提供する。
- 既存 CLI 版に不足している視覚的な履歴管理を補い、ダウンロードフローの UX を向上させる。
- 参考実装として `reference_git_clones/civitiai-tools/civitai-downloader-v2` にある React UI（特にサイドバー／一覧表示）を再利用する。

## 参考リポジトリから流用するパーツ
- 左側タブ（サイドバー）: `reference_git_clones/civitiai-tools/civitai-downloader-v2/src/web/components/layout/Sidebar.tsx`
- メインレイアウト: `.../src/web/components/layout/MainLayout.tsx`
- モデル一覧モック: `.../src/web/mockups/LocalLibrary.tsx`, `.../src/web/pages/LocalModels.tsx`
- 共通スタイル／ユーティリティ: `.../src/web/main.tsx`, `.../src/web/App.tsx`, `.../src/web/components/common/SearchBar.tsx`

これらは Tailwind 風のクラスや `lucide-react` アイコンを利用しているため、再利用時は該当依存関係を `package.json` に加える想定で検討する。

## 実装ステップ案
1. **UI プロジェクト雛形**  
   - `src/sd_model_manager/ui/frontend/` に Vite + React (TypeScript) ベースのプロジェクト構成を用意。  
   - ルーティングは `react-router-dom`、スタイルは Tailwind または軽量な CSS Modules を利用。  
   - 左サイドバーのタブを上記参考コードから移植し、`LoRA / Checkpoint / VAE / Embedding` を縦並びで表示。

2. **履歴一覧コンポーネント**  
   - Phase 3 の DownloadHistory API と連携する `HistoryList` コンポーネントを作成。  
   - `GET /api/history` のレスポンスを `react-query` などで取得し、カテゴリ別（タブで切替）にフィルタして表示。  
   - 各行（カード）にモデル名、ファイル名、サイズ、ダウンロード日時、再ダウンロード／削除アクションを配置。

3. **API 連携**  
   - Phase 2.7 で実装予定の `/api/download` から返る `task_id` を UI で受け取り、進捗表示や完了後の自動リフレッシュに利用。  
   - Phase 3.6 の履歴 API から得られるデータ構造（`DownloadHistory`）と UI の表示項目を照合し、必要なら追加フィールドを検討。

4. **TDD / テスト方針**  
   - React Testing Library でコンポーネント単体テスト（タブ切替、データレンダリング、ボタン押下イベント）を Phase 3.9 の RED として書く。  
   - Phase 3.10 で Playwright による E2E（サイドタブ→履歴表示→削除）を計画。  
   - WebSocket の進捗連携は Phase 2.8 の実装後に追加入力。

## Phase 2-3 への組み込み提案
- **Phase 2.6/2.7（ダウンロード API）**  
  - UI から呼び出すことを前提に API のリクエスト/レスポンス形式を確定する。  
  - `DownloadRequest` では URL バリデーション（`HttpUrl`）を導入し、UI 側のエラー表示仕様も合わせて設計。

- **Phase 2.8（WebSocket 進捗）**  
  - UI の進捗表示コンポーネントをこのタイミングで追加。サイドバー上部に進行中タスク数を表示するなど、ComfyUI の UX を参考にする。

- **Phase 3.5/3.6（履歴 API）**  
  - UI が利用する CRUD エンドポイントのレスポンスフォーマットを確定し、`HistoryService` の検索・フィルタロジックを揃える。  
  - UI テスト用に固定データを返すモックエンドポイントや fixtures を用意。

- **Phase 3.9（History タブ UI 実装）**  
  - 本ドキュメントの実装ステップに従って React コンポーネントを組み込み、TDD で検証。  
  - 左タブレイアウトを採用し、トップレベルのナビゲーションはサイドバーに集約。

- **Phase 3.10（E2E テスト）**  
  - Playwright で「モデルダウンロード → 履歴自動保存 → 左タブから該当カテゴリを開く → 一覧表示確認」のフローをカバー。

## 次のアクション
1. `docs/tdd_plan.md` の Phase 3.9 セクションへ本方針を反映し、左タブ UI とコンポーネント構成を明記する。  
2. `package.json` (未作成なら追加) およびフロントエンドセットアップ手順を整理し、`tailwindcss`, `react-router-dom`, `@tanstack/react-query`, `lucide-react` など必要な依存を洗い出す。  
3. Playwright など E2E ツールの導入手順を `docs/` 配下に追記し、Phase 3.10 のテストがスムーズに実行できる環境を準備する。
