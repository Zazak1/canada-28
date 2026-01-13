"""
反转算法 - 基于均值回归假设（优化版）
引入时间衰减权重和随机扰动，避免长期相同预测
"""

import random
import hashlib
from typing import Dict, Any
from .base import BaseAlgorithm


class ReversionAlgorithm(BaseAlgorithm):
    """反转算法 - 带时间衰减和随机扰动"""
    
    version = "v2.0"
    
    # 当分布偏离小于此阈值时，引入随机性
    RANDOM_THRESHOLD = 0.15
    
    def _weighted_stats(self, limit: int = 20) -> Dict[str, float]:
        """计算带时间衰减权重的统计（近期数据权重更高）"""
        records = self.get_history(limit)
        if not records:
            return None
        
        weighted_big = 0
        weighted_small = 0
        weighted_odd = 0
        weighted_even = 0
        total_weight = 0
        
        for i, r in enumerate(records):
            # 指数衰减权重：最近的权重最高
            weight = 0.9 ** i  # 第0期权重1.0，第1期0.9，第2期0.81...
            total_weight += weight
            
            is_big = r.sum_val >= 14
            is_odd = r.sum_val % 2 != 0
            
            if is_big:
                weighted_big += weight
            else:
                weighted_small += weight
            
            if is_odd:
                weighted_odd += weight
            else:
                weighted_even += weight
        
        return {
            "big_ratio": weighted_big / total_weight,
            "small_ratio": weighted_small / total_weight,
            "odd_ratio": weighted_odd / total_weight,
            "even_ratio": weighted_even / total_weight,
        }
    
    def _get_seed_random(self, target_issue: str) -> random.Random:
        """基于期号生成确定性随机数生成器"""
        seed = int(hashlib.md5(target_issue.encode()).hexdigest()[:8], 16)
        return random.Random(seed)
    
    def predict(self, target_issue: str) -> Dict[str, Any]:
        stats = self.get_stats(limit=20)
        if not stats:
            return {"error": "Insufficient data"}
        
        weighted = self._weighted_stats(limit=20)
        rng = self._get_seed_random(target_issue)
        
        # 计算加权后的偏离度
        bs_deviation = abs(weighted["big_ratio"] - 0.5)
        oe_deviation = abs(weighted["odd_ratio"] - 0.5)
        
        # 大小预测：偏离度小时引入随机性
        if bs_deviation < self.RANDOM_THRESHOLD:
            # 分布接近均衡，随机选择但稍微倾向于反转
            reverse_prob = 0.5 + bs_deviation
            predicted_bs = "Small" if rng.random() < reverse_prob and weighted["big_ratio"] > 0.5 else "Big"
            bs_reason = "分布均衡，随机扰动"
        else:
            # 明显偏离，执行反转
            predicted_bs = "Small" if weighted["big_ratio"] > 0.5 else "Big"
            bs_reason = "加权反转"
        
        # 单双预测
        if oe_deviation < self.RANDOM_THRESHOLD:
            reverse_prob = 0.5 + oe_deviation
            predicted_oe = "Even" if rng.random() < reverse_prob and weighted["odd_ratio"] > 0.5 else "Odd"
            oe_reason = "分布均衡，随机扰动"
        else:
            predicted_oe = "Even" if weighted["odd_ratio"] > 0.5 else "Odd"
            oe_reason = "加权反转"
        
        # 热号：加入冷号轮换
        sorted_sums = sorted(stats["sum_counts"].items(), key=lambda x: x[1], reverse=True)
        if sorted_sums:
            # 70% 概率选热号，30% 概率选次热号或随机
            if rng.random() < 0.7:
                hot_sum = sorted_sums[0][0]
            elif len(sorted_sums) > 1:
                hot_sum = sorted_sums[1][0]
            else:
                hot_sum = rng.randint(0, 27)
        else:
            hot_sum = 14
        
        # 置信度
        bs_confidence = min(bs_deviation * 2 + 0.3, 0.9)
        oe_confidence = min(oe_deviation * 2 + 0.3, 0.9)
        
        return {
            "big_small": predicted_bs,
            "odd_even": predicted_oe,
            "hot_number": hot_sum,
            "confidence": round((bs_confidence + oe_confidence) / 2, 2),
            "reason": f"加权大{weighted['big_ratio']:.0%}小{weighted['small_ratio']:.0%}；{bs_reason}；{oe_reason}",
            "stats": {
                "big_pct": round(stats["big"] / stats["total"], 2),
                "small_pct": round(stats["small"] / stats["total"], 2),
                "odd_pct": round(stats["odd"] / stats["total"], 2),
                "even_pct": round(stats["even"] / stats["total"], 2),
                "weighted_big": round(weighted["big_ratio"], 2),
                "weighted_odd": round(weighted["odd_ratio"], 2),
            }
        }
