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
            const response = await fetch("http://127.0.0.1:8000/login", {
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
        } catch {
            setError("Failed to connect. Please try again.");
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Sign in</h2>
                {error && <p className="error-message">{error}</p>}
                <label>Email Address</label>
                <input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <button onClick={handleLogin}>Continue</button>
                <p className="new-user">New to our store? <a href="#">Create an account</a></p>
            </div>
        </div>
    );
};

export default Login;
