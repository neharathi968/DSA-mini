// src/assets/api.js
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function simplifyExpression(infix, returnKmap = false) {
  try {
    const response = await axios.post(`${API_BASE_URL}/simplify`, {
      infix,
      return_kmap: returnKmap,
    });
    return response.data;
  } catch (error) {
    console.error("Simplify API Error:", error);

    // Try to pick a useful message from the response body if available
    const respData = error?.response?.data;
    const bodyMsg =
      typeof respData === "string"
        ? respData
        : respData?.detail || respData?.error || (respData ? JSON.stringify(respData) : null);

    const message = bodyMsg || error.message || "Server error";
    // Always throw an Error instance
    throw new Error(message);
  }
}

export async function checkHealth() {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  } catch (error) {
    console.error("Health check failed:", error);
    throw new Error(error?.message || "Health check failed");
  }
}
