import config from "./config";
import React, { useState } from "react";

const Login = ({ setCustomerId }) => {
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");

    const handleLogin = async () => {
        if (!email) {
            setError("Please enter your email.");
            return;
        }

        try {
            const response = await fetch(`${config.API_URL}/login`, {  
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ email }),
            });

            const data = await response.json();

            if (data.success) {
                setCustomerId(data.customer_id);
            } else {
                setError("Invalid email. Please try again.");
            }
        } catch (error) {
            setError("Failed to connect. Please try again.");
            console.error("Login request failed:", error);
        }
    };

    return (
        <div className="container">
            {/* ✅ Removed the link - Now it's just a div */}
            <div className="header-title">Returns Processing Agent</div> 
            
            <h2>Sign in</h2>
            
            <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
                <label>Email Address</label>
                <input 
                    type="email" 
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <button type="submit">Continue</button>
            </form>

            {error && <p className="error-message">{error}</p>}
        </div>
    );
};

export default Login;
