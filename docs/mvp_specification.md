# SD-Model-Manager MVP仕様書

**バージョン**: 1.0
**対象**: 個人利用 MVP
**期間**: 実装開始～実用可能な状態

---

## 1. 概要

### プロジェクト目的
- Stable Diffusion / ComfyUI のモデル（LoRA, Checkpoint, VAE, Embedding）を効率的に管理・ダウンロード
- Web UI ベースで、ローカル・クラウド両対応（初期はローカル）
- ComfyUI-Lora-Manager と同等の使いやすさ

### MVP の位置づけ
- **対象ユーザー**: 個人利用
- **デプロイ先**: ローカルマシン（localhost:8000）
- **優先度**: 機能性 ≥ UI/UX > パフォーマンス

---

## 2. 機能要件

### 2.1 主要機能（MVP で実装）

#### (1) ローカルモデルスキャン・表示
**目的**: ローカルの既存モデルを自動認識・管理

```
【機能詳細】
- 指定フォルダの再帰的スキャン
- 対応ファイル形式の検出:
  LoRA: *.safetensors, *.ckpt, *.pt, *.pth
  Checkpoint: *.safetensors, *.ckpt, *.pt, *.pth
  VAE: *.safetensors, *.pt
  Embedding: *.safetensors, *.pt, *.bin

【表示方法】
- フォルダツリーサイドバー（ComfyUI-Lora-Manager 形式）
- グリッド/リスト表示の切替
- ファイル名、ファイルサイズ、更新日時を表示

【メタデータ】
- ファイル名
- ファイルサイズ
- 最終更新日
- ファイル形式（モデルタイプの自動判定）
- プレビュー画像（あれば。Civitai から自動取得も検討）

【UI要件】
- 起動時に自動スキャン
- 手動更新ボタン
- スキャン進捗表示
- スキャン完了後、モデル総数を表示
```

#### (2) Civitai からのダウンロード
**目的**: Civitai.com からモデルを検索・ダウンロード

```
【操作フロー】
1. Web UI の「ダウンロード」タブを開く
2. Civitai の URL またはモデル ID を入力
3. 保存先フォルダを選択
4. ダウンロード開始
5. 進捗表示（ダウンロード速度、残り時間、パーセンテージ）
6. 完了後、自動的に history.json に記録

【対応モデルタイプ】
- LoRA
- Checkpoint
- VAE
- Embedding
- （その他 Civitai で配布されているタイプ）

【ダウンロード仕様】
- 単一ダウンロードのみ（並列ダウンロード非対応）
- レジューム機能（ダウンロード途中で中断→再開可能）
- タイムアウト: 30分
- リトライ: 最大 3回（ネットワークエラー時）

【UI要件】
- URL 入力フィールド
- 保存先フォルダ選択ボタン
- ダウンロードボタン
- 進捗バー（100% 表示）
- 進捗テキスト（「2.5GB / 5.0GB (50%)」「速度: 25MB/s」「残り時間: 100秒」）
- キャンセルボタン
```

#### (3) ダウンロード履歴管理
**目的**: ダウンロード済みモデルを記録・検索

```
【保存フォーマット】
ファイル: data/download_history.json

構造:
[
  {
    "id": "unique-uuid",
    "model_type": "lora" | "checkpoint" | "vae" | "embedding",
    "name": "Model Name",
    "civitai_model_id": "123456",
    "civitai_version_id": "789012",
    "description": "Model description",
    "url": "https://civitai.com/api/download/models/...",
    "file_name": "model.safetensors",
    "file_path": "/Users/user/models/loras/model.safetensors",
    "file_size": 2147483648,
    "preview_image_url": "https://image-url.jpg",
    "downloaded_at": "2024-10-29T10:30:00Z",
    "downloaded_by_version": "0.1.0"
  },
  ...
]

【UI表示】
- 「履歴」タブに一覧表示
- 表示項目:
  - サムネイル（プレビュー画像があれば表示）
  - モデル名
  - モデルタイプ
  - ダウンロード日時
  - ファイルサイズ
  - ファイルパス

【操作】
- 履歴から再ダウンロード（URL をコピーして新規ダウンロード）
- 履歴から削除（JSON から削除）
- ファイルを開く（Finder / エクスプローラー で表示）
```

