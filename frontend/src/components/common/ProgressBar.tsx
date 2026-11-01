import React from 'react';

interface Props {
  actual: number;
  max: number;
}

export const ProgressBar: React.FC<Props> = ({ actual, max }) => {
  const porcentaje = max > 0 ? Math.min(Math.round((actual / max) * 100), 100) : 0;
  
  const getColor = () => {
    if (porcentaje >= 100) return 'bg-red-500';
    if (porcentaje >= 80) return 'bg-amber-500';
    return 'bg-emerald-600';
  };

  return (
    <div className="w-full">
      <div className="flex justify-between text-xs font-semibold mb-1.5 text-slate-700">
        <span>Ocupación: {actual} / {max} libros</span>
        <span className="font-bold">{porcentaje}%</span>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
        <div
          className={`h-2.5 rounded-full transition-all duration-300 ${getColor()}`}
          style={{ width: `${porcentaje}%` }}
        />
      </div>
      {porcentaje >= 100 && (
        <span className="text-[11px] text-red-600 font-semibold mt-1 inline-block">
          Estante al límite físico de capacidad.
        </span>
      )}
    </div>
  );
};