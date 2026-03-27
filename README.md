# UrbanWear

### Sistema E-commerce y Panel Administrativo para Tienda de Ropa Urbana

---

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Arquitectura](#arquitectura)
- [Stack Tecnológico](#stack-tecnológico)
- [Modelo de Base de Datos](#modelo-de-base-de-datos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Primeros Pasos](#primeros-pasos)
- [Estado del Proyecto](#estado-del-proyecto)
- [Objetivo Profesional](#objetivo-profesional)

---

## Descripción

**UrbanWear** es un sistema web e-commerce desarrollado para la gestión y comercialización de ropa urbana oversize. El proyecto combina una tienda online moderna con un panel administrativo completo, control automático de stock y una arquitectura preparada para futuras integraciones como pasarelas de pago y automatización empresarial.

---

## Características

### Tienda Pública (Clientes)

| Módulo                   | Descripción                                                           |
| ------------------------ | --------------------------------------------------------------------- |
| **Home**                 | Hero banner, sección New In, banners HOMBRE/MUJER y editorial         |
| **Catálogo**             | Tabs HOMBRE / MUJER / TODOS con filtrado cliente sin recarga          |
| **Detalle de producto**  | Vista completa con descripción, tallas, stock e imagen                |
| **Carrito dinámico**     | Agregar, modificar y eliminar ítems sin recargar                      |
| **Checkout**             | Flujo completo: identificación → envío → pago → confirmación          |
| **Autenticación**        | Registro, inicio de sesión y Google OAuth                             |
| **Perfil**               | Datos editables y contraseña                                          |
| **Historial de pedidos** | Seguimiento de órdenes por usuario                                    |

### Panel Administrativo

| Módulo               | Descripción                                                             |
| -------------------- | ----------------------------------------------------------------------- |
| **Dashboard**        | Métricas clave, gráficas de ventas mensuales (Chart.js) y top productos |
| **Productos (CRUD)** | Crear, editar, eliminar; campo género (hombre/mujer/unisex) y destacado |
| **Pedidos**          | Visualización y actualización de estado de órdenes                      |
| **Clientes**         | Consulta y administración de usuarios registrados                       |
| **Editorial**        | Editar hero, banner lookbook y banners HOMBRE/MUJER con imagen y texto  |

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
         SQLAlchemy ORM
              ↓
         PostgreSQL
```

- Las **vistas públicas** se renderizan con Flask + Jinja2 (SSR).
- Los **datos dinámicos** (carrito, stock, dashboard) se consumen via `fetch()` desde endpoints `/api/`.
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
| OAuth                | Authlib (Google OAuth2)   | Latest            |
| Plantillas           | Jinja2                    | Incluido en Flask |
| Frontend             | HTML5 + CSS3 + JavaScript | —                 |
| API interna          | Fetch API (nativa)        | —                 |
| Gráficas             | Chart.js                  | 4.4               |
| Control de versiones | Git & GitHub              | —                 |

---

## Modelo de Base de Datos

```
users
  └── orders ──── order_items ──── products ──── categories
                                      └── (gender, destacado)
carts
  └── cart_items ──── products

banners  (hero | editorial | categoria_hombre | categoria_mujer)
```

**Tablas principales:**

| Tabla         | Descripción                                                        |
| ------------- | ------------------------------------------------------------------ |
| `users`       | Clientes y administradores del sistema                             |
| `categories`  | Categorías de productos (Oversize, Hoodies, etc.)                  |
| `products`    | Catálogo con precio, stock, género y flag de destacado             |
| `banners`     | Banners editables por posición (hero, editorial, hombre, mujer)    |
| `carts`       | Carritos activos por usuario                                       |
| `cart_items`  | Productos y cantidades dentro de un carrito                        |
| `orders`      | Órdenes de compra con estado y total                               |
| `order_items` | Detalle de productos por orden                                     |

---

## Estructura del Proyecto

```
sistema-ventas/
│
├── backend/
│   ├── app.py              # Application factory + todas las rutas
│   ├── database.py         # Instancia SQLAlchemy
│   └── models/
│       ├── user.py
│       ├── product.py
│       ├── banner.py
│       ├── order.py
│       └── cart.py
│
├── frontend/
│   ├── templates/
│   │   ├── public/         # home, catalogo, producto, checkout, perfil...
│   │   └── admin/          # dashboard, products, orders, editorial...
│   └── static/
│       ├── css/
│       ├── js/
│       └── uploads/        # Imágenes subidas desde el admin
│
├── migrations/             # Migraciones Alembic (Flask-Migrate)
├── instance/               # Configuración local (no versionada)
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
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
   git clone https://github.com/tussy-77/sistema-ventas.git
   cd sistema-ventas
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

5. **Aplica migraciones**

   ```bash
   flask db upgrade
   ```

6. **Inicia la aplicación**

   ```bash
   python run.py
   ```

   Accede en → `http://127.0.0.1:5000`

### Variables de Entorno

```env
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta
DATABASE_URL=postgresql://usuario:password@localhost:5432/urbanwear
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

> Nunca versiones tu `.env`. Verifica que esté incluido en `.gitignore`.

---

## Estado del Proyecto

**Fase 1 — En desarrollo activo**

- [x] Arquitectura base del proyecto
- [x] Modelado y migraciones de base de datos
- [x] Autenticación de clientes (registro, login, Google OAuth)
- [x] Módulo de productos (CRUD completo + género + destacado)
- [x] Catálogo público con tabs HOMBRE / MUJER / TODOS
- [x] Carrito dinámico con Fetch API
- [x] Checkout completo paso a paso
- [x] Historial de pedidos por usuario
- [x] Perfil de usuario editable
- [x] Dashboard administrativo con gráficas Chart.js
- [x] Panel editorial: hero, lookbook y banners de categoría editables
- [ ] Control automático de inventario al procesar pedidos
- [ ] Integración con pasarela de pago (MercadoPago / Stripe)
- [ ] Notificaciones por email al confirmar pedido

---

## Objetivo Profesional

Este proyecto está diseñado como **pieza principal de portafolio** para demostrar capacidad técnica en:

- Desarrollo de e-commerce personalizados con Python/Flask
- Sistemas administrativos empresariales con dashboard
- Arquitecturas híbridas SSR + API interna
- Modelado relacional con PostgreSQL y SQLAlchemy
- Integración de OAuth y autenticación segura
- Automatización e integración futura con APIs externas (Stripe, MercadoPago, etc.)

> Diseñado para pequeñas tiendas de ropa que necesitan gestionar su catálogo, ventas e inventario desde una sola plataforma.

---
