CREATE DATABASE IF NOT EXISTS gastrolab;
USE gastrolab;


DELIMITER $$

CREATE PROCEDURE sp_informe_costes()
BEGIN
    SELECT
        e.puesto,
        COUNT(DISTINCT e.id_empleado) AS num_empleados,
        fn_salario_anual_puesto(e.puesto) AS coste_anual,
        ROUND(fn_salario_anual_puesto(e.puesto) / 12, 2) AS coste_mensual,
        ROUND(fn_salario_anual_puesto(e.puesto) / COUNT(DISTINCT e.id_empleado), 2) AS media_por_empleado
    FROM empleados e
    JOIN contratos c ON e.id_empleado = c.id_empleado
    WHERE e.activo = 1 AND c.activo = 1
    GROUP BY e.puesto
    ORDER BY coste_anual DESC;
END$$

CREATE PROCEDURE sp_resumen_empleado(
    IN p_id_empleado INT,
    OUT p_total_recetas INT,
    OUT p_contrato_activo TINYINT(1),
    OUT p_salario_bruto DECIMAL(10,2)
)
BEGIN
    SELECT COUNT(*) INTO p_total_recetas
    FROM recetas
    WHERE id_creador = p_id_empleado;

    SELECT activo INTO p_contrato_activo
    FROM contratos
    WHERE id_empleado = p_id_empleado AND activo = 1;

    SELECT salario_bruto_anual INTO p_salario_bruto
    FROM contratos
    WHERE id_empleado = p_id_empleado AND activo = 1;

    IF p_contrato_activo IS NULL THEN
        SET p_contrato_activo = 0;
    END IF;

    IF p_salario_bruto IS NULL THEN
        SET p_salario_bruto = 0.00;
    END IF;
END$$

CREATE FUNCTION fn_calcular_calorias_receta(p_id_receta INT)
RETURNS DECIMAL(10,2) DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE f_calorias DECIMAL(10,2);

    SELECT SUM((i.calorias_100g * ri.cantidad) / 100)
    INTO f_calorias
    FROM recetas_ingredientes ri
    JOIN ingredientes i ON ri.id_ingrediente = i.id_ingrediente
    WHERE ri.id_receta = p_id_receta;

    IF f_calorias IS NULL THEN
        RETURN 0;
    ELSE
        RETURN f_calorias;
    END IF;
END$$

CREATE FUNCTION fn_generar_username(p_id_empleado INT)
RETURNS VARCHAR(80) DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE v_nombre VARCHAR(100);
    DECLARE v_apellidos VARCHAR(150);
    DECLARE v_username VARCHAR(80);

    SELECT nombre, apellidos
    INTO v_nombre, v_apellidos
    FROM empleados
    WHERE id_empleado = p_id_empleado;

    SET v_username = LOWER(CONCAT(v_nombre, '.', v_apellidos));
    SET v_username = REPLACE(v_username, ' ', '');

    RETURN v_username;
END$$

CREATE FUNCTION fn_salario_anual_puesto(p_puesto VARCHAR(50))
RETURNS DECIMAL(12,2) DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(12,2);

    SELECT SUM(c.salario_bruto_anual)
    INTO v_total
    FROM contratos c
    JOIN empleados e ON c.id_empleado = e.id_empleado
    WHERE e.puesto = p_puesto
      AND e.activo = 1
      AND c.activo = 1;

    RETURN IFNULL(v_total, 0.00);
END$$

DELIMITER ;


