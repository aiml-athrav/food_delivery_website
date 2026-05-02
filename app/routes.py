from flask import render_template, redirect, url_for, flash, request, session
from app import app
from app.models import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------
# Context Processor for Cart
# ---------------------------
@app.context_processor
def inject_cart_count():
    count = 0
    if 'cart' in session:
        count = sum(session['cart'].values())
    return dict(cart_count=count)


# ---------------------------
# 1. Home Page
# ---------------------------
@app.route('/')
def index():
    return render_template('index.html', title='Home')


# ---------------------------
# 2. Menu Page
# ---------------------------
@app.route('/menu')
def menu():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM menu_items WHERE is_available = TRUE")
    items = cursor.fetchall()  # This will include 'image_url'

    cursor.close()
    connection.close()

    return render_template('menu.html', title='Menu', items=items)


# ---------------------------
# 3. Cart Routes
# ---------------------------
@app.route('/cart')
def cart():
    cart_items = []
    total_price = 0

    if 'cart' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        for item_id, quantity in session['cart'].items():
            cursor.execute("SELECT * FROM menu_items WHERE id=%s", (item_id,))
            item = cursor.fetchone()
            if item:
                subtotal = item['price'] * quantity
                total_price += subtotal
                cart_items.append({
                    'id': item['id'],
                    'name': item['name'],
                    'price': item['price'],
                    'image': item['image_url'],
                    'quantity': quantity,
                    'subtotal': subtotal
                })

        cursor.close()
        connection.close()

    return render_template('cart.html', title='Your Cart', cart_items=cart_items, total_price=total_price)


@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM menu_items WHERE id=%s AND is_available=TRUE", (item_id,))
    item = cursor.fetchone()
    cursor.close()
    connection.close()

    if not item:
        flash("Item not found!", "danger")
        return redirect(url_for('menu'))

    cart = session.get('cart', {})
    item_id_str = str(item_id)
    if item_id_str in cart:
        cart[item_id_str] += 1
    else:
        cart[item_id_str] = 1

    session['cart'] = cart
    session.modified = True
    flash(f"{item['name']} added to cart!", 'success')
    return redirect(url_for('menu'))


