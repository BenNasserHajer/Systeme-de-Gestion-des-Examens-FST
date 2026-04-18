import Link from "next/link";

const links = [
  { href: "/planification", label: "Planification" },
  { href: "/surveillance", label: "Surveillance" },
  { href: "/salles", label: "Salles" },
  { href: "/matieres", label: "Matieres" },
  { href: "/enseignants", label: "Enseignants" },
  { href: "/convocation", label: "Convocation" },
];

export function Sidebar() {
  return (
    <aside className="w-64 border-r border-slate-200 bg-slate-50 p-4">
      <nav className="space-y-1">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="block rounded-md px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200"
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
