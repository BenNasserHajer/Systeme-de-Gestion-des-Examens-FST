"use client";

import { useRouter, usePathname } from "next/navigation";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

const API_ENDPOINTS = {
  AUTH_LOGOUT: `${API_BASE_URL}/auth/logout`,
};

const FST_LOGO = "/assets/fst.jpg";
const UTM_LOGO = "/assets/ut.jpg";

export function AdminNavbar() {
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = async () => {
    await fetch(API_ENDPOINTS.AUTH_LOGOUT, { method: "POST", credentials: "include" });
    router.replace("/login");
  };

  const navLinks = [
    { href: "/planification", label: "Planification" },
    { href: "/surveillance", label: "Surveillance" },
    { href: "/salles", label: "Salles" },
  ];

  return (
    <nav style={{
      background: "#ffffff",
      borderBottom: "1px solid #e9eef3",
      padding: "0 40px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      height: 80,
      position: "sticky",
      top: 0,
      zIndex: 100,
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <img src={UTM_LOGO} alt="UTM" style={{ height: 48, width: "auto", objectFit: "contain" }} />
          <div style={{ width: 1, height: 36, background: "#e9eef3" }} />
          <img src={FST_LOGO} alt="FST" style={{ height: 48, width: "auto", objectFit: "contain" }} />
        </div>
        <div>
          <div style={{ fontSize: 11, fontWeight: 500, color: "#94a3b8", letterSpacing: "0.5px", textTransform: "uppercase" }}>
            Université de Tunis El Manar
          </div>
          <div style={{ fontSize: 14, fontWeight: 600, color: "#1e293b" }}>
            Faculté des Sciences de Tunis
          </div>
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
        {/* Navigation Links */}
        <div style={{ display: "flex", gap: "24px", marginRight: "32px" }}>
          {navLinks.map(link => {
            const isActive = pathname?.startsWith(link.href);
            return (
              <a 
                key={link.href}
                href={link.href} 
                style={{
                  textDecoration: "none",
                  color: isActive ? "#4f46e5" : "#64748b",
                  fontWeight: isActive ? 600 : 500,
                  fontSize: "15px",
                  paddingBottom: "4px",
                  borderBottom: `2px solid ${isActive ? "#4f46e5" : "transparent"}`,
                  transition: "all 0.2s"
                }} 
                onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.color = "#4f46e5"; }}
                onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.color = "#64748b"; }}
              >
                {link.label}
              </a>
            );
          })}
        </div>
        
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: "#1e293b" }}>Administrateur</div>
          <div style={{ fontSize: 12, color: "#94a3b8" }}>Admin</div>
        </div>
        
        <button
          onClick={handleLogout}
          style={{
            background: "transparent",
            border: "1px solid #e2e8f0",
            borderRadius: 40,
            padding: "8px 22px",
            color: "#64748b",
            fontSize: 13,
            fontWeight: 500,
            cursor: "pointer",
            fontFamily: "inherit",
            transition: "all 0.2s ease",
          }}
          onMouseEnter={e => { e.currentTarget.style.background = "#afd6fc"; e.currentTarget.style.borderColor = "#cbd5e1"; }}
          onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#e2e8f0"; }}
        >
          Déconnexion
        </button>
      </div>
    </nav>
  );
}
