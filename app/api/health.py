"""健康检查接口"""

from typing import Any
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.config import config
from app.core.chroma_client import chroma_manager
from loguru import logger

router = APIRouter()


@router.get("/health")
async def health_check():
    
    """健康检查接口
    检查服务状态和数据库连接状态
    
    Returns:
        JSONResponse: 健康检查结果
    """
    # 检查服务基本状态
    health_data: dict[str, Any] = {  # pyright: ignore[reportExplicitAny]
        "service": config.app_name,
        "version": config.app_version,
        "status": "healthy"
    }
    
    # 检查 ChromaDB 连接状态
    try:
        chroma_healthy = chroma_manager.health_check()
        chroma_status: str = "connected" if chroma_healthy else "disconnected"
        chroma_message: str = "ChromaDB 连接正常" if chroma_healthy else "ChromaDB 连接异常"
        health_data["chroma"] = {
            "status": chroma_status,
            "message": chroma_message
        }
    except Exception as e:
        logger.warning(f"ChromaDB 健康检查失败: {e}")
        health_data["chroma"] = {
            "status": "error",
            "message": f"ChromaDB 检查失败: {str(e)}"
        }
    
    # 判断整体健康状态
    overall_status = "healthy"
    status_code = 200
    
    # 如果 ChromaDB 不可用，服务降级（仍可提供基本服务）
    if health_data["chroma"]["status"] != "connected":
        overall_status = "degraded"
        status_code = 503
        health_data["error"] = "向量数据库不可用"
    
    health_data["status"] = overall_status
    
    return JSONResponse(
        status_code=status_code,
        content={
            "code": status_code,
            "message": "服务运行正常" if overall_status == "healthy" else "服务降级运行",
            "data": health_data
        }
    )
