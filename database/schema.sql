-- Database Schema for Food Delivery Website

-- 1. Users Table
-- Stores customer and admin information
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Never store plain text passwords!
    is_admin BOOLEAN DEFAULT FALSE,      -- TRUE for admin, FALSE for regular customers
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Menu Items Table
-- Stores the food items available for order
CREATE TABLE IF NOT EXISTS menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,       -- DECIMAL is best for currency
    image_url VARCHAR(255),              -- URL or path to the food image
    is_available BOOLEAN DEFAULT TRUE,   -- Allows admins to hide items without deleting
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Orders Table
-- Stores the summary of a user's order
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status ENUM('Order Placed', 'Preparing', 'Out for Delivery', 'Delivered') DEFAULT 'Order Placed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Order Items Table
-- Stores the individual items within a specific order
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price_at_purchase DECIMAL(10, 2) NOT NULL, -- Stores the price of the item AT THE TIME of the order
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_items(id) ON DELETE RESTRICT
);


-- Default menu items for demo
INSERT IGNORE INTO menu_items (id, name, description, price, image_url) VALUES
(1, 'Classic Burger', 'Juicy beef patty with fresh lettuce, tomatoes, and our secret sauce.', 8.99, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd'),
(2, 'Pepperoni Pizza', 'Crispy crust topped with homemade tomato sauce and mozzarella.', 14.99, 'https://images.unsplash.com/photo-1628840042765-356cda07504e'),
(3, 'Spicy Noodles', 'Wok-tossed noodles with vegetables and chili oil.', 11.50, 'https://images.unsplash.com/photo-1585032226651-759b368d7246'),
(4, 'Caesar Salad', 'Fresh romaine lettuce with parmesan and croutons.', 7.50, 'https://images.unsplash.com/photo-1550304943-4f24f54ddde9'),
(5, 'Chocolate Brownie', 'Warm brownie served with vanilla ice cream.', 5.00, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c'),
(6, 'Iced Lemonade', 'Fresh lemonade with mint.', 3.50, 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd');