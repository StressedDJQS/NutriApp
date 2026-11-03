import { Link, Outlet, useLocation } from 'react-router-dom';
import { Apple, UtensilsCrossed, Activity, CalendarDays } from 'lucide-react';

export default function Layout() {
  const location = useLocation();

  const navItems = [
    { name: 'Alimentos', path: '/', icon: Apple },
    { name: 'Recetas', path: '/recipes', icon: UtensilsCrossed },
    { name: 'Menús', path: '/menus', icon: CalendarDays },
  ];

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-[#1A365D] text-white flex flex-col">
        <div className="p-6 border-b border-blue-800">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-8 h-8 text-blue-400" />
            <h1 className="text-2xl font-bold">NutriApp</h1>
          </div>
          <p className="text-xs text-blue-200">Sistema de Planificación Nutricional</p>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive ? 'bg-[#2B6CB0] text-white' : 'text-slate-300 hover:bg-blue-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-semibold">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white shadow-sm h-16 flex items-center px-8">
          <h2 className="text-xl font-bold text-slate-800">
            {navItems.find(i => i.path === location.pathname)?.name || 'Dashboard'}
          </h2>
        </header>
        <div className="flex-1 overflow-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}