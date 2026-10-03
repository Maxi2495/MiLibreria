-- ============================================================
-- BookNest: Datos de Prueba Iniciales (Seeds)
-- ============================================================

USE booknest;

-- 1. Usuario de prueba (password temporal: 'password123')
INSERT INTO usuario (id, nombre, apellido, email, password_hash, estado)
VALUES (1, 'Maximiliano', 'Niemiec', 'maxi@example.com', '$2b$12$e80bSgI5T0uN1E9xGz6YqeT7JzM7e1t2a3b4c5d6e7f8g9h0i1j2k', 'ACTIVA')
ON DUPLICATE KEY UPDATE id=id;

-- 2. Clasificación Bibliográfica
INSERT INTO editorial (id, nombre) VALUES 
(1, 'Minotauro'), 
(2, 'Debolsillo'), 
(3, 'Planeta')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO autor (id, nombre) VALUES 
(1, 'J.R.R. Tolkien'), 
(2, 'George Orwell'), 
(3, 'Gabriel García Márquez')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO genero (id, nombre) VALUES 
(1, 'Fantasía'), 
(2, 'Ciencia Ficción'), 
(3, 'Realismo Mágico')
ON DUPLICATE KEY UPDATE id=id;

-- 3. Catálogo de Libros (Ediciones)
INSERT INTO libro (id, titulo, isbn, fecha_publicacion, sinopsis, editorial_id) VALUES
(1, 'La Comunidad del Anillo', '9789505470648', '1954-07-29', 'Primer tomo de El Señor de los Anillos.', 1),
(2, '1984', '9788499890944', '1949-06-08', 'Distopía sobre la vigilancia total y el Gran Hermano.', 2)
ON DUPLICATE KEY UPDATE id=id;

-- Relaciones Libro - Autor y Libro - Género
INSERT IGNORE INTO libro_autor (libro_id, autor_id) VALUES (1, 1), (2, 2);
INSERT IGNORE INTO libro_genero (libro_id, genero_id) VALUES (1, 1), (2, 2);

-- 4. Ubicación Física
INSERT INTO biblioteca (id, usuario_id, nombre) VALUES 
(1, 1, 'Biblioteca Principal - Living')
ON DUPLICATE KEY UPDATE id=id;

INSERT INTO estante (id, biblioteca_id, nombre, capacidad) VALUES 
(1, 1, 'Estante Superior (Fantasía)', 15),
(2, 1, 'Estante Medio (Clásicos)', 20)
ON DUPLICATE KEY UPDATE id=id;

-- 5. Copias Físicas (Ejemplares)
INSERT INTO ejemplar (id, usuario_id, libro_id, estante_id, estado_fisico, activo) VALUES
(1, 1, 1, 1, 'MUY_BUENO', TRUE),
(2, 1, 2, 2, 'BUENO', TRUE)
ON DUPLICATE KEY UPDATE id=id;

-- 6. Lectura inicial
INSERT INTO lectura (ejemplar_id, estado, calificacion, resena) VALUES
(1, 'LEIDO', 5, 'Una de las mejores obras de literatura fantástica.'),
(2, 'PENDIENTE', NULL, NULL);

-- 7. Préstamo
INSERT INTO prestamo (ejemplar_id, nombre_destinatario, apellido_destinatario, fecha_prestamo, fecha_prevista_devolucion, estado) VALUES
(2, 'Carlos', 'Gómez', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 15 DAY), 'ACTIVO');