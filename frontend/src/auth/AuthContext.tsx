import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import * as authApi from "../api/auth";
import { clearToken, getToken, setToken } from "../api/authToken";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function rehydrate() {
      if (!getToken()) {
        setIsLoading(false);
        return;
      }
      try {
        setUser(await authApi.getMe());
      } catch {
        clearToken();
      } finally {
        setIsLoading(false);
      }
    }
    void rehydrate();
  }, []);

  useEffect(() => {
    function handleUnauthorized() {
      setUser(null);
    }
    window.addEventListener("issuehub:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("issuehub:unauthorized", handleUnauthorized);
  }, []);

  async function login(email: string, password: string) {
    const { access_token } = await authApi.login(email, password);
    setToken(access_token);
    setUser(await authApi.getMe());
  }

  async function signup(name: string, email: string, password: string) {
    await authApi.signup(name, email, password);
    await login(email, password);
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
