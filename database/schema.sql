-- ============================================================
-- BookNest
-- Esquema inicial de base de datos
-- Motor: MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS booknest
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE booknest;

-- ============================================================
-- USUARIO
-- ============================================================

CREATE TABLE usuario (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL,

    CONSTRAINT uq_usuario_email UNIQUE (email),
    CONSTRAINT chk_usuario_estado
        CHECK (estado IN ('ACTIVA', 'INACTIVA'))
);

-- ============================================================
-- EDITORIAL
-- ============================================================

CREATE TABLE editorial (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL
);

-- ============================================================
-- SAGA
-- ============================================================

CREATE TABLE saga (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL
);

-- ============================================================
-- AUTOR
-- ============================================================

CREATE TABLE autor (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL
);

-- ============================================================
-- GENERO
-- ============================================================

CREATE TABLE genero (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- ============================================================
-- LIBRO
-- ============================================================

CREATE TABLE libro (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) NULL,
    fecha_publicacion DATE NULL,
    sinopsis TEXT NULL,
    portada_url VARCHAR(500) NULL,
    editorial_id BIGINT NULL,
    saga_id BIGINT NULL,
    posicion_saga DECIMAL(5,2) NULL,

    CONSTRAINT fk_libro_editorial
        FOREIGN KEY (editorial_id)
        REFERENCES editorial(id),

    CONSTRAINT fk_libro_saga
        FOREIGN KEY (saga_id)
        REFERENCES saga(id)
);

-- ============================================================
-- LIBRO - AUTOR
-- ============================================================

CREATE TABLE libro_autor (
    libro_id BIGINT NOT NULL,
    autor_id BIGINT NOT NULL,

    PRIMARY KEY (libro_id, autor_id),

    CONSTRAINT fk_libro_autor_libro
        FOREIGN KEY (libro_id)
        REFERENCES libro(id),

    CONSTRAINT fk_libro_autor_autor
        FOREIGN KEY (autor_id)
        REFERENCES autor(id)
);

-- ============================================================
-- LIBRO - GENERO
-- ============================================================

CREATE TABLE libro_genero (
    libro_id BIGINT NOT NULL,
    genero_id BIGINT NOT NULL,

    PRIMARY KEY (libro_id, genero_id),

    CONSTRAINT fk_libro_genero_libro
        FOREIGN KEY (libro_id)
        REFERENCES libro(id),

    CONSTRAINT fk_libro_genero_genero
        FOREIGN KEY (genero_id)
        REFERENCES genero(id)
);

-- ============================================================
-- BIBLIOTECA
-- ============================================================

CREATE TABLE biblioteca (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT NOT NULL,
    nombre VARCHAR(100) NOT NULL,

    CONSTRAINT uq_biblioteca_usuario_nombre
        UNIQUE (usuario_id, nombre),

    CONSTRAINT fk_biblioteca_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario(id)
);

-- ============================================================
-- ESTANTE
-- ============================================================

CREATE TABLE estante (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    biblioteca_id BIGINT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    capacidad INT NOT NULL,

    CONSTRAINT uq_estante_biblioteca_nombre
        UNIQUE (biblioteca_id, nombre),

    CONSTRAINT chk_estante_capacidad
        CHECK (capacidad > 0),

    CONSTRAINT fk_estante_biblioteca
        FOREIGN KEY (biblioteca_id)
        REFERENCES biblioteca(id)
);

-- ============================================================
-- EJEMPLAR
-- ============================================================

CREATE TABLE ejemplar (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT NOT NULL,
    libro_id BIGINT NOT NULL,
    estante_id BIGINT NULL,
    fecha_adquisicion DATE NULL,
    estado_fisico VARCHAR(20) NULL,
    precio_compra DECIMAL(10,2) NULL,
    moneda VARCHAR(10) NULL,
    observacion TEXT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_ejemplar_estado_fisico
        CHECK (
            estado_fisico IS NULL
            OR estado_fisico IN (
                'NUEVO',
                'MUY_BUENO',
                'BUENO',
                'REGULAR',
                'DETERIORADO'
            )
        ),

    CONSTRAINT chk_ejemplar_precio
        CHECK (precio_compra IS NULL OR precio_compra >= 0),

    CONSTRAINT fk_ejemplar_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario(id),

    CONSTRAINT fk_ejemplar_libro
        FOREIGN KEY (libro_id)
        REFERENCES libro(id),

    CONSTRAINT fk_ejemplar_estante
        FOREIGN KEY (estante_id)
        REFERENCES estante(id)
);

