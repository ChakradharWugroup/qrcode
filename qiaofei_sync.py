from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import requests
import hashlib

import traceback

router = APIRouter()

@router.post("/api/sync_qiaofei")
async def sync_qiaofei(request: Request, timeframe: str = 'month'):
    try:
        # 1. Login to Qiaofei
        session = requests.Session()
        headers = {
            "Origin": "https://qiaofei.huole.cn",
            "Referer": "https://qiaofei.huole.cn/",
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*"
        }
        login_payload = {
            "mobile": "933762865",
            "password": hashlib.md5(b"Stephan16146038").hexdigest(),
            "area_code": "886"
        }
        
        login_resp = session.post("https://dark-lab-2998.kallec.workers.dev/common/login/login", json=login_payload, headers=headers)
        login_data = login_resp.json()
        
        if str(login_data.get('code')) not in ['1', '200']:
            return JSONResponse(status_code=400, content={"error": f"Login failed: {login_data.get('msg')}"})
            
        data = login_data['data']
        params = {
            "token": data['token'],
            "cid": data['cid'],
            "uid": data['uid'],
            "plate_type": "backend",
            "v": login_data.get('v', '')
        }
        
        # 2. Compute target date
        import datetime
        today = datetime.date.today()
        if timeframe == 'today':
            target_date = today
        elif timeframe == 'yesterday':
            target_date = today - datetime.timedelta(days=1)
        elif timeframe == 'week':
            target_date = today - datetime.timedelta(days=7)
        elif timeframe == '3months':
            target_date = today - datetime.timedelta(days=90)
        else: # month
            target_date = today - datetime.timedelta(days=30)
            
        target_date_str = target_date.strftime("%Y-%m-%d")

        # 3. Fetch the Production Orders List
        list_url = "https://dark-lab-2998.kallec.workers.dev/common/cut_order/get_product_list"
        list_resp = session.post(list_url, params=params, json={"page": 1, "page_size": 2000}, headers=headers)
        list_data = list_resp.json()
        
        if str(list_data.get('code')) not in ['1', '200']:
            return JSONResponse(status_code=400, content={"error": "Failed to fetch production list"})
            
        raw_orders = list_data.get('data', {}).get('list', [])
        
        # Filter orders by cut_time >= target_date
        orders = []
        for o in raw_orders:
            cut_time = o.get('cut_time')
            if not cut_time:
                # If no cut_time, just include it to be safe if it's recent
                orders.append(o)
                continue
                
            # cut_time format: "2026-09-01"
            if cut_time >= target_date_str:
                orders.append(o)
                
        # Hard limit to 2000 orders to prevent server timeouts (this is ~100k tickets!)
        orders = orders[:2000]
        
        
        all_tickets = {}
        
        # 3. For each Order, fetch the Tickets CONCURRENTLY
        import concurrent.futures
        
        def fetch_ticket_for_order(order):
            cut_order_id = order.get('cut_order_id')
            style_name = order.get('spu_name', '')
            if not cut_order_id:
                return {}
                
            ticket_url = "https://dark-lab-2998.kallec.workers.dev/common/cut_order/get_cut_order_ticket_list"
            try:
                ticket_resp = requests.post(ticket_url, params=params, json={"cut_order_id": cut_order_id, "page": 1, "page_size": 10000}, headers=headers, timeout=10)
                ticket_data = ticket_resp.json()
                
                res = {}
                if str(ticket_data.get('code')) in ['1', '200']:
                    tickets = ticket_data.get('data', {}).get('list', [])
                    for t in tickets:
                        header = t.get('header_data', {})
                        tid = header.get('ticket_id')
                        if tid:
                            # Guessing bundle number field based on common Qiaofei schemas
                            bundle_no = header.get('ticket_no', '')
                            
                            res[str(tid)] = {
                                "color": header.get('co_val', ''),
                                "size": header.get('si_val', ''),
                                "quantity": header.get('num', ''),
                                "style": order.get('spu_no', '') + ' ' + order.get('spu_name', ''),
                                "bed": order.get('cut_order_no', ''),
                                "company": order.get('custom_name', ''),
                                "bundle": bundle_no,
                                "cut_order_id": cut_order_id
                            }
                return res
            except:
                return {}
                
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            futures = [executor.submit(fetch_ticket_for_order, o) for o in orders]
            for future in concurrent.futures.as_completed(futures):
                all_tickets.update(future.result())
        
        return JSONResponse(status_code=200, content={"success": True, "total_tickets": len(all_tickets), "tickets": all_tickets})
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback.format_exc()})
