import React, { useEffect, useState } from "react";
import config from "./config";

const Dashboard = ({ customerId, setCustomerId }) => {
    const [purchases, setPurchases] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null); // ✅ Ensure this updates
    const [returnImage, setReturnImage] = useState(null);
    const [returnMessage, setReturnMessage] = useState("");
    const [loading, setLoading] = useState(false);

    // ✅ Fetch purchases when customer logs in
    useEffect(() => {
        if (!customerId) return;

        fetch(`${config.API_URL}/get-purchases?customer_id=${customerId}`)
            .then((response) => response.json())
            .then((data) => setPurchases(data))
            .catch((error) => console.error("Error fetching purchases:", error));
    }, [customerId]);

    // ✅ Handle return button click - Ensure state updates properly
    const handleReturnClick = (product) => {
        console.log("Product selected for return:", product);
        setSelectedProduct(product);
        setReturnMessage(""); // Reset previous message
    };

    // ✅ Handle file selection
    const handleImageChange = (e) => {
        setReturnImage(e.target.files[0]);
    };

    // ✅ Submit return request
    const handleReturnSubmit = async () => {
        if (!returnImage || !selectedProduct) {
            alert("Please select an image.");
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append("customer_id", customerId);
        formData.append("product_id", selectedProduct.product_id);
        formData.append("file", returnImage);

        try {
            const response = await fetch(`${config.API_URL}/process-return/`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) throw new Error("Return request failed.");

            const data = await response.json();
            setReturnMessage(data.message);
        } catch (error) {
            setReturnMessage("Error processing return request.");
            console.error(error);
        }

        setLoading(false);
        setSelectedProduct(null);
        setReturnImage(null);
    };

    // ✅ Logout function
    const handleLogout = () => {
        setCustomerId(null);
    };

    return (
        <div className="container">
            {/* ✅ Header with Logout */}
            <div className="header">
                <h2>Your Purchases</h2>
                <button className="logout-btn" onClick={handleLogout}>Logout</button>
            </div>

            {/* ✅ Purchases Table */}
            <table className="purchase-table">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Purchase Date</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {purchases.length > 0 ? (
                        purchases.map((purchase) => (
                            <tr key={purchase.purchase_id}>
                                <td><strong>{purchase.product_name}</strong></td>
                                <td>{purchase.purchase_date}</td>
                                <td>
                                    <button className="return-btn" onClick={() => handleReturnClick(purchase)}>Return</button>
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="3" style={{ textAlign: "center" }}>No purchases found.</td>
                        </tr>
                    )}
                </tbody>
            </table>

            {/* ✅ Return Modal (Only visible when a product is selected) */}
            {selectedProduct && (
                <div className="modal">
                    <div className="modal-content">
                        <h3>Return: {selectedProduct.product_name}</h3>
                        <input type="file" onChange={handleImageChange} />
                        <button onClick={handleReturnSubmit} disabled={loading}>
                            {loading ? "Processing..." : "Submit Return"}
                        </button>
                        <button className="close-btn" onClick={() => setSelectedProduct(null)}>Back</button>
                    </div>
                </div>
            )}

            {/* ✅ AI Response Message */}
            {returnMessage && <div className="alert-box">{returnMessage}</div>}
        </div>
    );
};

export default Dashboard;
