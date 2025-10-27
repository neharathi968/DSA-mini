import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function simplifyExpression(infix, returnKmap = false) {
  try {
    const response = await axios.post(`${API_BASE_URL}/simplify`, {
      infix,
      return_kmap: returnKmap,
    });
    
    const data = response.data;
    if (!data.success) {
      throw new Error(data.message || "Simplification failed");
    }
    
    return {
      success: data.success,
      infix: data.infix || infix,
      postfix: data.postfix || "",
      simplified: data.simplified || "",
      variables: data.variables || [],
      minterms: data.minterms || [],
      kmap: data.kmap || null,
      message: data.message || "Success"
    };
  } catch (error) {
    console.error("Simplify API Error:", error);
    
    const respData = error?.response?.data;
    const bodyMsg =
      typeof respData === "string"
        ? respData
        : respData?.detail || respData?.error || (respData ? JSON.stringify(respData) : null);

    const message = bodyMsg || error.message || "Server error";
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

export function getApiBaseUrl() {
  return API_BASE_URL;
}