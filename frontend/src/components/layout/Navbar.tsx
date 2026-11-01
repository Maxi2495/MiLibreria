import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Book, Library, Users, LogOut } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  const activeLink = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition ${
      isActive ? 'bg-slate-800 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
    }`;

  return (
    <nav className="bg-slate-900 text-white border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <span className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-orange-500"></span>
            BookNest
          </span>
          <div className="hidden md:flex gap-2">
            <NavLink to="/catalogo" className={activeLink}>
              <Book size={16} /> Catálogo
            </NavLink>
            <NavLink to="/bibliotecas" className={activeLink}>
              <Library size={16} /> Bibliotecas
            </NavLink>
            <NavLink to="/prestamos" className={activeLink}>
              <Users size={16} /> Préstamos
            </NavLink>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-xs text-slate-400 hidden sm:inline">{user?.email}</span>
          <button
            onClick={logout}
            className="text-slate-400 hover:text-white p-1 rounded-md transition"
            title="Cerrar sesión"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </nav>
  );
};