@app.route('/update_cart/<int:item_id>', methods=['POST'])
def update_cart(item_id):
    cart = session.get('cart', {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        new_quantity = int(request.form.get('quantity', 1))
        if new_quantity > 0:
            cart[item_id_str] = new_quantity
        else:
            cart.pop(item_id_str, None)

        session['cart'] = cart
        session.modified = True

    flash("Cart updated!", 'info')
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    cart = session.get('cart', {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        cart.pop(item_id_str)
        session['cart'] = cart
        session.modified = True
        flash("Item removed from cart.", 'warning')

    return redirect(url_for('cart'))


@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        flash("Please login to place an order.", "warning")
        return redirect(url_for('login'))

    if 'cart' not in session or not session['cart']:
        flash("Your cart is empty!", 'danger')
        return redirect(url_for('cart'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        total_price = 0
        for item_id, qty in session['cart'].items():
            cursor.execute("SELECT price FROM menu_items WHERE id=%s", (item_id,))
            price = cursor.fetchone()[0]
            total_price += price * qty

        cursor.execute(
            "INSERT INTO orders (user_id, total_price) VALUES (%s, %s)",
            (session['user_id'], total_price)
        )
        order_id = cursor.lastrowid

        for item_id, qty in session['cart'].items():
            cursor.execute("SELECT price FROM menu_items WHERE id=%s", (item_id,))
            price_at_purchase = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO order_items (order_id, item_id, quantity, price_at_purchase) VALUES (%s,%s,%s,%s)",
                (order_id, item_id, qty, price_at_purchase)
            )

        connection.commit()
        session.pop('cart', None)
        flash("Order placed successfully! Check your order history.", "success")

    except Exception as e:
        connection.rollback()
        print("Checkout DB error:", e)
        flash("An error occurred while placing the order.", "danger")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('history'))


# ---------------------------
# 4. Auth Routes
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # ---------- HARD-CODED ADMIN CHECK ----------
        if email == 'admin@example.com' and password == 'admin123':
            session['username'] = 'Admin'
            session['is_admin'] = True
            session['user_id'] = None  # No DB ID needed for hardcoded admin
            flash("Admin login successful!", "success")
            return redirect(url_for('admin'))

        # ---------- DATABASE USER CHECK ----------
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and check_password_hash(user['password_hash'], password):
            session['username'] = user['username']
            session['user_id'] = user['id']
            session['is_admin'] = bool(user['is_admin'])
            flash("Login successful!", "success")
            if user['is_admin']:
                return redirect(url_for('admin'))
            return redirect(url_for('menu'))
        else:
            flash("Invalid email or password", "danger")

    return render_template('login.html', title='Login')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("Please fill all fields", "danger")
            return redirect(url_for('register'))

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE email=%s OR username=%s", (email, username))
        if cursor.fetchone():
            flash("User already exists!", "warning")
            cursor.close()
            connection.close()
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s,%s,%s)",
            (username, email, password_hash)
        )
        connection.commit()
        cursor.close()
        connection.close()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', title='Register')


# ---------------------------
# 5. History Route
# ---------------------------
@app.route('/history')
def history():
    if 'user_id' not in session:
        flash("Please login to view your order history.", "warning")
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE user_id=%s ORDER BY created_at DESC", (session['user_id'],))
    orders = cursor.fetchall()

    for order in orders:
        cursor.execute("""
            SELECT mi.name, oi.quantity, oi.price_at_purchase
            FROM order_items oi
            JOIN menu_items mi ON oi.item_id = mi.id
            WHERE oi.order_id = %s
        """, (order['id'],))
        order_items = cursor.fetchall()
        order['items'] = order_items

    cursor.close()
    connection.close()

    return render_template('history.html', title='Order History', orders=orders)


# ---------------------------
# 6. Admin Routes
# ---------------------------
@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        flash("Access denied!", "danger")
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch menu items
    cursor.execute("SELECT * FROM menu_items")
    items = cursor.fetchall()

    # Fetch orders
    cursor.execute("""
        SELECT o.id, u.username AS customer, o.total_price AS total, o.status, o.created_at AS date
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    """)
    orders = cursor.fetchall()

    # Fetch order items for each order
    for order in orders:
        cursor.execute("""
            SELECT mi.name, oi.quantity, oi.price_at_purchase
            FROM order_items oi
            JOIN menu_items mi ON oi.item_id = mi.id
            WHERE oi.order_id = %s
        """, (order['id'],))
        order_items = cursor.fetchall()  # ✅ this is a list
        order['items'] = order_items  # ✅ attach list to key 'items'

    cursor.close()
    connection.close()

    return render_template('admin.html', title='Admin Dashboard', items=items, orders=orders)


@app.route('/admin/add_item', methods=['POST'])
def add_item():
    name = request.form.get('name')
    price = float(request.form.get('price'))
    description = request.form.get('description')
    image_url = request.form.get('image') or 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=600&auto=format&fit=crop'

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO menu_items (name, price, description, image_url) VALUES (%s,%s,%s,%s)",
        (name, price, description, image_url)
    )
    connection.commit()
    cursor.close()
    connection.close()

    flash(f"{name} added to the menu!", "success")
    return redirect(url_for('admin'))


# ---------------------------
# Toggle Availability Route
# ---------------------------
@app.route('/admin/toggle_item_status/<int:item_id>', methods=['POST'])
def toggle_item_status(item_id):
    if not session.get('is_admin'):
        flash("Access denied!", "danger")
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    # Get current status
    cursor.execute("SELECT is_available FROM menu_items WHERE id=%s", (item_id,))
    item = cursor.fetchone()
    if item:
        new_status = not item['is_available']
        cursor.execute("UPDATE menu_items SET is_available=%s WHERE id=%s", (new_status, item_id))
        connection.commit()
        flash(f"Menu item status updated!", "success")
    else:
        flash("Item not found!", "danger")

    cursor.close()
    connection.close()
    return redirect(url_for('admin'))


@app.route('/admin/update_order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    new_status = request.form.get('status')
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE orders SET status=%s WHERE id=%s", (new_status, order_id))
    connection.commit()
    cursor.close()
    connection.close()

    flash(f"Order #{order_id} status updated to {new_status}.", "info")
    return redirect(url_for('admin'))

# ---------------------------
# Edit Menu Item (Admin)
# ---------------------------
@app.route('/admin/edit_item/<int:item_id>', methods=['POST'])
def edit_item(item_id):
    if not session.get('is_admin'):
        flash("Access denied!", "danger")
        return redirect(url_for('login'))

    name = request.form.get('name')
    price = float(request.form.get('price'))
    description = request.form.get('description')
    image_url = request.form.get('image') or 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=600&auto=format&fit=crop'

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE menu_items SET name=%s, price=%s, description=%s, image_url=%s WHERE id=%s",
        (name, price, description, image_url, item_id)
    )
    connection.commit()
    cursor.close()
    connection.close()

    flash(f"{name} updated successfully!", "success")
    return redirect(url_for('admin'))