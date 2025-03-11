import os
import mysql.connector
from datetime import datetime, timedelta
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
import uvicorn
import logging
from dotenv import load_dotenv
from image_match import compare_uploaded_image  # Image matching for fraud detection

# Load environment variables
load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("ERROR: Missing OPENAI_API_KEY environment variable!")

openai.api_key = OPENAI_API_KEY
logging.info("OpenAI API Key Loaded Successfully!")

# Establish Database Connection
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="****",
            user="****",
            password="****",
            database="****",
            port=****
        )
    except mysql.connector.Error as e:
        logging.error(f"Database Connection Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed!")

# Fetch Customer Details
def get_customer_details(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT customer_name FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    return customer['customer_name'] if customer else "Valued Customer"

# Generate AI Response for Return Decision
def generate_ai_response(customer_name, product_name, purchase_date, return_status, reason):
    """Generate a professional AI response for the return request."""
    
    prompt = f"""
    Dear {customer_name},

    We have processed your return request for {product_name}, purchased on {purchase_date}.
    Return Status: {"Approved" if return_status else "Rejected"}

    Reason for Decision:
    {reason}

    If you have any further questions, feel free to contact our customer support team. 
    We appreciate your understanding and thank you for choosing our services.

    Best Regards,
    Returns Management Team
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

# Login Endpoint
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

# Fetch Customer Purchases
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

# Process Return Request (Fraud Detection & AI Response)
@app.post("/process-return/")
async def process_return(customer_id: int = Form(...), file: UploadFile = File(...)):
    """Handles return processing by verifying product match, purchase record, and policy compliance."""
    
    logging.info(f"Processing return request for customer_id: {customer_id}")

    # Validate customer existence
    customer_name = get_customer_details(customer_id)
    if not customer_name:
        return {"status": "rejected", "message": "Return rejected: Customer not found in the database."}

    # Save uploaded file temporarily
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    uploaded_image_path = os.path.join(upload_dir, file.filename)

    with open(uploaded_image_path, "wb") as f:
        f.write(file.file.read())

    # Image Fraud Detection - Compare uploaded image with database
    best_match, best_score = compare_uploaded_image(uploaded_image_path)

    if best_match is None or best_score < 0.85:
        reason = "The uploaded product image does not match our records. Ensure the correct product is uploaded."
        ai_response = generate_ai_response(customer_name, "Unknown Product", "N/A", False, reason)
        return {"status": "rejected", "message": ai_response}

    product_id = int(best_match)

    # Fetch product and return policy details
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
    product = cursor.fetchone()

    cursor.execute("SELECT * FROM returnpolicy WHERE product_id=%s", (product_id,))
    policy = cursor.fetchone()

    cursor.close()
    conn.close()

    if not product or not policy:
        return {"status": "rejected", "message": "Return rejected: Product or policy not found."}

    # Fetch purchase details
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT purchase_date FROM purchases WHERE customer_id=%s AND product_id=%s", 
                   (customer_id, product_id))
    purchase_record = cursor.fetchone()
    cursor.close()
    conn.close()

    if not purchase_record:
        return {"status": "rejected", "message": "Return rejected: No purchase record found."}

    purchase_date = purchase_record["purchase_date"]
    return_window_days = int(policy["return_window_days"])
    return_deadline = purchase_date + timedelta(days=return_window_days)

    # Return Eligibility Check
    current_date = datetime.now().date()
    
    if current_date > return_deadline:
        reason = f"Return period expired. The return window for {product['product_name']} was {return_window_days} days."
        ai_response = generate_ai_response(customer_name, product["product_name"], purchase_date, False, reason)
        return {"status": "rejected", "message": ai_response}

    # Approved Return
    reason = f"Return request for {product['product_name']} has been approved. Please follow return instructions."
    ai_response = generate_ai_response(customer_name, product["product_name"], purchase_date, True, reason)
    return {"status": "approved", "message": ai_response}

# Start FastAPI Server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
