// src/assets/api.js
import axios from "axios";

// Vite-specific environment variable (fallback to localhost)
const API_BASE_URL = import.meta?.env?.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Detect dev mode (Vite exposes MODE)
const IS_DEV = import.meta?.env?.MODE !== "production";

apiClient.interceptors.request.use(
  (config) => {
    if (IS_DEV) {
      const method = String(config.method || "GET").toUpperCase();
      console.log(`[API] ${method} ${config.url}`, config.data ?? config.params ?? "");
    }
    return config;
  },
  (error) => {
    console.error("[API] Request Error:", error);
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    if (IS_DEV) {
      console.log(`[API] Response from ${response.config.url}:`, response.data);
    }
    return response;
  },
  (error) => {
    console.error("[API] Response Error:", error);
    return Promise.reject(error);
  }
);

/**
 * Simplifies a Boolean expression
 * @param {string} infix
 * @param {boolean} returnKmap
 * @param {boolean} returnCircuit
 * @returns {Promise<Object>}
 */
export async function simplifyExpression(infix, returnKmap = false, returnCircuit = true) {
  try {
    const response = await apiClient.post("/simplify", {
      infix,
      return_kmap: returnKmap,
      return_circuit: returnCircuit,
    });

    const data = response.data;
    if (!data) throw new Error("Empty response from server");
    if (!data.success) throw new Error(data.message || "Simplification failed");

    return {
      success: data.success,
      infix: data.infix || infix,
      postfix: data.postfix || "",
      simplified: data.simplified || "",
      variables: Array.isArray(data.variables) ? data.variables : [],
      minterms: Array.isArray(data.minterms) ? data.minterms : [],
      kmap: data.kmap ?? null,
      circuit_url: data.circuit_url ?? null,
      logic_graph: data.logic_graph ?? null,
      message: data.message ?? "Success",
    };
  } catch (error) {
    console.error("Simplify API Error (raw):", error);

    // Timeout
    if (error.code === "ECONNABORTED") {
      throw new Error("Request timeout - server took too long to respond");
    }

    // Network errors: axios may set message "Network Error"
    if (error.message && error.message.toLowerCase().includes("network")) {
      throw new Error("Network error - please check your connection and ensure the backend server is running");
    }

    // No response => network / CORS / server offline
    if (!error.response) {
      if (error.request) {
        throw new Error("No response received from server - possible CORS or network issue");
      }
      throw new Error(error.message || "Unknown client error");
    }

    // Extract server error message
    const respData = error.response.data;
    let message = "Server error";

    if (!respData) {
      message = `HTTP ${error.response.status} ${error.response.statusText}`;
    } else if (typeof respData === "string") {
      message = respData;
    } else if (respData.detail) {
      if (Array.isArray(respData.detail)) {
        message = respData.detail.map(err => err.msg || JSON.stringify(err)).join("; ");
      } else {
        message = String(respData.detail);
      }
    } else if (respData.message) {
      message = respData.message;
    } else if (respData.error) {
      message = respData.error;
    } else {
      try {
        message = JSON.stringify(respData);
      } catch {
        message = String(respData);
      }
    }

    throw new Error(message);
  }
}

/**
 * Checks the health status of the API
 * @returns {Promise<Object>}
 */
export async function checkHealth() {
  try {
    const response = await apiClient.get("/health");
    return response.data;
  } catch (error) {
    console.error("Health check failed:", error);
    if (error.message && error.message.toLowerCase().includes("network")) {
      throw new Error("Cannot connect to backend server. Please ensure it is running on " + API_BASE_URL);
    }
    throw new Error(error?.message || "Health check failed");
  }
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export async function testConnection() {
  try {
    await checkHealth();
    return true;
  } catch (e) {
    return false;
  }
}

export default apiClient;
