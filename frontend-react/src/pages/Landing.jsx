import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { MapPin, Brain, Shield, Zap, ArrowRight } from "lucide-react";
import Navbar from "../components/Navbar";

const features = [
  { icon: MapPin, title: "Smart Locator", desc: "Real-time ATM map with live status indicators." },
  { icon: Brain, title: "AI Recommendations", desc: "ML-powered scoring picks the best ATM for you." },
  { icon: Shield, title: "Bank-Grade Security", desc: "JWT authentication. Zero card data ever stored." },
  { icon: Zap, title: "Instant Reports", desc: "Crowdsourced reliability updates in seconds." },
];

export default function Landing() {
  return (
    <div className="min-h-screen gradient-mesh">
      <Navbar />

      <section className="max-w-6xl mx-auto px-6 py-20 text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <span className="inline-block bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 px-4 py-1 rounded-full text-sm font-medium mb-6">
            ✨ AI-Powered ATM Discovery
          </span>
          <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight mb-6">
            Find the <span className="bg-gradient-to-r from-brand-600 to-accent-500 bg-clip-text text-transparent">perfect ATM</span>
            <br />in seconds.
          </h1>
          <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-10">
            Real-time availability. Bank-aware recommendations. Crowdsourced reliability.
            All without ever exposing your card details.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link to="/register" className="btn-primary text-lg px-8 py-3 inline-flex items-center gap-2">
              Get Started <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/dashboard" className="btn-ghost text-lg px-8 py-3 border-2 border-slate-300 dark:border-slate-700 rounded-xl">
              Try Demo
            </Link>
          </div>
        </motion.div>
      </section>

      <section className="max-w-6xl mx-auto px-6 pb-20 grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((f, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            viewport={{ once: true }}
            className="glass-card hover:-translate-y-1 transition-transform"
          >
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center mb-4 shadow-lg shadow-brand-500/30">
              <f.icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-bold text-lg mb-2">{f.title}</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">{f.desc}</p>
          </motion.div>
        ))}
      </section>

      <footer className="text-center py-8 text-sm text-slate-500 dark:text-slate-500">
        Smart ATM Platform · Built with FastAPI + React
      </footer>
    </div>
  );
}