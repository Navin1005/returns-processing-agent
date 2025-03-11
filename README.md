📦 Returns Processing Agent
A vision-based AI pipeline that automates returns processing by verifying customer purchases, checking return policies, and detecting fraud through image comparison.

🚀 Features
✅ Customer Authentication – Validates customer identity through email.
✅ Purchase Verification – Ensures only purchased items are eligible for return.
✅ AI-powered Image Matching – Uses OpenAI's CLIP model to detect fraud.
✅ Return Policy Enforcement – Checks packaging, defect rules, and return timeframe.
✅ Automated Decision Making – AI-generated approval/rejection messages.
✅ Real-time FastAPI Backend – Built with FastAPI, MySQL, and AI models.

🛠 Technologies Used
Backend: FastAPI (Python)
Database: MySQL
AI Model: OpenAI CLIP (for Image Matching)
Cloud Services: OpenAI API (for AI-generated responses)
Frontend (Optional): React (for UI)
🔧 Installation & Setup
1️⃣ Clone the Repository
sh
Copy
Edit
git clone https://github.com/Navin1005/returns-processing-agent.git
cd returns-processing-agent
2️⃣ Create and Activate Virtual Environment
sh
Copy
Edit
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows
3️⃣ Install Dependencies
sh
Copy
Edit
pip install -r requirements.txt
4️⃣ Set Up MySQL Database
Open MySQL Workbench.
Create a database named returns_db.
Run the database_setup.sql script to create necessary tables.
5️⃣ Start FastAPI Server
sh
Copy
Edit
uvicorn main:app --reload
✅ Server Running at: http://127.0.0.1:8000

6️⃣ Test API via Swagger UI
📌 Visit: http://127.0.0.1:8000/docs

📊 Database Schema
🧑 Customers Table
customer_id	customer_name	email
1	John Doe	john.doe@example.com
2	Jane Smith	jane.smith@example.com
🛍️ Products Table
product_id	product_name	return_window_days	acceptable_packaging	acceptable_defects
1	Wireless Headphones	30	Original packaging required	No physical damage
2	Smartphone Case	15	Original packaging required	Minor scratches allowed
📦 Purchases Table
purchase_id	customer_id	product_id	purchase_date
1	1	1	2025-01-21
2	1	3	2025-02-01
✅ API Endpoints
🔹 Customer Login
📌 POST /login
🔸 Request: email
🔸 Response: Returns customer_id if valid, error if invalid.

🔹 Get Customer Purchases
📌 GET /get-purchases/?customer_id={id}
🔸 Response: Returns list of purchased products.

🔹 Process Return Request
📌 POST /process-return/
🔸 Request: customer_id, image
🔸 Response: "Return Approved" or "Return Rejected" with AI-generated reason.

📋 Return Policy Rules Implemented
✔ Purchase Validation: Only customers who purchased the product can return it.
✔ Return Window Check: Ensures return requests are made within the allowed period.
✔ Image Fraud Detection: Uses AI to match the uploaded product image with stored images.
✔ Packaging Requirement Check: Some products require original/sealed packaging.
✔ Defect Allowance Check: Minor scratches may be allowed, but major damages are rejected.
✔ AI Decision Making: Uses OpenAI GPT-4 for approval/rejection messages.

🔬 Testing Scenarios
Test Case	Expected Result
✅ Valid return request (correct product, within return window, packaging rules met)	Return Approved
❌ Customer tries to return a product they never purchased	Return Rejected – "No purchase record found"
❌ Return request made after return period expires	Return Rejected – "Return period expired"
❌ Uploaded image does not match stored image	Return Rejected – "Product image does not match records"
❌ Product packaging does not meet policy requirements	Return Rejected – "Original packaging required"
❌ Defective product returned when defects are not allowed	Return Rejected – "Defective products are not eligible for return"
🚀 Future Improvements
🌍 Live API Deployment – Deploy API on AWS/GCP.
📸 Advanced Image Recognition – Improve AI fraud detection accuracy.
📦 Courier Integration – Automate return pickups via logistics API.
📊 Analytics Dashboard – Use Power BI/Tableau for return analysis.
🤖 AI Chatbot – Automate return queries using conversational AI.
✅ Blockchain Tracking – Secure return transactions using blockchain.
🤝 Contribution
👥 Contributions are welcome! Fork the repo, create a branch, and submit a Pull Request.

📌 Steps to Contribute:
Fork this repository.
Create a new branch (git checkout -b feature-branch).
Commit your changes (git commit -m "Added new feature").
Push your branch (git push origin feature-branch).
Create a Pull Request for review.
