from extensions import db
from datetime import datetime


class LotteryRecord(db.Model):
    """开奖记录"""
    id = db.Column(db.Integer, primary_key=True)
    issue = db.Column(db.String(20), unique=True, nullable=False)
    open_time = db.Column(db.DateTime, nullable=True)
    code1 = db.Column(db.Integer, nullable=False)
    code2 = db.Column(db.Integer, nullable=False)
    code3 = db.Column(db.Integer, nullable=False)
    sum_val = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        big_small = "大" if self.sum_val >= 14 else "小"
        odd_even = "单" if self.sum_val % 2 != 0 else "双"
        return {
            "issue": self.issue,
            "open_time": self.open_time.isoformat() if self.open_time else None,
            "code1": self.code1,
            "code2": self.code2,
            "code3": self.code3,
            "numbers": f"{self.code1},{self.code2},{self.code3}",
            "sum_val": self.sum_val,
            "type_dx": big_small,
            "type_ds": odd_even,
            "type_zh": f"{big_small}{odd_even}"
        }


class Prediction(db.Model):
    """预测记录 - 每个算法独立保存"""
    id = db.Column(db.Integer, primary_key=True)
    target_issue = db.Column(db.String(20), nullable=False)
    algorithm_id = db.Column(db.String(20), nullable=False, default='algo1')  # 算法ID
    predicted_val = db.Column(db.String(200), nullable=False)  # JSON存储预测详情
    is_correct = db.Column(db.Boolean, nullable=True)  # 整体是否正确
    bs_correct = db.Column(db.Boolean, nullable=True)  # 大小是否正确
    oe_correct = db.Column(db.Boolean, nullable=True)  # 单双是否正确
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 联合唯一索引：同一期号同一算法只能有一条预测
    __table_args__ = (
        db.UniqueConstraint('target_issue', 'algorithm_id', name='uix_issue_algo'),
    )

    def to_dict(self):
        import json
        data = json.loads(self.predicted_val) if self.predicted_val else {}
        return {
            "issue": self.target_issue,
            "algorithm_id": self.algorithm_id,
            "big_small": data.get("big_small"),
            "odd_even": data.get("odd_even"),
            "is_correct": self.is_correct,
            "bs_correct": self.bs_correct,
            "oe_correct": self.oe_correct,
        }
