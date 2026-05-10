# GastroApp

GastroApp es un sistema completo de administración gastronómica creado para centralizar todas las operaciones de una escuela de cocina. Integra una potente base de datos relacional con dos aplicaciones web diferenciadas: un portal público para consultar recetas y un panel interno de gestión, ofreciendo una solución integral tanto para el personal como para los usuarios externos.

---

## 🗂️ Descripción del proyecto

El repositorio se organiza en dos módulos principales y los ficheros de base de datos necesarios para desplegarlos:

- **`GastroApp/`** – Aplicación web pública (Flask)
- **`GastroManagment/`** – Panel de administración interna (Flask)
- **`gastrolab.sql`** – Volcado completo de la base de datos MySQL
- **`RolesUsuarios.sql`** – Definición de roles y permisos para la base de datos

La base de datos, denominada **Gastrolab**, unifica el recetario, la información nutricional, la planificación de menús y la gestión de personal en un solo lugar.

---

## 🚀 Funcionalidades principales

### GastroApp (portal público)

- Página de inicio con buscador y listado de recetas
- Vista detallada de cada receta (ingredientes, pasos, tiempo, dificultad)
- Página "Sobre nosotros" con información del proyecto

### GastroManagment (panel de administración)

- Sistema de autenticación con sesiones y contraseñas hasheadas (bcrypt)
- Dashboard con tarjetas de acceso rápido a ingredientes recientes y empleados nuevos
- Listado de recetas paginado con filtros por categoría y dificultad
- Vista detallada de cada receta: pasos, ingredientes, alérgenos e información nutricional
- Formulario para insertar nuevas recetas completas (ingredientes, cantidades, pasos)
- Gestión de ingredientes, empleados y contratos

---

## 🛠️ Tecnologías utilizadas

| Capa | Tecnología |
|---|---|
| Backend | Python 3, Flask |
| Base de datos | MySQL 8.0 |
| Frontend | HTML5, CSS3 (variables CSS, grid, flexbox) |
| Librerías | `mysql-connector-python`, `bcrypt`, `pytest` |
| Herramientas | Git, GitHub |

---

## 📁 Estructura del proyecto y partes de cada colaborador

```
GastroApp/
├── GastroApp/                    # Aplicación web pública
│   ├── static/
│   │   ├── img/                  # Mikel V.
│   │   └── style.css             # Jon M.
│   ├── templates/
│   │   ├── index.html            # Jon M.
│   │   └── nosotros.html         # Mikel V.
│   ├── app.py                    # Jon M.
│   ├── test.py                   # Jon M.
|
├── GastroManagment/              # Panel de administración
│   ├── static/                   # Aaron B.
│   ├── templates/                # Joseba L.
│   ├── app.py                    # Aaron B.
│   ├── db.py                     # Joseba L.
│   ├── README.md                 
|
├── gastrolab.sql                 
└── RolesUsuarios.sql             
```

---

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/Joseba19/GastroApp.git
cd GastroApp
```

### 2. Configurar la base de datos

El volcado completo se encuentra en `gastrolab.sql`. Ejecútalo en tu servidor MySQL:

```bash
mysql -u root -p < gastrolab.sql
```

Posteriormente, carga los roles y usuarios:

```bash
mysql -u root -p < RolesUsuarios.sql
```

### 3. Configurar las credenciales de conexión

Edita los archivos de configuración en ambas aplicaciones:

- En `GastroApp/app.py` (línea 4)
- En `GastroManagment/db.py` (líneas 4-6)

Ajusta `host`, `user`, `password` y `database` según tu entorno.

### 4. Instalar dependencias

```bash
pip install flask mysql-connector-python bcrypt pytest
```

### 5. Ejecutar las aplicaciones

**Portal público:**

```bash
cd GastroApp
python app.py
```

**Panel de administración:**

```bash
cd GastroManagment
python app.py
```
