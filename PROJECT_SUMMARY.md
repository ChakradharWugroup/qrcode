# Project Summary: Master QR Manager (Garment Tracking System)

## 1. Abstract
The **Master QR Manager** is a mobile-first, cloud-hosted web application designed to streamline inventory tracking for garment manufacturing factories. It has evolved into a **100% Offline Progressive Web App (PWA)**. Factory workers can synchronize factory batch data in the morning, walk onto a factory floor with zero internet connection, rapidly scan physical QR codes using a highly-optimized in-browser camera scanner, and push the aggregated batch logs back to the cloud at the end of their shift.

---

## 2. Technology Stack
*   **Backend / API:** Python, FastAPI (High-performance asynchronous web framework)
*   **Frontend:** HTML5, Vanilla JavaScript, Tailwind CSS (Mobile-responsive UI), Service Workers, IndexedDB (PWA Offline Storage)
*   **Database:** TiDB Serverless (MySQL-compatible) via SQLAlchemy ORM (Configured with connection pooling & pre-ping to handle serverless timeouts)
*   **Deployment & DevOps:** Docker (Nixpacks/Dockerfile), Oracle Cloud (Always Free Tier), Coolify (Self-hosted PaaS), `nip.io` Dynamic DNS
*   **Security & Networking:** Cloudflare Workers (Edge Proxy for Firewall Bypassing)

---

## 3. Core Architecture & Workflow

### Phase 1: The Qiaofei Data Sync (Online)
The factory utilizes an external enterprise ERP system (Qiaofei). To avoid manually entering garment data, the worker presses **"Sync"** while connected to WiFi:
1. The frontend requests tickets from the FastAPI backend based on a selected timeframe (e.g., "This Month").
2. The FastAPI backend authenticates with the Qiaofei API. *(Note: Because the Qiaofei API is hosted on Huawei Cloud, which actively blocks Oracle Cloud IPs, the backend traffic is securely routed through a lightweight **Cloudflare Worker Proxy** to successfully bypass the firewall).*
3. The backend returns a cleaned JSON payload of thousands of tickets.
4. The frontend utilizes **IndexedDB** to store this massive dataset directly in the smartphone's local memory.

### Phase 2: Factory Floor Scanning (100% Offline)
Once synchronized, the worker can disconnect from the internet completely.
1. The frontend utilizes `Html5Qrcode` configured for high-speed mobile scanning (30 FPS, optimized scanning box, native BarcodeDetector API).
2. When a QR code is scanned, the app extracts the Ticket ID (`tid`).
3. The app queries the local IndexedDB. If a match is found, it instantly auto-fills all metadata: `Company`, `Style`, `Bed`, `Bundle`, `Color`, `Size`, and `Quantity`.
4. The scanned records are logged into a local HTML table and saved persistently to IndexedDB so they are not lost if the browser is closed.

### Phase 3: Push to Cloud Database (Online)
At the end of a shift, the worker connects back to WiFi and presses **"Push to Cloud Database"**.
1. The frontend extracts all offline scans from IndexedDB and sends them via a POST payload to the FastAPI backend.
2. The backend connects to the remote **TiDB Serverless** MySQL database.
3. Because serverless databases aggressively sleep idle connections, SQLAlchemy is configured with `pool_pre_ping=True` and `pool_recycle=300` to automatically wake the database and ensure zero dropped connections.
4. The records are saved to the `GarmentQRCode` table and can be viewed globally on the Master Dashboard.

---

## 4. Bypassing the Chinese Firewall (The Cloudflare Proxy)
During deployment, the Qiaofei API (Huawei Cloud) rejected connection attempts from the Oracle Cloud (Tokyo) server with `Timeout 522` / `403` errors. This was caused by enterprise anti-bot filters blocking foreign cloud datacenter IP ranges. 

To resolve this without migrating away from the free Oracle Cloud tier, a **Cloudflare Worker** was deployed:
```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const targetUrl = "https://saofeiapi.huole.cn" + url.pathname + url.search;
    const modifiedRequest = new Request(targetUrl, {
      method: request.method,
      headers: request.headers,
      body: request.method === "POST" ? request.body : null,
      redirect: "follow"
    });
    return fetch(modifiedRequest);
  },
};
```
The Python backend in `qiaofei_sync.py` routes all requests to `https://dark-lab-2998.kallec.workers.dev`. Cloudflare acts as a transparent, highly-trusted edge node that proxies the payload to Qiaofei successfully, completely eliminating the IP block.

---

## 5. Deployment Setup
The application is deployed for free forever using:
*   **Host:** Oracle Cloud (Ubuntu 22.04).
*   **Manager:** Coolify (Automated Docker deployments from GitHub).
*   **Domain:** `https://131.186.57.252.nip.io` (Provides free, automatic SSL certificates required by iOS Safari for accessing the camera without needing to purchase a domain name).
