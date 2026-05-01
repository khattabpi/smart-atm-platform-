import { createContext, useContext, useState, useEffect } from "react";
import { authAPI, profileAPI } from "../api/client";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { setLoading(false); return; }
    profileAPI.getMe()
      .then((r) => setUser(r.data))
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const r = await authAPI.login({ email, password });
    localStorage.setItem("token", r.data.access_token);
    const me = await profileAPI.getMe();
    setUser(me.data);
    return me.data;
  };

  const register = async (data) => {
    const r = await authAPI.register(data);
    localStorage.setItem("token", r.data.access_token);
    const me = await profileAPI.getMe();
    setUser(me.data);
    return me.data;
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  const refresh = async () => {
    const me = await profileAPI.getMe();
    setUser(me.data);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}