import { AdminNavbar } from "@/components/ui/AdminNavbar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      minHeight: "100vh",
      background: "#f8fafc",
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    }}>
      <AdminNavbar />
      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "40px" }}>
        {children}
      </main>
    </div>
  );
}