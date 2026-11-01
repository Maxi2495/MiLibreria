import React from 'react';
import { Libro } from '../../types';
import { FallbackImage } from '../common/FallbackImage';

interface Props {
  libro: Libro;
}

export const LibroCard: React.FC<Props> = ({ libro }) => {
  const autoresTexto = libro.autores && libro.autores.length > 0
    ? libro.autores.map((a) => (typeof a === 'string' ? a : a.nombre)).join(', ')
    : 'Autor desconocido';

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden flex flex-col hover:shadow-md transition">
      <FallbackImage
        src={libro.portada_url || undefined}
        alt={libro.titulo}
        className="w-full h-56 object-cover bg-slate-100"
      />
      <div className="p-3 flex-1 flex flex-col justify-between">
        <div>
          <h3 className="font-semibold text-slate-800 text-sm line-clamp-2 leading-tight" title={libro.titulo}>
            {libro.titulo}
          </h3>
          <p className="text-xs text-slate-500 mt-1 line-clamp-1">
            {autoresTexto}
          </p>
        </div>
        <div className="mt-3 pt-2 border-t border-slate-100 flex justify-between items-center text-[11px] text-slate-500">
          <span>ISBN: {libro.isbn || 'S/D'}</span>
          <span className="font-semibold text-slate-700">{libro.cantidad_ejemplares ?? 0} ejs.</span>
        </div>
      </div>
    </div>
  );
};