type NavbarProps = {
  title: string;
};

export function Navbar({ title }: NavbarProps) {
  return (
    <header className="h-16 border-b border-slate-200 bg-white px-6 flex items-center justify-between">
      <h1 className="text-lg font-semibold text-slate-900">{title}</h1>
      <span className="text-sm text-slate-500">Soutenance Mode</span>
    </header>
  );
}
