import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface AuthUser {
  email: string;
  accessToken: string;
  username: string;
  password: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  signIn: (username: string, password: string) => Promise<void>;
  signUp: (username: string, password: string) => Promise<{ message: string }>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.toString() || "https://multiagent-insurance-claim-validation.onrender.com/api";

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("auth_user");
    if (stored) {
      try {
        const parsedUser = JSON.parse(stored) as AuthUser;
        // Ensure the stored user has the required fields for Basic Auth
        if (parsedUser.username && parsedUser.password) {
          setUser(parsedUser);
        } else {
          // Old format without username/password, clear it to force re-login
          localStorage.removeItem("auth_user");
        }
      } catch {
        localStorage.removeItem("auth_user");
      }
    }
    setIsLoading(false);
  }, []);

  const signUp = async (username: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Sign up failed" }));
      throw new Error(err.detail || "Sign up failed");
    }
    return res.json();
  };

  const signIn = async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const res = await fetch(`${API_BASE}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Sign in failed" }));
      throw new Error(err.detail || "Invalid credentials");
    }
    const data = await res.json();
    const authUser: AuthUser = {
      email: data.email,
      accessToken: data.access_token,
      username,
      password,
    };
    setUser(authUser);
    localStorage.setItem("auth_user", JSON.stringify(authUser));
  };

  const signOut = () => {
    setUser(null);
    localStorage.removeItem("auth_user");
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
