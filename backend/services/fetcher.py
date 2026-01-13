import requests
import logging
from datetime import datetime
from flask import current_app
from extensions import db
from models import LotteryRecord
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

def _build_params(act, extra=None):
    params = {
        "act": act,
        "type": current_app.config.get("GAME_TYPE", "jnd28"),
        "token": current_app.config.get("API_TOKEN")
    }
    if extra:
        params.update({k: v for k, v in extra.items() if v is not None})
    return params

def _request_api(act, extra=None):
    try:
        resp = requests.get(
            current_app.config.get("API_BASE_URL", "http://hanxin28.com/api/api.php"),
            params=_build_params(act, extra),
            timeout=current_app.config.get("API_TIMEOUT", 10)
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("code") != 200:
            raise ValueError(payload.get("msg", "API returned error"))
        return payload.get("data")
    except Exception as e:
        logger.error(f"API request failed for act={act}: {e}")
        return None

def _parse_time(time_str):
    if not time_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    return None

def _extract_numbers(item):
    """
    Extract number list [n1, n2, n3] from API payload.
    """
    nums = None
    numbers_str = item.get("numbers")
    if isinstance(numbers_str, str):
        try:
            nums = [int(x) for x in numbers_str.split(",") if x != ""]
        except Exception:
            nums = None

    if not nums or len(nums) != 3:
        parts = [item.get("num1"), item.get("num2"), item.get("num3")]
        if all(p is not None for p in parts):
            try:
                nums = [int(p) for p in parts]
            except Exception:
                nums = None
    return nums

def _save_record(issue, nums, sum_val, open_time=None):
    record = LotteryRecord(
        issue=issue,
        open_time=open_time,
        code1=nums[0],
        code2=nums[1],
        code3=nums[2],
        sum_val=sum_val
    )
    db.session.add(record)
    return record

def persist_latest_record(latest_payload):
    """
    Ensure the latest draw from `act=new` is saved to the database.
    """
    if not latest_payload:
        return None
    issue = str(latest_payload.get("current_stage") or "")
    if not issue:
        return None

    existing = LotteryRecord.query.filter_by(issue=issue).first()
    if existing:
        return existing

    nums = _extract_numbers(latest_payload)
    if not nums or len(nums) != 3:
        logger.warning(f"Cannot parse numbers for latest issue {issue}")
        return None

    sum_val = int(latest_payload.get("sum") or sum(nums))
    open_time = _parse_time(latest_payload.get("time"))

    record = _save_record(issue, nums, sum_val, open_time)
    try:
        from services.predictor import verify_predictions_for_issue, generate_all_predictions
        verify_predictions_for_issue(record)
        generate_all_predictions(str(int(issue) + 1))
    except Exception as e:
        logger.error(f"Prediction hooks failed for issue {issue}: {e}")

    try:
        db.session.commit()
        return record
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Failed to persist latest issue {issue}: {e}")
        return None

def fetch_history(limit=None):
    """
    Fetch historical data from the API and save to DB.
    """
    fetch_limit = limit or current_app.config.get("HISTORY_FETCH_LIMIT", 50)
    records = _request_api("history", {"limit": fetch_limit})
    if not records:
        return

    count_new = 0
    for item in records:
        issue = str(item.get("stage") or "")
        if not issue:
            continue

        if LotteryRecord.query.filter_by(issue=issue).first():
            continue

        nums = _extract_numbers(item)
        if not nums or len(nums) != 3:
            logger.warning(f"Skip issue {issue}: invalid numbers payload {item}")
            continue

        sum_val = int(item.get("sum") or sum(nums))
        open_time = _parse_time(item.get("time"))

        record = _save_record(issue, nums, sum_val, open_time)
        count_new += 1

        try:
            from services.predictor import verify_predictions_for_issue, generate_all_predictions
            verify_predictions_for_issue(record)
            generate_all_predictions(str(int(issue) + 1))
        except Exception as e:
            logger.error(f"Auto-logic failed for {issue}: {e}")

    if count_new > 0:
        try:
            db.session.commit()
            logger.info(f"Fetched and saved {count_new} new records.")
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Commit failed while saving history: {e}")

def get_latest_snapshot():
    """
    Fetch latest draw info + countdown from external API and normalize response.
    """
    latest = _request_api("new")
    countdown = _request_api("countdown")

    payload = {"success": bool(latest or countdown)}

    if latest:
        nums = _extract_numbers(latest) or []
        payload.update({
            "current_stage": latest.get("current_stage"),
            "next_stage": latest.get("next_stage"),
            "numbers": nums,
            "sum": latest.get("sum") or (sum(nums) if nums else None),
            "type_dx": latest.get("type_dx"),
            "type_ds": latest.get("type_ds"),
            "type_zh": latest.get("type_zh"),
            "opened_at": latest.get("time")
        })

        try:
            persist_latest_record(latest)
        except Exception as e:
            logger.error(f"Failed to persist latest draw: {e}")

    if countdown:
        payload.update({
            "remaining_seconds": countdown.get("remaining_seconds"),
            "next_stage": countdown.get("next_stage") or payload.get("next_stage")
        })
        # Compatibility alias for frontend countdown component
        payload["djs"] = countdown.get("remaining_seconds")

    return payload

def get_next_issue():
    """
    Backwards-compatible wrapper for /api/latest endpoint.
    """
    return get_latest_snapshot()

def fetch_data_job(app):
    """
    Job wrapper to run with app context.
    This is the main scheduled task that keeps data up-to-date.
    """
    with app.app_context():
        # 1. Fetch latest draw + countdown (this also persists new draws to DB)
        try:
            snapshot = get_latest_snapshot()
            if snapshot.get("success"):
                logger.debug(f"Realtime snapshot: stage={snapshot.get('current_stage')}, countdown={snapshot.get('remaining_seconds')}s")
        except Exception as e:
            logger.error(f"Failed to fetch latest snapshot: {e}")
        
        # 2. Fetch recent history to catch any missed records
        try:
            fetch_history(limit=10)  # Only fetch recent to reduce load
        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
