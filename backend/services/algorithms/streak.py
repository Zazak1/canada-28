"""
连续追踪算法（优化版）
动态阈值 + 渐进反转概率 + 历史波动性分析
"""

import random
import hashlib
from typing import Dict, Any, List
from .base import BaseAlgorithm


class StreakAlgorithm(BaseAlgorithm):
    """连续追踪算法 - 动态阈值版"""
    
    version = "v2.0"
    
    # 基础反转阈值
    BASE_THRESHOLD = 3
    # 最小/最大动态阈值
    MIN_THRESHOLD = 2
    MAX_THRESHOLD = 5
    
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
    
    def _get_historical_streaks(self, results: list, key: str) -> List[int]:
        """分析历史连续模式"""
        if not results:
            return []
        
        streaks = []
        current = results[0][key]
        streak = 1
        
        for r in results[1:]:
            if r[key] == current:
                streak += 1
            else:
                streaks.append(streak)
                current = r[key]
                streak = 1
        streaks.append(streak)
        
        return streaks
    
    def _calculate_dynamic_threshold(self, historical_streaks: List[int]) -> int:
        """根据历史波动计算动态阈值"""
        if not historical_streaks:
            return self.BASE_THRESHOLD
        
        avg_streak = sum(historical_streaks) / len(historical_streaks)
        max_streak = max(historical_streaks)
        
        # 动态阈值 = 平均连续次数 + 1，但限制在范围内
        dynamic = int(avg_streak + 1)
        
        # 如果历史最大连续很高，适当提高阈值
        if max_streak >= 5:
            dynamic = min(dynamic + 1, self.MAX_THRESHOLD)
        
        return max(self.MIN_THRESHOLD, min(dynamic, self.MAX_THRESHOLD))
    
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
        stats = self.get_stats(limit=30)  # 增加样本量用于分析历史模式
        if not stats:
            return {"error": "Insufficient data"}
        
        recent = stats["recent_results"]
        rng = self._get_seed_random(target_issue)
        
        # 计算当前连续
        bs_current, bs_streak = self._get_streak(recent, "big_small")
        oe_current, oe_streak = self._get_streak(recent, "odd_even")
        
        # 分析历史连续模式，计算动态阈值
        bs_historical = self._get_historical_streaks(recent, "big_small")
        oe_historical = self._get_historical_streaks(recent, "odd_even")
        
        bs_threshold = self._calculate_dynamic_threshold(bs_historical)
        oe_threshold = self._calculate_dynamic_threshold(oe_historical)
        
        # 大小预测：渐进反转概率
        if bs_streak >= bs_threshold:
            # 超过阈值，高概率反转
            reversal_prob = 0.7 + (bs_streak - bs_threshold) * 0.1
            reversal_prob = min(reversal_prob, 0.95)
            
            if rng.random() < reversal_prob:
                predicted_bs = self._opposite(bs_current)
                bs_reason = f"连续{bs_streak}次≥阈值{bs_threshold}，{reversal_prob:.0%}概率反转"
            else:
                predicted_bs = bs_current
                bs_reason = f"连续{bs_streak}次≥阈值{bs_threshold}，继续跟随"
        else:
            # 未达阈值，渐进跟随概率
            follow_prob = 0.8 - (bs_streak * 0.1)
            follow_prob = max(follow_prob, 0.5)
            
            if rng.random() < follow_prob:
                predicted_bs = bs_current if bs_current else "Big"
                bs_reason = f"连续{bs_streak}次<阈值{bs_threshold}，{follow_prob:.0%}跟随"
            else:
                predicted_bs = self._opposite(bs_current) if bs_current else "Small"
                bs_reason = f"连续{bs_streak}次，提前反转"
        
        # 单双预测
        if oe_streak >= oe_threshold:
            reversal_prob = 0.7 + (oe_streak - oe_threshold) * 0.1
            reversal_prob = min(reversal_prob, 0.95)
            
            if rng.random() < reversal_prob:
                predicted_oe = self._opposite(oe_current)
                oe_reason = f"连续{oe_streak}次≥阈值{oe_threshold}，{reversal_prob:.0%}概率反转"
            else:
                predicted_oe = oe_current
                oe_reason = f"连续{oe_streak}次≥阈值{oe_threshold}，继续跟随"
        else:
            follow_prob = 0.8 - (oe_streak * 0.1)
            follow_prob = max(follow_prob, 0.5)
            
            if rng.random() < follow_prob:
                predicted_oe = oe_current if oe_current else "Odd"
                oe_reason = f"连续{oe_streak}次<阈值{oe_threshold}，{follow_prob:.0%}跟随"
            else:
                predicted_oe = self._opposite(oe_current) if oe_current else "Even"
                oe_reason = f"连续{oe_streak}次，提前反转"
        
        # 热号：考虑奇偶性
        sorted_sums = sorted(stats["sum_counts"].items(), key=lambda x: x[1], reverse=True)
        if sorted_sums:
            # 筛选符合预测奇偶性的和值
            if predicted_oe == "Odd":
                valid_sums = [(s, c) for s, c in sorted_sums if s % 2 != 0]
            else:
                valid_sums = [(s, c) for s, c in sorted_sums if s % 2 == 0]
            
            # 再筛选符合大小的
            if predicted_bs == "Big":
                valid_sums = [(s, c) for s, c in valid_sums if s >= 14]
            else:
                valid_sums = [(s, c) for s, c in valid_sums if s < 14]
            
            if valid_sums:
                hot_sum = valid_sums[0][0]
            else:
                hot_sum = sorted_sums[0][0]
        else:
            hot_sum = 14
        
        # 置信度
        bs_confidence = 0.5 + min(bs_streak * 0.08, 0.35)
        oe_confidence = 0.5 + min(oe_streak * 0.08, 0.35)
        
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
                "bs_threshold": bs_threshold,
                "oe_threshold": oe_threshold,
                "bs_avg_streak": round(sum(bs_historical) / len(bs_historical), 1) if bs_historical else 0,
                "oe_avg_streak": round(sum(oe_historical) / len(oe_historical), 1) if oe_historical else 0,
            }
        }
