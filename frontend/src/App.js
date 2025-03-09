import React, { useState } from "react";
import Dashboard from "./Dashboard";
import Login from "./Login";
import Navbar from "./Navbar";
import ReturnForm from "./ReturnForm"; // ✅ Import ReturnForm
import "./styles.css";  // ✅ Ensure styles are applied

function App() {
    const [customerId, setCustomerId] = useState(null);
    const [selectedProduct, setSelectedProduct] = useState(null); // ✅ Track selected product

    // ✅ Function to handle return form toggle
    const handleReturnClick = (product) => {
        setSelectedProduct(product);
    };

    const handleCloseForm = () => {
        setSelectedProduct(null); // Close return form
    };

    return (
        <div>
            <Navbar />
            {customerId ? (
                <Dashboard 
                    customerId={customerId} 
                    setCustomerId={setCustomerId}
                    onReturnClick={handleReturnClick} // ✅ Pass function to open ReturnForm
                />
            ) : (
                <Login setCustomerId={setCustomerId} />
            )}

            {/* ✅ Render ReturnForm only when a product is selected */}
            {selectedProduct && <ReturnForm productId={selectedProduct.product_id} closeForm={handleCloseForm} />}
        </div>
    );
}

export default App;
