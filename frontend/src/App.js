import React, { useState } from "react";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";

function App() {
    const [customerId, setCustomerId] = useState(null);

    return (
        <div className="App">
            {customerId ? (
                <Dashboard customerId={customerId} setCustomerId={setCustomerId} />
            ) : (
                <Login setCustomerId={setCustomerId} />
            )}
        </div>
    );
}

export default App;
