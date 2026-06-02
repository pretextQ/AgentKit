"""AgentKit 统一启动入口

使用方式：uv run python start.py
"""

import sys
import threading
import logging
from pathlib import Path

# 确保项目根目录在 Python 路径中
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("AgentKit")


def run_cls_server():
    """启动 CLS MCP 服务（端口 8003）"""
    from mcp_servers.cls_server import mcp

    logger.info("CLS MCP 服务启动中... (端口 8003)")
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8003, path="/mcp")


def run_monitor_server():
    """启动 Monitor MCP 服务（端口 8004）"""
    from mcp_servers.monitor_server import mcp

    logger.info("Monitor MCP 服务启动中... (端口 8004)")
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8004, path="/mcp")


def run_fastapi():
    """启动 FastAPI 主服务（端口 9900）"""
    import uvicorn
    from app.config import config

    logger.info(f"FastAPI 主服务启动中... (端口 {config.port})")
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=False,
    )


def main():
    """启动所有服务"""
    logger.info("=" * 60)
    logger.info("AgentKit 启动中...")
    logger.info("=" * 60)

    # 启动 MCP 服务（守护线程，主进程退出时自动结束）
    cls_thread = threading.Thread(target=run_cls_server, daemon=True, name="cls-server")
    monitor_thread = threading.Thread(target=run_monitor_server, daemon=True, name="monitor-server")

    cls_thread.start()
    monitor_thread.start()

    # 等待 MCP 服务启动
    import time
    time.sleep(2)

    # 主线程运行 FastAPI（阻塞）
    try:
        run_fastapi()
    except KeyboardInterrupt:
        logger.info("收到退出信号，正在关闭...")
        sys.exit(0)


if __name__ == "__main__":
    main()
