from fastapi import FastAPI, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from io import BytesIO
import qrcode
import base64
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from rapidocr_onnxruntime import RapidOCR
import os

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Master QR Manager")

# Add CORS so Vercel can talk to Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change this to your Vercel URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")
ocr = RapidOCR()

# ==========================================
# REST API ENDPOINTS (FOR VERCEL FRONTEND)
# ==========================================

@app.get("/api/collections")
def api_get_collections(db: Session = Depends(get_db)):
    collections = db.query(models.Collection).all()
    # return list of dictionaries with length of qr_codes
    return [
        {
            "id": c.id,
            "name": c.name,
            "qr_count": len(c.qr_codes)
        } for c in collections
    ]

@app.post("/api/collections/create")
def api_create_collection(collection: schemas.CollectionCreate, db: Session = Depends(get_db)):
    db_collection = models.Collection(name=collection.name)
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return {"id": db_collection.id, "name": db_collection.name}

@app.get("/api/collections/{collection_id}")
def api_get_collection(collection_id: str, request: Request, db: Session = Depends(get_db)):
    c = db.query(models.Collection).filter(models.Collection.id == collection_id).first()
    if not c:
        return JSONResponse({"error": "Not found"}, status_code=404)
        
    master_url = f"https://{request.headers.get('host')}/q/{c.id}" # Will be updated in frontend
    qr = qrcode.make(master_url)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    master_qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return {
        "id": c.id,
        "name": c.name,
        "master_qr": master_qr_base64,
        "qr_codes": [
            {
                "id": qr.id,
                "qr_data": qr.qr_data,
                "style_no": qr.style_no,
                "size": qr.size,
                "quantity": qr.quantity,
                "company_name": qr.company_name,
                "bed_no": qr.bed_no,
                "bundle_no": qr.bundle_no,
                "color": qr.color,
                "total_bundles": qr.total_bundles,
                "total_quantity": qr.total_quantity
            } for qr in c.qr_codes
        ]
    }

@app.post("/api/collections/{collection_id}/add_qr")
def api_add_qr(collection_id: str, item: schemas.GarmentQRCodeCreate, db: Session = Depends(get_db)):
    db_qr = models.GarmentQRCode(
        collection_id=collection_id,
        qr_data=item.qr_data,
        company_name=item.company_name,
        style_no=item.style_no,
        bed_no=item.bed_no,
        bundle_no=item.bundle_no,
        quantity=item.quantity,
        color=item.color,
        size=item.size,
        total_bundles=item.total_bundles,
        total_quantity=item.total_quantity
    )
    db.add(db_qr)
    db.commit()
    return {"status": "success"}

@app.post("/api/collections/{collection_id}/upload_qr")
async def api_upload_qr(collection_id: str, file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return JSONResponse({"error": "Invalid image"}, status_code=400)

    qr_data = "No QR detected"
    decoded_objects = decode(img)
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode("utf-8")
        
    result, elapse = ocr(img)
    texts = [item[1] for item in result] if result else []
        
    style_no, bed_no, bundle_no, quantity, color, size, total_bundles, total_quantity = "Unknown", "0", "0", 0, "Unknown", "Unknown", 0, 0
    
    for text in texts:
        if "款号:" in text or "款号" in text:
            style_no = text.replace("款号:", "").replace("款号", "").strip()
        elif "床次:" in text or "床次" in text:
            bed_no = text.replace("床次:", "").replace("床次", "").strip()
        elif "扎号:" in text or "扎号" in text:
            bundle_no = text.replace("扎号:", "").replace("扎号", "").strip()
        elif "数量" in text and "总数" not in text:
            try: quantity = int(''.join(filter(str.isdigit, text)))
            except: pass
        elif "颜色:" in text or "颜色" in text:
            color = text.replace("颜色:", "").replace("颜色", "").strip()
        elif "总扎" in text:
            try: total_bundles = int(''.join(filter(str.isdigit, text)))
            except: pass
        elif "总数" in text:
            try: total_quantity = int(''.join(filter(str.isdigit, text)))
            except: pass
        elif text.strip().upper() in ["S", "M", "L", "XL", "XXL", "XXXL"]:
            size = text.strip().upper()

    return {
        "qr_data": qr_data,
        "company_name": "江西大藤制衣有限公司",
        "style_no": style_no,
        "bed_no": bed_no,
        "bundle_no": bundle_no,
        "quantity": quantity,
        "color": color,
        "size": size,
        "total_bundles": total_bundles,
        "total_quantity": total_quantity
    }

# ==========================================
# OLD JINJA2 ROUTES (Keep for local testing)
# ==========================================

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    collections = db.query(models.Collection).all()
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"request": request, "collections": collections})

