# UrbanWear

## Sistema E-commerce y Panel Administrativo para Tienda de Ropa Urbana

---

## Descripción

UrbanWear es un sistema web e-commerce desarrollado para la gestión y comercialización de ropa urbana oversize.

El proyecto combina:

- Tienda online moderna
- Carrito de compras funcional
- Checkout simulado
- Control automático de stock
- Panel administrativo con dashboard
- Base de datos PostgreSQL

Está diseñado con una arquitectura híbrida preparada para futuras integraciones como pasarelas de pago y automatización empresarial.

---

## Características Principales

### Parte Pública (Clientes)

- Catálogo de productos
- Filtros por categoría
- Vista detallada del producto
- Carrito dinámico
- Checkout simulado
- Registro e inicio de sesión
- Historial de pedidos

---

### Panel Administrativo

- Dashboard con métricas clave
- Gestión de productos (CRUD)
- Gestión de categorías
- Gestión de pedidos
- Gestión de clientes
- Control automático de inventario

---

## Arquitectura

Arquitectura híbrida:

Frontend (Templates + JS)
↓
Flask (renderizado + API interna)
↓
PostgreSQL

- Las vistas públicas se renderizan con Flask.
- Los datos dinámicos se consumen desde endpoints `/api/`.
- La lógica de negocio se maneja en servicios.
- La base de datos está estructurada con modelo relacional.

---

## Tecnologías Utilizadas

- Python
- Flask
- PostgreSQL
- SQLAlchemy
- HTML5
- CSS3
- JavaScript (Fetch API)
- Chart.js
- Git & GitHub

---

## Modelo de Base de Datos

Tablas principales:

- users
- categories
- products
- carts
- cart_items
- orders
- order_items

Diseñado para escalabilidad y automatización futura.

---

## Estructura del Proyecto

sistema-ventas/
│
├── backend/
│ ├── models/
│ ├── routes/
│ ├── services/
│
├── frontend/
│ ├── templates/
│ ├── static/
│
├── database/
│
├── README.md
└── requirements.txt

---

## Equipo de Desarrollo

- Backend Developer – Arquitectura, lógica de negocio y base de datos.
- Frontend Developer – Experiencia visual, catálogo, carrito y dashboard.

---

## Estado del Proyecto

En desarrollo activo – Fase 1:

- Estructura base
- Modelado de base de datos
- Implementación módulo productos

---

## Objetivo Profesional

Este proyecto está diseñado como pieza principal de portafolio para:

- Aplicaciones a proyectos en Workana
- Desarrollo de e-commerce personalizados
- Sistemas administrativos empresariales
- Automatización e integración futura con APIs externas
