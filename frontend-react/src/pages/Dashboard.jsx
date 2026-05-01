import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import { MapPin, Filter, Sparkles, Navigation, X, AlertTriangle } from "lucide-react";
import Navbar from "../components/Navbar";
import MapView from "../components/MapView";
import ATMCard from "../components/ATMCard";
import { atmAPI } from "../api/client";
import { useAuth } from "../context/AuthContext";

const CURRENCIES = ["", "USD", "EUR", "GBP", "JPY", "CNY"];

export default function Dashboard() {
  const { user } = useAuth();
  const [userLoc, setUserLoc] = useState(null);
  const [atms, setAtms] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [filters, setFilters] = useState({
    radius: 10, workingOnly: true, needsDeposit: false, needsEwallet: false, currency: "",
  });
  const [loading, setLoading] = useState(false);
  const [reportATM, setReportATM] = useState(null);

  const detectLocation = useCallback(() => {
    if (!navigator.geolocation) {
      toast.error("Geolocation not supported");
      setUserLoc({ lat: 40.7128, lng: -74.006 });
      return;
    }
    toast.loading("Detecting your location...", { id: "loc" });
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLoc({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        toast.success("Location detected!", { id: "loc" });
      },
      () => {
        setUserLoc({ lat: 40.7128, lng: -74.006 });
        toast.error("Using demo location (NYC)", { id: "loc" });
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }, []);

  useEffect(() => { detectLocation(); }, [detectLocation]);

  const fetchData = useCallback(async () => {
    if (!userLoc) return;
    setLoading(true);
    try {
      const [atmsRes, recRes] = await Promise.all([
        atmAPI.getNearby({
          lat: userLoc.lat, lng: userLoc.lng,
          radius_km: filters.radius,
          working_only: filters.workingOnly,
          needs_deposit: filters.needsDeposit,
          needs_ewallet: filters.needsEwallet,
          currency: filters.currency || undefined,
        }),
        atmAPI.getRecommendation({
          latitude: userLoc.lat, longitude: userLoc.lng,
          user_id: user?.user_id || null,
          needs_deposit: filters.needsDeposit,
          needs_currency: filters.currency || null,
        }),
      ]);
      setAtms(atmsRes.data);
      setRecommendation(recRes.data);
    } catch (err) {
      toast.error("Failed to load ATMs");
    } finally {
      setLoading(false);
    }
  }, [userLoc, filters, user]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleReport = async (e) => {
    e.preventDefault();
    const issueType = e.target.issue_type.value;
    const description = e.target.description.value;
    try {
      await atmAPI.submitReport({ atm_id: reportATM.id, issue_type: issueType, description });
      toast.success("Report submitted. Thanks!");
      setReportATM(null);
      fetchData();
    } catch {
      toast.error("Failed to submit report");
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <div className="flex-1 grid lg:grid-cols-[400px_1fr] gap-4 p-4 max-h-[calc(100vh-72px)]">
        {/* Sidebar */}
        <aside className="space-y-4 overflow-y-auto pr-2">
          {/* Recommendation Card */}
          {recommendation?.best_atm && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-card bg-gradient-to-br from-amber-50/80 to-orange-50/80 dark:from-amber-900/30 dark:to-orange-900/20 border-amber-300 dark:border-amber-700"
            >
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-5 h-5 text-amber-500" />
                <h2 className="font-bold text-lg">AI Recommendation</h2>
              </div>
              <h3 className="font-bold text-xl mb-1">{recommendation.best_atm.name}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">{recommendation.reason}</p>
              <div className="flex items-center justify-between">
                <span className="bg-amber-500 text-white px-3 py-1 rounded-full text-xs font-bold">
                  Score: {(recommendation.score * 100).toFixed(0)}%
                </span>
                <a
                  href={`https://www.google.com/maps/dir/?api=1&destination=${recommendation.best_atm.latitude},${recommendation.best_atm.longitude}`}
                  target="_blank" rel="noreferrer"
                  className="flex items-center gap-1 bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
                >
                  <Navigation className="w-4 h-4" /> Navigate
                </a>
              </div>
            </motion.div>
          )}

          {/* Filters */}
          <div className="glass-card">
            <div className="flex items-center gap-2 mb-4">
              <Filter className="w-5 h-5 text-brand-600" />
              <h2 className="font-bold">Filters</h2>
            </div>
            <div className="space-y-4 text-sm">
              <div>
                <label className="flex justify-between mb-1">
                  <span>Radius</span>
                  <span className="font-semibold">{filters.radius} km</span>
                </label>
                <input
                  type="range" min="1" max="50" value={filters.radius}
                  onChange={(e) => setFilters({ ...filters, radius: +e.target.value })}
                  className="w-full accent-brand-600"
                />
              </div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox" checked={filters.workingOnly}
                  onChange={(e) => setFilters({ ...filters, workingOnly: e.target.checked })}
                  className="w-4 h-4 accent-brand-600"
                /> Working only
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox" checked={filters.needsDeposit}
                  onChange={(e) => setFilters({ ...filters, needsDeposit: e.target.checked })}
                  className="w-4 h-4 accent-brand-600"
                /> Cash deposit
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox" checked={filters.needsEwallet}
                  onChange={(e) => setFilters({ ...filters, needsEwallet: e.target.checked })}
                  className="w-4 h-4 accent-brand-600"
                /> E-wallet support
              </label>
              <div>
                <label className="block mb-1">Currency</label>
                <select
                  value={filters.currency}
                  onChange={(e) => setFilters({ ...filters, currency: e.target.value })}
                  className="input-field py-2"
                >
                  {CURRENCIES.map((c) => <option key={c} value={c}>{c || "Any"}</option>)}
                </select>
              </div>
              <button onClick={detectLocation} className="btn-primary w-full flex items-center justify-center gap-2">
                <MapPin className="w-4 h-4" /> Refresh Location
              </button>
            </div>
          </div>

          {/* ATM List */}
          <div className="glass-card">
            <h2 className="font-bold mb-3">Nearby ATMs ({atms.length})</h2>
            {loading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => <div key={i} className="skeleton h-32" />)}
              </div>
            ) : atms.length === 0 ? (
              <p className="text-sm text-slate-500">No ATMs match your filters.</p>
            ) : (
              <div className="space-y-3">
                {atms.map((atm) => (
                  <ATMCard
                    key={atm.id}
                    atm={atm}
                    isRecommended={atm.id === recommendation?.best_atm?.id}
                    onSelect={() => {}}
                    onReport={setReportATM}
                  />
                ))}
              </div>
            )}
          </div>
        </aside>

        {/* Map */}
        <main className="rounded-2xl overflow-hidden glass relative min-h-[400px]">
          {userLoc && <MapView user={userLoc} atms={atms} recommendedId={recommendation?.best_atm?.id} />}
        </main>
      </div>

      {/* Report Modal */}
      <AnimatePresence>
        {reportATM && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[1000] flex items-center justify-center p-4"
            onClick={() => setReportATM(null)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-card w-full max-w-md"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <AlertTriangle className="w-5 h-5 text-red-500" />
                    <h2 className="font-bold text-xl">Report Issue</h2>
                  </div>
                  <p className="text-sm text-slate-500">{reportATM.name}</p>
                </div>
                <button onClick={() => setReportATM(null)} className="btn-ghost p-1">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <form onSubmit={handleReport} className="space-y-4">
                <div>
                  <label className="block text-sm mb-1">Issue type</label>
                  <select name="issue_type" required className="input-field">
                    <option value="not_working">Not working</option>
                    <option value="missing_service">Missing service</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm mb-1">Description (optional)</label>
                  <textarea name="description" rows="3" className="input-field" placeholder="Describe the issue..." />
                </div>
                <button type="submit" className="btn-primary w-full">Submit Report</button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}