CREATE TABLE alergenos (
    id_alergeno INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE categorias_receta (
    id_categoria INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE empleados (
    id_empleado INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    telefono VARCHAR(20) DEFAULT NULL,
    puesto ENUM('cocinero','docente','apoyo','alumno_cocina','alumno_dietetica') NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    fecha_alta DATE NOT NULL
);

CREATE TABLE ingredientes (
    id_ingrediente INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    unidad_medida VARCHAR(50) NOT NULL,
    categoria VARCHAR(100) DEFAULT NULL,
    calorias_100g DECIMAL(7,2) DEFAULT NULL,
    proteinas_100g DECIMAL(6,2) DEFAULT NULL,
    carbohidratos_100g DECIMAL(6,2) DEFAULT NULL,
    grasas_100g DECIMAL(6,2) DEFAULT NULL,
    fibra_100g DECIMAL(6,2) DEFAULT NULL,
    sodio_100g DECIMAL(7,2) DEFAULT NULL
);

CREATE TABLE usuarios (
    id_usuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activo TINYINT(1) NOT NULL DEFAULT 1
);

CREATE TABLE contratos (
    id_contrato INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    tipo_contrato VARCHAR(100) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE DEFAULT NULL,
    horas_semanales DECIMAL(5,2) NOT NULL,
    salario_bruto_anual DECIMAL(10,2) NOT NULL,
    salario_neto DECIMAL(10,2) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1
);

CREATE TABLE recetas (
    id_receta INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tiempo_preparacion INT DEFAULT NULL,
    tiempo_coccion INT DEFAULT NULL,
    raciones INT DEFAULT NULL,
    dificultad ENUM('facil','medio','dificil') DEFAULT NULL,
    id_categoria INT DEFAULT NULL,
    id_creador INT NOT NULL,
    fecha_creacion DATE NOT NULL
);

CREATE TABLE ingredientes_alergenos (
    id_ingrediente INT NOT NULL,
    id_alergeno INT NOT NULL,
    PRIMARY KEY (id_ingrediente, id_alergeno)
);

CREATE TABLE menus (
    id_menu INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo ENUM('diario','semanal','especial') NOT NULL,
    id_creador INT NOT NULL,
    fecha_creacion DATE NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1
);

CREATE TABLE menus_recetas (
    id_menu INT NOT NULL,
    id_receta INT NOT NULL,
    tipo_plato ENUM('entrante','principal','postre','bebida') NOT NULL,
    orden INT NOT NULL DEFAULT 1,
    PRIMARY KEY (id_menu, id_receta)
);

CREATE TABLE pasos_receta (
    id_paso INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_receta INT NOT NULL,
    numero_paso INT NOT NULL,
    descripcion TEXT NOT NULL,
    UNIQUE KEY uq_receta_paso (id_receta, numero_paso)
);

CREATE TABLE recetas_ingredientes (
    id_receta INT NOT NULL,
    id_ingrediente INT NOT NULL,
    cantidad DECIMAL(8,3) NOT NULL,
    unidad VARCHAR(50) NOT NULL,
    notas VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (id_receta, id_ingrediente)
);

CREATE TABLE favoritos (
    id_usuario INT NOT NULL,
    id_receta INT NOT NULL,
    fecha_adicion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_receta)
);

CREATE TABLE usuarios_login (
    id_usuario INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL,
    username VARCHAR(80) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1
);


ALTER TABLE empleados ADD UNIQUE KEY uq_empleados_email (email);
ALTER TABLE usuarios ADD UNIQUE KEY uq_usuarios_email (email);
ALTER TABLE usuarios_login ADD UNIQUE KEY uq_username (username);
ALTER TABLE contratos ADD KEY idx_contratos_empleado (id_empleado);
ALTER TABLE recetas ADD KEY idx_recetas_creador (id_creador);


INSERT INTO alergenos (id_alergeno, nombre, descripcion) VALUES
(1, 'Gluten', 'Cereales que contienen gluten: trigo, centeno, cebada, avena, espelta, kamut y sus variedades híbridas'),
(2, 'Crustáceos', 'Cangrejos, langostas, gambas, langostinos, quisquillas y productos derivados'),
(3, 'Huevo', 'Huevos de gallina y otras aves, así como productos derivados del huevo'),
(4, 'Pescado', 'Todo tipo de pescado y productos a base de pescado'),
(5, 'Cacahuetes', 'Cacahuetes y productos a base de cacahuetes'),
(6, 'Soja', 'Soja y productos a base de soja'),
(7, 'Lácteos', 'Leche y productos lácteos incluida la lactosa'),
(8, 'Frutos de cáscara', 'Almendras, avellanas, nueces, anacardos, pacanas, nueces de Brasil, pistachos, nueces de macadamia'),
(9, 'Apio', 'Apio y productos a base de apio'),
(10, 'Mostaza', 'Mostaza y productos a base de mostaza'),
(11, 'Sésamo', 'Semillas de sésamo y productos a base de sésamo'),
(12, 'Dióxido de azufre', 'Sulfitos en concentraciones superiores a 10 mg/kg o 10 mg/l expresado como SO2'),
(13, 'Altramuces', 'Altramuces y productos a base de altramuces'),
(14, 'Moluscos', 'Mejillones, almejas, ostras, calamares y productos derivados');

INSERT INTO categorias_receta (id_categoria, nombre, descripcion) VALUES
(1, 'Entrantes y aperitivos', 'Platos para comenzar la comida, tapas y pequeños bocados'),
(2, 'Sopas y cremas', 'Caldos, sopas frías y calientes, cremas y gazpachos'),
(3, 'Ensaladas', 'Ensaladas templadas, frías y composiciones vegetales'),
(4, 'Arroces y cereales', 'Paellas, risottos, quinoa, cuscús y otros cereales'),
(5, 'Pastas', 'Pastas italianas y fideos de diversas cocinas'),
(6, 'Carnes', 'Aves, vacuno, cerdo, cordero y caza'),
(7, 'Pescados y mariscos', 'Pescados al horno, a la plancha, mariscos y cefalópodos'),
(8, 'Vegetariano y vegano', 'Platos sin carne ni pescado, opción vegana donde se indique'),
(9, 'Postres y repostería', 'Dulces, tartas, mousses, helados y petit fours'),
(10, 'Panadería', 'Panes, masas, bollería y productos de horno'),
(11, 'Salsas y condimentos', 'Salsas madres, aderezos, encurtidos y conservas'),
(12, 'Cocina de autor', 'Creaciones de alta cocina y técnicas de vanguardia');

INSERT INTO empleados (id_empleado, nombre, apellidos, email, telefono, puesto, activo, fecha_alta) VALUES
(1, 'Carlos', 'Romero Vidal', 'carlos.romero@gastrolab.es', '612345001', 'docente', 1, '2019-09-01'),
(2, 'Laura', 'Martínez Ruiz', 'laura.martinez@gastrolab.es', '612345002', 'docente', 1, '2020-01-15'),
(3, 'Sergio', 'Fuentes Díaz', 'sergio.fuentes@gastrolab.es', '612345003', 'cocinero', 1, '2020-03-10'),
(4, 'Ana', 'López Herrera', 'ana.lopez@gastrolab.es', '612345004', 'cocinero', 1, '2021-02-01'),
(5, 'Miguel', 'Torres Castillo', 'miguel.torres@gastrolab.es', '612345005', 'apoyo', 1, '2021-06-15'),
(6, 'Elena', 'Sánchez Mora', 'elena.sanchez@gastrolab.es', '612345006', 'docente', 1, '2019-11-01'),
(7, 'Pablo', 'Navarro Gil', 'pablo.navarro@gastrolab.es', '612345007', 'apoyo', 1, '2022-01-10'),
(8, 'Sofía', 'Gómez Ramos', 'sofia.gomez@gastrolab.es', '612345008', 'alumno_cocina', 1, '2023-09-15'),
(9, 'Javier', 'Pérez Alonso', 'javier.perez@gastrolab.es', '612345009', 'alumno_cocina', 1, '2023-09-15'),
(10, 'María', 'Fernández Ortiz', 'maria.fernandez@gastrolab.es', '612345010', 'alumno_cocina', 1, '2023-09-15'),
(11, 'Roberto', 'Iglesias Vega', 'roberto.iglesias@gastrolab.es', '612345011', 'alumno_dietetica', 1, '2023-09-15'),
(12, 'Clara', 'Jiménez Blanco', 'clara.jimenez@gastrolab.es', '612345012', 'alumno_dietetica', 1, '2023-09-15'),
(13, 'Daniel', 'Moreno Santos', 'daniel.moreno@gastrolab.es', '612345013', 'alumno_cocina', 1, '2024-02-01'),
(14, 'Lucía', 'Rubio Campos', 'lucia.rubio@gastrolab.es', '612345014', 'alumno_dietetica', 1, '2024-02-01'),
(15, 'Adrián', 'Cano Reyes', 'adrian.cano@gastrolab.es', '612345015', 'cocinero', 1, '2022-09-01'),
(16, 'Natalia', 'Flores Medina', 'natalia.flores@gastrolab.es', '612345016', 'apoyo', 0, '2021-03-01'),
(17, 'Hugo', 'Molina Vargas', 'hugo.molina@gastrolab.es', '612345017', 'alumno_cocina', 1, '2024-09-15'),
(18, 'Valentina', 'Cruz Guerrero', 'valentina.cruz@gastrolab.es', '612345018', 'alumno_dietetica', 1, '2024-09-15'),
(19, 'Iñaki', 'Arrizabalaga Osa', 'inaki.arrizabalaga@gastrolab.es', '612345019', 'docente', 1, '2020-09-01'),
(20, 'Marta', 'Delgado Pineda', 'marta.delgado@gastrolab.es', '612345020', 'cocinero', 1, '2023-01-15');

INSERT INTO ingredientes (id_ingrediente, nombre, unidad_medida, categoria, calorias_100g, proteinas_100g, carbohidratos_100g, grasas_100g, fibra_100g, sodio_100g) VALUES
(1, 'Leche entera', 'ml', 'Lácteos', 61.00, 3.20, 4.80, 3.30, 0.00, 44.00),
(2, 'Nata para cocinar 35%', 'ml', 'Lácteos', 345.00, 2.80, 3.20, 35.00, 0.00, 38.00),
(3, 'Queso parmesano', 'g', 'Lácteos', 431.00, 38.50, 0.00, 29.00, 0.00, 1529.00),
(4, 'Queso manchego curado', 'g', 'Lácteos', 394.00, 26.80, 0.50, 32.00, 0.00, 620.00),
(5, 'Mantequilla sin sal', 'g', 'Lácteos', 717.00, 0.85, 0.06, 81.00, 0.00, 11.00),
(6, 'Yogur natural', 'g', 'Lácteos', 61.00, 3.50, 4.70, 3.30, 0.00, 46.00),
(7, 'Queso crema', 'g', 'Lácteos', 342.00, 6.15, 4.10, 33.20, 0.00, 321.00),
(8, 'Mozzarella fresca', 'g', 'Lácteos', 253.00, 17.10, 2.20, 19.90, 0.00, 373.00),
(9, 'Huevo entero L', 'ud', 'Huevos', 143.00, 12.60, 0.72, 10.00, 0.00, 142.00),
(10, 'Clara de huevo', 'g', 'Huevos', 52.00, 10.90, 0.73, 0.17, 0.00, 166.00),
(11, 'Pechuga de pollo', 'g', 'Carnes', 110.00, 23.10, 0.00, 1.24, 0.00, 74.00),
(12, 'Muslo de pollo s/h', 'g', 'Carnes', 177.00, 18.60, 0.00, 11.00, 0.00, 90.00),
(13, 'Solomillo de cerdo', 'g', 'Carnes', 143.00, 20.50, 0.00, 6.90, 0.00, 53.00),
(14, 'Lomo de ternera', 'g', 'Carnes', 158.00, 22.00, 0.00, 7.50, 0.00, 56.00),
(15, 'Panceta de cerdo', 'g', 'Carnes', 518.00, 10.20, 0.10, 53.00, 0.00, 655.00),
(16, 'Jamón serrano', 'g', 'Carnes', 241.00, 30.50, 0.50, 13.00, 0.00, 2527.00),
(17, 'Salmón fresco', 'g', 'Pescados', 208.00, 20.40, 0.00, 13.40, 0.00, 59.00),
(18, 'Bacalao fresco', 'g', 'Pescados', 82.00, 18.00, 0.00, 0.67, 0.00, 54.00),
(19, 'Gambas peladas', 'g', 'Mariscos', 99.00, 20.10, 0.91, 1.73, 0.00, 943.00),
(20, 'Mejillones', 'g', 'Mariscos', 86.00, 11.90, 3.69, 2.24, 0.00, 286.00),
(21, 'Tomate pera', 'g', 'Verduras', 18.00, 0.88, 3.89, 0.20, 1.20, 5.00),
(22, 'Cebolla', 'g', 'Verduras', 40.00, 1.10, 9.34, 0.10, 1.70, 4.00),
(23, 'Ajo', 'g', 'Verduras', 149.00, 6.36, 33.00, 0.50, 2.10, 17.00),
(24, 'Pimiento rojo', 'g', 'Verduras', 31.00, 1.00, 6.00, 0.30, 2.10, 2.00),
(25, 'Espinacas frescas', 'g', 'Verduras', 23.00, 2.86, 3.63, 0.39, 2.20, 79.00),
(26, 'Zanahoria', 'g', 'Verduras', 41.00, 0.93, 9.58, 0.24, 2.80, 69.00),
(27, 'Calabacín', 'g', 'Verduras', 17.00, 1.21, 3.11, 0.32, 1.00, 8.00),
(28, 'Berenjena', 'g', 'Verduras', 25.00, 0.98, 5.88, 0.18, 3.00, 2.00),
(29, 'Patata', 'g', 'Verduras', 77.00, 2.00, 17.49, 0.09, 2.20, 6.00),
(30, 'Puerro', 'g', 'Verduras', 61.00, 1.50, 14.15, 0.30, 1.80, 20.00),
(31, 'Garbanzos cocidos', 'g', 'Legumbres', 164.00, 8.86, 27.42, 2.59, 7.60, 24.00),
(32, 'Lentejas cocidas', 'g', 'Legumbres', 116.00, 9.02, 20.13, 0.38, 7.90, 2.00),
(33, 'Alubias blancas cocidas', 'g', 'Legumbres', 127.00, 8.97, 22.80, 0.50, 6.30, 2.00),
(34, 'Arroz bomba', 'g', 'Cereales', 358.00, 6.70, 79.00, 0.50, 1.40, 1.00),
(35, 'Pasta seca (tallarines)', 'g', 'Cereales', 371.00, 13.00, 74.67, 1.51, 2.70, 6.00),
(36, 'Harina de trigo T55', 'g', 'Cereales', 364.00, 10.33, 76.31, 0.98, 2.70, 2.00),
(37, 'Pan de baguette', 'g', 'Cereales', 272.00, 9.00, 52.00, 1.30, 2.70, 485.00),
(38, 'Quinoa cocida', 'g', 'Cereales', 120.00, 4.40, 21.30, 1.92, 2.80, 7.00),
(39, 'Aceite de oliva virgen extra', 'ml', 'Aceites', 884.00, 0.00, 0.00, 100.00, 0.00, 0.00),
(40, 'Caldo de pollo casero', 'ml', 'Caldos', 15.00, 1.80, 1.50, 0.50, 0.00, 450.00),
(41, 'Caldo de verduras', 'ml', 'Caldos', 8.00, 0.40, 1.60, 0.10, 0.00, 280.00),
(42, 'Limón', 'g', 'Frutas', 29.00, 1.10, 9.32, 0.30, 2.80, 2.00),
(43, 'Naranja', 'g', 'Frutas', 47.00, 0.94, 11.75, 0.12, 2.40, 0.00),
(44, 'Mango', 'g', 'Frutas', 60.00, 0.82, 14.98, 0.38, 1.60, 1.00),
(45, 'Fresas', 'g', 'Frutas', 32.00, 0.67, 7.68, 0.30, 2.00, 1.00),
(46, 'Plátano', 'g', 'Frutas', 89.00, 1.09, 22.84, 0.33, 2.60, 1.00),
(47, 'Azúcar blanquilla', 'g', 'Azúcares', 387.00, 0.00, 99.80, 0.00, 0.00, 1.00),
(48, 'Miel de flores', 'g', 'Azúcares', 304.00, 0.30, 82.40, 0.00, 0.20, 4.00),
(49, 'Almendras crudas', 'g', 'Frutos secos', 579.00, 21.15, 21.55, 49.93, 12.50, 1.00),
(50, 'Levadura seca de panadero', 'g', 'Levaduras', 325.00, 40.44, 41.22, 7.61, 26.90, 51.00);

INSERT INTO usuarios (id_usuario, nombre, email, password_hash, fecha_registro, activo) VALUES
(1, 'Pedro Alarcón', 'pedro.alarcon@email.com', '$2b$12$hashed_pedro_001', '2023-01-10 10:00:00', 1),
(2, 'Raquel Soto', 'raquel.soto@email.com', '$2b$12$hashed_raquel_002', '2023-02-14 11:30:00', 1),
(3, 'Tomás Vera', 'tomas.vera@email.com', '$2b$12$hashed_tomas_003', '2023-03-05 09:15:00', 1),
(4, 'Inés Pascual', 'ines.pascual@email.com', '$2b$12$hashed_ines_004', '2023-04-20 16:45:00', 1),
(5, 'Marcos Hidalgo', 'marcos.hidalgo@email.com', '$2b$12$hashed_marcos_005', '2023-05-08 12:00:00', 1),
(6, 'Silvia Aguilar', 'silvia.aguilar@email.com', '$2b$12$hashed_silvia_006', '2023-06-17 08:30:00', 1),
(7, 'Andrés Calvo', 'andres.calvo@email.com', '$2b$12$hashed_andres_007', '2023-07-22 14:20:00', 1),
(8, 'Patricia Lozano', 'patricia.lozano@email.com', '$2b$12$hashed_patricia_008', '2023-08-03 17:00:00', 1),
(9, 'Guillermo Ibáñez', 'guillermo.ibanez@email.com', '$2b$12$hashed_guiller_009', '2023-09-11 10:45:00', 1),
(10, 'Beatriz Serrano', 'beatriz.serrano@email.com', '$2b$12$hashed_beatriz_010', '2023-10-29 13:10:00', 1),
(11, 'Fernando Muñoz', 'fernando.munoz@email.com', '$2b$12$hashed_fernan_011', '2023-11-15 09:00:00', 1),
(12, 'Cristina Domínguez', 'cristina.dominguez@email.com', '$2b$12$hashed_cristi_012', '2024-01-07 11:00:00', 1),
(13, 'Álvaro Méndez', 'alvaro.mendez@email.com', '$2b$12$hashed_alvaro_013', '2024-02-19 15:30:00', 1),
(14, 'Nuria Prieto', 'nuria.prieto@email.com', '$2b$12$hashed_nuria_014', '2024-03-28 10:20:00', 0),
(15, 'Jorge Cabrera', 'jorge.cabrera@email.com', '$2b$12$hashed_jorge_015', '2024-04-12 08:00:00', 1);

INSERT INTO contratos (id_contrato, id_empleado, tipo_contrato, fecha_inicio, fecha_fin, horas_semanales, salario_bruto_anual, salario_neto, activo) VALUES
(1, 1, 'Indefinido a tiempo completo', '2019-09-01', NULL, 37.50, 42000.00, 29820.00, 1),
(2, 2, 'Indefinido a tiempo completo', '2020-01-15', NULL, 37.50, 38000.00, 27200.00, 1),
(3, 6, 'Indefinido a tiempo completo', '2019-11-01', NULL, 37.50, 40000.00, 28400.00, 1),
(4, 19, 'Indefinido a tiempo completo', '2020-09-01', NULL, 37.50, 44000.00, 31020.00, 1),
(5, 3, 'Indefinido a tiempo completo', '2020-03-10', NULL, 40.00, 32000.00, 23200.00, 1),
(6, 4, 'Indefinido a tiempo completo', '2021-02-01', NULL, 40.00, 30000.00, 21900.00, 1),
(7, 15, 'Indefinido a tiempo completo', '2022-09-01', NULL, 40.00, 28000.00, 20500.00, 1),
(8, 20, 'Indefinido a tiempo completo', '2023-01-15', NULL, 40.00, 27000.00, 19800.00, 1),
(9, 5, 'Indefinido a tiempo parcial', '2021-06-15', NULL, 20.00, 18000.00, 13500.00, 1),
(10, 7, 'Indefinido a tiempo parcial', '2022-01-10', NULL, 20.00, 17000.00, 12800.00, 1),
(11, 16, 'Temporal a tiempo parcial', '2021-03-01', '2023-02-28', 20.00, 16000.00, 12100.00, 0),
(12, 8, 'Convenio de prácticas', '2023-09-15', '2024-06-30', 8.00, 3600.00, 3600.00, 1),
(13, 9, 'Convenio de prácticas', '2023-09-15', '2024-06-30', 8.00, 3600.00, 3600.00, 1),
(14, 10, 'Convenio de prácticas', '2023-09-15', '2024-06-30', 8.00, 3600.00, 3600.00, 1),
(15, 11, 'Convenio de prácticas', '2023-09-15', '2024-06-30', 8.00, 3600.00, 3600.00, 1),
(16, 12, 'Convenio de prácticas', '2023-09-15', '2024-06-30', 8.00, 3600.00, 3600.00, 1),
(17, 13, 'Convenio de prácticas', '2024-02-01', '2024-07-31', 8.00, 2400.00, 2400.00, 1),
(18, 14, 'Convenio de prácticas', '2024-02-01', '2024-07-31', 8.00, 2400.00, 2400.00, 1),
(19, 17, 'Convenio de prácticas', '2024-09-15', '2025-06-30', 8.00, 3600.00, 3600.00, 1),
(20, 18, 'Convenio de prácticas', '2024-09-15', '2025-06-30', 8.00, 3600.00, 3600.00, 1);

INSERT INTO recetas (id_receta, nombre, descripcion, tiempo_preparacion, tiempo_coccion, raciones, dificultad, id_categoria, id_creador, fecha_creacion) VALUES
(1, 'Croquetas de jamón ibérico', 'Clásicas croquetas cremosas de jamón ibérico rebozadas en panko crujiente', 30, 20, 4, 'medio', 1, 3, '2022-03-10'),
(2, 'Patatas bravas con alioli', 'Patatas fritas crujientes con salsa brava picante y alioli casero', 20, 25, 4, 'facil', 1, 4, '2022-04-05'),
(3, 'Pulpo a la gallega', 'Pulpo cocido sobre lecho de patata cachelos con pimentón y aceite de oliva virgen', 15, 60, 4, 'medio', 1, 1, '2022-05-20'),
(4, 'Gazpacho andaluz', 'Sopa fría de tomate y verduras frescas, tradición andaluza en cada cucharada', 20, 0, 6, 'facil', 2, 6, '2021-07-01'),
(5, 'Crema de calabaza y jengibre', 'Crema aterciopelada de calabaza asada con toque de jengibre fresco y nata', 15, 35, 4, 'facil', 2, 2, '2022-09-15'),
(6, 'Sopa de lentejas con chorizo', 'Reconfortante sopa de lentejas pardinas con chorizo ahumado y verduras de temporada', 20, 40, 6, 'facil', 2, 15, '2023-01-10'),
(7, 'Ensalada de quinoa y mango', 'Ensalada refrescante con quinoa, mango fresco, aguacate y vinagreta de lima', 20, 0, 4, 'facil', 3, 20, '2023-05-01'),
(8, 'Ensalada tibia de espinacas', 'Espinacas frescas con panceta crujiente, huevo poché y vinagreta de mostaza', 15, 10, 4, 'facil', 3, 4, '2022-06-12'),
(9, 'Paella valenciana', 'Paella tradicional con pollo, conejo, garrofón y judía verde, socarrat garantizado', 30, 40, 6, 'dificil', 4, 1, '2021-10-10'),
(10, 'Risotto de setas y parmesano', 'Risotto cremoso con mix de setas silvestres, vino blanco y parmesano reggiano', 15, 30, 4, 'medio', 4, 19, '2022-11-08'),
(11, 'Arroz negro con sepia y alioli', 'Arroz meloso teñido con tinta de sepia, alioli casero y limón', 20, 35, 4, 'medio', 4, 3, '2023-02-14'),
(12, 'Carbonara auténtica', 'Pasta con guanciale, huevo, pecorino y pimienta negra, sin nata añadida', 10, 15, 4, 'medio', 5, 6, '2022-08-20'),
(13, 'Lasaña boloñesa', 'Lasaña de pasta fresca con ragú de ternera y cerdo, bechamel y parmesano gratinado', 45, 60, 8, 'dificil', 5, 1, '2021-12-05'),
(14, 'Pesto genovese con trofie', 'Pasta trofie con pesto de albahaca, piñones, parmesano y patata', 20, 15, 4, 'facil', 5, 19, '2023-04-22'),
(15, 'Pollo asado al limón y hierbas', 'Pollo entero asado lentamente con limón, ajo, romero y tomillo sobre lecho de patatas', 20, 90, 4, 'facil', 6, 2, '2022-02-28'),
(16, 'Solomillo de cerdo en salsa de mostaza', 'Medallones de solomillo con salsa cremosa de mostaza antigua y manzana reineta', 15, 20, 4, 'medio', 6, 15, '2023-03-17'),
(17, 'Carrilleras de ternera al vino tinto', 'Carrilleras estofadas lentamente en vino tinto con verduras, puré de patata trufado', 30, 180, 4, 'dificil', 6, 19, '2022-10-30'),
(18, 'Bacalao al pil-pil', 'Bacalao confitado en aceite de oliva con guindilla, elaborado con técnica tradicional vasca', 20, 30, 4, 'dificil', 7, 19, '2022-07-15'),
(19, 'Salmón teriyaki con arroz', 'Lomo de salmón lacado en salsa teriyaki casera con arroz jazmín y sésamo', 15, 20, 4, 'facil', 7, 20, '2023-06-10'),
(20, 'Gambas al ajillo', 'Gambas salteadas en aceite de oliva con ajo laminado, guindilla y perejil fresco', 10, 10, 4, 'facil', 7, 3, '2022-05-01'),
(21, 'Curry de garbanzos y espinacas', 'Curry aromático vegano con garbanzos, espinacas, tomate y leche de coco', 15, 25, 4, 'facil', 8, 2, '2023-07-08'),
(22, 'Cuscús de verduras asadas', 'Cuscús esponjoso acompañado de verduras asadas al horno con ras el hanout', 20, 30, 4, 'facil', 8, 20, '2023-08-20'),
(23, 'Revuelto de espárragos y trufa', 'Revuelto cremoso de huevos con espárragos trigueros y láminas de trufa negra', 10, 10, 2, 'facil', 8, 4, '2022-04-15'),
(24, 'Tarta de queso San Sebastián', 'Cheesecake horneado al horno vivo estilo La Viña, cremoso por dentro y caramelizado por fuera', 20, 50, 8, 'medio', 9, 6, '2022-01-20'),
(25, 'Mousse de chocolate negro 70%', 'Mousse aireada de chocolate negro con claras montadas, crujiente de cacao', 25, 0, 6, 'medio', 9, 15, '2023-09-05'),
(26, 'Panna cotta de vainilla con coulis', 'Panna cotta sedosa de nata y vainilla Tahití con coulis de fresas frescas', 15, 10, 4, 'facil', 9, 2, '2023-10-12'),
(27, 'Pan de masa madre', 'Pan artesanal de masa madre con harina integral, corteza crujiente y miga alveolada', 30, 240, 2, 'dificil', 10, 1, '2021-11-01'),
(28, 'Focaccia con aceitunas y romero', 'Focaccia esponjosa de masa hidratada con aceitunas Kalamata, romero y flor de sal', 20, 25, 6, 'medio', 10, 19, '2022-12-10'),
(29, 'Salsa romesco', 'Salsa catalana de tomates asados, ñoras, almendras y avellanas tostadas', 20, 0, 8, 'facil', 11, 1, '2022-03-01'),
(30, 'Esferificación de aceite de oliva', 'Aceite de oliva virgen extra en esferas gelatinosas, técnica de cocina molecular', 60, 0, 4, 'dificil', 12, 19, '2023-11-15');

INSERT INTO ingredientes_alergenos (id_ingrediente, id_alergeno) VALUES
(35, 1), (36, 1), (37, 1), (50, 1),
(19, 2),
(9, 3), (10, 3),
(17, 4), (18, 4),
(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
(49, 8),
(20, 14);

INSERT INTO menus (id_menu, nombre, descripcion, tipo, id_creador, fecha_creacion, activo) VALUES
(1, 'Menú diario lunes semana 1', 'Menú equilibrado para el lunes de la primera semana de octubre', 'diario', 1, '2024-09-30', 1),
(2, 'Menú diario martes semana 1', 'Menú mediterráneo del martes', 'diario', 6, '2024-09-30', 1),
(3, 'Menú diario miércoles semana 1', 'Platos de temporada del miércoles', 'diario', 2, '2024-09-30', 1),
(4, 'Menú diario jueves semana 1', 'Opciones vegetarianas y cárnicas del jueves', 'diario', 19, '2024-09-30', 1),
(5, 'Menú diario viernes semana 1', 'Menú de pescado para el viernes', 'diario', 1, '2024-09-30', 1),
(6, 'Menú semanal octubre A', 'Propuesta semanal completa con variedad de técnicas y productos', 'semanal', 6, '2024-09-25', 1),
(7, 'Menú semanal octubre B', 'Semana alternativa con enfoque en cocina de temporada otoño', 'semanal', 1, '2024-09-25', 1),
(8, 'Menú especial Navidad', 'Menú de celebración para las fiestas navideñas con productos premium', 'especial', 19, '2024-10-01', 1),
(9, 'Menú especial San Valentín', 'Menú romántico para parejas con recetas sofisticadas', 'especial', 2, '2024-10-01', 1),
(10, 'Menú especial Vegano', 'Propuesta totalmente plant-based apta para veganos', 'especial', 6, '2024-10-05', 1),
(11, 'Menú semanal noviembre A', 'Primera propuesta semanal de noviembre con platos de cuchara', 'semanal', 2, '2024-10-20', 1),
(12, 'Menú diario lunes semana 2', 'Arranque semanal con platos ligeros y nutritivos', 'diario', 1, '2024-10-07', 0);

INSERT INTO menus_recetas (id_menu, id_receta, tipo_plato, orden) VALUES
(1, 4, 'entrante', 1), (1, 9, 'principal', 2), (1, 24, 'postre', 3),
(2, 8, 'entrante', 1), (2, 13, 'principal', 2), (2, 25, 'postre', 3),
(3, 3, 'entrante', 1), (3, 17, 'principal', 2), (3, 26, 'postre', 3),
(4, 7, 'entrante', 1), (4, 21, 'principal', 2), (4, 24, 'postre', 3),
(5, 18, 'principal', 2), (5, 20, 'entrante', 1), (5, 26, 'postre', 3),
(6, 1, 'entrante', 1), (6, 9, 'principal', 2), (6, 15, 'principal', 3), (6, 18, 'principal', 4), (6, 24, 'postre', 5), (6, 25, 'postre', 6),
(7, 4, 'entrante', 1), (7, 10, 'principal', 2), (7, 16, 'principal', 3), (7, 19, 'principal', 4), (7, 26, 'postre', 5),
(8, 3, 'entrante', 1), (8, 17, 'principal', 3), (8, 24, 'postre', 4), (8, 25, 'postre', 5), (8, 30, 'entrante', 2),
(9, 17, 'principal', 2), (9, 25, 'postre', 3), (9, 30, 'entrante', 1),
(10, 7, 'entrante', 1), (10, 21, 'principal', 2), (10, 22, 'principal', 3), (10, 29, 'entrante', 4),
(11, 5, 'entrante', 2), (11, 6, 'entrante', 1), (11, 17, 'principal', 3), (11, 24, 'postre', 4),
(12, 8, 'entrante', 1), (12, 12, 'principal', 2), (12, 26, 'postre', 3);

INSERT INTO pasos_receta (id_paso, id_receta, numero_paso, descripcion) VALUES
(1, 1, 1, 'Derretir la mantequilla en un cazo a fuego medio. Añadir el jamón picado fino y rehogar 2 minutos hasta que suelte el aroma.'),
(2, 1, 2, 'Incorporar la harina de golpe y remover enérgicamente con una espátula durante 3 minutos para tostarla bien y eliminar el sabor a crudo.'),
(3, 1, 3, 'Verter la leche caliente poco a poco sin dejar de remover con varillas. Cocinar la bechamel unos 12 minutos a fuego medio-bajo hasta que se despegue de las paredes.'),
(4, 1, 4, 'Extender la masa en una bandeja, cubrir con film a piel y dejar enfriar completamente en nevera al menos 4 horas, preferiblemente toda la noche.'),
(5, 1, 5, 'Formar croquetas con las manos o con dos cucharas. Pasar por harina, huevo batido y panko. Freír en aceite abundante a 180 °C hasta que estén doradas.'),
(6, 1, 6, 'Escurrir sobre papel absorbente y servir inmediatamente para mantener el crujiente exterior y el interior cremoso.'),
(7, 4, 1, 'Lavar y trocar todas las verduras. Triturar los tomates, pimiento, cebolla y ajo con una batidora potente o Thermomix durante 2 minutos a máxima potencia.'),
(8, 4, 2, 'Añadir el pan remojado previamente en agua, el aceite de oliva y el vinagre de jerez. Triturar de nuevo hasta obtener una textura completamente homogénea.'),
(9, 4, 3, 'Colar la mezcla por un chino fino o colador de malla, presionando bien para extraer todos los jugos. Ajustar la sal.'),
(10, 4, 4, 'Refrigerar mínimo 2 horas. Servir muy frío acompañado de guarnición de pepino, pimiento y tomate en daditos.'),
(11, 9, 1, 'Calentar el aceite en la paellera a fuego fuerte. Dorar el pollo troceado por todos los lados hasta que esté bien sellado. Reservar.'),
(12, 9, 2, 'En el mismo aceite, sofreír el pimiento cortado en tiras durante 5 minutos. Añadir el tomate rallado y cocinar hasta que pierda el agua y quede concentrado, unos 8 minutos.'),
(13, 9, 3, 'Incorporar el pollo de nuevo, el pimentón dulce y el azafrán tostado. Rehogar 1 minuto sin que se queme el pimentón.'),
(14, 9, 4, 'Verter el caldo caliente (doble volumen que el arroz) y dejar hervir. Añadir el arroz distribuyéndolo uniformemente. Cocinar 18-20 minutos sin remover.'),
(15, 9, 5, 'Los últimos 2 minutos, subir el fuego para conseguir el socarrat. Retirar del fuego, cubrir con papel de periódico y reposar 5 minutos antes de servir.'),
(16, 24, 1, 'Precalentar el horno a 220 °C con calor arriba y abajo. Forrar un molde desmontable de 22 cm con papel de hornear arrugado (que sobresalga por los bordes).'),
(17, 24, 2, 'Batir el queso crema con el azúcar hasta que quede suave y sin grumos. Añadir los huevos de uno en uno, integrando bien cada uno antes de añadir el siguiente.'),
(18, 24, 3, 'Incorporar la nata y la harina tamizada. Mezclar con movimientos envolventes hasta obtener una crema homogénea y sin burbujas.'),
(19, 24, 4, 'Verter la mezcla en el molde y hornear durante 45-50 minutos. La superficie debe quedar muy oscura y el centro aún temblar ligeramente al mover el molde.'),
(20, 24, 5, 'Dejar enfriar completamente a temperatura ambiente y luego refrigerar al menos 4 horas antes de desmoldar y servir.'),
(21, 18, 1, 'Confitar el ajo laminado en el aceite de oliva a fuego muy bajo (60-70 °C) durante 10 minutos. Retirar el ajo y reservar.'),
(22, 18, 2, 'Introducir los lomos de bacalao con la piel hacia arriba en el aceite templado. Confitar a 65 °C durante 15-20 minutos. El bacalao soltará la gelatina natural.'),
(23, 18, 3, 'Retirar el bacalao y reservar. Con el aceite de la cazuela, comenzar a mover en círculos (o agitar la cazuela) para emulsionar la gelatina del bacalao con el aceite. Añadir el bacalao de nuevo y continuar moviendo hasta que la salsa espese y quede untuosa.'),
(24, 18, 4, 'Añadir la guindilla y el ajo confitado. Rectificar de sal. La salsa debe tener textura de crema ligada, brillante y de color dorado.'),
(25, 18, 5, 'Servir el bacalao en plato hondo o cazuelita de barro, cubierto con el pil-pil. Acompañar con pimiento del piquillo asado y pan para mojar. Esencial servir bien caliente.'),
(26, 17, 1, 'Limpiar las carrilleras eliminando los excesos de grasa y nervios. Salpimentar generosamente. Sellar en una cazuela con aceite caliente a fuego fuerte por todos los lados hasta dorar bien. Reservar.'),
(27, 17, 2, 'En la misma cazuela, pochar la cebolla, zanahoria y ajo picados a fuego medio durante 15 minutos. Añadir el tomate concentrado y cocinar 3 minutos más.'),
(28, 17, 3, 'Incorporar las carrilleras, verter el vino tinto y dejar reducir a la mitad. Añadir el caldo de carne hasta cubrir. Llevar a ebullición, bajar el fuego, tapar y guisar 2,5-3 horas hasta que estén muy tiernas.'),
(29, 17, 4, 'Retirar las carrilleras. Colar la salsa, reducirla si fuera necesario hasta que nape la cuchara. Rectificar de sal. Volver a introducir las carrilleras para que se impregnen bien.'),
(30, 17, 5, 'Preparar el puré de patata: cocer las patatas peladas, chafar con mantequilla, nata caliente y sal. Debe quedar muy fino y sedoso. Servir las carrilleras sobre el puré con la salsa y láminas de trufa.'),
(31, 13, 1, 'Preparar el ragú: sofreír cebolla y ajo picados. Añadir las carnes picadas y dorar bien. Incorporar el tomate triturado, sal, pimienta y un poco de vino tinto. Cocinar 45 minutos a fuego lento.'),
(32, 13, 2, 'Preparar la bechamel: derretir mantequilla, añadir harina, tostar 2 minutos. Incorporar la leche caliente poco a poco con varillas. Cocer 10 minutos hasta que espese. Salpimentar con nuez moscada.'),
(33, 13, 3, 'Montar la lasaña: en una fuente engrasada, alternar capas de pasta, ragú, bechamel y parmesano rallado. Repetir hasta terminar los ingredientes. La última capa debe ser de bechamel con abundante parmesano.'),
(34, 13, 4, 'Hornear a 180 °C durante 35-40 minutos hasta que esté dorada y burbujeante. Dejar reposar 10 minutos antes de cortar para que las capas se asienten.'),
(35, 15, 1, 'Precalentar el horno a 200 °C. Secar bien el pollo con papel. Frotarlo por dentro y por fuera con sal, pimienta, aceite de oliva, ajo machacado, romero y tomillo. Introducir medio limón en la cavidad.'),
(36, 15, 2, 'Colocar las patatas cortadas en gajos en el fondo de la bandeja. Salar y rociar con aceite. Poner el pollo encima con el pecho hacia arriba. Añadir el otro medio limón partido alrededor.'),
(37, 15, 3, 'Hornear 30 minutos a 200 °C. Bajar a 180 °C y continuar 50-60 minutos más, regando el pollo cada 20 minutos con sus propios jugos. Estará listo cuando al pinchar el muslo los jugos salgan claros.'),
(38, 15, 4, 'Reposar el pollo 10 minutos antes de trinchar. Servir con las patatas asadas y los jugos de la bandeja desglasada con un poco de agua o caldo.'),
(39, 25, 1, 'Fundir el chocolate al 70% al baño María o en microondas a potencia media en intervalos de 30 segundos, removiendo entre cada uno. Añadir la mantequilla y mezclar hasta que quede brillante y homogéneo. Dejar templar.'),
(40, 25, 2, 'Separar los huevos. Batir las yemas con la mitad del azúcar hasta que blanqueen y doblen su volumen. Incorporar el chocolate fundido templado a las yemas con movimientos envolventes.'),
(41, 25, 3, 'Montar las claras a punto de nieve firme con una pizca de sal. Cuando estén casi montadas, añadir el resto del azúcar y seguir batiendo hasta obtener un merengue brillante y firme.'),
(42, 25, 4, 'Incorporar las claras montadas a la mezcla de chocolate en tres tandas, con movimientos envolventes y suaves de abajo hacia arriba para no perder el aire. El resultado debe ser ligero y esponjoso.'),
(43, 25, 5, 'Distribuir en copas o vasitos. Cubrir con film y refrigerar mínimo 3 horas. Servir con un crujiente de cacao, frambuesas frescas y una pizca de sal en escamas.'),
(44, 26, 1, 'Hidratar las hojas de gelatina en agua fría durante 5 minutos. En un cazo, calentar la nata con la leche, el azúcar y la vaina de vainilla abierta. Llevar a 80 °C sin hervir.'),
(45, 26, 2, 'Retirar la vaina. Escurrir bien la gelatina hidratada y disolverla en la mezcla caliente removiendo hasta que no quede ningún rastro. Colar por un colador fino.'),
(46, 26, 3, 'Verter en moldes o vasitos previamente humedecidos. Dejar enfriar a temperatura ambiente y refrigerar al menos 4 horas.'),
(47, 26, 4, 'Preparar el coulis: triturar las fresas con azúcar glas y zumo de limón. Colar para eliminar las pepitas. Ajustar el dulzor. Reservar en nevera.'),
(48, 26, 5, 'Para desmoldar: pasar un cuchillo fino por el borde, cubrir con el plato y volcar con un golpe seco. Salsear con el coulis de fresas, decorar con fresas frescas y hojas de menta.'),
(49, 28, 1, 'Disolver la levadura seca en agua tibia con una pizca de azúcar. Dejar reposar 10 minutos hasta que forme espuma. Mezclar la harina con la sal en un bol grande.'),
(50, 28, 2, 'Incorporar el agua con levadura y 30 ml de aceite a la harina. Mezclar hasta integrar y amasar 10 minutos hasta obtener una masa lisa y elástica.'),
(51, 28, 3, 'Untar un bol con aceite, colocar la masa, cubrir con film y dejar fermentar 1,5-2 horas hasta que doble su volumen.'),
(52, 28, 4, 'Volcar la masa en una bandeja engrasada. Con los dedos, extenderla hasta los bordes haciendo hoyuelos profundos. Dejar reposar 30 minutos más.'),
(53, 28, 5, 'Repartir las aceitunas, el romero y la flor de sal. Regar con el aceite restante. Hornear a 220 °C durante 20-25 minutos hasta que esté dorada. Servir templada.'),
(54, 29, 1, 'Asar los tomates y la cabeza de ajos entera en el horno a 200 °C durante 30 minutos. Dejar templar.'),
(55, 29, 2, 'Hidratar las ñoras secas en agua caliente 20 minutos. Retirar la pulpa raspando con una cuchara. Tostar las almendras en sartén seca.'),
(56, 29, 3, 'Pelar los tomates asados y exprimir la pulpa de los ajos. Colocar en el vaso de la batidora junto con la pulpa de ñora, los frutos secos, el pan tostado y el vinagre de jerez.'),
(57, 29, 4, 'Triturar incorporando el aceite en hilo fino para emulsionar. La textura debe ser rústica, no completamente lisa. Rectificar de sal y pimentón.'),
(58, 29, 5, 'Dejar reposar 30 minutos antes de servir. Acompañar con calçots, verduras a la brasa o pescado a la plancha.'),
(59, 30, 1, 'Verter aceite de girasol neutro en un vaso alto y estrecho. Introducir en el congelador 30 minutos hasta que esté muy frío (no congelado).'),
(60, 30, 2, 'Calentar ligeramente el aceite de oliva virgen extra a 40 °C. Añadir la lecitina de soja y mezclar con la batidora de brazo hasta que se disuelva completamente.'),
(61, 30, 3, 'Cargar una jeringa con la mezcla de aceite con lecitina. Dejar caer gotas desde unos 10 cm de altura sobre el aceite frío. Las gotas se solidificarán formando esferas.'),
(62, 30, 4, 'Recoger las esferas con una cuchara perforada. Pasarlas por un baño de agua a temperatura ambiente para eliminar el exceso de aceite.'),
(63, 30, 5, 'Servir las esferas inmediatamente sobre tostada, tartar o como elemento decorativo. Al morderlas explotan liberando el sabor del aceite. Acompañar con sal Maldon y microhierbas.'),
(64, 19, 1, 'Preparar la salsa teriyaki casera: mezclar salsa de soja, mirin, sake y miel en un cazo. Llevar a ebullición y reducir a fuego medio 5 minutos hasta que espese ligeramente.'),
(65, 19, 2, 'Secar bien los lomos de salmón con papel. Marinar en la mitad de la salsa teriyaki 15 minutos a temperatura ambiente.'),
(66, 19, 3, 'Cocer el arroz jazmín según instrucciones del paquete. Reservar caliente tapado.'),
(67, 19, 4, 'Calentar una sartén antiadherente a fuego medio-alto. Cocinar el salmón 3-4 minutos por cada lado. En el último minuto, añadir la salsa teriyaki restante y glasear el salmón girándolo para que quede lacado.'),
(68, 19, 5, 'Servir el salmón sobre el arroz jazmín. Salsear con el resto de la salsa teriyaki. Decorar con semillas de sésamo tostadas y cebollino picado.'),
(69, 20, 1, 'Si las gambas son congeladas, descongelar en nevera la noche anterior y secar bien con papel. Salar ligeramente.'),
(70, 20, 2, 'Laminar el ajo fino. Calentar el aceite de oliva en una cazuelita de barro a fuego medio hasta unos 100 °C. Añadir el ajo y freír lentamente hasta que esté dorado.'),
(71, 20, 3, 'Subir el fuego a máximo. Añadir la guindilla y las gambas de golpe. Saltear enérgicamente 1-2 minutos hasta que las gambas estén rosadas y jugosas.'),
(72, 20, 4, 'Añadir un chorrito de coñac o vino blanco y dejar evaporar 30 segundos. Rectificar de sal.'),
(73, 20, 5, 'Retirar del fuego, espolvorear perejil fresco picado y servir inmediatamente en la misma cazuela de barro, con pan rústico para mojar.'),
(74, 21, 1, 'Calentar aceite de oliva en una cazuela amplia. Sofreír la cebolla picada 10 minutos. Añadir el ajo y el jengibre rallado, cocinar 2 minutos más.'),
(75, 21, 2, 'Incorporar las especias: curry, cúrcuma, comino y garam masala. Tostar 1 minuto removiendo para activar los aromas.'),
(76, 21, 3, 'Añadir el tomate triturado y cocinar 8 minutos. Incorporar los garbanzos cocidos y mezclar bien.'),
(77, 21, 4, 'Verter el caldo de verduras y la leche de coco. Cocinar 15 minutos. Añadir las espinacas los últimos 3 minutos hasta que se marchiten.'),
(78, 21, 5, 'Rectificar de sal. Servir con arroz basmati o pan naan. Decorar con cilantro fresco y un chorrito de yogur natural.'),
(79, 22, 1, 'Precalentar el horno a 200 °C. Cortar la berenjena, el calabacín, el pimiento y la zanahoria en trozos de 3 cm. Extender en bandejas sin amontonar.'),
(80, 22, 2, 'Aliñar las verduras con aceite de oliva, sal, pimienta y ras el hanout. Asar 25-30 minutos hasta que estén tiernas y con bordes caramelizados.'),
(81, 22, 3, 'Preparar el cuscús: llevar el caldo de verduras a ebullición, verter sobre el cuscús en proporción 1:1. Cubrir con film y reposar 5 minutos.'),
(82, 22, 4, 'Esponjar el cuscús con un tenedor. Añadir aceite de oliva, ralladura de limón y perejil picado.'),
(83, 22, 5, 'Servir el cuscús como base y disponer las verduras asadas encima. Acompañar con harissa y gajos de limón.'),
(84, 23, 1, 'Limpiar los espárragos trigueros y cortarlos en trozos de 3 cm conservando las puntas enteras.'),
(85, 23, 2, 'Calentar la mantequilla con un hilo de aceite en sartén antiadherente. Saltear los espárragos 3-4 minutos hasta que estén al dente y ligeramente tostados.'),
(86, 23, 3, 'Batir los huevos suavemente solo para romper la yema. Salpimentar.'),
(87, 23, 4, 'Bajar el fuego al mínimo. Verter los huevos sobre los espárragos. Con espátula de silicona, remover muy lentamente. El revuelto debe quedar muy cremoso y húmedo.'),
(88, 23, 5, 'Retirar del fuego antes de que esté completamente cuajado. Servir en plato caliente y terminar con láminas de trufa negra rallada al momento.'),
(89, 10, 1, 'Calentar el caldo de verduras y mantenerlo caliente a fuego mínimo durante toda la elaboración.'),
(90, 10, 2, 'Pochar la cebolla en mantequilla y aceite durante 8 minutos sin que coja color. Añadir el arroz y nacarar 2 minutos removiendo.'),
(91, 10, 3, 'Incorporar las setas salteadas previamente en mantequilla con ajo. Añadir el vino blanco y dejar evaporar.'),
(92, 10, 4, 'Ir añadiendo el caldo caliente cazo a cazo, esperando que el arroz absorba cada adición antes de añadir la siguiente. Remover continuamente durante 18 minutos.'),
(93, 10, 5, 'Fuera del fuego, incorporar la mantequilla fría en dados y el parmesano rallado. Mantecar enérgicamente hasta obtener una textura cremosa. Reposar 2 minutos y servir.'),
(94, 16, 1, 'Cortar el solomillo en medallones de 3 cm. Salpimentar. Sellar en sartén muy caliente con un poco de aceite, 2 minutos por cada lado para que queden jugosos. Reservar.'),
(95, 16, 2, 'En la misma sartén, pochar la cebolla picada fina 8 minutos. Añadir la manzana pelada y troceada, cocinar 5 minutos más.'),
(96, 16, 3, 'Incorporar la mostaza antigua y la nata. Llevar a ebullición suave y reducir 5 minutos hasta que espese. Salpimentar.'),
(97, 16, 4, 'Introducir los medallones de nuevo en la salsa y calentar 2 minutos sin que hierva para no endurecer la carne. Servir con la salsa por encima.'),
(98, 11, 1, 'Sofreír la cebolla, el ajo y el pimiento en aceite de oliva durante 10 minutos. Añadir la tinta de sepia y remover bien para que todo se impregne.'),
(99, 11, 2, 'Incorporar el arroz y nacarar 2 minutos. Verter el vino blanco y dejar evaporar.'),
(100, 11, 3, 'Añadir el caldo caliente poco a poco como un risotto, removiendo. Cocinar 18-20 minutos hasta que el arroz esté en su punto. Debe quedar meloso, no seco.'),
(101, 11, 4, 'Saltear la sepia limpia y troceada en sartén aparte con ajo y aceite 3-4 minutos. Añadir encima del arroz al servir.'),
(102, 11, 5, 'Servir el arroz negro con la sepia encima, acompañado de alioli casero y gajos de limón.'),
(103, 12, 1, 'Cocer la pasta en abundante agua con sal hasta que esté al dente. Reservar un vaso del agua de cocción.'),
(104, 12, 2, 'Cortar el guanciale o panceta en dados y freír en sartén sin aceite hasta que esté crujiente y haya soltado su grasa.'),
(105, 12, 3, 'Batir los huevos con el queso rallado y pimienta negra abundante hasta obtener una crema.'),
(106, 12, 4, 'Fuera del fuego, mezclar la pasta caliente con la grasa del guanciale. Añadir la crema de huevo y queso, removiendo rápidamente. Agregar agua de cocción poco a poco para conseguir una salsa cremosa sin que cuaje el huevo.'),
(107, 12, 5, 'Incorporar el guanciale. Servir inmediatamente con más queso rallado y pimienta negra recién molida.'),
(108, 14, 1, 'Majar en el mortero el ajo con sal gorda. Añadir las hojas de albahaca y seguir majando. Incorporar los frutos secos y continuar hasta obtener una pasta.'),
(109, 14, 2, 'Añadir el queso parmesano rallado y mezclar. Incorporar el aceite de oliva en hilo fino removiendo para emulsionar. El pesto debe quedar untuoso pero con algo de textura.'),
(110, 14, 3, 'Cocer la pasta en agua con sal hasta al dente. Reservar agua de cocción.'),
(111, 14, 4, 'Mezclar la pasta con el pesto añadiendo un poco del agua de cocción para aligerar. Nunca calentar el pesto para preservar el color y el aroma.'),
(112, 14, 5, 'Servir inmediatamente con más parmesano rallado por encima y unas hojas de albahaca fresca.'),
(113, 5, 1, 'Cortar la calabaza en dados grandes. Asar en el horno a 200 °C con un poco de aceite y sal durante 25 minutos hasta que esté tierna y ligeramente caramelizada.'),
(114, 5, 2, 'Pochar la cebolla en aceite de oliva 10 minutos. Añadir el jengibre fresco rallado y cocinar 2 minutos más.'),
(115, 5, 3, 'Incorporar la calabaza asada y el caldo de verduras. Llevar a ebullición y cocer 10 minutos.'),
(116, 5, 4, 'Triturar todo con la batidora hasta obtener una crema fina. Añadir la nata y rectificar de sal y pimienta.'),
(117, 5, 5, 'Servir caliente decorada con un hilo de nata, semillas de calabaza tostadas y un poco de jengibre en polvo.'),
(118, 6, 1, 'Poner las lentejas a remojar la noche anterior (si son pardinas, no hace falta). Picar la cebolla, el ajo, el tomate y la zanahoria en brunoise.'),
(119, 6, 2, 'Sofreír la cebolla y el ajo en aceite de oliva 8 minutos. Añadir la zanahoria y cocinar 5 minutos más. Incorporar el tomate y el pimentón, rehogar 3 minutos.'),
(120, 6, 3, 'Añadir las lentejas, el chorizo en rodajas y cubrir con el caldo. Llevar a ebullición, bajar el fuego y cocer 35-40 minutos hasta que las lentejas estén tiernas.'),
(121, 6, 4, 'Retirar el chorizo, chafar unas cucharadas de lentejas con el tenedor y reintegrarlas para dar cuerpo al caldo. Rectificar de sal.'),
(122, 6, 5, 'Servir en cuenco hondo con el chorizo en rodajas encima. Acompañar con pan rústico.'),
(123, 7, 1, 'Cocer la quinoa en el doble de agua con sal durante 15 minutos. Escurrir bien y dejar enfriar.'),
(124, 7, 2, 'Pelar y cortar el mango en dados. Preparar la vinagreta con zumo de lima, aceite de oliva, sal y pimienta.'),
(125, 7, 3, 'Mezclar la quinoa con el mango, el aguacate en dados y el pepino picado.'),
(126, 7, 4, 'Aliñar con la vinagreta de lima y ajustar el sabor. Añadir cilantro fresco picado.'),
(127, 7, 5, 'Servir a temperatura ambiente o ligeramente fría. Decorar con semillas de sésamo y gajos de lima.'),
(128, 8, 1, 'Escalfar los huevos: llevar agua con un chorrito de vinagre a 80 °C. Cascar el huevo en un bol y deslizarlo suavemente al agua. Cocer 3 minutos. Reservar en agua fría.'),
(129, 8, 2, 'Dorar la panceta en sartén sin aceite hasta que esté crujiente. Reservar.'),
(130, 8, 3, 'Preparar la vinagreta de mostaza: mezclar mostaza, vinagre de jerez, aceite de oliva, sal y pimienta.'),
(131, 8, 4, 'Disponer las espinacas baby en el plato. Añadir la panceta crujiente caliente por encima para que las espinacas se marchiten ligeramente.'),
(132, 8, 5, 'Colocar el huevo poché encima. Aliñar con la vinagreta de mostaza. Servir inmediatamente.'),
(133, 2, 1, 'Pelar y cortar las patatas en dados o bastones gruesos. Secar bien con papel.'),
(134, 2, 2, 'Freír las patatas en aceite abundante a 150 °C durante 8 minutos para precocinarlas. Escurrir y reservar.'),
(135, 2, 3, 'Preparar la salsa brava: sofreír ajo y cebolla, añadir tomate triturado, pimentón picante y un poco de vinagre. Triturar y colar.'),
(136, 2, 4, 'Dar el segundo golpe de fritura a las patatas en aceite a 180 °C hasta que estén doradas y crujientes. Escurrir bien.'),
(137, 2, 5, 'Salar las patatas y servir inmediatamente con la salsa brava por encima y alioli casero a un lado.'),
(138, 3, 1, 'Cocer el pulpo: congelar previamente 24h para romper las fibras. Descongelar, limpiar y cocer en agua hirviendo sin sal durante 40-45 minutos. Comprobar pinchando con un palillo.'),
(139, 3, 2, 'Cocer las patatas enteras con piel en el agua del pulpo durante 20 minutos. Pelar y cortar en rodajas.'),
(140, 3, 3, 'Cortar el pulpo en rodajas de 1 cm con tijera de cocina.'),
(141, 3, 4, 'Colocar las patatas en el plato de madera como base. Disponer el pulpo encima.'),
(142, 3, 5, 'Aliñar con sal gruesa, pimentón dulce y picante al gusto, y aceite de oliva virgen extra generoso. Servir templado.');

INSERT INTO recetas_ingredientes (id_receta, id_ingrediente, cantidad, unidad, notas) VALUES
(1, 1, 500.000, 'ml', 'Leche caliente'),
(1, 5, 80.000, 'g', 'Mantequilla fría para la bechamel'),
(1, 9, 2.000, 'ud', 'Huevo para rebozar'),
(1, 16, 150.000, 'g', 'Jamón serrano en taquitos finos'),
(1, 36, 100.000, 'g', 'Harina tamizada'),
(1, 37, 200.000, 'g', 'Pan rallado estilo panko'),
(2, 21, 400.000, 'g', 'Tomate pera para salsa brava'),
(2, 22, 60.000, 'g', 'Cebolla'),
(2, 23, 20.000, 'g', 'Ajo'),
(2, 29, 800.000, 'g', 'Patatas medianas'),
(2, 39, 50.000, 'ml', 'Aceite de oliva'),
(3, 22, 80.000, 'g', 'Cebolla'),
(3, 29, 600.000, 'g', 'Patatas para cachelos'),
(3, 39, 60.000, 'ml', 'Aceite de oliva virgen extra'),
(4, 21, 1000.000, 'g', 'Tomates pera maduros'),
(4, 22, 100.000, 'g', 'Cebolla blanca'),
(4, 23, 10.000, 'g', 'Ajo'),
(4, 24, 200.000, 'g', 'Pimiento rojo'),
(4, 37, 60.000, 'g', 'Miga de pan del día anterior'),
(4, 39, 100.000, 'ml', 'Aceite de oliva virgen extra'),
(4, 42, 40.000, 'ml', 'Vinagre de jerez'),
(5, 2, 100.000, 'ml', 'Nata para cocinar'),
(5, 22, 100.000, 'g', 'Cebolla'),
(5, 26, 200.000, 'g', 'Zanahoria'),
(5, 39, 30.000, 'ml', 'Aceite de oliva'),
(5, 41, 500.000, 'ml', 'Caldo de verduras'),
(6, 22, 120.000, 'g', 'Cebolla'),
(6, 23, 15.000, 'g', 'Ajo'),
(6, 26, 150.000, 'g', 'Zanahoria'),
(6, 32, 400.000, 'g', 'Lentejas pardinas secas'),
(6, 41, 800.000, 'ml', 'Caldo de pollo casero'),
(7, 38, 200.000, 'g', 'Quinoa en seco'),
(7, 39, 30.000, 'ml', 'Aceite de oliva virgen extra'),
(7, 42, 20.000, 'ml', 'Zumo de lima'),
(7, 44, 200.000, 'g', 'Mango maduro'),
(8, 9, 4.000, 'ud', 'Huevos para escalfar'),
(8, 15, 100.000, 'g', 'Panceta en tacos'),
(8, 25, 200.000, 'g', 'Espinacas baby frescas'),
(8, 39, 20.000, 'ml', 'Aceite de oliva'),
(9, 11, 600.000, 'g', 'Pechuga y muslos de pollo troceados'),
(9, 21, 400.000, 'g', 'Tomate rallado'),
(9, 24, 200.000, 'g', 'Pimiento rojo'),
(9, 34, 400.000, 'g', 'Arroz bomba D.O. Valencia'),
(9, 39, 80.000, 'ml', 'Aceite de oliva virgen extra'),
(9, 40, 800.000, 'ml', 'Caldo de pollo caliente'),
(10, 3, 80.000, 'g', 'Parmesano Reggiano rallado'),
(10, 5, 60.000, 'g', 'Mantequilla'),
(10, 22, 100.000, 'g', 'Cebolla blanca'),
(10, 34, 320.000, 'g', 'Arroz arborio o carnaroli'),
(10, 41, 900.000, 'ml', 'Caldo de verduras caliente'),
(11, 22, 100.000, 'g', 'Cebolla'),
(11, 23, 20.000, 'g', 'Ajo'),
(11, 24, 150.000, 'g', 'Pimiento rojo'),
(11, 34, 360.000, 'g', 'Arroz bomba'),
(11, 39, 60.000, 'ml', 'Aceite de oliva'),
(12, 3, 80.000, 'g', 'Queso parmesano o pecorino'),
(12, 9, 4.000, 'ud', 'Huevos enteros (2 yemas + 2 enteros)'),
(12, 15, 150.000, 'g', 'Panceta o guanciale'),
(12, 35, 400.000, 'g', 'Pasta larga tipo spaghetti'),
(13, 1, 600.000, 'ml', 'Leche para bechamel'),
(13, 3, 80.000, 'g', 'Parmesano rallado'),
(13, 13, 200.000, 'g', 'Carne de cerdo picada'),
(13, 14, 400.000, 'g', 'Carne de ternera picada'),
(13, 21, 400.000, 'g', 'Tomate triturado'),
(13, 22, 100.000, 'g', 'Cebolla'),
(13, 35, 300.000, 'g', 'Láminas de pasta para lasaña'),
(13, 36, 60.000, 'g', 'Harina para bechamel'),
(14, 3, 60.000, 'g', 'Parmesano rallado'),
(14, 35, 400.000, 'g', 'Pasta trofie o linguine'),
(14, 39, 80.000, 'ml', 'Aceite de oliva virgen extra'),
(14, 49, 40.000, 'g', 'Almendras o piñones tostados'),
(15, 11, 1600.000, 'g', 'Pollo entero troceado'),
(15, 23, 30.000, 'g', 'Ajo'),
(15, 29, 600.000, 'g', 'Patatas para guarnición'),
(15, 39, 60.000, 'ml', 'Aceite de oliva'),
(15, 42, 2.000, 'ud', 'Limones en mitades'),
(16, 2, 150.000, 'ml', 'Nata líquida para la salsa'),
(16, 13, 800.000, 'g', 'Solomillo de cerdo'),
(16, 22, 100.000, 'g', 'Cebolla'),
(16, 39, 30.000, 'ml', 'Aceite de oliva'),
(17, 14, 1200.000, 'g', 'Carrilleras de ternera limpias'),
(17, 22, 200.000, 'g', 'Cebolla'),
(17, 23, 30.000, 'g', 'Ajo'),
(17, 26, 200.000, 'g', 'Zanahoria'),
(17, 29, 400.000, 'g', 'Patatas para puré'),
(17, 40, 400.000, 'ml', 'Caldo de carne'),
(18, 18, 800.000, 'g', 'Lomos de bacalao desalado'),
(18, 23, 40.000, 'g', 'Ajo laminado'),
(18, 39, 200.000, 'ml', 'Aceite de oliva virgen extra'),
(19, 17, 600.000, 'g', 'Lomos de salmón sin piel'),
(19, 34, 300.000, 'g', 'Arroz jazmín'),
(19, 42, 30.000, 'ml', 'Zumo de limón'),
(19, 48, 30.000, 'g', 'Miel para la salsa teriyaki'),
(20, 19, 500.000, 'g', 'Gambas peladas frescas o descongeladas'),
(20, 23, 40.000, 'g', 'Ajo laminado fino'),
(20, 39, 80.000, 'ml', 'Aceite de oliva virgen extra'),
(21, 21, 400.000, 'g', 'Tomate triturado'),
(21, 22, 120.000, 'g', 'Cebolla'),
(21, 23, 20.000, 'g', 'Ajo'),
(21, 25, 200.000, 'g', 'Espinacas frescas'),
(21, 31, 480.000, 'g', 'Garbanzos cocidos (2 botes escurridos)'),
(21, 41, 200.000, 'ml', 'Caldo de verduras'),
(22, 24, 150.000, 'g', 'Pimiento rojo'),
(22, 26, 150.000, 'g', 'Zanahoria'),
(22, 27, 200.000, 'g', 'Calabacín'),
(22, 28, 200.000, 'g', 'Berenjena'),
(22, 39, 40.000, 'ml', 'Aceite de oliva'),
(23, 5, 20.000, 'g', 'Mantequilla'),
(23, 9, 6.000, 'ud', 'Huevos frescos'),
(23, 39, 20.000, 'ml', 'Aceite de oliva'),
(24, 2, 200.000, 'ml', 'Nata 35% materia grasa'),
(24, 7, 900.000, 'g', 'Queso crema tipo Philadelphia'),
(24, 9, 5.000, 'ud', 'Huevos L'),
(24, 36, 30.000, 'g', 'Harina tamizada'),
(24, 47, 200.000, 'g', 'Azúcar blanquilla'),
(25, 5, 30.000, 'g', 'Mantequilla'),
(25, 9, 4.000, 'ud', 'Yemas de huevo'),
(25, 10, 6.000, 'ud', 'Claras de huevo (aprox. 180g)'),
(25, 47, 60.000, 'g', 'Azúcar'),
(26, 1, 100.000, 'ml', 'Leche entera'),
(26, 2, 500.000, 'ml', 'Nata 35% para cocinar'),
(26, 45, 200.000, 'g', 'Fresas para el coulis'),
(26, 47, 60.000, 'g', 'Azúcar'),
(27, 36, 500.000, 'g', 'Harina de fuerza'),
(27, 47, 10.000, 'g', 'Sal marina fina'),
(27, 50, 10.000, 'g', 'Levadura masa madre activa'),
(28, 36, 500.000, 'g', 'Harina 00 o de fuerza'),
(28, 39, 60.000, 'ml', 'Aceite de oliva virgen extra'),
(28, 47, 10.000, 'g', 'Sal en escamas'),
(28, 50, 7.000, 'g', 'Levadura seca de panadero'),
(29, 21, 300.000, 'g', 'Tomates asados'),
(29, 23, 20.000, 'g', 'Ajo asado'),
(29, 39, 80.000, 'ml', 'Aceite de oliva virgen extra'),
(29, 49, 100.000, 'g', 'Almendras tostadas'),
(30, 39, 100.000, 'ml', 'Aceite de oliva virgen extra de alta calidad'),
(30, 41, 500.000, 'ml', 'Agua para baño de cloruro cálcico'),
(30, 47, 2.000, 'g', 'Alginato sódico');

INSERT INTO favoritos (id_usuario, id_receta, fecha_adicion) VALUES
(1, 1, '2023-11-01 09:00:00'), (1, 9, '2023-10-15 12:30:00'), (1, 24, '2024-01-10 18:45:00'),
(2, 4, '2023-08-20 14:00:00'), (2, 20, '2023-09-05 11:20:00'), (2, 26, '2023-10-30 20:00:00'),
(3, 9, '2023-10-20 13:00:00'), (3, 17, '2024-02-14 21:00:00'), (3, 18, '2023-11-15 19:30:00'),
(4, 7, '2024-01-05 10:00:00'), (4, 21, '2024-01-05 10:05:00'), (4, 22, '2024-02-20 16:00:00'),
(5, 24, '2023-12-20 11:00:00'), (5, 25, '2023-12-20 11:05:00'), (5, 26, '2024-01-15 09:30:00'),
(6, 4, '2023-07-10 08:00:00'), (6, 12, '2023-09-12 19:00:00'), (6, 14, '2023-10-01 12:30:00'),
(7, 15, '2023-11-25 13:00:00'), (7, 16, '2024-01-08 20:00:00'),
(8, 10, '2023-12-05 17:00:00'), (8, 30, '2024-03-01 15:00:00'),
(9, 2, '2024-02-10 12:00:00'), (9, 3, '2024-02-10 12:10:00'),
(10, 6, '2024-03-15 10:00:00'), (10, 27, '2024-03-20 09:00:00'),
(11, 21, '2024-01-30 11:00:00'), (11, 22, '2024-01-30 11:10:00'),
(12, 9, '2024-04-01 14:00:00'), (12, 13, '2024-04-05 19:00:00'),
(13, 24, '2024-02-25 16:00:00'), (13, 25, '2024-03-10 20:30:00'),
(14, 8, '2024-04-08 11:00:00'),
(15, 9, '2024-04-15 13:00:00'), (15, 29, '2024-04-15 13:15:00'), (15, 30, '2024-04-20 10:00:00');

INSERT INTO usuarios_login (id_usuario, id_empleado, username, password_hash, activo) VALUES
(1, 1, 'carlos.romero', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1),
(2, 2, 'laura.martinez', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1),
(3, 3, 'sergio.fuentes', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1),
(4, 4, 'ana.lopez', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1),
(5, 5, 'miguel.torres', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1),
(6, 6, 'elena.sanchez', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1),
(7, 7, 'pablo.navarro', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1),
(8, 15, 'adrian.cano', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1),
(9, 19, 'inaki.arrizabalaga', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1),
(10, 20, 'marta.delgado', '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy', 1);


DELIMITER $$

CREATE TRIGGER trg_validar_contrato BEFORE INSERT ON contratos FOR EACH ROW
BEGIN
    DECLARE t_activo INT(1);

    SELECT activo INTO t_activo
    FROM empleados
    WHERE id_empleado = NEW.id_empleado;

    IF t_activo = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se puede crear un contrato para un empleado inactivo.';
    END IF;
END$$

CREATE TRIGGER trg_empleado_login AFTER INSERT ON empleados FOR EACH ROW
BEGIN
    IF NEW.puesto = 'docente' OR NEW.puesto = 'cocinero' THEN
        INSERT INTO usuarios_login (id_empleado, username, password_hash, activo)
        VALUES (
            NEW.id_empleado,
            fn_generar_username(NEW.id_empleado),
            '$2b$12$O0/T11gn0jVPP60DBuIHWeQiqEPi7nx8JvWvUyeW21/AvFWJZ.nWy',
            1
        );
    END IF;
END$$

DELIMITER ;


ALTER TABLE contratos ADD CONSTRAINT fk_contratos_empleado FOREIGN KEY (id_empleado) REFERENCES empleados (id_empleado) ON UPDATE CASCADE;
ALTER TABLE favoritos ADD CONSTRAINT fk_favoritos_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE favoritos ADD CONSTRAINT fk_favoritos_receta FOREIGN KEY (id_receta) REFERENCES recetas (id_receta) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE ingredientes_alergenos ADD CONSTRAINT fk_ing_alerg_ingrediente FOREIGN KEY (id_ingrediente) REFERENCES ingredientes (id_ingrediente) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE ingredientes_alergenos ADD CONSTRAINT fk_ing_alerg_alergeno FOREIGN KEY (id_alergeno) REFERENCES alergenos (id_alergeno) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE menus ADD CONSTRAINT fk_menus_creador FOREIGN KEY (id_creador) REFERENCES empleados (id_empleado) ON UPDATE CASCADE;
ALTER TABLE menus_recetas ADD CONSTRAINT fk_menus_recetas_menu FOREIGN KEY (id_menu) REFERENCES menus (id_menu) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE menus_recetas ADD CONSTRAINT fk_menus_recetas_receta FOREIGN KEY (id_receta) REFERENCES recetas (id_receta) ON UPDATE CASCADE;
ALTER TABLE pasos_receta ADD CONSTRAINT fk_pasos_receta FOREIGN KEY (id_receta) REFERENCES recetas (id_receta) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE recetas ADD CONSTRAINT fk_recetas_categoria FOREIGN KEY (id_categoria) REFERENCES categorias_receta (id_categoria) ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE recetas ADD CONSTRAINT fk_recetas_creador FOREIGN KEY (id_creador) REFERENCES empleados (id_empleado) ON UPDATE CASCADE;
ALTER TABLE recetas_ingredientes ADD CONSTRAINT fk_rec_ing_receta FOREIGN KEY (id_receta) REFERENCES recetas (id_receta) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE recetas_ingredientes ADD CONSTRAINT fk_rec_ing_ingrediente FOREIGN KEY (id_ingrediente) REFERENCES ingredientes (id_ingrediente) ON UPDATE CASCADE;
ALTER TABLE usuarios_login ADD CONSTRAINT fk_login_empleado FOREIGN KEY (id_empleado) REFERENCES empleados (id_empleado) ON DELETE CASCADE ON UPDATE CASCADE;


CREATE VIEW vista_nutricion_receta AS
SELECT
    r.id_receta,
    r.nombre,
    r.raciones,
    ROUND(SUM((i.calorias_100g      * ri.cantidad) / 100) / NULLIF(r.raciones, 0), 2) AS calorias_por_racion,
    ROUND(SUM((i.proteinas_100g     * ri.cantidad) / 100) / NULLIF(r.raciones, 0), 2) AS proteinas_por_racion,
    ROUND(SUM((i.carbohidratos_100g * ri.cantidad) / 100) / NULLIF(r.raciones, 0), 2) AS carbohidratos_por_racion,
    ROUND(SUM((i.grasas_100g        * ri.cantidad) / 100) / NULLIF(r.raciones, 0), 2) AS grasas_por_racion,
    ROUND(SUM((i.fibra_100g         * ri.cantidad) / 100) / NULLIF(r.raciones, 0), 2) AS fibra_por_racion,
    ROUND(SUM((i.sodio_100g         * ri.cantidad) / 100) / NULLIF(r.raciones, 0), 2) AS sodio_por_racion,
    GROUP_CONCAT(DISTINCT a.nombre ORDER BY a.nombre SEPARATOR ', ') AS alergenos
FROM recetas r
JOIN recetas_ingredientes ri ON r.id_receta = ri.id_receta
JOIN ingredientes i ON ri.id_ingrediente = i.id_ingrediente
LEFT JOIN ingredientes_alergenos ia ON i.id_ingrediente = ia.id_ingrediente
LEFT JOIN alergenos a ON ia.id_alergeno = a.id_alergeno
GROUP BY r.id_receta, r.nombre, r.raciones;