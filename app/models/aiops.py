"""
AIOps 请求和响应模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class AIOpsRequest(BaseModel):
    """AIOps 诊断请求"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "session-123"
            }
        },
    )

    session_id: Optional[str] = Field(
        default="default",
        description="会话ID，用于追踪诊断历史"
    )


class AlertInfo(BaseModel):
    """告警信息"""
    alertname: str
    severity: str
    instance: str
    duration: str
    description: Optional[str] = None


class DiagnosisResponse(BaseModel):
    """诊断响应（非流式）"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 200,
                "message": "success",
                "data": {
                    "status": "completed",
                    "target_alert": {
                        "alertname": "HighCPUUsage",
                        "severity": "critical"
                    },
                    "diagnosis": {
                        "root_cause": "数据库连接池耗尽",
                        "recommendations": ["扩容数据库连接池", "优化SQL查询"]
                    }
                }
            }
        },
    )

    code: int = 200
    message: str = "success"
    data: Dict[str, Any]
