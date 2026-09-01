from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import requests
import hashlib

import traceback

router = APIRouter()

@router.post("/api/sync_qiaofei")
async def sync_qiaofei(request: Request, limit: int = 50):
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
        
        login_resp = session.post("https://saofeiapi.huole.cn/common/login/login", json=login_payload, headers=headers)
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
        
        # 2. Fetch the Production Orders List
        list_url = "https://saofeiapi.huole.cn/common/cut_order/get_product_list"
        # Fetching first 50 latest orders
        list_resp = session.post(list_url, params=params, json={"page": 1, "page_size": 100000}, headers=headers)
        list_data = list_resp.json()
        
        if str(list_data.get('code')) not in ['1', '200']:
            return JSONResponse(status_code=400, content={"error": "Failed to fetch production list"})
            
        orders = list_data.get('data', {}).get('list', [])[:limit]
        
        all_tickets = {}
        
        # 3. For each Order, fetch the Tickets CONCURRENTLY
        import concurrent.futures
        
        def fetch_ticket_for_order(order):
            cut_order_id = order.get('cut_order_id')
            style_name = order.get('spu_name', '')
            if not cut_order_id:
                return {}
                
            ticket_url = "https://saofeiapi.huole.cn/common/cut_order/get_cut_order_ticket_list"
            try:
                ticket_resp = requests.post(ticket_url, params=params, json={"cut_order_id": cut_order_id}, headers=headers, timeout=15)
                ticket_data = ticket_resp.json()
                
                res = {}
                if str(ticket_data.get('code')) in ['1', '200']:
                    tickets = ticket_data.get('data', {}).get('list', [])
                    for t in tickets:
                        header = t.get('header_data', {})
                        tid = header.get('ticket_id')
                        if tid:
                            res[str(tid)] = {
                                "color": header.get('co_val', ''),
                                "size": header.get('si_val', ''),
                                "quantity": header.get('num', ''),
                                "style": style_name,
                                "cut_order_id": cut_order_id
                            }
                return res
            except:
                return {}
                
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(fetch_ticket_for_order, o) for o in orders]
            for future in concurrent.futures.as_completed(futures):
                all_tickets.update(future.result())
        
        return JSONResponse(status_code=200, content={"success": True, "total_tickets": len(all_tickets), "tickets": all_tickets})
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "traceback": traceback.format_exc()})
