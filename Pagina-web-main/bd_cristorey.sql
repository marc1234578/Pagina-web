DROP DATABASE IF EXISTS bd_cristorey;
CREATE DATABASE bd_cristorey 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE bd_cristorey;

-- =========================================================
-- BASE DE DATOS: HIJOS DE CRISTO REY
-- =========================================================

-- =========================================================
-- USUARIOS / CLIENTES / ADMINISTRADORES
-- =========================================================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('usuario','admin') DEFAULT 'usuario',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO usuarios (nombres, apellidos, telefono, correo, password, rol) VALUES
('MARCO ANTONIO', 'GALLEGOS LOAIZA', '999999999', 'marco@gmail.com', 'abc123$', 'admin'),
('FABRIZZIO FREDDY', 'HUARCA CALDUA', '999999999', 'fabrizzio@gmail.com', 'abc123$', 'admin'),
('JUAN PARIS', 'ROJAS PAJARES', '999999999', 'juan@gmail.com', 'abc123$', 'admin'),
('MARCOS', 'TORRES BARAS', '999999999', 'marcos@gmail.com', 'abc123$', 'admin');

-- =========================================================
-- CHOFERES
-- =========================================================
CREATE TABLE choferes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL DEFAULT '123456',
    placa VARCHAR(20) UNIQUE NOT NULL,
    licencia VARCHAR(50),
    vehiculo VARCHAR(80),
    estado ENUM('Activo','Suspendido') DEFAULT 'Activo',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO choferes 
(nombres, apellidos, telefono, correo, password, placa, licencia, vehiculo, estado) 
VALUES
('Carlos', 'Mamani Quispe', '71234567', 'carlos.chofer@gmail.com', '123456', 'ABC-123', 'A-IIb 123456', 'Minivan', 'Activo'),
('Juan', 'Flores Condori', '72345678', 'juan.chofer@gmail.com', '123456', 'XYZ-456', 'A-IIb 654321', 'Minivan', 'Activo'),
('Pedro', 'Ticona Huanca', '73456789', 'pedro.chofer@gmail.com', '123456', 'DEF-789', 'A-IIb 987654', 'Combi', 'Activo'),
('Luis', 'Mamani Chura', '74567890', 'luis.chofer@gmail.com', '123456', 'GHI-012', 'A-IIb 456789', 'Minivan', 'Activo'),
('Roberto', 'Condori Apaza', '75678901', 'roberto.chofer@gmail.com', '123456', 'JKL-345', 'A-IIb 112233', 'Minivan', 'Activo');

-- =========================================================
-- TARIFAS
-- =========================================================
CREATE TABLE tarifas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tramo VARCHAR(180) NOT NULL,
    tipo_ruta ENUM('Bajada','Subida') NOT NULL,
    adulto DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    escolar DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    estado ENUM('Activo','Inactivo') DEFAULT 'Activo',
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_tarifa_tramo_tipo (tramo, tipo_ruta)
);

INSERT INTO tarifas (tramo, tipo_ruta, adulto, escolar, estado) VALUES
('Ampliación II a Estación', 'Bajada', 2.00, 1.50, 'Activo'),
('Ampliación II al 5 Wiesse', 'Bajada', 1.50, 1.00, 'Activo'),
('Nueva Luz a Estación', 'Bajada', 2.00, 1.50, 'Activo'),
('Nueva Luz al 5 Wiesse', 'Bajada', 1.00, 1.00, 'Activo'),
('Estación a Ampliación II', 'Subida', 3.00, 1.50, 'Activo'),
('5 Wiesse a Ampliación II', 'Subida', 2.50, 1.50, 'Activo'),
('Estación a Nueva Luz', 'Subida', 2.00, 1.50, 'Activo'),
('5 Wiesse a Nueva Luz', 'Subida', 1.50, 1.00, 'Activo');

-- =========================================================
-- NOVEDADES Y AVISOS
-- =========================================================
CREATE TABLE novedades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    contenido TEXT NOT NULL,
    fecha_publicacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO novedades (titulo, contenido) VALUES
('Nuevos horarios de atención', 'Las unidades operarán desde las 5:00 a.m. hasta las 10:00 p.m. para mejorar la cobertura.'),
('Modernización de unidades', 'La empresa continúa renovando su flota para brindar un servicio más seguro y cómodo.');

-- =========================================================
-- QUEJAS / AYUDA
-- =========================================================
CREATE TABLE reportes_ayuda (
    id_reporte INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    correo_contacto VARCHAR(100) NOT NULL,
    detalle_queja TEXT NOT NULL,
    estado_reporte ENUM('Pendiente','En revisión','Atendido') DEFAULT 'Pendiente',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quejas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_correo VARCHAR(100),
    descripcion TEXT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- CARRERAS PRIVADAS
-- =========================================================
CREATE TABLE solicitudes_carrera (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cliente VARCHAR(120),
    telefono_cliente VARCHAR(25),
    direccion_origen VARCHAR(255) NOT NULL,
    direccion_destino VARCHAR(255) NOT NULL,
    monto_ofrecido DECIMAL(8,2) NOT NULL,
    estado_solicitud ENUM('Pendiente','Aceptada','Cancelada','Finalizada') DEFAULT 'Pendiente',
    chofer_id INT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_aceptacion DATETIME NULL,
    CONSTRAINT fk_carrera_chofer 
        FOREIGN KEY (chofer_id) REFERENCES choferes(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

INSERT INTO solicitudes_carrera 
(nombre_cliente, telefono_cliente, direccion_origen, direccion_destino, monto_ofrecido, estado_solicitud) 
VALUES
('Cliente prueba', '900111222', 'Nueva Luz', 'Estación Bayóvar', 18.00, 'Pendiente'),
('María López', '988777666', '5 Wiesse', 'Ampliación II', 15.00, 'Pendiente');

-- =========================================================
-- CONSULTAS DE VERIFICACIÓN
-- =========================================================
SELECT * FROM usuarios;
SELECT * FROM choferes;
SELECT * FROM tarifas;
SELECT * FROM novedades;
SELECT * FROM reportes_ayuda;
SELECT * FROM solicitudes_carrera;