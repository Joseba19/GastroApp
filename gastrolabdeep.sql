DROP DATABASE IF EXISTS `gastrolab`;
CREATE DATABASE `gastrolab`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE `gastrolab`;

-- Tablas maestras
CREATE TABLE `alergenos` (
  `id_alergeno` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  PRIMARY KEY (`id_alergeno`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `categorias_receta` (
  `id_categoria` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `empleados` (
  `id_empleado` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellidos` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `puesto` enum('cocinero','docente','apoyo','alumno_cocina','alumno_dietetica') NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_alta` date NOT NULL,
  PRIMARY KEY (`id_empleado`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `ingredientes` (
  `id_ingrediente` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `unidad_medida` varchar(50) NOT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `calorias_100g` decimal(7,2) DEFAULT NULL,
  `proteinas_100g` decimal(6,2) DEFAULT NULL,
  `carbohidratos_100g` decimal(6,2) DEFAULT NULL,
  `grasas_100g` decimal(6,2) DEFAULT NULL,
  `fibra_100g` decimal(6,2) DEFAULT NULL,
  `sodio_100g` decimal(7,2) DEFAULT NULL,
  PRIMARY KEY (`id_ingrediente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tablas con dependencias de primer nivel
CREATE TABLE `recetas` (
  `id_receta` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text,
  `tiempo_preparacion` int DEFAULT NULL,
  `tiempo_coccion` int DEFAULT NULL,
  `raciones` int DEFAULT NULL,
  `dificultad` enum('facil','medio','dificil') DEFAULT NULL,
  `id_categoria` int DEFAULT NULL,
  `id_creador` int NOT NULL,
  `fecha_creacion` date NOT NULL,
  PRIMARY KEY (`id_receta`),
  KEY `id_categoria` (`id_categoria`),
  KEY `id_creador` (`id_creador`),
  CONSTRAINT `Recetas_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categorias_receta` (`id_categoria`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `Recetas_ibfk_2` FOREIGN KEY (`id_creador`) REFERENCES `empleados` (`id_empleado`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `menus` (
  `id_menu` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text,
  `tipo` enum('diario','semanal','especial') NOT NULL,
  `id_creador` int NOT NULL,
  `fecha_creacion` date NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_menu`),
  KEY `id_creador` (`id_creador`),
  CONSTRAINT `Menus_ibfk_1` FOREIGN KEY (`id_creador`) REFERENCES `empleados` (`id_empleado`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `contratos` (
  `id_contrato` int NOT NULL AUTO_INCREMENT,
  `id_empleado` int NOT NULL,
  `tipo_contrato` varchar(100) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date DEFAULT NULL,
  `horas_semanales` decimal(5,2) NOT NULL,
  `salario_bruto_anual` decimal(10,2) NOT NULL,
  `salario_neto` decimal(10,2) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_contrato`),
  KEY `id_empleado` (`id_empleado`),
  CONSTRAINT `Contratos_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tablas de relación y detalle
CREATE TABLE `ingredientes_alergenos` (
  `id_ingrediente` int NOT NULL,
  `id_alergeno` int NOT NULL,
  PRIMARY KEY (`id_ingrediente`,`id_alergeno`),
  KEY `id_alergeno` (`id_alergeno`),
  CONSTRAINT `Ingredientes_Alergenos_ibfk_1` FOREIGN KEY (`id_ingrediente`) REFERENCES `ingredientes` (`id_ingrediente`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Ingredientes_Alergenos_ibfk_2` FOREIGN KEY (`id_alergeno`) REFERENCES `alergenos` (`id_alergeno`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `recetas_ingredientes` (
  `id_receta` int NOT NULL,
  `id_ingrediente` int NOT NULL,
  `cantidad` decimal(8,3) NOT NULL,
  `unidad` varchar(50) NOT NULL,
  `notas` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_receta`,`id_ingrediente`),
  KEY `id_ingrediente` (`id_ingrediente`),
  CONSTRAINT `Recetas_Ingredientes_ibfk_1` FOREIGN KEY (`id_receta`) REFERENCES `recetas` (`id_receta`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Recetas_Ingredientes_ibfk_2` FOREIGN KEY (`id_ingrediente`) REFERENCES `ingredientes` (`id_ingrediente`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `pasos_receta` (
  `id_paso` int NOT NULL AUTO_INCREMENT,
  `id_receta` int NOT NULL,
  `numero_paso` int NOT NULL,
  `descripcion` text NOT NULL,
  PRIMARY KEY (`id_paso`),
  UNIQUE KEY `id_receta_paso` (`id_receta`,`numero_paso`),
  CONSTRAINT `Pasos_Receta_ibfk_1` FOREIGN KEY (`id_receta`) REFERENCES `recetas` (`id_receta`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `menus_recetas` (
  `id_menu` int NOT NULL,
  `id_receta` int NOT NULL,
  `tipo_plato` enum('entrante','principal','postre','bebida') NOT NULL,
  `orden` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id_menu`,`id_receta`),
  KEY `id_receta` (`id_receta`),
  CONSTRAINT `Menus_Recetas_ibfk_1` FOREIGN KEY (`id_menu`) REFERENCES `menus` (`id_menu`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Menus_Recetas_ibfk_2` FOREIGN KEY (`id_receta`) REFERENCES `recetas` (`id_receta`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `favoritos` (
  `id_usuario` int NOT NULL,
  `id_receta` int NOT NULL,
  `fecha_adicion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_usuario`, `id_receta`),
  KEY `id_receta` (`id_receta`),
  CONSTRAINT `favoritos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `favoritos_ibfk_2` FOREIGN KEY (`id_receta`) REFERENCES `recetas` (`id_receta`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;