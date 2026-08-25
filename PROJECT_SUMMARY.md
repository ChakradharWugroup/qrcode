# Project Summary: Master QR Manager (Garment Tracking System)

## 1. Abstract
The **Master QR Manager** is a mobile-first, cloud-hosted web application designed to streamline inventory tracking for garment manufacturing factories. It eliminates manual data entry by allowing factory workers to take photos of garment tags directly from their smartphones. Using an AI-powered Optical Character Recognition (OCR) pipeline and dynamic spatial text parsing, the system automatically extracts critical manufacturing metadata (such as Style No, Bed No, Bundle No, Quantity, Color, and Size) alongside decoding any embedded QR data. Finally, it aggregates these individual items into a unified "Collection" and generates a single **Master QR Code** that represents the entire batch, vastly simplifying factory logistics, shipping, and tracking.

---

## 2. Technology Stack
*   **Backend / API:** Python, FastAPI (High-performance asynchronous web framework)
*   **Frontend:** HTML5, Vanilla JavaScript, Tailwind CSS (Mobile-responsive UI), Jinja2 Templates
*   **Database:** SQLite via SQLAlchemy ORM (Configured to support seamless migration to PostgreSQL)
*   **Deployment & DevOps:** Docker, Railway Cloud, GitHub

---

## 3. AI Models & Computer Vision Used
The project avoids expensive cloud API calls (like OpenAI or Google Vision) by running highly optimized AI models directly on the server's CPU:

1.  **RapidOCR (ONNX Runtime):** 
    *   *What it is:* A lightweight, highly accurate, open-source OCR engine based on the PaddleOCR architecture. 
    *   *Why it's used:* It runs on the ONNX runtime (allowing for extremely fast CPU inference) and is specifically trained to accurately read both complex Chinese characters and English alphanumerics simultaneously, which is critical for Chinese factory tags.
2.  **OpenCV (Open Source Computer Vision Library):** 
    *   Used for processing the raw image byte streams uploaded from mobile cameras, converting them into multi-dimensional NumPy arrays for the AI to read.
3.  **PyZbar:** 
    *   A specialized C-library wrapper used to scan the image for QR code patterns and decode their embedded URLs/data instantly.

---

## 4. Methodology & How It Works

### Step 1: Mobile Data Capture
The frontend utilizes HTML5's `capture="environment"` attribute, allowing workers to seamlessly trigger their smartphone's rear camera directly from the web browser. The captured image is sent as a `multipart/form-data` payload to the FastAPI backend.

### Step 2: Computer Vision Pipeline
Once the image reaches the server, it passes through a dual-processing pipeline:
1.  **QR Decoding:** PyZbar scans the image array for QR codes. If found, it decodes the payload (e.g., `tid=93069837`).
2.  **AI Text Extraction:** The image is passed to RapidOCR, which analyzes the pixels, draws bounding boxes around text elements, and returns a sequential array of recognized text strings.

### Step 3: Dynamic Spatial NLP (Natural Language Processing)
Because OCR models often split labels and values into separate, unpredictable "invisible boxes" (e.g., reading "Size:" and "L" as two entirely different elements), the system uses a custom **Dynamic Spatial Parser**. 
*   The algorithm iterates through the OCR text blocks chronologically. 
*   When it identifies a keyword (e.g., `款号` for Style No, or `尺码` for Size), it dynamically checks the immediate adjacent bounding boxes to capture the corresponding value.
*   It utilizes advanced Regular Expressions (Regex) to clean up OCR noise (like dust interpreted as punctuation) and identifies complex, floating industry patterns (like `170/90A` for height/chest sizes) even if a label is missing entirely.

### Step 4: Aggregation & Master QR Generation
The parsed data is sent back to the frontend for human review. Once confirmed, the data is committed to the SQLite database and linked to a unique Collection ID. The Python `qrcode` library then dynamically generates a high-resolution Master QR Code image. Scanning this Master QR Code routes users to a public webpage displaying the aggregated data for the entire batch.
