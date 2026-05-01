import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import { useEffect } from "react";

// Fix default Leaflet icons in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

const makeIcon = (color, isUser = false) =>
  L.divIcon({
    className: "custom-marker",
    html: isUser
      ? `<div style="background:#3b82f6;width:18px;height:18px;border-radius:50%;border:3px solid white;box-shadow:0 0 0 6px rgba(59,130,246,0.25);"></div>`
      : `<div style="background:${color};width:36px;height:36px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid white;box-shadow:0 4px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;">
           <span style="transform:rotate(45deg);font-size:16px;">🏧</span>
         </div>`,
    iconSize: isUser ? [18, 18] : [36, 36],
    iconAnchor: isUser ? [9, 9] : [18, 36],
  });

function FitBounds({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points.length === 0) return;
    map.fitBounds(points, { padding: [50, 50] });
  }, [points, map]);
  return null;
}

export default function MapView({ user, atms, recommendedId }) {
  const center = user ? [user.lat, user.lng] : [40.7128, -74.0060];
  const points = [];
  if (user) points.push([user.lat, user.lng]);
  atms.forEach((a) => points.push([a.latitude, a.longitude]));

  return (
    <MapContainer center={center} zoom={13} className="w-full h-full rounded-2xl overflow-hidden z-0">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap'
      />
      {user && (
        <Marker position={[user.lat, user.lng]} icon={makeIcon("", true)}>
          <Popup>📍 You are here</Popup>
        </Marker>
      )}
      {atms.map((atm) => {
        const color = !atm.is_working ? "#ef4444" : atm.id === recommendedId ? "#f59e0b" : "#10b981";
        return (
          <Marker key={atm.id} position={[atm.latitude, atm.longitude]} icon={makeIcon(color)}>
            <Popup>
              <div className="text-sm">
                <div className="font-bold">{atm.name}</div>
                <div className="text-slate-500">{atm.bank}</div>
                <div>📍 {atm.distance_km} km · ⭐ {atm.rating}</div>
                <div>{atm.is_working ? "✅ Working" : "❌ Down"}</div>
              </div>
            </Popup>
          </Marker>
        );
      })}
      <FitBounds points={points} />
    </MapContainer>
  );
}