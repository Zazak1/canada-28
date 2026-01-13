"""
马丁格尔算法 - 跟随趋势（优化版）
加入最大跟随次数限制和概率衰减，避免无限跟随
"""

import random
import hashlib
from typing import Dict, Any
from .base import BaseAlgorithm


class MartingaleAlgorithm(BaseAlgorithm):
    """马丁格尔算法 - 带衰减的趋势跟随"""
    
    version = "v2.0"
    
    # 最大跟随次数，超过后触发反转
    MAX_FOLLOW_STREAK = 5
    # 每次连续后跟随概率衰减
    DECAY_RATE = 0.15
    
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
    
    def _get_seed_random(self, target_issue: str) -> random.Random:
        """基于期号生成确定性随机数生成器"""
        seed = int(hashlib.md5(target_issue.encode()).hexdigest()[:8], 16)
        return random.Random(seed)
    
    def predict(self, target_issue: str) -> Dict[str, Any]:
        stats = self.get_stats(limit=20)
        if not stats:
            return {"error": "Insufficient data"}
        
        recent = stats["recent_results"]
        rng = self._get_seed_random(target_issue)
        
        # 计算大小连续
        bs_current, bs_streak = self._get_streak(recent, "big_small")
        # 计算单双连续
        oe_current, oe_streak = self._get_streak(recent, "odd_even")
        
        # 大小预测：带衰减的跟随
        if bs_streak >= self.MAX_FOLLOW_STREAK:
            # 超过最大跟随次数，强制反转
            predicted_bs = self._opposite(bs_current)
            bs_reason = f"连续{bs_streak}次达上限，强制反转"
        else:
            # 跟随概率随连续次数衰减
            follow_prob = 1.0 - (bs_streak * self.DECAY_RATE)
            follow_prob = max(follow_prob, 0.3)  # 最低30%跟随概率
            
            if rng.random() < follow_prob:
                predicted_bs = bs_current if bs_current else "Big"
                bs_reason = f"连续{bs_streak}次，概率{follow_prob:.0%}跟随"
            else:
                predicted_bs = self._opposite(bs_current) if bs_current else "Small"
                bs_reason = f"连续{bs_streak}次，概率反转"
        
        # 单双预测
        if oe_streak >= self.MAX_FOLLOW_STREAK:
            predicted_oe = self._opposite(oe_current)
            oe_reason = f"连续{oe_streak}次达上限，强制反转"
        else:
            follow_prob = 1.0 - (oe_streak * self.DECAY_RATE)
            follow_prob = max(follow_prob, 0.3)
            
            if rng.random() < follow_prob:
                predicted_oe = oe_current if oe_current else "Odd"
                oe_reason = f"连续{oe_streak}次，概率{follow_prob:.0%}跟随"
            else:
                predicted_oe = self._opposite(oe_current) if oe_current else "Even"
                oe_reason = f"连续{oe_streak}次，概率反转"
        
        # 热号：结合连续趋势
        sorted_sums = sorted(stats["sum_counts"].items(), key=lambda x: x[1], reverse=True)
        if sorted_sums:
            # 根据预测结果筛选热号范围
            if predicted_bs == "Big":
                valid_sums = [(s, c) for s, c in sorted_sums if s >= 14]
            else:
                valid_sums = [(s, c) for s, c in sorted_sums if s < 14]
            
            if valid_sums:
                # 从符合条件的和值中选择
                hot_sum = valid_sums[0][0] if rng.random() < 0.7 else rng.choice(valid_sums)[0]
            else:
                hot_sum = sorted_sums[0][0]
        else:
            hot_sum = 14
        
        # 置信度：考虑连续次数和衰减
        bs_confidence = min(0.4 + bs_streak * 0.1, 0.85)
        oe_confidence = min(0.4 + oe_streak * 0.1, 0.85)
        
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
                "max_follow": self.MAX_FOLLOW_STREAK,
            }
        }
