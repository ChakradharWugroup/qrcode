from fastapi import FastAPI, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from io import BytesIO
import qrcode
import base64
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from rapidocr_onnxruntime import RapidOCR

import models, schemas
from database import engine, get_db

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Master QR Manager")
templates = Jinja2Templates(directory="templates")
ocr = RapidOCR()

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
    
    if img is None:
        return JSONResponse({"error": "Invalid image"}, status_code=400)

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


# Public URL that people see when they scan the Master QR
@app.get("/q/{collection_id}", response_class=HTMLResponse)
def view_master_qr(request: Request, collection_id: str, db: Session = Depends(get_db)):
    collection = db.query(models.Collection).filter(models.Collection.id == collection_id).first()
    if not collection:
        return HTMLResponse(content="Collection not found", status_code=404)
    return templates.TemplateResponse(request=request, name="public_view.html", context={"request": request, "collection": collection})
