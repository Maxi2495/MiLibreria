import React, { useState } from 'react';
import { Search, Loader2, X, PlusCircle } from 'lucide-react';
import { catalogoService } from '../../services/catalogoService';
import { LibroISBNResponse, Biblioteca } from '../../types';
import { FallbackImage } from '../common/FallbackImage';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  bibliotecas: Biblioteca[];
}

export const ModalAltaISBN: React.FC<Props> = ({ isOpen, onClose, onSuccess, bibliotecas }) => {
  const [isbn, setIsbn] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [libroData, setLibroData] = useState<LibroISBNResponse | null>(null);

  // Datos del ejemplar
  const [estanteId, setEstanteId] = useState<number | ''>('');
  const [condicion, setCondicion] = useState('BUENO');
  const [estadoLectura, setEstadoLectura] = useState('PENDIENTE');

  if (!isOpen) return null;

  const handleBuscarISBN = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const data = await catalogoService.buscarPorISBN(isbn);
      setLibroData(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'No se encontró el ISBN especificado.');
      setLibroData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGuardar = async () => {
    if (!libroData) return;
    setSubmitting(true);
    setError(null);
    try {
      await catalogoService.crearLibroConEjemplar({
        libro: {
          isbn: libroData.isbn,
          titulo: libroData.titulo,
          autores: libroData.autores,
          editorial: libroData.editorial,
          fecha_publicacion: libroData.fecha_publicacion,
          sinopsis: libroData.sinopsis,
          generos: libroData.generos,
          portada_url: libroData.portada_url,
        },
        estante_id: estanteId !== '' ? Number(estanteId) : null,
        condicion,
        estado_lectura: estadoLectura,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al persistir libro y ejemplar.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex justify-between items-center p-4 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <PlusCircle className="text-orange-600" size={20} />
            Ingreso Rápido por Código ISBN
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-5">
          <form onSubmit={handleBuscarISBN} className="flex gap-2">
            <input
              type="text"
              placeholder="Ingresá ISBN-10 o ISBN-13 (ej: 9789877382860)"
              value={isbn}
              onChange={(e) => setIsbn(e.target.value)}
              className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-800 outline-none text-sm"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="bg-slate-800 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-slate-700 transition flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader2 className="animate-spin" size={16} /> : <Search size={16} />}
              Consultar
            </button>
          </form>

          {error && <div className="p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-200">{error}</div>}

          {libroData && (
            <div className="space-y-4 border-t pt-4 border-slate-200">
              <div className="flex gap-4">
                <FallbackImage
                  src={libroData.portada_url || undefined}
                  alt={libroData.titulo}
                  className="w-24 h-36 object-cover rounded shadow border"
                />
                <div className="flex-1 space-y-1">
                  <h3 className="font-bold text-slate-900 leading-tight">{libroData.titulo}</h3>
                  <p className="text-sm text-slate-600 font-medium">
                    {libroData.autores.join(', ') || 'Autor desconocido'}
                  </p>
                  <p className="text-xs text-slate-500">
                    {libroData.editorial || 'Sin editorial'} {libroData.fecha_publicacion && `(${libroData.fecha_publicacion})`}
                  </p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {libroData.generos.map((g, i) => (
                      <span key={i} className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-700 rounded-full">
                        {g}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Ubicación Física</label>
                  <select
                    value={estanteId}
                    onChange={(e) => setEstanteId(e.target.value === '' ? '' : Number(e.target.value))}
                    className="w-full p-2 border rounded-md text-sm bg-white"
                  >
                    <option value="">Sin estante asignado</option>
                    {bibliotecas.flatMap((b) =>
                      b.estantes.map((e) => (
                        <option
                          key={e.id}
                          value={e.id}
                          disabled={e.ejemplares_actuales >= e.capacidad_maxima}
                        >
                          {b.nombre} - {e.nombre} ({e.ejemplares_actuales}/{e.capacidad_maxima})
                        </option>
                      ))
                    )}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Condición Física</label>
                  <select
                    value={condicion}
                    onChange={(e) => setCondicion(e.target.value)}
                    className="w-full p-2 border rounded-md text-sm bg-white"
                  >
                    <option value="NUEVO">Nuevo</option>
                    <option value="BUENO">Bueno</option>
                    <option value="REGULAR">Regular</option>
                    <option value="DETERIORADO">Deteriorado</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">Estado de Lectura</label>
                  <select
                    value={estadoLectura}
                    onChange={(e) => setEstadoLectura(e.target.value)}
                    className="w-full p-2 border rounded-md text-sm bg-white"
                  >
                    <option value="PENDIENTE">Pendiente</option>
                    <option value="LEYENDO">Leyendo</option>
                    <option value="LEIDO">Leído</option>
                    <option value="ABANDONADO">Abandonado</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-slate-200 bg-slate-50 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border rounded-lg text-sm text-slate-600 hover:bg-slate-100"
          >
            Cancelar
          </button>
          <button
            type="button"
            disabled={!libroData || submitting}
            onClick={handleGuardar}
            className="px-5 py-2 bg-orange-600 text-white rounded-lg text-sm font-semibold hover:bg-orange-700 disabled:opacity-50 transition"
          >
            {submitting ? 'Guardando...' : 'Confirmar e Incorporar a Colección'}
          </button>
        </div>
      </div>
    </div>
  );
};