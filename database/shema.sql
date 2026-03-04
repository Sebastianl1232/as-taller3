-- TODO: Definir las tablas del sistema

-- Tabla de usuarios
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla de productos  
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    image_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla de carritos
CREATE TABLE carts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla de items del carrito
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (cart_id, product_id)
);

-- TODO: Agregar índices y restricciones de clave foránea
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_carts_user_id ON carts(user_id);
CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);

-- TODO: Insertar datos de prueba
INSERT INTO users (username, email, password_hash)
VALUES
    ('juanperez', 'juan@tienda.com', 'hash_demo_juan'),
    ('mariagarcia', 'maria@tienda.com', 'hash_demo_maria');

INSERT INTO products (name, description, price, stock, image_url)
VALUES
    ('Laptop Gamer', 'Laptop de alto rendimiento para juegos', 4500000.00, 8, 'https://example.com/images/laptop-gamer.jpg'),
    ('Mouse Inalambrico', 'Mouse ergonomico con conexion Bluetooth', 85000.00, 30, 'https://example.com/images/mouse.jpg'),
    ('Teclado Mecanico', 'Teclado mecanico RGB con switches azules', 210000.00, 20, 'https://example.com/images/teclado.jpg');

INSERT INTO carts (user_id)
SELECT id FROM users WHERE email = 'juan@tienda.com';

INSERT INTO cart_items (cart_id, product_id, quantity)
SELECT c.id, p.id, 1
FROM carts c
JOIN users u ON u.id = c.user_id
JOIN products p ON p.name = 'Mouse Inalambrico'
WHERE u.email = 'juan@tienda.com';