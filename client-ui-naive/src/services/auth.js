// services/auth.js
import axios from "axios";
const BASE_URL = "http://localhost:8000";   // make env-driven later

export function setAuthHeader(token) {
  axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
}

export function clearAuthHeader() {
  delete axios.defaults.headers.common["Authorization"];
}

export async function signup(data) {
  return axios.post(`${BASE_URL}/auth/signup`, data);
}

export async function login(data) {
  const res = await axios.post(`${BASE_URL}/auth/login`, data);
  const token = res.data.access_token;
  localStorage.setItem("token", token);
  setAuthHeader(token);
  return token;
}

export function logout() {
  localStorage.removeItem("token");
  clearAuthHeader();
}
