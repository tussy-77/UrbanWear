-- ============================
-- CATEGORÍAS
-- ============================

INSERT INTO categories (name) VALUES
('Oversize'),
('Hoodies'),
('Camisetas'),
('Pantalones');

-- ============================
-- PRODUCTOS
-- ============================

INSERT INTO products (name, description, price, stock, image_url, category_id)
VALUES
('Camiseta Oversize Negra', 'Camiseta urbana corte amplio', 95000, 20, '/static/images/oversize1.jpg', 1),
('Hoodie Street Gris', 'Hoodie urbano con capucha', 180000, 15, '/static/images/hoodie1.jpg', 2),
('Camiseta Oversize Blanca', 'Camiseta básica oversize', 90000, 25, '/static/images/oversize2.jpg', 1),
('Pantalón Cargo Urbano', 'Pantalón cargo estilo streetwear', 160000, 10, '/static/images/pantalon1.jpg', 4);

-- ============================
-- USUARIO ADMIN
-- ============================

INSERT INTO users (name, email, password_hash, role)
VALUES ('Admin UrbanWear', 'admin@urbanwear.com', 'hashed_password_placeholder', 'admin');