import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { MainLayout } from '../components/layout/MainLayout';
import { LoginPage } from '../pages/LoginPage';
import { CatalogoPage } from '../pages/CatalogoPage';
import { BibliotecasPage } from '../pages/BibliotecasPage';
import { PrestamosPage } from '../pages/PrestamosPage';

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Ruta pública */}
      <Route path="/login" element={<LoginPage />} />

      {/* Rutas protegidas */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>
          <Route index element={<Navigate to="/catalogo" replace />} />
          <Route path="catalogo" element={<CatalogoPage />} />
          <Route path="bibliotecas" element={<BibliotecasPage />} />
          <Route path="prestamos" element={<PrestamosPage />} />
        </Route>
      </Route>

      {/* Comodín de captura */}
      <Route path="*" element={<Navigate to="/catalogo" replace />} />
    </Routes>
  );
};