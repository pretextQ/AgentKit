"""向量存储管理器 - 封装 ChromaDB VectorStore 操作"""

from typing import List

from langchain_core.documents import Document
from langchain_chroma import Chroma
from loguru import logger

from app.config import config
from app.core.chroma_client import chroma_manager
from app.services.vector_embedding_service import vector_embedding_service


COLLECTION_NAME = "biz"


class VectorStoreManager:
    """向量存储管理器"""

    def __init__(self):
        self.vector_store = None
        self.collection_name = COLLECTION_NAME
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        try:
            client = chroma_manager.get_client()

            self.vector_store = Chroma(
                client=client,
                collection_name=self.collection_name,
                embedding_function=vector_embedding_service,
                collection_metadata={"hnsw:space": "cosine"},
            )

            logger.info(
                f"ChromaDB VectorStore 初始化成功, "
                f"collection: {self.collection_name}"
            )

        except Exception as e:
            logger.error(f"VectorStore 初始化失败: {e}")
            raise

    def add_documents(self, documents: List[Document]) -> List[str]:
        try:
            import time
            import uuid
            start_time = time.time()

            ids = [str(uuid.uuid4()) for _ in documents]

            result_ids = self.vector_store.add_documents(documents, ids=ids)

            elapsed = time.time() - start_time
            logger.info(
                f"批量添加 {len(documents)} 个文档到 VectorStore 完成, "
                f"耗时: {elapsed:.2f}秒, 平均: {elapsed/len(documents):.2f}秒/个"
            )
            return result_ids
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            raise

    def delete_by_source(self, file_path: str) -> int:
        try:
            client = chroma_manager.get_client()
            collection = client.get_collection(self.collection_name)

            results = collection.get(where={"source": file_path})
            if results and results.get("ids"):
                collection.delete(ids=results["ids"])
                deleted_count = len(results["ids"])
            else:
                deleted_count = 0

            logger.info(f"删除文件旧数据: {file_path}, 删除数量: {deleted_count}")
            return deleted_count

        except Exception as e:
            logger.warning(f"删除旧数据失败 (可能是首次索引): {e}")
            return 0

    def get_vector_store(self) -> Chroma:
        return self.vector_store

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            logger.debug(f"相似度搜索完成: query='{query}', 结果数={len(docs)}")
            return docs
        except Exception as e:
            logger.error(f"相似度搜索失败: {e}")
            return []


vector_store_manager = VectorStoreManager()
