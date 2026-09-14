import api from "./api";
import {
  clearStoredUser,
  clearToken,
  getStoredUser,
  getToken,
  setStoredUser,
  setToken,
} from "./token";

function persistSession({ access_token, user }) {
  setToken(access_token);
  setStoredUser(user);
  return user;
}

export async function signup({ name, email, password }) {
  const response = await api.post("/api/auth/signup", { name, email, password });
  return persistSession(response.data);
}

export async function login({ email, password }) {
  const response = await api.post("/api/auth/login", { email, password });
  return persistSession(response.data);
}

export function logout() {
  clearToken();
  clearStoredUser();
}

export function isAuthenticated() {
  return Boolean(getToken());
}

export function getCurrentUser() {
  return getStoredUser();
}
