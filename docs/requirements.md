# SD-Model-Manager 要件定義書

## プロジェクト概要

SD-Model-Manager は、Stable Diffusion および ComfyUI のモデル管理を統一・効率化するための統合プラットフォームです。複数の参考実装（ComfyUI-Lora-Manager、paperspace-civitiai-downloader、civitiai-tools）の知見を活用し、モデルの検索、ダウンロード、メタデータ管理、ワークフロー統合を一元化します。

## 参考リポジトリと特徴

### 1. ComfyUI-Lora-Manager
- **用途**: ComfyUI向けのLoRA管理専門ツール
- **主要機能**:
  - Web UI（http://localhost:8188/loras）
  - LoRAモデルの検索・ダウンロード
  - Civitai APIとの連携
  - カスタムタグによるモデル分類
  - ワークフロー統合とワンクリック適用
  - ブラウザ拡張機能
  - メタデータアーカイブ対応

### 2. paperspace-civitiai-downloader
- **用途**: Civitai.comからのモデルダウンロード
- **主要機能**:
  - SHA256ハッシュベースのメタデータ取得
  - バージョン情報の自動抽出
  - 既存モデルからのメタデータ逆引き
  - ダウンロード履歴管理
  - CSV形式でのメタデータ出力
  - レジューム対応ダウンロード

### 3. civitiai-tools (civitai-downloader-v2)
- **用途**: 高性能・セキュアなモデルダウンローダー
- **主要設計**:
  - 3層アーキテクチャ（API・Core・Data層）
  - セキュリティファースト（SafeTensors優先）
  - Pydantic V2による型安全性
  - 統一エラー処理システム
  - テスト駆動開発（TDD）
  - 大規模データセット対応（10,000+モデル）

## 対象ユーザーと使用シーン

- **主要ユーザー**: Stable Diffusion / ComfyUI ユーザー
- **優先対象**: LoRAモデル管理
- **使用環境**: ローカルマシン（単一マシン想定）

## MVP段階でのユースケース

### MVP UC-1: Civitaiからのダウンロード
ユーザーが Civitai URL を入力して、Web UI からワンクリックでLoRAモデルをダウンロード可能にする。

### MVP UC-2: ダウンロード履歴管理
ダウンロードしたモデルの情報（URL、ダウンロード日時、ファイル名）を JSON で記録し、履歴から再ダウンロード可能にする。

### MVP UC-3: シンプルなメタデータ表示
ダウンロード済みモデルの基本情報（名前、説明、バージョン）を Web UI で表示する。

## MVP実装計画

### MVP Phase 1: 基盤システム・Web UI基盤（必須）
- [ ] Python プロジェクト構造（src/、tests/、docs/）
- [ ] FastAPI による Web API の最小実装
- [ ] 設定管理（.env 対応）
- [ ] 基本的なエラーハンドリング
- [ ] Pydantic による基本データモデル
  - `LoraModel`: 名前、URL、ダウンロード日時、ファイルパス
  - `DownloadHistory`: ダウンロード履歴
- [ ] 簡単な HTML/JS による Web UI フロントエンド（CDN ライブラリ利用可）

### MVP Phase 2: ダウンロード機能（必須）
- [ ] Civitai API クライアントの最小実装
  - URLからのモデル情報取得（名前、説明、ダウンロードURL）
  - URLバリデーション
- [ ] 基本的なダウンロード実装
  - Civitai URL からのモデルダウンロード
  - 進捗表示（基本的なパーセンテージ）
  - エラーハンドリング（基本）
- [ ] ダウンロード履歴を JSON ファイルで管理
  - ダウンロード完了時に履歴に自動追加
  - 履歴ファイル：`data/download_history.json`

### MVP Phase 3: Web UI（ダウンロード & 履歴表示）
- [ ] トップページ（ダウンロードフォーム）
  - URL入力フィールド
  - ダウンロードボタン
  - 進捗表示
- [ ] 履歴ページ
  - ダウンロード済みモデル一覧
  - 基本情報表示（名前、URL、日時）
  - 削除機能（オプション）

## 非MVP（後回し）

以下は MVP 後の段階で実装予定：

