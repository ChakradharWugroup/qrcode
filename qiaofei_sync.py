"""
Qiaofei Ticket Sync Module
--------------------------
Handles server-side authentication and data fetching from the Qiaofei production
management system (https://qiaofei.huole.cn). All API calls are proxied through
a Cloudflare Worker to support access from restricted networks.

Environment Variables Required:
    QIAOFEI_MOBILE   - Qiaofei account phone number
    QIAOFEI_PASSWORD - Qiaofei account password (plain text, hashed with MD5 before sending)
    QIAOFEI_AREA_CODE - Country calling code (e.g. "886" for Taiwan)
    QIAOFEI_PROXY_URL - Cloudflare Worker proxy base URL
"""

import os
import hashlib
import datetime
import traceback
import concurrent.futures

import requests
from fastapi import APIRouter, Request, BackgroundTasks
import uuid

SYNC_TASKS = {}
from fastapi.responses import JSONResponse

router = APIRouter()

# --- Configuration (read from environment at request time, not module import) ---
# This ensures load_dotenv() in main.py always runs first.
def _get_config() -> dict:
    return {
        "mobile": os.getenv("QIAOFEI_MOBILE", ""),
        "password": os.getenv("QIAOFEI_PASSWORD", ""),
        "area_code": os.getenv("QIAOFEI_AREA_CODE", "886"),
        "proxy_url": os.getenv("QIAOFEI_PROXY_URL", ""),
    }

# Max orders to process per sync request (prevents server timeouts)
MAX_ORDERS_PER_SYNC = 2000

# Standard headers for all Qiaofei API requests
QIAOFEI_HEADERS = {
    "Origin": "https://qiaofei.huole.cn",
    "Referer": "https://qiaofei.huole.cn/",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
}


def _get_start_date(timeframe: str) -> str:
    """Calculate the start date string for a given timeframe label."""
    today = datetime.date.today()
    offsets = {
        "today": 0,
        "yesterday": 1,
        "week": 7,
        "month": 30,
        "3months": 90,
    }
    days = offsets.get(timeframe, 30)
    return (today - datetime.timedelta(days=days)).strftime("%Y-%m-%d")


def _fetch_tickets_for_order(order: dict, params: dict, proxy_url: str) -> dict:
    """Fetch all tickets for a single cut order. Returns a dict keyed by ticket_id."""
    cut_order_id = order.get("cut_order_id")
    if not cut_order_id:
        return {}

    url = f"{proxy_url}/common/cut_order/get_cut_order_ticket_list"
    try:
        resp = requests.post(
            url,
            params=params,
            json={"cut_order_id": cut_order_id, "page": 1, "page_size": 10000},
            headers=QIAOFEI_HEADERS,
            timeout=10,
        )
        data = resp.json()
        if str(data.get("code")) not in ["1", "200"]:
            return {}

        result = {}
        for ticket in data.get("data", {}).get("list", []):
            header = ticket.get("header_data", {})
            tid = header.get("ticket_id")
            if tid:
                result[str(tid)] = {
                    "color": header.get("co_val", ""),
                    "size": header.get("si_val", ""),
                    "quantity": header.get("num", ""),
                    "style": order.get("spu_no", "") + " " + order.get("spu_name", ""),
                    "bed": order.get("cut_order_no", ""),
                    "company": order.get("custom_name", ""),
                    "bundle": header.get("ticket_no", ""),
                    "cut_order_id": cut_order_id,
                }
        return result
    except Exception:
        return {}


@router.post("/api/sync_qiaofei")
async def sync_qiaofei(request: Request, background_tasks: BackgroundTasks, timeframe: str = "3months"):
    task_id = str(uuid.uuid4())
    SYNC_TASKS[task_id] = {"status": "running", "tickets": {}}
    background_tasks.add_task(_run_sync_task, task_id, timeframe)
    return JSONResponse({"task_id": task_id, "status": "running"})

@router.get("/api/sync_qiaofei/status")
async def sync_qiaofei_status(task_id: str):
    if task_id not in SYNC_TASKS:
        return JSONResponse({"status": "error", "error": "Task not found"}, status_code=404)
    task_data = SYNC_TASKS[task_id]
    if task_data["status"] == "done":
        return JSONResponse({"status": "done", "total_tickets": len(task_data["tickets"]), "tickets": task_data["tickets"]})
    if task_data["status"] == "error":
        return JSONResponse({"status": "error", "error": task_data.get("error")}, status_code=400)
    return JSONResponse({"status": "running"})

def _run_sync_task(task_id: str, timeframe: str):
    """
    Authenticate with Qiaofei and download all production tickets for the given timeframe.

    Args:
        timeframe: One of 'today', 'yesterday', 'week', 'month', '3months'.
                   Defaults to '3months'.

    Returns:
        JSON with total_tickets count and a tickets dict keyed by ticket_id.
    """
    cfg = _get_config()
    if not cfg["mobile"] or not cfg["password"] or not cfg["proxy_url"]:
        SYNC_TASKS[task_id] = {"status": "error", "error": "Qiaofei credentials not configured. Set QIAOFEI_MOBILE, QIAOFEI_PASSWORD, and QIAOFEI_PROXY_URL environment variables."}
        return

    try:
        # Step 1: Authenticate
        session = requests.Session()
        login_payload = {
            "mobile": cfg["mobile"],
            "password": hashlib.md5(cfg["password"].encode()).hexdigest(),
            "area_code": cfg["area_code"],
        }
        login_resp = session.post(
            f"{cfg['proxy_url']}/common/login/login",
            json=login_payload,
            headers=QIAOFEI_HEADERS,
        )
        login_data = login_resp.json()

        if str(login_data.get("code")) not in ["1", "200"]:
            SYNC_TASKS[task_id] = {"status": "error", "error": f"Login failed: {login_data.get('msg')}"}
            return

        auth = login_data["data"]
        params = {
            "token": auth["token"],
            "cid": auth["cid"],
            "uid": auth["uid"],
            "plate_type": "backend",
            "v": login_data.get("v", ""),
        }

        # Step 2: Fetch production order list
        start_date = _get_start_date(timeframe)
        list_resp = session.post(
            f"{cfg['proxy_url']}/common/cut_order/get_product_list",
            params=params,
            json={"page": 1, "page_size": 2000},
            headers=QIAOFEI_HEADERS,
        )
        list_data = list_resp.json()

        if str(list_data.get("code")) not in ["1", "200"]:
            SYNC_TASKS[task_id] = {"status": "error", "error": "Failed to fetch production order list"}
            return

        # Filter orders by cut_time >= start_date
        all_orders = list_data.get("data", {}).get("list", [])
        filtered_orders = [
            o for o in all_orders
            if not o.get("cut_time") or o.get("cut_time", "") >= start_date
        ][:MAX_ORDERS_PER_SYNC]

        # Step 3: Fetch tickets concurrently (40 parallel threads)
        all_tickets = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            futures = [
                executor.submit(_fetch_tickets_for_order, order, params, cfg['proxy_url'])
                for order in filtered_orders
            ]
            for future in concurrent.futures.as_completed(futures):
                all_tickets.update(future.result())

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "total_tickets": len(all_tickets),
                "tickets": all_tickets,
            },
        )

    except Exception as e:
        SYNC_TASKS[task_id] = {"status": "error", "error": f"{str(e)}"}
        return
