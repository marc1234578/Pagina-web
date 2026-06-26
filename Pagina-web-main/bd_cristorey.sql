-- 1. Creamos la base de datos para el proyecto (si no existe)
CREATE DATABASE IF NOT EXISTS bd_cristorey;
USE bd_cristorey;

-- 2. Creamos la tabla exacta para el formulario de quejas
CREATE TABLE reportes_ayuda (
    id_reporte INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    correo_contacto VARCHAR(100) NOT NULL,
    detalle_queja TEXT NOT NULL,
    estado_reporte VARCHAR(20) DEFAULT 'Pendiente',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- 3. La creamos de nuevo con absolutamente TODO lo que pide tu formulario
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE solicitudes_carrera (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    direccion_origen VARCHAR(255) NOT NULL,
    direccion_destino VARCHAR(255) NOT NULL,
    monto_ofrecido DECIMAL(8, 2) NOT NULL,
    estado_solicitud VARCHAR(50) DEFAULT 'Pendiente',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- 5. Aseguramos que existan las tablas para el administrador
CREATE TABLE IF NOT EXISTS novedades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    contenido TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quejas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_correo VARCHAR(100),
    descripcion TEXT NOT NULL
);

-- 6. Insertamos a los 4 administradores oficiales en tu tabla de usuarios
INSERT INTO usuarios (nombres, apellidos, telefono, correo, password) VALUES 
('MARCO ANTONIO', 'GALLEGOS LOAIZA', '999999999', 'marco@gmail.com', 'abc123$'),
('FABRIZZIO FREDDY', 'HUARCA CALDUA', '999999999', 'fabrizzio@gmail.com', 'abc123$'),
('JUAN PARIS', 'ROJAS PAJARES', '999999999', 'juan@gmail.com', 'abc123$'),
('MARCOS', 'TORRES BARAS', '999999999', 'marcos@gmail.com', 'abc123$');

-- 3. para ver la tabla
Select * From reportes_ayuda