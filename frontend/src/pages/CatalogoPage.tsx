import React, { useEffect, useState } from 'react';
import { catalogoService } from '../services/catalogoService';
import { bibliotecaService } from '../services/bibliotecaService';
import { Libro, Biblioteca } from '../types';
import { LibroCard } from '../components/libros/LibroCard';
import { ModalAltaISBN } from '../components/libros/ModalAltaISBN';
import { BookPlus, Search, BookOpen, X } from 'lucide-react';

export const CatalogoPage: React.FC = () => {
  const [libros, setLibros] = useState<Libro[]>([]);
  const [bibliotecas, setBibliotecas] = useState<Biblioteca[]>([]);
  const [busqueda, setBusqueda] = useState('');
  const [loading, setLoading] = useState(true);
  const [modalAbierto, setModalAbierto] = useState(false);

  useEffect(() => {
    let activo = true;
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const terminoLimpio = busqueda.trim();
        const [dataLibros, dataBiblio] = await Promise.all([
          catalogoService.listarLibros(terminoLimpio ? { buscar: terminoLimpio } : undefined),
          bibliotecaService.listarBibliotecas(),
        ]);
        if (activo) {
          setLibros(dataLibros);
          setBibliotecas(dataBiblio);
        }
      } catch (err) {
        console.error("Error al cargar catálogo:", err);
      } finally {
        if (activo) setLoading(false);
      }
    }, 300);

    return () => {
      activo = false;
      clearTimeout(timer);
    };
  }, [busqueda]);

  const recargarCatalogo = async () => {
    setLoading(true);
    try {
      const terminoLimpio = busqueda.trim();
      const [dataLibros, dataBiblio] = await Promise.all([
        catalogoService.listarLibros(terminoLimpio ? { buscar: terminoLimpio } : undefined),
        bibliotecaService.listarBibliotecas(),
      ]);
      setLibros(dataLibros);
      setBibliotecas(dataBiblio);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-amber-50 drop-shadow-sm tracking-tight">
            Catálogo Bibliográfico
          </h1>
          <p className="text-sm text-amber-200/80 mt-1 font-medium">
            Gestión de títulos, metadatos y ejemplares físicos.
          </p>
        </div>
        <button
          onClick={() => setModalAbierto(true)}
          className="bg-amber-600 text-stone-950 px-4 py-2.5 rounded-lg font-bold text-sm flex items-center gap-2 hover:bg-amber-500 transition shadow-md"
        >
          <BookPlus size={18} />
          Alta por ISBN
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3.5 top-3 text-slate-500" size={18} />
        <input
          type="text"
          placeholder="Buscar por título, autor, editorial o ISBN..."
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
          className="w-full pl-10 pr-10 py-2.5 border border-amber-950/40 rounded-xl text-sm bg-stone-100 text-slate-900 placeholder-slate-500 outline-none focus:ring-2 focus:ring-amber-500 shadow-sm font-medium"
        />
        {busqueda && (
          <button
            onClick={() => setBusqueda('')}
            className="absolute right-3 top-3 text-slate-500 hover:text-slate-800"
            title="Limpiar búsqueda"
          >
            <X size={18} />
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-16 text-amber-200/70 font-medium">
          Consultando registros...
        </div>
      ) : libros.length === 0 ? (
        <div className="text-center py-16 bg-stone-900/60 rounded-2xl border border-dashed border-amber-900/40 p-8 backdrop-blur-sm">
          <BookOpen className="mx-auto text-amber-400/60 mb-3" size={36} />
          <p className="text-amber-100 font-semibold">No se registraron títulos coincidentes.</p>
          <p className="text-xs text-amber-200/60 mt-1">Probá modificando el criterio o agregá uno nuevo por ISBN.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
          {libros.map((libro) => (
            <LibroCard key={libro.id} libro={libro} />
          ))}
        </div>
      )}

      <ModalAltaISBN
        isOpen={modalAbierto}
        onClose={() => setModalAbierto(false)}
        onSuccess={recargarCatalogo}
        bibliotecas={bibliotecas}
      />
    </div>
  );
};