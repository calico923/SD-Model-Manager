"""WebSocket エンドポイント"""

import logging
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from sd_model_manager.ui.api.progress import get_progress_manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/download/{task_id}")
async def websocket_download_progress(websocket: WebSocket, task_id: str):
    """ダウンロードプログレス WebSocket エンドポイント

    クライアントが接続すると、タスク完了（または失敗）まで
    リアルタイムでプログレス情報を配信します。
    """
    await websocket.accept()
    logger.info("WebSocket connected: task_id=%s", task_id)

    progress_manager = get_progress_manager()
    poll_interval = 0.5  # 500ms ごとに進捗をポーリング

    try:
        while True:
            progress = progress_manager.get_progress(task_id)

            if progress is None:
                # タスクが見つからない場合はエラーを送信して切断
                await websocket.send_json({
                    "type": "error",
                    "message": f"Task not found: {task_id}"
                })
                break

            # 進捗情報を配信
            await websocket.send_json({
                "type": "progress",
                "data": progress.to_dict()
            })

            # タスクが完了または失敗したら終了
            if progress.status in ["completed", "failed"]:
                logger.info(
                    "WebSocket closing: task_id=%s, status=%s",
                    task_id,
                    progress.status
                )
                break

            # 次のポーリングまで待機
            await asyncio.sleep(poll_interval)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: task_id=%s", task_id)
    except Exception as e:
        logger.error(
            "WebSocket error: task_id=%s, error=%s",
            task_id,
            str(e),
            exc_info=True
        )
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except Exception:
            pass
    finally:
        await websocket.close()
