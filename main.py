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

# ✅ Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://returns-processing-agent-production.up.railway.app"],  # ✅ Allow frontend requests only from Railway app
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

# ✅ Serve React Frontend
FRONTEND_BUILD_DIR = "backend/build"
if os.path.exists(FRONTEND_BUILD_DIR):
    app.mount("/static", StaticFiles(directory=f"{FRONTEND_BUILD_DIR}/static"), name="static")

@app.get("/")
async def serve_homepage():
    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(content={"error": "Frontend not found!"}, status_code=404)

# ✅ Database Connection Function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        logging.info("✅ Database connection successful!")
        return conn
    except mysql.connector.Error as e:
        logging.error(f"❌ Database Connection Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed!")

# ✅ Login Endpoint
@app.post("/login")
async def login(email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT customer_id FROM customers WHERE email=%s", (email,))
        result = cursor.fetchone()
        if result:
            return JSONResponse(content={"success": True, "customer_id": result["customer_id"]})
        return JSONResponse(content={"success": False, "message": "Customer not found"}, status_code=404)
    finally:
        cursor.close()
        conn.close()

# ✅ Fetch Customer Purchases
@app.get("/get-purchases/")
async def get_purchases(customer_id: int):
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
    finally:
        cursor.close()
        conn.close()

# ✅ Process Return Request
@app.post("/process-return/")
async def process_return(customer_id: int = Form(...), product_id: int = Form(...), file: UploadFile = File(...)):
    """Process product return and generate GenAI response"""
    try:
        # Save file
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(file.file.read())

        # ✅ Generate AI response using OpenAI API
        ai_prompt = f"Customer {customer_id} is returning product {product_id}. Provide a return status update."
        ai_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": ai_prompt}]
        )
        return_message = ai_response["choices"][0]["message"]["content"]

        return JSONResponse(content={"message": return_message})
    except Exception as e:
        logging.error(f"❌ Return Processing Error: {e}")
        raise HTTPException(status_code=500, detail="Return processing failed!")

# ✅ Start FastAPI Server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
