"""
连续追踪算法
根据连续出现次数判断：连续次数达到阈值后反转
"""

from typing import Dict, Any
from .base import BaseAlgorithm


class StreakAlgorithm(BaseAlgorithm):
    """连续追踪算法"""
    
    version = "v1.0"
    
    # 连续多少次后触发反转
    REVERSAL_THRESHOLD = 3
    
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
    
    def _opposite(self, value: str) -> str:
        """获取相反值"""
        opposites = {
            "Big": "Small", "Small": "Big",
            "Odd": "Even", "Even": "Odd",
        }
        return opposites.get(value, value)
    
    def predict(self, target_issue: str) -> Dict[str, Any]:
        stats = self.get_stats(limit=20)
        if not stats:
            return {"error": "Insufficient data"}
        
        recent = stats["recent_results"]
        
        # 计算连续
        bs_current, bs_streak = self._get_streak(recent, "big_small")
        oe_current, oe_streak = self._get_streak(recent, "odd_even")
        
        # 达到阈值则反转，否则跟随
        if bs_streak >= self.REVERSAL_THRESHOLD:
            predicted_bs = self._opposite(bs_current)
            bs_reason = f"连续{bs_streak}次{bs_current}，触发反转"
        else:
            predicted_bs = bs_current
            bs_reason = f"连续{bs_streak}次{bs_current}，继续跟随"
        
        if oe_streak >= self.REVERSAL_THRESHOLD:
            predicted_oe = self._opposite(oe_current)
            oe_reason = f"连续{oe_streak}次{oe_current}，触发反转"
        else:
            predicted_oe = oe_current
            oe_reason = f"连续{oe_streak}次{oe_current}，继续跟随"
        
        # 置信度
        bs_confidence = 0.5 + min(bs_streak * 0.1, 0.4)
        oe_confidence = 0.5 + min(oe_streak * 0.1, 0.4)
        
        # 热号
        sorted_sums = sorted(stats["sum_counts"].items(), key=lambda x: x[1], reverse=True)
        hot_sum = sorted_sums[0][0] if sorted_sums else 14
        
        return {
            "big_small": predicted_bs,
            "odd_even": predicted_oe,
            "hot_number": hot_sum,
            "confidence": round((bs_confidence + oe_confidence) / 2, 2),
            "reason": f"{bs_reason}；{oe_reason}",
            "stats": {
                "big_pct": round(stats["big"] / stats["total"], 2),
                "small_pct": round(stats["small"] / stats["total"], 2),
                "odd_pct": round(stats["odd"] / stats["total"], 2),
                "even_pct": round(stats["even"] / stats["total"], 2),
                "bs_streak": bs_streak,
                "oe_streak": oe_streak,
                "threshold": self.REVERSAL_THRESHOLD,
            }
        }
