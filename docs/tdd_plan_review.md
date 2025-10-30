# TDD Plan Review

## 評価対象
- `docs/tdd_plan.md` Phase 1（基盤システム構築）の RED/GREEN/REFACTOR 計画

## 主な指摘事項
- `tests/sd_model_manager/registry/test_lora_model.py` が `ValueError` を期待しているが、Pydantic v2 の必須項目欠如や `HttpUrl` バリデーションは `pydantic.ValidationError` を送出するため、GREEN フェーズの実装と整合しない。例外型を揃えるか、カスタム検証で `ModelValidationError` を投げる仕様に合わせて調整が必要。
- LoRA バリデーションで `.safetensors` のみを許容するテスト（docs/tdd_plan.md:295-301）が将来の拡張子対応（.ckpt, .pt 等）と矛盾。MVP スコープでも `.safetensors` 固定でよいか再検討し、テスト条件を柔軟にすることを推奨。
- Phase 1 で `/api/download` が未実装にもかかわらず、`tests/sd_model_manager/ui/api/test_error_handling.py` で 422 応答を期待している。Endpoint がないため RED にならないので、ダミールートで `ModelValidationError` を発生させるか Phase 2 に移すべき。
- CORS を `OPTIONS /health` で検証するテストは `TestClient` がプリフライト用のヘッダを送らないため失敗しがち。`Origin`/`Access-Control-Request-Method` を明示するか、CORS 検証そのものを後段フェーズに移すのが現実的。
- 複数テストが `sd_model_manager.ui.api.routes.app` を直接 import しており、Phase 1.11 で導入した `create_app()` を使う構成に揃っていない。テストと CLI 起動のコードパスを `create_app()` に統一すべき。

## 妥当と考えられるテスト
- `tests/sd_model_manager/test_sample.py`: pytest セットアップ確認として適切。
- `tests/sd_model_manager/test_config.py`: `.env` 読み込み、デフォルト値、ディレクトリ作成をカバーし TDD サイクルに有効。
- `tests/sd_model_manager/lib/test_errors.py`: カスタム例外のコード・詳細情報を確認するテストとして有効（`ModelValidationError` 名称への調整済み）。

## 推奨対応
1. LoRA モデルテストの例外期待値を `pydantic.ValidationError` または `ModelValidationError` に揃え、バリデーション仕様と一致させる。
2. `.safetensors` 固定のバリデーション条件を見直し、拡張子の許容範囲をテストに反映。
3. `/api/download` に依存するエラーハンドリングテストは Phase 2 へ移動、もしくは仮ルートを定義。
4. CORS ヘッダ検証はプリフライト前提のヘッダを付与した上でテストするか、初期フェーズでは範囲外とする。
5. 全ての API テストを `create_app()` ファクトリ経由でアプリを生成する形に統一し、起動コードとテストの一貫性を高める。

---

## 追加レビュー（Phase 2-3）

### 評価対象
- `docs/tdd_plan.md` Phase 2（ダウンロード機能）および Phase 3（履歴管理 & 仕上げ）の RED/GREEN 以降の計画

### 主な指摘事項
- docs/tdd_plan.md:1566 — `DownloadRequest` の `url` が `str` のままのため FastAPI のバリデーションが働かず、RED テストで期待している 400 応答が再現できません。`HttpUrl` 型にするか、同期ハンドラ内で正規化・検証して 4xx を返す設計にしてください（422 を許容する想定でも可）。
- docs/tdd_plan.md:1554 — `uuid.uuid4()` を使用しているのに `uuid` の import が抜けています。実装時に `NameError` となるので忘れずに追加する必要があります。
- docs/tdd_plan.md:1600 — バックグラウンドタスク `execute_download` が本物のダウンロード処理を即時実行する構成のため、RED テストで実際にネットワークアクセスが発生します。依存性注入で `DownloadService` を差し替えるか、テスト中はタスクをモックする手順を組み込んで TDD を安全に回せるようにしてください。
- docs/tdd_plan.md:2219 — 履歴 API の RED テストが事前データ投入を行わず、`status_code in [200, 404]` など曖昧な期待値になっているため、期待するレスポンスが検証できません。`HistoryService` をスタブして確実に 200 を返す流れを作り、レスポンス本文まで検証する内容に改めることを推奨します。
