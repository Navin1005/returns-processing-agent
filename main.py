import os
import mysql.connector
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
import uvicorn
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("ERROR: Missing OPENAI_API_KEY environment variable!")

openai.api_key = OPENAI_API_KEY
logging.info("OpenAI API Key Loaded Successfully!")

# ✅ Establish database connection function
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="****",
            user="****",
            password="***",
            database="****",
            port=****
        )
    except mysql.connector.Error as e:
        logging.error(f"Database Connection Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed!")

# ✅ Login Endpoint
@app.post("/login")
async def login(email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT customer_id FROM customers WHERE email=%s", (email,))
        result = cursor.fetchone()
        return {"success": True, "customer_id": result["customer_id"]} if result else {"success": False, "message": "Customer not found"}
    finally:
        cursor.close()
        conn.close()

# ✅ Fetch Customer Purchases
@app.get("/get-purchases/")
async def get_purchases(customer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT p.purchase_id, pr.product_name, p.purchase_date, p.product_id
            FROM purchases p
            JOIN products pr ON p.product_id = pr.product_id
            WHERE p.customer_id = %s
        """, (customer_id,))
        return cursor.fetchall() or []
    finally:
        cursor.close()
        conn.close()

# ✅ Function to generate AI response (Fixed JSON)
def generate_ai_response(customer_name, product_name, purchase_date, return_status, reason):
    """Generate an AI-generated return decision message using OpenAI GPT."""
    
    prompt = f"""
    Customer Name: {customer_name}
    Product: {product_name}
    Purchase Date: {purchase_date}
    Return Status: {"Approved" if return_status else "Rejected"}
    Reason: {reason}

    Please generate a customer-friendly return decision message:
    - Address the customer by their name.
    - Use a polite and understanding tone.
    - If rejected, clearly explain the specific reason.
    - End with a professional signature from the customer service team.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"OpenAI API Error: {e}")
        return "There was an issue generating the AI response. Please try again."

# ✅ Return Processing Endpoint (Handles AI Response)
@app.post("/process-return/")
async def process_return(customer_id: int = Form(...), product_id: int = Form(...), file: UploadFile = File(...)):
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # ✅ Fetch Product and Return Policy Details (Fixed Table Name)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
        product = cursor.fetchone()
        
        cursor.execute("SELECT * FROM returnpolicy WHERE product_id=%s", (product_id,))  # FIXED table name
        policy = cursor.fetchone()

        cursor.close()
        conn.close()

        if not product or not policy:
            raise HTTPException(status_code=404, detail="Product or policy not found")

        # ✅ Fetch purchase details (Fixed Date Format)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT purchase_date FROM purchases WHERE customer_id=%s AND product_id=%s", 
                       (customer_id, product_id))
        purchase_record = cursor.fetchone()
        cursor.close()
        conn.close()

        if not purchase_record:
            return {"status": "rejected", "message": "Return rejected: No purchase record found."}

        # ✅ Convert purchase_date to proper format
        purchase_date = purchase_record["purchase_date"]
        if isinstance(purchase_date, str):
            purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()  # Convert to datetime object
        
        return_window_days = int(policy["return_window_days"])
        return_deadline = purchase_date + timedelta(days=return_window_days)

        # ✅ Validate return eligibility
        current_date = datetime.now().date()
        if current_date > return_deadline:
            reason = f"Return period expired. The return window for {product['product_name']} was {return_window_days} days."
            ai_response = generate_ai_response("Customer", product["product_name"], purchase_date, False, reason)
            return {"status": "rejected", "message": ai_response}

        if policy["packaging_required"] == 1:  
            reason = f"Return rejected: {product['product_name']} must be in a sealed box."
            ai_response = generate_ai_response("Customer", product["product_name"], purchase_date, False, reason)
            return {"status": "rejected", "message": ai_response}

        if policy["accepted_defects"] == "No":
            reason = f"Return rejected: {product['product_name']} cannot have defects."
            ai_response = generate_ai_response("Customer", product["product_name"], purchase_date, False, reason)
            return {"status": "rejected", "message": ai_response}

        # ✅ APPROVED RETURN CASE
        reason = f"Return request for {product['product_name']} has been accepted."
        ai_response = generate_ai_response("Customer", product["product_name"], purchase_date, True, reason)
        return {"status": "approved", "message": ai_response}

    except Exception as e:
        logging.error(f"Return Processing Error: {e}")
        raise HTTPException(status_code=500, detail="Return processing failed!")

# ✅ Start FastAPI Locally
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
