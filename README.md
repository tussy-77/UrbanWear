# UrbanWear

### Sistema E-commerce y Panel Administrativo para Tienda de Ropa Urbana

---

## Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Stack Tecnológico](#-stack-tecnológico)
- [Modelo de Base de Datos](#-modelo-de-base-de-datos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Primeros Pasos](#-primeros-pasos)
- [Estado del Proyecto](#-estado-del-proyecto)
- [Objetivo Profesional](#-objetivo-profesional)
- [Equipo](#-equipo)

---

## Descripción

**UrbanWear** es un sistema web e-commerce desarrollado para la gestión y comercialización de ropa urbana oversize. El proyecto combina una tienda online moderna con un panel administrativo completo, control automático de stock y una arquitectura preparada para futuras integraciones como pasarelas de pago y automatización empresarial.

---

## Características

### Tienda Pública (Clientes)

| Módulo                   | Descripción                                      |
| ------------------------ | ------------------------------------------------ |
| **Catálogo**             | Exploración de productos con imágenes y precios  |
| **Filtros**              | Búsqueda y filtrado por categoría                |
| **Detalle de producto**  | Vista completa con descripción, talla y stock    |
| **Carrito dinámico**     | Agregar, modificar y eliminar ítems sin recargar |
| **Checkout simulado**    | Flujo de compra completo paso a paso             |
| **Autenticación**        | Registro e inicio de sesión de clientes          |
| **Historial de pedidos** | Seguimiento de órdenes por usuario               |

### Panel Administrativo

| Módulo               | Descripción                                        |
| -------------------- | -------------------------------------------------- |
| **Dashboard**        | Métricas clave: ventas, stock, pedidos recientes   |
| **Productos (CRUD)** | Crear, editar, archivar y eliminar productos       |
| **Categorías**       | Gestión completa de categorías                     |
| **Pedidos**          | Visualización y actualización de estado de órdenes |
| **Clientes**         | Consulta y administración de usuarios registrados  |
| **Inventario**       | Control automático de stock al procesar pedidos    |

---

## Arquitectura

UrbanWear usa una **arquitectura híbrida** que combina renderizado por servidor con endpoints de API interna:

```
Frontend (Templates Jinja2 + JavaScript)
              ↓
     Flask — Renderizado SSR
              ↓
     Endpoints internos /api/
              ↓
  Capa de Servicios (lógica de negocio)
              ↓
     SQLAlchemy ORM
              ↓
         PostgreSQL
```

- Las **vistas públicas** se renderizan con Flask + Jinja2 (SSR).
- Los **datos dinámicos** (carrito, stock, dashboard) se consumen via `fetch()` desde endpoints `/api/`.
- La **lógica de negocio** está desacoplada en servicios reutilizables.
- La **base de datos** sigue un modelo relacional normalizado, diseñado para escalar.

---

## Stack Tecnológico

| Capa                 | Tecnología                | Versión           |
| -------------------- | ------------------------- | ----------------- |
| Lenguaje             | Python                    | 3.12              |
| Framework web        | Flask                     | 3.1               |
| Base de datos        | PostgreSQL                | 17                |
| ORM                  | SQLAlchemy                | 2.0               |
| Migraciones          | Flask-Migrate (Alembic)   | Latest            |
| Autenticación        | Flask-Login + Bcrypt      | Latest            |
| Plantillas           | Jinja2                    | Incluido en Flask |
| Frontend             | HTML5 + CSS3 + JavaScript | —                 |
| API interna          | Fetch API (nativa)        | —                 |
| Gráficas             | Chart.js                  | 4.x               |
| Control de versiones | Git & GitHub              | —                 |

---

## Modelo de Base de Datos

El esquema relacional está diseñado para escalabilidad y automatización futura:

```
users
  └── orders ──── order_items ──── products
                                      └── categories
carts
  └── cart_items ──── products
```

**Tablas principales:**

| Tabla         | Descripción                                       |
| ------------- | ------------------------------------------------- |
| `users`       | Clientes y administradores del sistema            |
| `categories`  | Categorías de productos (Oversize, Hoodies, etc.) |
| `products`    | Catálogo con precio, stock y estado               |
| `carts`       | Carritos activos por usuario                      |
| `cart_items`  | Productos y cantidades dentro de un carrito       |
| `orders`      | Órdenes de compra con estado y total              |
| `order_items` | Detalle de productos por orden                    |

---

## Estructura del Proyecto

```
urbanwear/
│
├── backend/
│   ├── models/             # Modelos SQLAlchemy (User, Product, Order...)
│   ├── routes/             # Blueprints Flask: public, admin, api
│   └── services/           # Lógica de negocio (inventario, pedidos...)
│
├── frontend/
│   ├── templates/          # Plantillas Jinja2 por módulo
│   └── static/
│       ├── css/            # Estilos globales y por módulo
│       ├── js/             # Scripts con Fetch API
│       └── img/            # Assets e imágenes de productos
│
├── database/
│   ├── schema.sql          # DDL — estructura de tablas
│   └── seed.sql            # DML — datos iniciales de prueba
│
├── migrations/             # Migraciones Alembic (Flask-Migrate)
├── instance/               # Configuración local (no versionada)
├── .env.example            # Variables de entorno requeridas
├── .gitignore
├── requirements.txt
├── run.py                  # Punto de entrada
└── README.md
```

---

## Primeros Pasos

### Prerrequisitos

- Python **3.12** o superior
- PostgreSQL **17** corriendo localmente
- `pip` y `venv`
- Git

### Instalación

1. **Clona el repositorio**

   ```bash
   git clone https://github.com/tu-usuario/urbanwear.git
   cd urbanwear
   ```

2. **Crea y activa el entorno virtual**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Instala dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configura variables de entorno**

   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales de PostgreSQL y demás valores
   ```

5. **Crea la base de datos y aplica migraciones**

   ```bash
   flask db upgrade
   ```

6. **Carga datos de prueba** _(opcional)_

   ```bash
   psql -U tu_usuario -d urbanwear -f database/seed.sql
   ```

7. **Inicia la aplicación**

   ```bash
   python run.py
   ```

   Accede en → `http://127.0.0.1:5000`

### Variables de Entorno

```env
# Flask
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta

# PostgreSQL
DATABASE_URL=postgresql://usuario:password@localhost:5432/urbanwear

# Admin por defecto
ADMIN_EMAIL=admin@urbanwear.com
ADMIN_PASSWORD=tu_password_seguro
```

> Nunca versiones tu `.env`. Verifica que esté incluido en `.gitignore`.

---

## 📊 Estado del Proyecto

**Fase 1 — En desarrollo activo**

- [x] Arquitectura base del proyecto
- [x] Modelado y migraciones de base de datos
- [x] Módulo de productos (CRUD completo)
- [x] Catálogo público con filtros por categoría
- [x] Carrito dinámico con Fetch API
- [ ] Checkout y generación de órdenes
- [ ] Dashboard administrativo con Chart.js
- [ ] Control automático de inventario
- [ ] Autenticación de clientes y administradores
- [ ] Historial de pedidos por usuario

---

## Objetivo Profesional

Este proyecto está diseñado como **pieza principal de portafolio** para demostrar capacidad técnica en:

- Desarrollo de e-commerce personalizados con Python/Flask
- Sistemas administrativos empresariales con dashboard
- Arquitecturas híbridas SSR + API interna
- Modelado relacional con PostgreSQL y SQLAlchemy
- Automatización e integración futura con APIs externas (Stripe, MercadoPago, etc.)

> Orientado a aplicaciones en **Workana**, proyectos freelance y desarrollo de sistemas a medida.

---

## 👥 Equipo

| Rol                    | Responsabilidad                                                  |
| ---------------------- | ---------------------------------------------------------------- |
| **Backend Developer**  | Arquitectura, lógica de negocio, base de datos y endpoints API   |
| **Frontend Developer** | Experiencia visual, catálogo, carrito y dashboard administrativo |

---

## 📄 Licencia

Distribuido bajo la licencia MIT. Ver [`LICENSE`](./LICENSE) para más información.

---