#### (4) Web UI（基本構成）
**目的**: 上記機能を提供する Web インターフェース

```
【ページレイアウト】
+─────────────────────────────────────────────+
│ Header (Logo / Title / Settings)            │
├─────────────┬───────────────────────────────┤
│             │                               │
│  Sidebar    │                               │
│ (Tabs:      │       Main Content            │
│ - Models    │                               │
│ - Download  │                               │
│ - History)  │                               │
│             │                               │
└─────────────┴───────────────────────────────┘

【各タブの内容】

Tab 1: Models（ローカルスキャン）
- フォルダツリー表示
- グリッド/リスト表示
- モデル詳細表示
- 検索フィルタ（モデル名、タイプ）

Tab 2: Download（ダウンロード）
- URL 入力フィールド
- 保存先選択
- ダウンロード開始/キャンセル
- 進捗表示
- ダウンロード完了通知

Tab 3: History（ダウンロード履歴）
- 履歴一覧（グリッド表示）
- 検索/フィルタ
- 履歴から再ダウンロード
- 削除機能
```

### 2.2 セッティング・設定（MVP段階）

```
【設定項目】
1. モデルフォルダパス（複数登録可）
   - LoRA フォルダ
   - Checkpoint フォルダ
   - VAE フォルダ
   - Embedding フォルダ

2. Civitai API キー（オプション）
   - 無料 API キーでも動作
   - 有料キーでレート制限回避

3. デフォルト保存先

【保存場所】
ファイル: .env（環境変数）またはconfig.json

例:
{
  "model_paths": {
    "lora": "/Users/user/models/loras",
    "checkpoint": "/Users/user/models/checkpoints",
    "vae": "/Users/user/models/vae",
    "embedding": "/Users/user/models/embeddings"
  },
  "civitai_api_key": "optional-api-key",
  "default_save_path": "/Users/user/models/loras"
}

【UI】
Settings ページで編集可能
初回起動時にセットアップウィザード
```

### 2.3 非実装機能（MVP後回し）

- ❌ 複数ダウンロード並列実行
- ❌ メタデータスキャナー（SHA256による逆引き）
- ❌ ComfyUI 統合（ノードへの直接適用）
- ❌ カスタムタグ・カテゴリ管理
- ❌ ユーザー評価・メモ機能
- ❌ バッチ操作（複数モデル一括削除等）
- ❌ SQLite データベース（JSON で十分）
- ❌ クラウド同期

---

## 3. 技術仕様

### 3.1 スタック

| レイヤー | 技術 | バージョン |
|---------|------|----------|
| **フロントエンド** | React | 18.x |
| | TypeScript | 5.x |
| | Vite | 5.x |
| | Tailwind CSS | 3.x |
| | shadcn/ui | Latest |
| **バックエンド** | Python | 3.9+ |
| | FastAPI | 0.100+ |
| | Pydantic | V2 |
| | httpx | (async HTTP client) |
| | python-dotenv | (環境変数) |
| **ファイルシステム** | JSON | (history.json) |
| | SQLite | (Optional, Phase 2) |

### 3.2 プロジェクト構造

