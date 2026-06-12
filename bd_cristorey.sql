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

-- 3. para ver la tabla
Select * From reportes_ayuda