CREATE TABLE orders_1100378 (
    order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    restaurant_name VARCHAR(100),
    item VARCHAR(100),
    amount NUMERIC(10, 2),
    order_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO orders_1100378 (customer_name, restaurant_name, item, amount, order_status, created_at) VALUES
('Aarav Sharma', 'Masala Magic', 'Butter Chicken', 350.00, 'PLACED', NOW() - INTERVAL '10 minutes'),
('Priya Patel', 'Saffron Sunrise', 'Paneer Tikka', 250.50, 'PREPARING', NOW() - INTERVAL '9 minutes'),
('Rahul Gupta', 'Biryani Buzz', 'Hyderabadi Biryani', 599.00, 'DELIVERED', NOW() - INTERVAL '8 minutes'),
('Ananya Singh', 'Chai Charm', 'Vada Pav', 220.00, 'PLACED', NOW() - INTERVAL '7 minutes'),
('Neha Verma', 'Rasoi Royals', 'Chole Bhature', 450.00, 'CANCELLED', NOW() - INTERVAL '6 minutes'),
('Karan Mehta', 'Tandoori Tadka', 'Chicken Tandoori', 180.00, 'PLACED', NOW() - INTERVAL '5 minutes'),
('Divya Joshi', 'Punjabi Palace', 'Dal Makhani', 250.00, 'DELIVERED', NOW() - INTERVAL '4 minutes'),
('Siddharth Rao', 'Jalebi Junction', 'Jalebi', 300.00, 'PREPARING', NOW() - INTERVAL '3 minutes'),
('Isha Malhotra', 'South Indian Delights', 'Masala Dosa', 120.00, 'PLACED', NOW() - INTERVAL '2 minutes'),
('Vikram Reddy', 'Naan Nirvana', 'Garlic Naan', 400.00, 'PLACED', NOW() - INTERVAL '1 minute');