```
SD-Model-Manager/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI エントリ
│   ├── config.py                  # 設定管理
│   ├── models.py                  # Pydantic models
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # エンドポイント定義
│   │   └── civitai_client.py      # Civitai API クライアント
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── downloader.py          # ダウンロード処理
│   │   ├── scanner.py             # ローカルスキャン
│   │   └── history_manager.py     # 履歴管理
│   │
│   └── static/                    # Frontend ビルド出力先
│       └── dist/
│
├── frontend/                      # React プロジェクト
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ModelsTab.tsx
│   │   │   ├── DownloadTab.tsx
│   │   │   ├── HistoryTab.tsx
│   │   │   └── Settings.tsx
│   │   ├── pages/
│   │   ├── api/
│   │   │   └── client.ts          # API クライアント
│   │   ├── types/
│   │   │   └── index.ts           # 型定義
│   │   ├── styles/
│   │   │   └── globals.css
│   │   └── main.tsx
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── package.json
│
├── data/
│   └── download_history.json      # ダウンロード履歴
│
├── tests/
│   ├── test_api.py
│   ├── test_downloader.py
│   └── test_scanner.py
│
├── .env.example
├── .gitignore
├── requirements.txt               # Python 依存
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

### 3.3 API エンドポイント

#### Models タブ

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| `GET` | `/api/models/scan` | ローカルモデルをスキャン |
| `GET` | `/api/models` | スキャン済みモデル一覧取得 |
| `GET` | `/api/models/{model_id}` | モデル詳細取得 |

**レスポンス例**:
```json
// GET /api/models
{
  "models": [
    {
      "id": "unique-file-hash",
      "name": "model.safetensors",
      "type": "lora",
      "size": 2147483648,
      "path": "/path/to/model.safetensors",
      "updated_at": "2024-10-29T10:30:00Z"
    }
  ],
  "total_count": 42,
  "scan_complete": true
}
```

#### Download タブ

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| `POST` | `/api/download/start` | ダウンロード開始 |
| `GET` | `/api/download/progress/{download_id}` | ダウンロード進捗 |
| `POST` | `/api/download/cancel/{download_id}` | ダウンロード中止 |

**リクエスト例**:
```json
// POST /api/download/start
{
  "url": "https://civitai.com/api/download/models/123456",
  "save_path": "/Users/user/models/loras"
}
```

**レスポンス例**:
```json
{
  "download_id": "uuid-xxx",
  "model_name": "Some LoRA",
  "status": "downloading",
  "progress": {
    "percent": 45.5,
    "downloaded": 2147483648,
    "total": 5368709120,
    "speed": 26214400,
    "eta_seconds": 120
  }
}
```

#### History タブ

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| `GET` | `/api/history` | ダウンロード履歴一覧 |
| `DELETE` | `/api/history/{history_id}` | 履歴から削除 |

**レスポンス例**:
```json
// GET /api/history
[
  {
    "id": "uuid-xxx",
    "model_type": "lora",
    "name": "Some LoRA",
    "civitai_model_id": "123456",
    "file_size": 2147483648,
    "downloaded_at": "2024-10-29T10:30:00Z",
    "preview_image_url": "https://image-url.jpg"
  }
]
```

#### Settings

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| `GET` | `/api/settings` | 設定取得 |
| `POST` | `/api/settings` | 設定更新 |

---

## 4. UI/UX 設計

### 4.1 デザイン方針

- **参考**: ComfyUI-Lora-Manager
- **フレームワーク**: shadcn/ui (Tailwind CSS ベース)
- **カラースキーム**: ダークモード対応
- **レスポンシブ**: デスクトップ最適化（タブレット以下は後回し）

### 4.2 各ページのワイヤーフレーム

#### Models タブ
```
┌─────────────────────────────────────────┐
│ 📁 Models                  [Scan] [🔄]  │
├──────────┬────────────────────────────────┤
│ 📁 Loras │ [Grid View] [List View]        │
│   📁 All │                                │
│   📁 Tag1│ ┌──────┐ ┌──────┐ ┌──────┐   │
│   📁 Tag2│ │Model │ │Model │ │Model │   │
│          │ │ (1)  │ │ (2)  │ │ (3)  │   │
│ 📁 Check │ └──────┘ └──────┘ └──────┘   │
│ 📁 VAE   │                                │
│ 📁 Embed │                                │
└──────────┴────────────────────────────────┘
```

#### Download タブ
```
┌─────────────────────────────────────────┐
│ ⬇️  Download                             │
├─────────────────────────────────────────┤
│                                         │
│ Civitai URL or Model ID:                │
│ [________________]  [Select Folder]    │
│                                         │
│ Save to: /Users/user/models/loras      │
│                                         │
│                    [Cancel] [Download]  │
│                                         │
│ Progress:                               │
│ ████████████░░░░░░░░░░  45.5%          │
│                                         │
│ Speed: 25MB/s                           │
│ Remaining: 100 seconds                  │
│ Downloaded: 2.0GB / 5.0GB              │
│                                         │
└─────────────────────────────────────────┘
```

#### History タブ
```
┌─────────────────────────────────────────┐
│ 📋 History            [Search] [Filter] │
├─────────────────────────────────────────┤
│ ┌──────┬──────────────┬────────┬──────┐ │
│ │ Img  │ Name         │ Type   │ Date │ │
│ ├──────┼──────────────┼────────┼──────┤ │
│ │[IMG] │ Model 1      │ LoRA   │ 10/29│ │
│ │      │ 2.5GB        │        │ 10:30│ │
│ │      │ /path/...    │ [•••]  │      │ │
│ ├──────┼──────────────┼────────┼──────┤ │
│ │[IMG] │ Model 2      │ Check  │ 10/28│ │
│ │      │ 5.0GB        │        │ 14:20│ │
│ │      │ /path/...    │ [•••]  │      │ │
│ └──────┴──────────────┴────────┴──────┘ │
│                                         │
└─────────────────────────────────────────┘
```

---

## 5. 実装フェーズ

### Phase 1: 基盤構築（1-2週間）
```
優先度: 🔴 Critical