### Phase 4: メタデータスキャナー
- ローカルモデルファイルからのメタデータ自動抽出
- SHA256ハッシュベースの検索
- モデル一覧スキャン

### Phase 5: 高度な検索・フィルタリング
- Civitai 検索機能の統合
- タグによるフィルタリング
- カスタムタグ設定

### Phase 6: SQLite DB化
- メタデータを SQLite に移行
- 高速検索対応

### Phase 7: ComfyUI統合
- ComfyUI ノード実装
- ワンクリック統合

### Phase 8: セキュリティ強化
- SafeTensors 検証
- API キー管理
- Pickle ファイル制限

## MVP段階の非機能要件

### パフォーマンス（MVP）
- Web UI 応答: <500ms
- ダウンロード: ネットワーク速度に依存
- 初期数十個のモデル管理に対応（スケーリングは後段階）

### セキュリティ（MVP）
- Civitai APIキーを環境変数で管理
- ダウンロードソースの基本的な検証（URL形式確認）
- エラーメッセージに機密情報を含まない

### 信頼性（MVP）
- ダウンロードエラー時の基本的なリトライ（最大3回）
- ダウンロード失敗時のエラーメッセージ表示
- 履歴ファイルの自動バックアップ（オプション）

### スケーラビリティ（後段階）
- 大規模モデル管理は Phase 6+ で対応

## 技術仕様（MVP）

### スタック
- **言語**: Python 3.9+
- **Web フレームワーク**: FastAPI
- **フロントエンド**: HTML + JavaScript（CDN ライブラリ活用、初期は Vanilla JS でも OK）
- **データモデル**: Pydantic V2
- **HTTP クライアント**: httpx または requests
- **設定管理**: python-dotenv
- **ファイル管理**: JSON ファイル

### MVP プロジェクト構造
```
SD-Model-Manager/
├── src/
│   ├── main.py                  # FastAPI アプリケーションエントリ
│   ├── config.py                # 設定管理
│   ├── models.py                # Pydantic モデル定義
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py            # エンドポイント定義
│   │   └── civitai_client.py    # Civitai API クライアント
│   ├── core/
│   │   ├── __init__.py
│   │   ├── downloader.py        # ダウンロード処理
│   │   └── history_manager.py   # 履歴管理
│   └── static/
│       ├── index.html           # Web UI
│       ├── styles.css
│       └── script.js
├── data/
│   └── download_history.json    # ダウンロード履歴
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_downloader.py
├── docs/
│   └── requirements.md
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

### MVP API エンドポイント

#### エンドポイント一覧
| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| `POST` | `/api/download` | Civitai URL からダウンロード開始 |
| `GET` | `/api/history` | ダウンロード履歴取得 |
| `GET` | `/api/model/{model_id}` | モデル情報取得 |
| `DELETE` | `/api/history/{model_id}` | 履歴から削除 |

#### リクエスト/レスポンス例
```json
// POST /api/download
Request:
{
  "url": "https://civitai.com/models/123/some-lora",
  "save_path": "/path/to/models/loras"
}

Response:
{
  "download_id": "uuid",
  "model_name": "Some LoRA",
  "status": "downloading",
  "progress": 45.5
}

// GET /api/history
Response:
[
  {
    "id": "uuid",
    "name": "Some LoRA",
    "url": "https://civitai.com/models/123",
    "file_path": "/path/to/models/loras/some-lora.safetensors",
    "downloaded_at": "2024-10-29T10:30:00Z"
  }
]
```

## MVP制約事項

1. **Civitai API**: 無料API使用（レート制限あり）
2. **ダウンロード対象**: LoRA形式のみ（MVP段階）
3. **ローカルストレージ**: ユーザーが事前に保存先ディレクトリを確保
4. **単一マシン**: 複数マシン同期は非対応

## MVP成功基準

実装完了時点で以下をクリア：

1. ✅ FastAPI サーバーが起動し、Web UI にアクセス可能
2. ✅ Civitai URL を入力して、LoRA をダウンロード可能
3. ✅ ダウンロード履歴が JSON に記録される
4. ✅ 履歴ページで過去のダウンロード情報を表示可能
5. ✅ 基本的なエラーハンドリング（ネットワークエラー等）
6. ✅ 簡単なテストが存在（最低限 API ルートのテスト）
