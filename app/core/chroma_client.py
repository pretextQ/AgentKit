"""ChromaDB 客户端工厂模块"""

import chromadb
from chromadb.config import Settings
from loguru import logger

from app.config import config


class ChromaClientManager:
    """ChromaDB 客户端管理器"""

    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=config.chroma_persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )
        logger.info(f"ChromaDB 初始化成功, 数据目录: {config.chroma_persist_directory}")

    def get_client(self) -> chromadb.ClientAPI:
        return self._client

    def health_check(self) -> bool:
        try:
            self._client.heartbeat()
            return True
        except Exception as e:
            logger.error(f"ChromaDB 健康检查失败: {e}")
            return False


chroma_manager = ChromaClientManager()
