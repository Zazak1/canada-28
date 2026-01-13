"""
算法基类 - 所有预测算法必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from models import LotteryRecord


class BaseAlgorithm(ABC):
    """预测算法基类"""
    
    # 算法版本，子类应覆盖
    version = "v1.0"
    
    def get_history(self, limit: int = 20) -> List[LotteryRecord]:
        """获取最近的历史记录"""
        return LotteryRecord.query.order_by(
            LotteryRecord.issue.desc()
        ).limit(limit).all()
    
    def get_stats(self, limit: int = 20) -> Optional[Dict[str, Any]]:
        """计算基础统计数据"""
        records = self.get_history(limit)
        if not records:
            return None
        
        stats = {
            "total": len(records),
            "big": 0,
            "small": 0,
            "odd": 0,
            "even": 0,
            "sum_counts": {},
            "recent_results": [],  # 最近结果序列
        }
        
        for r in records:
            # Big/Small (14-27 Big, 0-13 Small)
            is_big = r.sum_val >= 14
            is_odd = r.sum_val % 2 != 0
            
            if is_big:
                stats["big"] += 1
            else:
                stats["small"] += 1
            
            if is_odd:
                stats["odd"] += 1
            else:
                stats["even"] += 1
            
            stats["sum_counts"][r.sum_val] = stats["sum_counts"].get(r.sum_val, 0) + 1
            stats["recent_results"].append({
                "issue": r.issue,
                "sum": r.sum_val,
                "big_small": "Big" if is_big else "Small",
                "odd_even": "Odd" if is_odd else "Even",
            })
        
        return stats
    
    @abstractmethod
    def predict(self, target_issue: str) -> Dict[str, Any]:
        """
        生成预测 - 子类必须实现
        
        返回格式:
        {
            "big_small": "Big" | "Small",
            "odd_even": "Odd" | "Even",
            "confidence": 0.0 ~ 1.0,  # 可选：置信度
            "hot_number": int,         # 可选：热号
            "reason": str,             # 可选：预测理由
            "stats": {...},            # 可选：统计数据
        }
        """
        pass
    
    def get_algorithm_info(self) -> Dict[str, str]:
        """返回算法信息"""
        return {
            "version": self.version,
            "class": self.__class__.__name__,
        }
