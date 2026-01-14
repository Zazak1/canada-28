from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from extensions import db, scheduler
import logging
import models
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register scheduler (only once, avoid double-start in Flask debug reloader)
    from services.fetcher import fetch_data_job, get_next_issue, fetch_history
    
    if not scheduler.running:
        scheduler.add_job(
            func=fetch_data_job,
            trigger="interval",
            seconds=app.config['POLL_INTERVAL'],
            id='fetch_job',
            replace_existing=True,
            args=[app]
        )
        logger.info(f"Scheduler job registered: fetch every {app.config['POLL_INTERVAL']}s")

    with app.app_context():
        db.create_all()
        # Seed initial history so UI has data immediately after boot
        try:
            fetch_history(limit=app.config.get('HISTORY_FETCH_LIMIT'))
        except Exception as e:
            logger.error(f"Initial history fetch failed: {e}")
        
    @app.route('/api/status')
    def status():
        """
        Returns system status.
        """
        return jsonify({
            "status": "running", 
            "scheduler": scheduler.running
        })

    @app.route('/api/latest')
    def latest():
        """
        Returns the countdown and next issue info from external API (proxied).
        """
        data = get_next_issue()
        if data and data.get("success"):
            return jsonify(data)
        else:
            return jsonify({"success": False, "message": "Failed to fetch data"}), 500
    
    @app.route('/api/prediction')
    def prediction():
        """
        Returns prediction for the next issue.
        Supports algorithm selection via ?algorithm=xxx query param.
        """
        from services.predictor import get_latest_prediction
        algorithm_id = request.args.get('algorithm', 'algo1')
        pred = get_latest_prediction(algorithm_id)
        if pred:
            return jsonify(pred)
        else:
            return jsonify({"status": "no data"}), 404

    @app.route('/api/algorithms')
    def algorithms():
        """
        Returns list of available prediction algorithms.
        """
        from services.predictor import get_available_algorithms
        return jsonify(get_available_algorithms())

    @app.route('/api/predictions/all')
    def all_predictions():
        """
        Returns predictions from ALL algorithms for comparison.
        """
        from services.predictor import get_all_predictions
        predictions = get_all_predictions()
        return jsonify(predictions)

    @app.route('/api/algorithm/<algo_id>/history')
    def algorithm_history(algo_id):
        """
        Returns prediction history and stats for a specific algorithm.
        """
        from services.predictor import get_algorithm_history
        limit = int(request.args.get('limit', 100))
        data = get_algorithm_history(algo_id, limit)
        return jsonify(data)

    @app.route('/api/algorithms/stats')
    def algorithms_stats():
        """
        Returns stats for all algorithms.
        """
        from services.predictor import get_all_algorithm_stats
        stats = get_all_algorithm_stats()
        return jsonify(stats)

    @app.route('/api/query/<issue>')
    def query_issue(issue):
        """
        根据期号查询开奖结果
        """
        from models import LotteryRecord
        record = LotteryRecord.query.filter_by(issue=issue).first()
        if record:
            return jsonify({
                "success": True,
                "data": record.to_dict()
            })
        else:
            return jsonify({
                "success": False,
                "message": f"未找到期号 {issue} 的记录"
            }), 404

    @app.route('/api/history')
    def history():
        from models import LotteryRecord, Prediction
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('limit', 100))

        # Ensure we have fresh data when the system just started
        if LotteryRecord.query.count() == 0:
            try:
                fetch_history(limit=app.config.get('HISTORY_FETCH_LIMIT'))
            except Exception as e:
                logger.error(f"On-demand history fetch failed: {e}")
        
        # Join with Prediction table
        # We need an outer join to get all history even if no prediction exists
        # In SQLAlch: db.session.query(LotteryRecord, Prediction).outerjoin(Prediction, LotteryRecord.issue == Prediction.target_issue)...
        
        records = db.session.query(LotteryRecord, Prediction).\
            outerjoin(Prediction, LotteryRecord.issue == Prediction.target_issue).\
            order_by(LotteryRecord.issue.desc()).\
            paginate(page=page, per_page=per_page, error_out=False)
            
        data = []
        bs_map = {"Big": "大", "Small": "小"}
        oe_map = {"Odd": "单", "Even": "双"}
        
        for rec, pred in records.items:
            item = rec.to_dict()
            if pred:
                pred_data = json.loads(pred.predicted_val)
                raw_bs = pred_data.get('big_small')
                raw_oe = pred_data.get('odd_even')
                item['prediction'] = {
                    "big_small": bs_map.get(raw_bs, raw_bs),
                    "odd_even": oe_map.get(raw_oe, raw_oe),
                    "bs_correct": pred_data.get('bs_correct'),
                    "oe_correct": pred_data.get('oe_correct'),
                    "is_correct": pred.is_correct
                }
            else:
                item['prediction'] = None
            data.append(item)

        return jsonify({
            "total": records.total,
            "pages": records.pages,
            "data": data
        })

    return app

app = create_app()

def start_scheduler():
    """Start the scheduler if not already running."""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started - realtime data fetching enabled")

# Prevent double-start in Flask debug reloader
# WERKZEUG_RUN_MAIN is set to 'true' in the reloader child process
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
    start_scheduler()

if __name__ == '__main__':
    # In debug mode, scheduler starts via WERKZEUG_RUN_MAIN check above
    # In non-debug mode, start it here
    if not app.debug and not scheduler.running:
        start_scheduler()
    app.run(debug=True, port=5000, use_reloader=True)
