import { motion } from "framer-motion";
import { MapPin, Star, Wallet, Banknote, Globe, Navigation, AlertTriangle, CheckCircle, XCircle } from "lucide-react";

export default function ATMCard({ atm, isRecommended, onSelect, onReport }) {
  const services = [
    atm.cash_withdrawal && { icon: Banknote, label: "Withdraw" },
    atm.cash_deposit && { icon: Wallet, label: "Deposit" },
    atm.ewallet_support && { icon: Wallet, label: "E-Wallet" },
    atm.currency_exchange && { icon: Globe, label: "FX" },
  ].filter(Boolean);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      onClick={onSelect}
      className={`relative rounded-2xl p-4 cursor-pointer transition-all
        ${isRecommended
          ? "bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/20 border-2 border-amber-400 shadow-lg shadow-amber-500/20"
          : "bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 hover:border-brand-400"
        }`}
    >
      {isRecommended && (
        <div className="absolute -top-2 -right-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
          ⭐ AI PICK
        </div>
      )}

      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-bold text-base">{atm.name}</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">{atm.bank}</p>
        </div>
        <span className="bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 text-xs font-semibold px-2 py-1 rounded-lg">
          {atm.distance_km} km
        </span>
      </div>

      <div className="flex items-center gap-2 mb-3 text-xs">
        {atm.is_working ? (
          <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
            <CheckCircle className="w-3 h-3" /> Working
          </span>
        ) : (
          <span className="flex items-center gap-1 text-red-500">
            <XCircle className="w-3 h-3" /> Down
          </span>
        )}
        <span className="flex items-center gap-1 text-amber-500">
          <Star className="w-3 h-3 fill-current" /> {atm.rating}
        </span>
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {services.map((s, i) => (
          <span key={i} className="flex items-center gap-1 text-[10px] bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded-md">
            <s.icon className="w-3 h-3" /> {s.label}
          </span>
        ))}
        {atm.supported_currencies?.map((c) => (
          <span key={c} className="text-[10px] bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 px-2 py-0.5 rounded-md">
            💱 {c}
          </span>
        ))}
      </div>

      <div className="flex gap-2">
        <a
          href={`https://www.google.com/maps/dir/?api=1&destination=${atm.latitude},${atm.longitude}`}
          target="_blank" rel="noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="flex-1 flex items-center justify-center gap-1 bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-semibold py-2 rounded-lg transition-colors"
        >
          <Navigation className="w-3 h-3" /> Navigate
        </a>
        <button
          onClick={(e) => { e.stopPropagation(); onReport(atm); }}
          className="flex items-center justify-center gap-1 bg-red-500 hover:bg-red-600 text-white text-xs font-semibold px-3 py-2 rounded-lg transition-colors"
        >
          <AlertTriangle className="w-3 h-3" />
        </button>
      </div>
    </motion.div>
  );
}