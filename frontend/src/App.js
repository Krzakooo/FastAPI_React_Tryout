import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Login from "./components/Login";
import Profile from "./components/Profile";
import Payment from "./components/Payment";
import PrivateRoute from "./components/comp/PrivateRoute";

function App() {
  return (
    <Router>
      <div>
        <h1>React + FastAPI App</h1>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
          <Route path="/payment" element={<PrivateRoute><Payment /></PrivateRoute>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
