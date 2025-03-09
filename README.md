# Returns Processing Agent

## Overview
The **Returns Processing Agent** is an AI-powered system that automates the product return process by verifying product authenticity, purchase history, and return policy compliance. It integrates **computer vision, database validation, and AI-based decision-making** to streamline the returns experience.

## Features
✅ **Product Identification via Vision Matching** – Uses the CLIP model to compare uploaded images with database records.  
✅ **Customer Purchase Verification** – Confirms if the product was purchased by the user.  
✅ **Return Window Validation** – Ensures that return requests are within the allowed timeframe.  
✅ **Policy Compliance Checks** – Evaluates packaging requirements and defect acceptance conditions.  
✅ **AI-Powered Decision Making** – Generates automated responses explaining approval or rejection reasons.  

## System Architecture
The project is divided into multiple components:

- **Frontend**: Built using **React.js**, allowing users to log in, view purchases, and submit return requests.
- **Backend**: Developed with **FastAPI**, handling authentication, return processing, and AI integration.
- **Database**: **MySQL** is used to store customer purchases and return policies.
- **Image Processing**: AI-powered **image similarity comparison** for fraud detection.

## Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- Node.js (for frontend)
- FastAPI, OpenAI API, and dependencies from `requirements.txt`

### Steps to Set Up
1. **Clone the Repository**
   ```sh
   git clone https://github.com/Navin1005/returns-processing-agent.git
   cd returns-processing-agent
