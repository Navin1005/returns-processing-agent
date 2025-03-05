import os
import mysql.connector
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
import uvicorn
import logging

# ✅ Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: Missing OPENAI_API_KEY environment variable! Check Railway settings.")

openai.api_key = OPENAI_API_KEY  # ✅ Corrected API key setup

logging.info("✅ OpenAI API Key Loaded Successfully!")

# ✅ Root API Endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Returns Processing API!"}

# ✅ Test API
@app.get("/api/test")
def test_api():
    return {"message": "Backend API is working!"}

# ✅ Database Connection Function
def get_db_connection():
    try:
        # ✅ Print database connection details to logs (ensure no passwords are exposed)
        logging.info(f"🔍 Connecting to DB: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}, User: {os.getenv('DB_USER')}")
        
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306))  # Default to 3306
        )
        logging.info("✅ Database connection successful!")
        return conn
    except mysql.connector.Error as e:
        logging.error(f"❌ Database Connection Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed!")

# ✅ Function to Fetch Purchase Details
def get_purchase_details(customer_id: int, product_id: int):
    """Fetch the purchase date for the given customer and product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT purchase_date FROM purchases WHERE customer_id=%s AND product_id=%s",
            (customer_id, product_id)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as e:
        logging.error(f"❌ Database Error in get_purchase_details: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# ✅ Function to Fetch Return Policy Details
def get_return_policy(product_id: int):
    """Fetch the return policy for a given product"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT product_name, return_window_days, acceptable_packaging, acceptable_defects 
            FROM products 
            WHERE product_id=%s
            """,
            (product_id,)
        )
        result = cursor.fetchone()
        return result
    except mysql.connector.Error as e:
        logging.error(f"❌ Database Error in get_return_policy: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

# ✅ Function to generate AI response
def generate_ai_response(customer_name, product_name, purchase_date, return_status, reason):
    """Generate a return decision explanation using OpenAI GPT."""
    
    prompt = f"""
    Customer Name: {customer_name}
    Product: {product_name}
    Purchase Date: {purchase_date}
    Return Status: {"Approved" if return_status else "Rejected"}
    Reason: {reason}

    Write a **professional and friendly return decision message**:
    - Address the customer **by their name**.
    - Use **a polite and understanding tone**.
    - If rejected, explain the **specific reason clearly**.
    - End with **a professional signature from the customer service team**.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        ai_message = response["choices"][0]["message"]["content"].strip()
        return " ".join(ai_message.splitlines())  # ✅ Format into a single-line response
    except Exception as e:
        logging.error(f"❌ OpenAI API Error: {e}")
        return "There was an issue generating the response."

# ✅ Login Endpoint
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
            FROM Purchases p
            JOIN Products pr ON p.product_id = pr.product_id
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

# ✅ Return Processing Endpoint (Handles AI Response)
@app.post("/process-return/")
async def process_return(customer_id: int = Form(...), product_id: int = Form(...), file: UploadFile = File(...)):
    """Handles return processing, validates eligibility, and generates AI response."""

    # ✅ Save uploaded file temporarily
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    uploaded_image_path = os.path.join(upload_dir, file.filename)

    with open(uploaded_image_path, "wb") as f:
        f.write(await file.read())  # ✅ Fix async file handling

    # ✅ Check purchase history
    purchase_date = get_purchase_details(customer_id, product_id)
    if not purchase_date:
        return {"status": "rejected", "message": "Return rejected: No purchase record found."}

    # ✅ Fetch return policy
    return_policy = get_return_policy(product_id)
    if not return_policy:
        return {"status": "rejected", "message": "Return rejected: No return policy found."}

    product_name = return_policy["product_name"]
    return_window_days = int(return_policy["return_window_days"])
    return_deadline = purchase_date + timedelta(days=return_window_days)

    # ✅ Check return window eligibility
    current_date = datetime.now().date()
    if current_date > return_deadline:
        reason = f"Return period expired. The return window for {product_name} was {return_window_days} days."
        ai_response = generate_ai_response("Customer", product_name, purchase_date, False, reason)
        return {"status": "rejected", "message": ai_response}

    # ✅ Additional return conditions
    if return_policy["acceptable_packaging"] == "Sealed box required":
        reason = f"Return rejected: {product_name} must be in a sealed box."
        ai_response = generate_ai_response("Customer", product_name, purchase_date, False, reason)
        return {"status": "rejected", "message": ai_response}

    if return_policy["acceptable_defects"] == "No Defects Allowed":
        reason = f"Return rejected: {product_name} cannot have defects."
        ai_response = generate_ai_response("Customer", product_name, purchase_date, False, reason)
        return {"status": "rejected", "message": ai_response}

    # ✅ APPROVED RETURN CASE
    reason = f"Return request for {product_name} has been accepted."
    ai_response = generate_ai_response("Customer", product_name, purchase_date, True, reason)
    return {"status": "approved", "message": ai_response}

# ✅ Start the Uvicorn server when running on Railway
if __name__ == "__main__":
    logging.info("🚀 Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
