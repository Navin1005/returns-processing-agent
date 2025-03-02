import React, { useEffect, useState } from "react";

const Dashboard = ({ customerId, setCustomerId }) => {
    const [purchases, setPurchases] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [returnImage, setReturnImage] = useState(null);
    const [returnMessage, setReturnMessage] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!customerId) return;
        
        fetch(`http://127.0.0.1:8000/get-purchases?customer_id=${customerId}`)
            .then((response) => response.json())
            .then((data) => setPurchases(data))
            .catch(() => console.error("Failed to fetch purchases"));
    }, [customerId]);

    // ✅ Handle return button click
    const handleReturnClick = (product) => {
        console.log("Return button clicked for:", product);
        setSelectedProduct(product); // ✅ This should trigger modal to open
        setReturnMessage(""); // ✅ Reset previous response
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
            const response = await fetch("http://127.0.0.1:8000/process-return/", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            setReturnMessage(data.message);
        } catch {
            setReturnMessage("Error processing return request.");
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
            <div className="header">
                <h2>Your Purchases</h2>
                <button className="logout-btn" onClick={handleLogout}>Logout</button>
            </div>

            <table className="purchase-table">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Purchase Date</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {purchases.map((purchase) => (
                        <tr key={purchase.purchase_id}>
                            <td><strong>{purchase.product_name}</strong></td>
                            <td>{purchase.purchase_date}</td>
                            <td>
                                <button className="return-btn" onClick={() => handleReturnClick(purchase)}>Return</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* ✅ Return Modal - Only visible when selectedProduct is set */}
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
