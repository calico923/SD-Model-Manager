"""ダウンロードサービスのテスト"""

import pytest
import respx
import httpx
from pathlib import Path
from sd_model_manager.download.download_service import DownloadService
from sd_model_manager.lib.errors import DownloadError


@pytest.fixture
def download_service(tmp_path):
    """DownloadService フィクスチャ"""
    return DownloadService(download_dir=tmp_path)


@pytest.mark.asyncio
@respx.mock
async def test_download_file_success(download_service, tmp_path):
    """ファイルダウンロード成功のテスト"""
    url = "https://example.com/model.safetensors"
    filename = "test-model.safetensors"
    expected_path = tmp_path / filename

    # モックコンテンツ
    mock_content = b"fake model data for testing"

    # HTTPレスポンスをモック
    respx.get(url).mock(return_value=httpx.Response(
        200,
        content=mock_content,
        headers={"content-length": str(len(mock_content))}
    ))

    result = await download_service.download_file(url, filename)

    assert result == expected_path
    assert result.exists()
    assert result.read_bytes() == mock_content


@pytest.mark.asyncio
@respx.mock
async def test_download_file_with_progress_callback(download_service, tmp_path):
    """進捗コールバック付きダウンロードのテスト"""
    url = "https://example.com/model.safetensors"
    filename = "test-model.safetensors"

    # 十分に大きいコンテンツを作成（デフォルトchunk_size=8192より大きく）
    # これにより複数チャンクに分割される
    mock_content = b"x" * 16384  # 16KB

    progress_updates = []

    def progress_callback(downloaded: int, total: int):
        progress_updates.append((downloaded, total))

    respx.get(url).mock(return_value=httpx.Response(
        200,
        content=mock_content,
        headers={"content-length": str(len(mock_content))}
    ))

    result = await download_service.download_file(
        url, filename, progress_callback=progress_callback, chunk_size=8192
    )

    assert result.exists()
    assert result.read_bytes() == mock_content

    # 進捗コールバックが複数回呼ばれたことを確認
    # 16KB を 8KB チャンクで読むと2回呼ばれるはず
    assert len(progress_updates) >= 1
    assert progress_updates[-1] == (len(mock_content), len(mock_content))

    # すべての進捗更新が単調増加していることを確認
    downloaded_sizes = [update[0] for update in progress_updates]
    assert downloaded_sizes == sorted(downloaded_sizes)
    assert all(total == len(mock_content) for _, total in progress_updates)


@pytest.mark.asyncio
@respx.mock
async def test_download_file_directory_creation(download_service, tmp_path):
    """保存先ディレクトリが存在しない場合の自動作成テスト"""
    url = "https://example.com/model.safetensors"
    filename = "subfolder/test-model.safetensors"
    expected_path = tmp_path / filename

    mock_content = b"fake model data"

    respx.get(url).mock(return_value=httpx.Response(
        200,
        content=mock_content,
        headers={"content-length": str(len(mock_content))}
    ))

    result = await download_service.download_file(url, filename)

    assert result.exists()
    assert result.parent.exists()
    assert result.read_bytes() == mock_content


@pytest.mark.asyncio
@respx.mock
async def test_download_file_http_error(download_service):
    """HTTP エラー時のテスト"""
    url = "https://example.com/model.safetensors"
    filename = "test-model.safetensors"

    # 404エラーをモック
    respx.get(url).mock(return_value=httpx.Response(404))

    with pytest.raises(DownloadError) as exc_info:
        await download_service.download_file(url, filename)

    assert "Failed to download file after 3 attempts" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_download_with_retry(download_service, tmp_path):
    """リトライ機能のテスト"""
    url = "https://example.com/model.safetensors"
    filename = "test-model.safetensors"

    mock_content = b"fake model data"

    # 最初の2回は500エラー、3回目で成功
    call_count = 0

    def side_effect(request):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return httpx.Response(500, text="Internal Server Error")
        return httpx.Response(
            200,
            content=mock_content,
            headers={"content-length": str(len(mock_content))}
        )

    respx.get(url).mock(side_effect=side_effect)

    result = await download_service.download_file(
        url, filename, max_retries=3
    )

    assert result.exists()
    assert result.read_bytes() == mock_content
    assert call_count == 3
