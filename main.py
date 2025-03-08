import os
import mysql.connector
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import openai
import uvicorn
import logging
from dotenv import load_dotenv

load_dotenv()  # Ensure environment variables are loaded

# ✅ Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://returns-processing-agent-production.up.railway.app"],  # ✅ Update with frontend URL if needed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: Missing OPENAI_API_KEY environment variable! Check Railway settings.")

openai.api_key = OPENAI_API_KEY  # ✅ Set OpenAI API key

logging.info("✅ OpenAI API Key Loaded Successfully!")

# ✅ Root API Endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Returns Processing API!"}


# ✅ Test API
@app.get("/api/test")
def test_api():
    return {"message": "Backend API is working!"}


# ✅ Redirect GET /login to /docs (Prevents "Method Not Allowed")
@app.get("/login")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


# ✅ Login Endpoint (POST Only)
@app.post("/login")
async def login(email: str = Form(...)):
    """Login function that returns customer ID if found"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT customer_id FROM customers WHERE email=%s", (email,))
        result = cursor.fetchone()
        return {"success": True, "customer_id": result["customer_id"]} if result else {"success": False, "message": "Customer not found"}
    except mysql.connector.Error as e:
        logging.error(f"❌ Database Error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    finally:
        cursor.close()
        conn.close()


def get_db_connection():
    logging.info(f"🔍 Connecting to DB: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}, User: {os.getenv('DB_USER')}")
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "shortline.proxy.rlwy.net"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", "oPXNpKvqiltkSMPdcXOTffbtOLvxvYsm"),
            database=os.getenv("DB_NAME", "railway"),
            port=int(os.getenv("DB_PORT", 29496))  # Set the Railway MySQL port
        )
        logging.info("✅ Database connection successful!")
        return conn
    except mysql.connector.Error as e:
        logging.error(f"❌ Database Connection Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed!")


# ✅ Fetch Customer Purchases (Fixed Table Case)
@app.get("/get-purchases/")
async def get_purchases(customer_id: int):
    """Fetch customer purchases"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT p.purchase_id, pr.product_name, p.purchase_date, p.product_id
            FROM purchases p  -- ✅ Fixed table case
            JOIN products pr ON p.product_id = pr.product_id  -- ✅ Fixed table case
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
