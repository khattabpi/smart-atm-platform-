import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { User, Building2, Phone, Wallet, TrendingUp, TrendingDown, ArrowDownCircle, ArrowUpCircle } from "lucide-react";
import Navbar from "../components/Navbar";
import { profileAPI, txAPI } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user, refresh } = useAuth();
  const [banks, setBanks] = useState([]);
  const [form, setForm] = useState({ full_name: "", bank: "", phone: "", preferred_currency: "USD" });
  const [transactions, setTransactions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [txForm, setTxForm] = useState({ type: "withdraw", amount: "" });

  useEffect(() => {
    profileAPI.getBanks().then((r) => setBanks(r.data.banks));
    if (user) {
      setForm({
        full_name: user.full_name || "",
        bank: user.bank || "",
        phone: user.phone || "",
        preferred_currency: user.preferred_currency || "USD",
      });
    }
    loadTransactions();
  }, [user]);

  const loadTransactions = async () => {
    try {
      const [tx, an] = await Promise.all([txAPI.list(), txAPI.analytics()]);
      setTransactions(tx.data);
      setAnalytics(an.data);
    } catch {}
  };

  const saveProfile = async (e) => {
    e.preventDefault();
    try {
      await profileAPI.update(form);
      await refresh();
      toast.success("Profile updated!");
    } catch {
      toast.error("Failed to update profile");
    }
  };

  const submitTx = async (e) => {
    e.preventDefault();
    try {
      await txAPI.create({ type: txForm.type, amount: parseFloat(txForm.amount) });
      toast.success(`${txForm.type === "withdraw" ? "Withdrawal" : "Deposit"} successful!`);
      setTxForm({ type: "withdraw", amount: "" });
      await refresh();
      loadTransactions();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Transaction failed");
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen gradient-mesh">
      <Navbar />
      <div className="max-w-6xl mx-auto px-4 py-8 grid lg:grid-cols-3 gap-6">
        {/* Wallet card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-3 glass-card bg-gradient-to-br from-brand-600 to-brand-900 text-white relative overflow-hidden"
        >
          <div className="absolute -right-10 -top-10 w-48 h-48 bg-white/10 rounded-full blur-2xl" />
          <div className="absolute right-20 bottom-0 w-32 h-32 bg-amber-400/20 rounded-full blur-2xl" />
          <div className="relative z-10 flex flex-wrap justify-between items-center gap-4">
            <div>
              <p className="text-brand-200 text-sm mb-1">Simulated Balance</p>
              <h1 className="text-4xl sm:text-5xl font-extrabold">
                ${user.simulated_balance.toFixed(2)}
              </h1>
              <p className="text-brand-200 text-sm mt-2">{user.full_name} · {user.bank || "No bank selected"}</p>
            </div>
            <Wallet className="w-16 h-16 text-white/20" />
          </div>
        </motion.div>

        {/* Profile form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="glass-card lg:col-span-2"
        >
          <h2 className="font-bold text-xl mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-brand-600" /> Profile Settings
          </h2>
          <form onSubmit={saveProfile} className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm mb-1">Full Name</label>
                <input
                  type="text" className="input-field"
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm mb-1">Phone</label>
                <input
                  type="tel" className="input-field" placeholder="+1 555 123 4567"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm mb-1 flex items-center gap-1"><Building2 className="w-4 h-4" /> Bank</label>
                <select
                  className="input-field"
                  value={form.bank}
                  onChange={(e) => setForm({ ...form, bank: e.target.value })}
                >
                  <option value="">Select your bank</option>
                  {banks.map((b) => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm mb-1">Preferred Currency</label>
                <select
                  className="input-field"
                  value={form.preferred_currency}
                  onChange={(e) => setForm({ ...form, preferred_currency: e.target.value })}
                >
                  {["USD", "EUR", "GBP", "JPY", "CNY", "EGP"].map((c) => <option key={c}>{c}</option>)}
                </select>
              </div>
            </div>
            <div className="flex gap-3">
              <input className="input-field flex-1" disabled value={user.email} />
            </div>
            <button type="submit" className="btn-primary">Save Changes</button>
          </form>
        </motion.div>

        {/* Quick transaction */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="glass-card"
        >
          <h2 className="font-bold text-xl mb-4">Quick Transaction</h2>
          <form onSubmit={submitTx} className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setTxForm({ ...txForm, type: "withdraw" })}
                className={`p-3 rounded-xl border-2 flex items-center justify-center gap-2 text-sm font-semibold transition-all ${
                  txForm.type === "withdraw"
                    ? "border-red-500 bg-red-50 dark:bg-red-900/20 text-red-600"
                    : "border-slate-200 dark:border-slate-700"
                }`}
              >
                <ArrowUpCircle className="w-4 h-4" /> Withdraw
              </button>
              <button
                type="button"
                onClick={() => setTxForm({ ...txForm, type: "deposit" })}
                className={`p-3 rounded-xl border-2 flex items-center justify-center gap-2 text-sm font-semibold transition-all ${
                  txForm.type === "deposit"
                    ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600"
                    : "border-slate-200 dark:border-slate-700"
                }`}
              >
                <ArrowDownCircle className="w-4 h-4" /> Deposit
              </button>
            </div>
            <input
              type="number" min="1" step="0.01" required placeholder="Amount"
              className="input-field"
              value={txForm.amount}
              onChange={(e) => setTxForm({ ...txForm, amount: e.target.value })}
            />
            <button type="submit" className="btn-primary w-full">Confirm</button>
          </form>
        </motion.div>

        {/* Analytics */}
        {analytics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="lg:col-span-3 grid grid-cols-2 sm:grid-cols-4 gap-4"
          >
            {[
              { label: "Total Transactions", value: analytics.total_transactions, color: "text-brand-600" },
              { label: "Total Withdrawn", value: `
$$
{analytics.total_withdrawn.toFixed(2)}`, color: "text-red-500", icon: TrendingDown },
              { label: "Total Deposited", value: `
$$
{analytics.total_deposited.toFixed(2)}`, color: "text-emerald-500", icon: TrendingUp },
              { label: "Successful", value: `${analytics.successful}/${analytics.total_transactions}`, color: "text-amber-500" },
            ].map((s, i) => (
              <div key={i} className="glass-card">
                <p className="text-xs text-slate-500 mb-1">{s.label}</p>
                <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              </div>
            ))}
          </motion.div>
        )}

        {/* Transaction history */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="lg:col-span-3 glass-card"
        >
          <h2 className="font-bold text-xl mb-4">Recent Activity</h2>
          {transactions.length === 0 ? (
            <p className="text-sm text-slate-500">No transactions yet. Try a quick deposit or withdrawal above.</p>
          ) : (
            <div className="space-y-2">
              {transactions.slice(0, 10).map((tx) => (
                <div key={tx.id} className="flex justify-between items-center p-3 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      tx.type === "withdraw" ? "bg-red-100 dark:bg-red-900/30 text-red-600" : "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600"
                    }`}>
                      {tx.type === "withdraw" ? <ArrowUpCircle className="w-5 h-5" /> : <ArrowDownCircle className="w-5 h-5" />}
                    </div>
                    <div>
                      <p className="font-semibold capitalize">{tx.type}</p>
                      <p className="text-xs text-slate-500">{new Date(tx.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`font-bold ${tx.type === "withdraw" ? "text-red-500" : "text-emerald-500"}`}>
                      {tx.type === "withdraw" ? "−" : "+"}${tx.amount.toFixed(2)}
                    </p>
                    <p className={`text-xs ${tx.status === "completed" ? "text-emerald-500" : "text-red-500"}`}>{tx.status}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}