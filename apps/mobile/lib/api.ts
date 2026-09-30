import axios from "axios";
import * as SecureStore from "expo-secure-store";

const API_BASE = process.env.EXPO_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync("axis_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function login(email: string, password: string): Promise<string> {
  const params = new URLSearchParams({ username: email, password });
  const res = await api.post<{ access_token: string }>("/auth/login", params.toString(), {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  await SecureStore.setItemAsync("axis_token", res.data.access_token);
  return res.data.access_token;
}

export async function logout(): Promise<void> {
  await SecureStore.deleteItemAsync("axis_token");
}
