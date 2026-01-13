"""
反转算法 - 基于均值回归假设
近期大多则预测小，近期单多则预测双
"""

from typing import Dict, Any
from .base import BaseAlgorithm


class ReversionAlgorithm(BaseAlgorithm):
    """反转算法"""
    
    version = "v1.1"
    
    def predict(self, target_issue: str) -> Dict[str, Any]:
        stats = self.get_stats(limit=20)
        if not stats:
            return {"error": "Insufficient data"}
        
        # 反转逻辑：多的预测少
        predicted_bs = "Small" if stats["big"] > stats["small"] else "Big"
        predicted_oe = "Even" if stats["odd"] > stats["even"] else "Odd"
        
        # 热号
        sorted_sums = sorted(stats["sum_counts"].items(), key=lambda x: x[1], reverse=True)
        hot_sum = sorted_sums[0][0] if sorted_sums else 14
        
        # 置信度：偏离越大，置信度越高
        big_ratio = stats["big"] / stats["total"]
        bs_confidence = abs(big_ratio - 0.5) * 2  # 0~1
        
        odd_ratio = stats["odd"] / stats["total"]
        oe_confidence = abs(odd_ratio - 0.5) * 2
        
        return {
            "big_small": predicted_bs,
            "odd_even": predicted_oe,
            "hot_number": hot_sum,
            "confidence": round((bs_confidence + oe_confidence) / 2, 2),
            "reason": f"近20期大{stats['big']}次小{stats['small']}次，单{stats['odd']}次双{stats['even']}次",
            "stats": {
                "big_pct": round(stats["big"] / stats["total"], 2),
                "small_pct": round(stats["small"] / stats["total"], 2),
                "odd_pct": round(stats["odd"] / stats["total"], 2),
                "even_pct": round(stats["even"] / stats["total"], 2),
            }
        }
