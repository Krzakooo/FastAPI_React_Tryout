import React, { useState } from "react";

function Payment() {
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");

  const handlePayment = async () => {
    setMessage("");
  
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
      setMessage("Error: Please enter a valid payment amount");
      return;
    }
  
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setMessage("Error: You must be logged in to make a payment.");
        return;
      }
  
      const response = await fetch("http://localhost:8000/payments/charge", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ amount: parseFloat(amount) }),
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 401) {
          throw new Error("Unauthorized. Please log in to proceed.");
        }
        throw new Error(errorData.detail || "Payment failed");
      }
  
      const data = await response.json();
      setMessage(`Payment of $${data.amount} was successful!`);
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    }
  };
  

  const simulateWebhook = async () => {
    setMessage("");
    try {
      const response = await fetch("http://localhost:8000/webhooks/payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          payment_id: "abc123",
          status: "completed",
          amount: parseFloat(amount),
        }),
      });

      if (!response.ok) throw new Error("Webhook failed");
      setMessage("Webhook successfully received!");
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    }
  };

  return (
    <div>
      <h2>Payment</h2>
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />
      <button onClick={handlePayment}>Process Payment</button>
      <button onClick={simulateWebhook}>Simulate Webhook</button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Payment;
