# 📦 Returns Processing Agent

A **vision-based AI pipeline** that automates **returns processing** by verifying customer purchases, checking return policies, and detecting fraud through image comparison.

---

## ✨ Features

- ✅ **Customer Authentication** – Validates customer identity through email.
- ✅ **Purchase Verification** – Ensures only purchased items are eligible for return.
- ✅ **AI-powered Image Matching** – Uses OpenAI's CLIP model to detect fraud.
- ✅ **Return Policy Enforcement** – Checks packaging, defect rules, and return timeframe.
- ✅ **Automated Decision Making** – AI-generated approval/rejection messages.
- ✅ **Real-time FastAPI Backend** – Built with **FastAPI, MySQL, and AI models**.

---

## 🛠️ Technologies Used

- **Backend:** FastAPI (Python)
- **Database:** MySQL
- **AI Model:** OpenAI CLIP (for Image Matching)
- **Cloud Services:** OpenAI API (for AI-generated responses)
- **Frontend (Optional):** React (for UI)

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/Navin1005/returns-processing-agent.git
cd returns-processing-agent

2️⃣ Install Dependencies
sh
Copy
Edit
pip install -r requirements.txt
3️⃣ Set Up Database
Create a MySQL database named returns_db
Import the provided SQL schema (if available)
4️⃣ Run the FastAPI Server
sh
Copy
Edit
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
Open http://127.0.0.1:8000/docs to access the Swagger UI.
🔍 API Endpoints
🔹 Authentication
POST /login → Customer login with email
🔹 Fetch Purchases
GET /get-purchases/?customer_id={id} → Retrieve purchase history
🔹 Process Returns
POST /process-return/ → Upload product image & verify return eligibility
📸 Image Matching Process
Upload product image.
Compare with stored images using CLIP Model.
Determine if the product matches any existing records.
Validate against purchase history and return policy.
Approve or reject the return with an AI-generated explanation.
🔬 Testing Scenarios
Valid Return: Customer purchased the product and meets return conditions.
Invalid Product Image: Uploaded image doesn't match the product in the database.
Return Window Expired: Product return request is beyond the allowed timeframe.
Incorrect Packaging: Product not returned in required original packaging.
Defective Item Restriction: Product contains defects that violate return policies.
Unauthorized Purchase: Attempting to return a product not purchased by the user.
🚧 Future Enhancements
🔹 Real-time Fraud Detection – Improve accuracy with deep learning models.
🔹 Integration with E-commerce APIs – Fetch live purchase records.
🔹 Policy Customization – Allow businesses to define custom return rules.
🔹 User-friendly Dashboard – Provide a frontend interface for customers & admins.
🔹 Multi-language Support – Improve accessibility with AI-driven translations.
⚠️ Limitations
🚫 No Live Deployment – This project currently runs locally only.
🚫 Image Similarity Threshold – CLIP model matching may require tuning.
🚫 Dependent on Database Entries – Requires a populated database for testing.
