import { AdminNavbar } from "@/components/ui/AdminNavbar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      minHeight: "100vh",
      background: "radial-gradient(circle at top, #f0f9ff 0%, #f8fafc 45%, #ffffff 100%)",
    }}>
      <AdminNavbar />
      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "40px" }}>
        {children}
      </main>
    </div>
  );
}