@app.post("/collections/create")
def create_collection(name: str = Form(...), db: Session = Depends(get_db)):
    db_collection = models.Collection(name=name)
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return RedirectResponse(url=f"/collections/{db_collection.id}", status_code=303)

@app.get("/collections/{collection_id}", response_class=HTMLResponse)
def view_collection_manager(request: Request, collection_id: str, db: Session = Depends(get_db)):
    collection = db.query(models.Collection).filter(models.Collection.id == collection_id).first()
    if not collection:
        return HTMLResponse(content="Collection not found", status_code=404)
    
    # Generate Master QR Code image
    master_url = str(request.url_for("view_master_qr", collection_id=collection_id))
    qr = qrcode.make(master_url)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    master_qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return templates.TemplateResponse(request=request, name="collection_manager.html", context={
        "request": request, 
        "collection": collection,
        "master_qr": master_qr_base64,
        "master_url": master_url
    })

@app.post("/collections/{collection_id}/add_qr")
def add_qr_to_collection(
    collection_id: str,
    qr_data: str = Form(...),
    company_name: str = Form("江西大藤制衣有限公司"),
    style_no: str = Form(...),
    bed_no: str = Form(...),
    bundle_no: str = Form(...),
    quantity: int = Form(...),
    color: str = Form(...),
    size: str = Form(...),
    total_bundles: int = Form(None),
    total_quantity: int = Form(None),
    db: Session = Depends(get_db)
):
    db_qr = models.GarmentQRCode(
        collection_id=collection_id,
        qr_data=qr_data,
        company_name=company_name,
        style_no=style_no,
        bed_no=bed_no,
        bundle_no=bundle_no,
        quantity=quantity,
        color=color,
        size=size,
        total_bundles=total_bundles,
        total_quantity=total_quantity
    )
    db.add(db_qr)
    db.commit()
    return RedirectResponse(url=f"/collections/{collection_id}", status_code=303)

@app.post("/collections/{collection_id}/upload_qr")
async def upload_qr_image(collection_id: str, file: UploadFile = File(...)):
    from fastapi.responses import JSONResponse
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    try:
        if img is None:
            return JSONResponse({"error": "Invalid image format (e.g. unsupported HEIC) or corrupted file."}, status_code=400)

        # 1. Extract QR Code
        qr_data = "No QR detected"
        decoded_objects = decode(img)
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode("utf-8")
            
        # 2. Extract Text using OCR
        result, elapse = ocr(img)
        texts = []
        if result:
            texts = [item[1] for item in result]
            
        # 3. Simple parsing logic based on label format
        style_no = "Unknown"
        bed_no = "0"
        bundle_no = "0"
        quantity = 0
        color = "Unknown"
        size = "Unknown"
        total_bundles = 0
        total_quantity = 0
        
        for text in texts:
            if "款号:" in text or "款号" in text:
                style_no = text.replace("款号:", "").replace("款号", "").strip()
            elif "床次:" in text or "床次" in text:
                bed_no = text.replace("床次:", "").replace("床次", "").strip()
            elif "扎号:" in text or "扎号" in text:
                bundle_no = text.replace("扎号:", "").replace("扎号", "").strip()
            elif "数量" in text and "总数" not in text:
                try:
                    quantity = int(''.join(filter(str.isdigit, text)))
                except:
                    pass
            elif "颜色:" in text or "颜色" in text:
                color = text.replace("颜色:", "").replace("颜色", "").strip()
            elif "总扎" in text:
                try:
                    total_bundles = int(''.join(filter(str.isdigit, text)))
                except:
                    pass
            elif "总数" in text:
                try:
                    total_quantity = int(''.join(filter(str.isdigit, text)))
                except:
                    pass
            elif text.strip().upper() in ["S", "M", "L", "XL", "XXL", "XXXL"]:
                size = text.strip().upper()

        return JSONResponse({
            "qr_data": qr_data,
            "company_name": "江西大藤制衣有限公司",
            "style_no": style_no,
            "bed_no": bed_no,
            "bundle_no": bundle_no,
            "quantity": quantity,
            "color": color,
            "size": size,
            "total_bundles": total_bundles,
            "total_quantity": total_quantity
        })
    except Exception as e:
        import traceback
        return JSONResponse({"error": f"Server crash: {str(e)}"}, status_code=500)


# Public URL that people see when they scan the Master QR
@app.get("/q/{collection_id}", response_class=HTMLResponse)
def view_master_qr(request: Request, collection_id: str, db: Session = Depends(get_db)):
    collection = db.query(models.Collection).filter(models.Collection.id == collection_id).first()
    if not collection:
        return HTMLResponse(content="Collection not found", status_code=404)
    return templates.TemplateResponse(request=request, name="public_view.html", context={"request": request, "collection": collection})