-- ============================================================
-- LECTURA
-- ============================================================

CREATE TABLE lectura (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ejemplar_id BIGINT NOT NULL,
    estado VARCHAR(20) NOT NULL,
    fecha_inicio DATE NULL,
    fecha_fin DATE NULL,
    calificacion TINYINT NULL,
    resena TEXT NULL,

    CONSTRAINT chk_lectura_estado
        CHECK (
            estado IN (
                'PENDIENTE',
                'EN_CURSO',
                'ABANDONADO',
                'LEIDO'
            )
        ),

    CONSTRAINT chk_lectura_calificacion
        CHECK (
            calificacion IS NULL
            OR calificacion BETWEEN 1 AND 5
        ),

    CONSTRAINT fk_lectura_ejemplar
        FOREIGN KEY (ejemplar_id)
        REFERENCES ejemplar(id)
);

-- ============================================================
-- PRESTAMO
-- ============================================================

CREATE TABLE prestamo (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ejemplar_id BIGINT NOT NULL,
    nombre_destinatario VARCHAR(100) NOT NULL,
    apellido_destinatario VARCHAR(100) NOT NULL,
    telefono_destinatario VARCHAR(50) NULL,
    email_destinatario VARCHAR(255) NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_prevista_devolucion DATE NULL,
    fecha_devolucion DATE NULL,
    estado VARCHAR(20) NOT NULL,

    CONSTRAINT chk_prestamo_estado
        CHECK (
            estado IN (
                'ACTIVO',
                'VENCIDO',
                'DEVUELTO',
                'CANCELADO'
            )
        ),

    CONSTRAINT fk_prestamo_ejemplar
        FOREIGN KEY (ejemplar_id)
        REFERENCES ejemplar(id)
);

-- ============================================================
-- ANOTACION
-- ============================================================

CREATE TABLE anotacion (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT NOT NULL,
    ejemplar_id BIGINT NULL,
    titulo VARCHAR(255) NULL,
    contenido TEXT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_anotacion_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario(id),

    CONSTRAINT fk_anotacion_ejemplar
        FOREIGN KEY (ejemplar_id)
        REFERENCES ejemplar(id)
);

-- ============================================================
-- WISHLIST
-- ============================================================

CREATE TABLE wishlist (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    usuario_id BIGINT NOT NULL,
    libro_id BIGINT NULL,
    titulo VARCHAR(255) NOT NULL,
    autor_referencia VARCHAR(500) NULL,
    isbn VARCHAR(20) NULL,
    estado VARCHAR(20) NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_wishlist_estado
        CHECK (
            estado IN (
                'PENDIENTE',
                'ADQUIRIDO',
                'DESCARTADO'
            )
        ),

    CONSTRAINT fk_wishlist_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario(id),

    CONSTRAINT fk_wishlist_libro
        FOREIGN KEY (libro_id)
        REFERENCES libro(id)
);

-- ============================================================
-- INDICES PRINCIPALES
-- ============================================================

CREATE INDEX idx_libro_titulo
    ON libro(titulo);

CREATE INDEX idx_libro_isbn
    ON libro(isbn);

CREATE INDEX idx_autor_nombre
    ON autor(nombre);

CREATE INDEX idx_genero_nombre
    ON genero(nombre);

CREATE INDEX idx_editorial_nombre
    ON editorial(nombre);

CREATE INDEX idx_saga_nombre
    ON saga(nombre);

CREATE INDEX idx_ejemplar_usuario_activo
    ON ejemplar(usuario_id, activo);

CREATE INDEX idx_ejemplar_libro
    ON ejemplar(libro_id);

CREATE INDEX idx_ejemplar_estante
    ON ejemplar(estante_id);

CREATE INDEX idx_lectura_ejemplar_estado
    ON lectura(ejemplar_id, estado);

CREATE INDEX idx_prestamo_ejemplar_estado
    ON prestamo(ejemplar_id, estado);

CREATE INDEX idx_prestamo_fecha_prevista
    ON prestamo(fecha_prevista_devolucion);

CREATE INDEX idx_anotacion_usuario
    ON anotacion(usuario_id);

CREATE INDEX idx_anotacion_ejemplar
    ON anotacion(ejemplar_id);

CREATE INDEX idx_wishlist_usuario_estado
    ON wishlist(usuario_id, estado);

CREATE INDEX idx_wishlist_isbn
    ON wishlist(isbn);