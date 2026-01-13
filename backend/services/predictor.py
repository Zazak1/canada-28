"""
预测服务 - 每个算法独立保存预测记录
"""

from extensions import db
from models import LotteryRecord, Prediction
from services.algorithms import get_algorithm, list_algorithms, ALGORITHMS
import logging
import json

logger = logging.getLogger(__name__)

# 英文转中文映射
BS_MAP = {"Big": "大", "Small": "小"}
OE_MAP = {"Odd": "单", "Even": "双"}


def generate_prediction_for_algorithm(target_issue: str, algorithm_id: str) -> dict:
    """
    为指定算法生成预测并保存到数据库
    """
    # 检查是否已存在该算法对该期的预测
    existing = Prediction.query.filter_by(
        target_issue=target_issue,
        algorithm_id=algorithm_id
    ).first()
    
    if existing:
        return json.loads(existing.predicted_val)
    
    # 生成新预测
    algo = get_algorithm(algorithm_id)
    result = algo.predict(target_issue)
    
    if "error" in result:
        return result
    
    # 保存到数据库
    pred_obj = Prediction(
        target_issue=target_issue,
        algorithm_id=algorithm_id,
        predicted_val=json.dumps({
            "big_small": result.get("big_small"),
            "odd_even": result.get("odd_even"),
        })
    )
    
    try:
        db.session.add(pred_obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to save prediction for {algorithm_id}/{target_issue}: {e}")
    
    return result


def generate_all_predictions(target_issue: str):
    """
    为所有算法生成预测
    """
    for algo_id in ALGORITHMS.keys():
        try:
            generate_prediction_for_algorithm(target_issue, algo_id)
        except Exception as e:
            logger.error(f"Failed to generate prediction for {algo_id}: {e}")


def verify_predictions_for_issue(record: LotteryRecord):
    """
    验证所有算法对该期的预测是否正确
    """
    predictions = Prediction.query.filter_by(target_issue=record.issue).all()
    
    actual_bs = "Big" if record.sum_val >= 14 else "Small"
    actual_oe = "Odd" if record.sum_val % 2 != 0 else "Even"
    
    for pred in predictions:
        if pred.is_correct is not None:
            continue  # 已验证
        
        try:
            data = json.loads(pred.predicted_val)
            predicted_bs = data.get("big_small")
            predicted_oe = data.get("odd_even")
            
            bs_correct = (predicted_bs == actual_bs)
            oe_correct = (predicted_oe == actual_oe) if predicted_oe else None
            
            pred.bs_correct = bs_correct
            pred.oe_correct = oe_correct
            # 有一个对就算整体正确
            pred.is_correct = bs_correct or (oe_correct is True)
            
            logger.info(f"Verified {pred.algorithm_id}/{record.issue}: BS={'✓' if bs_correct else '✗'}, OE={'✓' if oe_correct else '✗'}")
        except Exception as e:
            logger.error(f"Verification failed for {pred.algorithm_id}/{record.issue}: {e}")
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to commit verification: {e}")


def get_latest_prediction(algorithm_id: str = "algo1") -> dict:
    """
    获取指定算法对下一期的预测
    """
    last_record = LotteryRecord.query.order_by(LotteryRecord.issue.desc()).first()
    if not last_record:
        return None
    
    try:
        next_issue = str(int(last_record.issue) + 1)
        result = generate_prediction_for_algorithm(next_issue, algorithm_id)
        
        # 获取算法名称
        algo_info = ALGORITHMS.get(algorithm_id, {})
        algo_name = algo_info.get("name", algorithm_id)
        
        return {
            "algorithm": algorithm_id,
            "algorithm_name": algo_name,
            "big_small": result.get("big_small"),
            "odd_even": result.get("odd_even"),
        }
    except Exception as e:
        logger.error(f"Failed to get prediction: {e}")
        return None


def get_all_predictions(target_issue: str = None) -> list:
    """
    获取所有算法对同一期的预测
    """
    if not target_issue:
        last_record = LotteryRecord.query.order_by(LotteryRecord.issue.desc()).first()
        if not last_record:
            return []
        target_issue = str(int(last_record.issue) + 1)
    
    results = []
    for algo_id, algo_info in ALGORITHMS.items():
        result = generate_prediction_for_algorithm(target_issue, algo_id)
        results.append({
            "algorithm": algo_id,
            "algorithm_name": algo_info["name"],
            "big_small": result.get("big_small"),
            "odd_even": result.get("odd_even"),
        })
    
    return results


def get_algorithm_history(algorithm_id: str, limit: int = 20) -> dict:
    """
    获取指定算法的历史预测记录和统计
    统计基于最近100期数据
    """
    # 获取用于显示的历史记录
    predictions = Prediction.query.filter_by(algorithm_id=algorithm_id)\
        .order_by(Prediction.target_issue.desc())\
        .limit(limit).all()
    
    # 获取用于统计的最近100期数据
    stats_predictions = Prediction.query.filter_by(algorithm_id=algorithm_id)\
        .order_by(Prediction.target_issue.desc())\
        .limit(100).all()
    
    # 统计（基于最近100期）
    total = len(stats_predictions)
    verified = [p for p in stats_predictions if p.is_correct is not None]
    correct = [p for p in verified if p.is_correct]
    bs_correct = [p for p in verified if p.bs_correct]
    oe_correct = [p for p in verified if p.oe_correct]
    
    # 构建历史数据
    history = []
    for pred in predictions:
        record = LotteryRecord.query.filter_by(issue=pred.target_issue).first()
        data = json.loads(pred.predicted_val) if pred.predicted_val else {}
        
        item = {
            "issue": pred.target_issue,
            "prediction": {
                "big_small": BS_MAP.get(data.get("big_small"), data.get("big_small")),
                "odd_even": OE_MAP.get(data.get("odd_even"), data.get("odd_even")),
                "bs_correct": pred.bs_correct,
                "oe_correct": pred.oe_correct,
                "is_correct": pred.is_correct,
            },
            "actual": None
        }
        
        if record:
            item["actual"] = {
                "numbers": f"{record.code1}+{record.code2}+{record.code3}",
                "sum": record.sum_val,
                "big_small": "大" if record.sum_val >= 14 else "小",
                "odd_even": "单" if record.sum_val % 2 != 0 else "双",
            }
        
        history.append(item)
    
    return {
        "algorithm_id": algorithm_id,
        "algorithm_name": ALGORITHMS.get(algorithm_id, {}).get("name", algorithm_id),
        "stats": {
            "total": total,
            "verified": len(verified),
            "correct": len(correct),
            "accuracy": round(len(correct) / len(verified) * 100, 1) if verified else 0,
            "bs_accuracy": round(len(bs_correct) / len(verified) * 100, 1) if verified else 0,
            "oe_accuracy": round(len(oe_correct) / len(verified) * 100, 1) if verified else 0,
        },
        "history": history
    }


def get_all_algorithm_stats() -> list:
    """
    获取所有算法的统计数据（基于最近100期）
    """
    stats = []
    for algo_id, algo_info in ALGORITHMS.items():
        # 获取最近100期的统计
        predictions = Prediction.query.filter_by(algorithm_id=algo_id)\
            .order_by(Prediction.target_issue.desc())\
            .limit(100).all()
        
        total = len(predictions)
        verified = [p for p in predictions if p.is_correct is not None]
        correct = [p for p in verified if p.is_correct]
        bs_correct = [p for p in verified if p.bs_correct]
        oe_correct = [p for p in verified if p.oe_correct]
        
        stats.append({
            "algorithm_id": algo_id,
            "algorithm_name": algo_info["name"],
            "stats": {
                "total": total,
                "verified": len(verified),
                "correct": len(correct),
                "accuracy": round(len(correct) / len(verified) * 100, 1) if verified else 0,
                "bs_accuracy": round(len(bs_correct) / len(verified) * 100, 1) if verified else 0,
                "oe_accuracy": round(len(oe_correct) / len(verified) * 100, 1) if verified else 0,
            }
        })
    return stats


def get_available_algorithms() -> list:
    """获取所有可用算法列表"""
    return list_algorithms()