実装内容:
  - FastAPI アプリケーション構造
  - React + Vite + TypeScript セットアップ
  - 設定管理システム
  - ローカルスキャン機能（バックエンド）
  - Models タブの UI（フロントエンド）

テスト:
  - スキャン機能の正確性

完了基準:
  - ✅ ローカルモデルをスキャンして表示可能
  - ✅ フォルダツリーで分類表示可能
  - ✅ 管理画面で設定変更可能
```

### Phase 2: ダウンロード機能（2-3週間）
```
優先度: 🔴 Critical

実装内容:
  - Civitai API クライアント
  - ダウンロード処理実装
  - WebSocket または Polling でプログレス表示
  - Download タブ UI
  - エラーハンドリング

テスト:
  - 各モデルタイプのダウンロード
  - エラーケース（404、タイムアウト等）
  - レジューム機能

完了基準:
  - ✅ Civitai URL からダウンロード可能
  - ✅ 進捗がリアルタイムで表示される
  - ✅ エラー時に適切なメッセージ表示
```

### Phase 3: 履歴管理 & 仕上げ（1-2週間）
```
優先度: 🔴 Critical

実装内容:
  - ダウンロード履歴の JSON 保存
  - History タブ UI
  - 履歴から再ダウンロード
  - UI/UX 仕上げ（shadcn/ui コンポーネント最適化）

テスト:
  - 履歴の永続化
  - UI の応答性
  - 全体的なワークフローテスト

完了基準:
  - ✅ ダウンロード履歴が保存・表示される
  - ✅ 全機能が正常に動作する
  - ✅ UI が ComfyUI-Lora-Manager 同等
```

---

## 6. 成功基準（MVP完了時）

### 機能面
- ✅ ローカルモデル（LoRA, Checkpoint, VAE, Embedding）をスキャン・表示可能
- ✅ Civitai から全モデルタイプをダウンロード可能
- ✅ ダウンロード進捗をリアルタイムで表示
- ✅ ダウンロード履歴を JSON で管理・表示
- ✅ エラーハンドリング完備（ネットワーク、404等）

### UI/UX 面
- ✅ ComfyUI-Lora-Manager と同等の使いやすさ
- ✅ 応答時間 <500ms
- ✅ モバイル・タブレット（レスポンシブ）対応

### 品質面
- ✅ テストカバレッジ >70%
- ✅ エラーメッセージが明確
- ✅ ドキュメント完備（README.md、セットアップガイド）

### リリース基準
- ✅ 1人で快適に使える（バグなし）
- ✅ セットアップが簡単（`pip install` + `npm run dev`）
- ✅ ローカル環境で 30分以上安定稼働

---

## 7. 今後の拡張（Phase 4+）

- 複数ダウンロード並列実行
- SQLite データベース化
- メタデータスキャナー（SHA256 逆引き）
- ComfyUI ワークフロー統合
- カスタムタグ・カテゴリ
- クラウド同期
- Electron/Tauri でのデスクトップアプリ化
- 複数言語対応

---

**以上、MVP仕様書**
