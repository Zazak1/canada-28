"""
随机算法 - 纯随机预测
基于期号生成确定性随机结果，同一期号预测一致
"""

import random
import hashlib
from typing import Dict, Any
from .base import BaseAlgorithm


class ReversionAlgorithm(BaseAlgorithm):
    """随机算法 - 纯随机预测"""
    
    version = "v3.0"
    
    def _get_seed_random(self, target_issue: str) -> random.Random:
        """基于期号生成确定性随机数生成器"""
        seed = int(hashlib.md5(target_issue.encode()).hexdigest()[:8], 16)
        return random.Random(seed)
    
    def predict(self, target_issue: str) -> Dict[str, Any]:
        stats = self.get_stats(limit=20)
        rng = self._get_seed_random(target_issue)
        
        # 随机选择大小（50% 概率）
        predicted_bs = "Big" if rng.random() < 0.5 else "Small"
        
        # 随机选择单双（50% 概率）
        predicted_oe = "Odd" if rng.random() < 0.5 else "Even"
        
        # 随机选择热号（根据预测的大小和单双范围内随机）
        if predicted_bs == "Big":
            # 大：14-27
            if predicted_oe == "Odd":
                # 大单：15, 17, 19, 21, 23, 25, 27
                valid_nums = [15, 17, 19, 21, 23, 25, 27]
            else:
                # 大双：14, 16, 18, 20, 22, 24, 26
                valid_nums = [14, 16, 18, 20, 22, 24, 26]
        else:
            # 小：0-13
            if predicted_oe == "Odd":
                # 小单：1, 3, 5, 7, 9, 11, 13
                valid_nums = [1, 3, 5, 7, 9, 11, 13]
            else:
                # 小双：0, 2, 4, 6, 8, 10, 12
                valid_nums = [0, 2, 4, 6, 8, 10, 12]
        
        hot_sum = rng.choice(valid_nums)
        
        # 随机置信度（0.4 - 0.7）
        confidence = round(0.4 + rng.random() * 0.3, 2)
        
        # 构建返回结果
        result = {
            "big_small": predicted_bs,
            "odd_even": predicted_oe,
            "hot_number": hot_sum,
            "confidence": confidence,
            "reason": f"随机预测：{predicted_bs} + {predicted_oe}",
        }
        
        # 如果有统计数据，附加上
        if stats:
            result["stats"] = {
                "big_pct": round(stats["big"] / stats["total"], 2),
                "small_pct": round(stats["small"] / stats["total"], 2),
                "odd_pct": round(stats["odd"] / stats["total"], 2),
                "even_pct": round(stats["even"] / stats["total"], 2),
            }
        
        return result
