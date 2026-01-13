"""
算法注册中心
新增算法只需：
1. 在本目录创建 xxx_algo.py
2. 继承 BaseAlgorithm 实现 predict() 方法
3. 在 ALGORITHMS 字典中注册
"""

from .base import BaseAlgorithm
from .reversion import ReversionAlgorithm
from .martingale import MartingaleAlgorithm
from .streak import StreakAlgorithm

# 算法注册表 - 黑箱处理，不暴露算法细节
ALGORITHMS = {
    "algo1": {
        "class": ReversionAlgorithm,
        "name": "算法一",
        "description": "",
    },
    "algo2": {
        "class": MartingaleAlgorithm,
        "name": "算法二",
        "description": "",
    },
    "algo3": {
        "class": StreakAlgorithm,
        "name": "算法三",
        "description": "",
    },
    # 预留：外部 API 算法
    # "algo4": {
    #     "class": ExternalAPIAlgorithm,
    #     "name": "算法四",
    #     "description": "",
    # },
}

def get_algorithm(algo_id: str) -> BaseAlgorithm:
    """获取算法实例"""
    if algo_id not in ALGORITHMS:
        algo_id = "algo1"  # 默认算法
    return ALGORITHMS[algo_id]["class"]()

def list_algorithms() -> list:
    """列出所有可用算法"""
    return [
        {
            "id": algo_id,
            "name": info["name"],
            "description": info["description"],
        }
        for algo_id, info in ALGORITHMS.items()
    ]
