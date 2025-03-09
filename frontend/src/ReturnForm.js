import React, { useState } from "react";
import config from "./config"; 

const ReturnForm = ({ productId, closeForm }) => {
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState("");
  const customerId = localStorage.getItem("customer_id");

  const handleFileChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleReturnRequest = async (e) => {
    e.preventDefault();

    if (!image) {
      alert("Please upload an image.");
      return;
    }

    const formData = new FormData();
    formData.append("customer_id", customerId);
    formData.append("product_id", productId);
    formData.append("file", image);

    try {
      const response = await fetch(`${config.API_URL}/process-return/`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setMessage(data.message); // ✅ Display AI-generated response
    } catch (error) {
      console.error("Return request error", error);
      setMessage("❌ Error processing return request. Please try again.");
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h3>Return Product</h3>
        <input type="file" onChange={handleFileChange} required />
        <button onClick={handleReturnRequest}>Submit Return</button>
        <button className="close-btn" onClick={closeForm}>Back</button>
        {message && <div className="alert-box">{message}</div>}
      </div>
    </div>
  );
};

export default ReturnForm;
