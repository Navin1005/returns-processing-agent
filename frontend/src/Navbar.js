import React from "react";
import { Link } from "react-router-dom"; // ✅ Ensure correct import

const Navbar = () => {
  return (
    <nav className="navbar navbar-dark bg-dark">
      <div className="container">
        <Link className="navbar-brand" to="/"> {/* ✅ Ensure it's inside Router */}
          Returns Processing Agent
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
