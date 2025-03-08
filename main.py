import os
import mysql.connector
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import openai
import uvicorn
import logging
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Allow frontend and API requests from any origin (change to your domain in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: Missing OPENAI_API_KEY environment variable! Check Railway settings.")

openai.api_key = OPENAI_API_KEY
logging.info("✅ OpenAI API Key Loaded Successfully!")

# ✅ Serve static files for React frontend
FRONTEND_BUILD_DIR = "backend/build"

if not os.path.exists(FRONTEND_BUILD_DIR):
    logging.error("❌ ERROR: Frontend build directory not found! Run `npm run build` inside the frontend folder.")
else:
    app.mount("/static", StaticFiles(directory=f"{FRONTEND_BUILD_DIR}/static"), name="static")

# ✅ Serve React Frontend
@app.get("/")
async def serve_homepage():
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    logging.error("❌ ERROR: index.html not found! Ensure frontend is built and located inside `backend/build`.")
    return JSONResponse(content={"error": "Frontend not found!"}, status_code=404)

# ✅ Serve React Login Page
@app.get("/login", response_class=FileResponse)
async def serve_login_page():
    return await serve_homepage()  # ✅ Redirects to index.html (React SPA handles routing)

# ✅ Catch-all route to serve frontend for React Router
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return await serve_homepage()  # ✅ Redirects unknown routes to React frontend


# ✅ Database Connection Function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "shortline.proxy.rlwy.net"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", "oPXNpKvqiltkSMPdcXOTffbtOLvxvYsm"),
            database=os.getenv("DB_NAME", "railway"),
            port=int(os.getenv("DB_PORT", 29496))
        )
        logging.info("✅ Database connection successful!")
        return conn
    except mysql.connector.Error as e:
        logging.error(f"❌ Database Connection Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed!")


# ✅ Login Endpoint (POST)
@app.post("/login")
async def login(email: str = Form(...)):
    """Login function that returns customer ID if found"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT customer_id FROM customers WHERE email=%s", (email,))
        result = cursor.fetchone()
        if result:
            return JSONResponse(content={"success": True, "customer_id": result["customer_id"]})
        return JSONResponse(content={"success": False, "message": "Customer not found"}, status_code=404)
    except mysql.connector.Error as e:
        logging.error(f"❌ Database Error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    finally:
        cursor.close()
        conn.close()


# ✅ Fetch Customer Purchases
@app.get("/get-purchases/")
async def get_purchases(customer_id: int):
    """Fetch customer purchases"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT p.purchase_id, pr.product_name, p.purchase_date, p.product_id
            FROM purchases p
            JOIN products pr ON p.product_id = pr.product_id
            WHERE p.customer_id = %s
            """,
            (customer_id,)
        )
        purchases = cursor.fetchall()
        return purchases if purchases else []
    except mysql.connector.Error as e:
        logging.error(f"❌ Database Error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    finally:
        cursor.close()
        conn.close()


# ✅ Dynamic Port Handling for Railway Deployment
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # ✅ Uses Railway assigned PORT
    print(f"🚀 Running FastAPI on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
