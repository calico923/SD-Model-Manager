"""プログレス状態管理モジュール"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ProgressInfo:
    """ダウンロードプログレス情報"""
    task_id: str
    filename: str
    total_bytes: int = 0
    downloaded_bytes: int = 0
    percentage: int = 0
    status: str = "started"  # started, downloading, completed, failed
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "task_id": self.task_id,
            "filename": self.filename,
            "total_bytes": self.total_bytes,
            "downloaded_bytes": self.downloaded_bytes,
            "percentage": self.percentage,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class ProgressManager:
    """プログレス状態の一元管理（In-Memory）"""

    def __init__(self):
        """初期化"""
        self._tasks: dict[str, ProgressInfo] = {}
        logger.debug("ProgressManager initialized")

    def create_task(self, task_id: str, filename: str, total_bytes: int = 0) -> ProgressInfo:
        """新しいタスクを作成"""
        progress = ProgressInfo(
            task_id=task_id,
            filename=filename,
            total_bytes=total_bytes,
            status="started"
        )
        self._tasks[task_id] = progress
        logger.info("Task created: task_id=%s, filename=%s", task_id, filename)
        return progress

    def update_progress(self, task_id: str, downloaded_bytes: int, total_bytes: int) -> Optional[ProgressInfo]:
        """プログレスを更新"""
        if task_id not in self._tasks:
            logger.warning("Task not found: task_id=%s", task_id)
            return None

        progress = self._tasks[task_id]
        progress.downloaded_bytes = downloaded_bytes
        progress.total_bytes = total_bytes
        progress.percentage = int((downloaded_bytes / total_bytes * 100)) if total_bytes > 0 else 0
        progress.status = "downloading"

        return progress

    def complete_task(self, task_id: str) -> Optional[ProgressInfo]:
        """タスクを完了"""
        if task_id not in self._tasks:
            logger.warning("Task not found: task_id=%s", task_id)
            return None

        progress = self._tasks[task_id]
        progress.status = "completed"
        progress.percentage = 100
        progress.completed_at = datetime.now()
        logger.info("Task completed: task_id=%s", task_id)

        return progress

    def fail_task(self, task_id: str, error_message: str) -> Optional[ProgressInfo]:
        """タスクを失敗状態に"""
        if task_id not in self._tasks:
            logger.warning("Task not found: task_id=%s", task_id)
            return None

        progress = self._tasks[task_id]
        progress.status = "failed"
        progress.error_message = error_message
        progress.completed_at = datetime.now()
        logger.error("Task failed: task_id=%s, error=%s", task_id, error_message)

        return progress

    def get_progress(self, task_id: str) -> Optional[ProgressInfo]:
        """タスクの進捗情報を取得"""
        return self._tasks.get(task_id)

    def delete_task(self, task_id: str) -> bool:
        """タスクを削除（クリーンアップ）"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            logger.debug("Task deleted: task_id=%s", task_id)
            return True
        return False


# グローバルプログレスマネージャー
_progress_manager: Optional[ProgressManager] = None


def get_progress_manager() -> ProgressManager:
    """プログレスマネージャーのシングルトン取得"""
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = ProgressManager()
    return _progress_manager
