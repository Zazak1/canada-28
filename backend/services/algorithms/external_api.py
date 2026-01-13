"""
外部 API 算法 - 预留接口
用于接入第三方预测服务或 AI 模型
"""

import requests
import logging
from typing import Dict, Any
from flask import current_app
from .base import BaseAlgorithm

logger = logging.getLogger(__name__)


class ExternalAPIAlgorithm(BaseAlgorithm):
    """
    外部 API 算法 - 预留接口
    
    使用方法:
    1. 在 config.py 中配置:
       EXTERNAL_PREDICTION_API = "https://your-api.com/predict"
       EXTERNAL_PREDICTION_API_KEY = "your-api-key"
    
    2. 在 algorithms/__init__.py 中取消注释并注册
    
    3. API 应返回格式:
       {
           "big_small": "Big" | "Small",
           "odd_even": "Odd" | "Even",
           "confidence": 0.0 ~ 1.0
       }
    """
    
    version = "v1.0"
    
    def predict(self, target_issue: str) -> Dict[str, Any]:
        # 获取配置
        api_url = current_app.config.get("EXTERNAL_PREDICTION_API")
        api_key = current_app.config.get("EXTERNAL_PREDICTION_API_KEY")
        
        if not api_url:
            return self._fallback_predict(target_issue)
        
        try:
            # 获取历史数据作为输入
            stats = self.get_stats(limit=50)
            
            # 调用外部 API
            response = requests.post(
                api_url,
                json={
                    "target_issue": target_issue,
                    "history": stats["recent_results"][:20] if stats else [],
                    "stats": stats,
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            
            # 验证返回格式
            if "big_small" not in result:
                raise ValueError("API response missing 'big_small'")
            
            return {
                "big_small": result.get("big_small"),
                "odd_even": result.get("odd_even"),
                "hot_number": result.get("hot_number"),
                "confidence": result.get("confidence", 0.5),
                "reason": result.get("reason", "External API prediction"),
                "stats": result.get("stats", {}),
            }
            
        except Exception as e:
            logger.error(f"External API prediction failed: {e}")
            return self._fallback_predict(target_issue)
    
    def _fallback_predict(self, target_issue: str) -> Dict[str, Any]:
        """API 失败时的回退方案"""
        stats = self.get_stats(limit=20)
        if not stats:
            return {"error": "No data available"}
        
        # 简单的随机预测
        import random
        return {
            "big_small": random.choice(["Big", "Small"]),
            "odd_even": random.choice(["Odd", "Even"]),
            "confidence": 0.5,
            "reason": "Fallback: External API unavailable",
            "stats": {
                "big_pct": round(stats["big"] / stats["total"], 2),
                "small_pct": round(stats["small"] / stats["total"], 2),
                "odd_pct": round(stats["odd"] / stats["total"], 2),
                "even_pct": round(stats["even"] / stats["total"], 2),
            }
        }
