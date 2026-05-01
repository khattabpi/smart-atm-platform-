import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { Sun, Moon, LogOut, User, Banknote } from "lucide-react";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();
  const navigate = useNavigate();

  return (
    <nav className="glass sticky top-0 z-50 px-6 py-3 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-2 group">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-lg shadow-brand-500/40 group-hover:scale-110 transition-transform">
          <Banknote className="w-5 h-5 text-white" />
        </div>
        <span className="font-bold text-lg bg-gradient-to-r from-brand-700 to-brand-500 bg-clip-text text-transparent">
          Smart ATM
        </span>
      </Link>

      <div className="flex items-center gap-2">
        <button onClick={toggle} className="btn-ghost p-2" aria-label="Toggle theme">
          {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        {user ? (
          <>
            <Link to="/dashboard" className="btn-ghost hidden sm:inline-block">Dashboard</Link>
            <Link to="/profile" className="btn-ghost flex items-center gap-2">
              <User className="w-4 h-4" />
              <span className="hidden sm:inline">{user.full_name?.split(" ")[0] || "Profile"}</span>
            </Link>
            <button onClick={() => { logout(); navigate("/"); }} className="btn-ghost text-red-500 flex items-center gap-2">
              <LogOut className="w-4 h-4" />
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn-ghost">Login</Link>
            <Link to="/register" className="btn-primary">Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
}