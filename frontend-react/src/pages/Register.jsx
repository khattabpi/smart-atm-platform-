import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { User, Mail, Lock, Building2, ArrowRight, Banknote } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { profileAPI } from "../api/client";

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [banks, setBanks] = useState([]);
  const [form, setForm] = useState({ full_name: "", email: "", password: "", bank: "" });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    profileAPI.getBanks().then((r) => setBanks(r.data.banks)).catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }
    setLoading(true);
    try {
      await register(form);
      toast.success("Account created! Welcome 🎉");
      navigate("/dashboard");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen gradient-mesh flex items-center justify-center px-4 py-10">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md glass-card"
      >
        <div className="text-center mb-6">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-lg shadow-brand-500/40 mb-4">
            <Banknote className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-3xl font-bold">Create Account</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-2">Join Smart ATM in seconds</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text" required placeholder="Full name"
              className="input-field pl-12"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            />
          </div>
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="email" required placeholder="you@example.com"
              className="input-field pl-12"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="password" required minLength={6} placeholder="Password (min 6 chars)"
              className="input-field pl-12"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
          <div className="relative">
            <Building2 className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <select
              className="input-field pl-12"
              value={form.bank}
              onChange={(e) => setForm({ ...form, bank: e.target.value })}
            >
              <option value="">Select your bank (optional)</option>
              {banks.map((b) => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>

          <p className="text-xs text-slate-500 bg-slate-100 dark:bg-slate-800 rounded-lg p-3">
            🔒 We never ask for or store your card details. Your account is purely for personalized recommendations.
          </p>

          <button type="submit" disabled={loading} className="btn-primary w-full text-lg flex items-center justify-center gap-2">
            {loading ? "Creating account..." : <>Create Account <ArrowRight className="w-5 h-5" /></>}
          </button>
        </form>

        <p className="text-center text-sm text-slate-500 mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-brand-600 dark:text-brand-400 font-semibold hover:underline">
            Sign in
          </Link>
        </p>
      </motion.div>
    </div>
  );
}