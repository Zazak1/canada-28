"""
马丁格尔算法 - 跟随趋势
如果最近连续出现同一结果，继续预测该结果
"""

from typing import Dict, Any
from .base import BaseAlgorithm


class MartingaleAlgorithm(BaseAlgorithm):
    """马丁格尔算法 - 趋势跟随"""
    
    version = "v1.0"
    
    def _get_streak(self, results: list, key: str) -> tuple:
        """计算连续出现次数"""
        if not results:
            return None, 0
        
        current = results[0][key]
        streak = 1
        
        for r in results[1:]:
            if r[key] == current:
                streak += 1
            else:
                break
        
        return current, streak
    
    def predict(self, target_issue: str) -> Dict[str, Any]:
        stats = self.get_stats(limit=20)
        if not stats:
            return {"error": "Insufficient data"}
        
        recent = stats["recent_results"]
        
        # 计算大小连续
        bs_current, bs_streak = self._get_streak(recent, "big_small")
        # 计算单双连续
        oe_current, oe_streak = self._get_streak(recent, "odd_even")
        
        # 马丁格尔：跟随趋势
        predicted_bs = bs_current if bs_current else "Big"
        predicted_oe = oe_current if oe_current else "Odd"
        
        # 连续次数越多，置信度越高（但有上限）
        bs_confidence = min(bs_streak * 0.15, 0.8)
        oe_confidence = min(oe_streak * 0.15, 0.8)
        
        # 热号
        sorted_sums = sorted(stats["sum_counts"].items(), key=lambda x: x[1], reverse=True)
        hot_sum = sorted_sums[0][0] if sorted_sums else 14
        
        return {
            "big_small": predicted_bs,
            "odd_even": predicted_oe,
            "hot_number": hot_sum,
            "confidence": round((bs_confidence + oe_confidence) / 2, 2),
            "reason": f"当前连续{bs_streak}次{bs_current}，连续{oe_streak}次{oe_current}",
            "stats": {
                "big_pct": round(stats["big"] / stats["total"], 2),
                "small_pct": round(stats["small"] / stats["total"], 2),
                "odd_pct": round(stats["odd"] / stats["total"], 2),
                "even_pct": round(stats["even"] / stats["total"], 2),
                "bs_streak": bs_streak,
                "oe_streak": oe_streak,
            }
        }
