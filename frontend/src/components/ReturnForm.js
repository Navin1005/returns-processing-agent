import React, { useState } from "react";
import axios from "axios";

const ReturnForm = ({ productId }) => {
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
    formData.append("file", image);

    try {
      const response = await axios.post("http://127.0.0.1:8000/process-return/", formData);
      setMessage(response.data.message);
    } catch (error) {
      console.error("Return request error", error);
      setMessage("Error processing return request.");
    }
  };

  return (
    <div>
      <form onSubmit={handleReturnRequest} className="mt-2">
        <input type="file" className="form-control mb-2" onChange={handleFileChange} required />
        <button type="submit" className="btn btn-danger">Request Return</button>
      </form>
      {message && <p className="mt-2 alert alert-info">{message}</p>}
    </div>
  );
};

export default ReturnForm;
