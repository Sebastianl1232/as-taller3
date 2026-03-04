from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
import os
from datetime import datetime

# TODO: Configurar la aplicación Flask
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave-por-defecto-cambiar')
app.config['JSON_SORT_KEYS'] = False

# TODO: Configurar la URL de la API
API_URL = os.getenv('API_URL', 'http://api:8000')


@app.context_processor
def inject_globals():
    return {
        'is_logged_in': is_logged_in(),
        'current_user': session.get('user'),
        'current_year': datetime.now().year,
    }

@app.route('/')
def index():
    # TODO: Implementar página principal
    # Obtener productos destacados de la API
    ok, _, data = api_request('/api/v1/products/', method='GET')
    featured_products = data[:6] if ok and isinstance(data, list) else []
    if not ok:
        flash('No fue posible cargar los productos destacados.', 'warning')

    return render_template('index.html', featured_products=featured_products)

@app.route('/products')
def products():
    # TODO: Implementar página de productos
    # Obtener lista de productos de la API
    ok, _, data = api_request('/api/v1/products/', method='GET')
    product_list = data if ok and isinstance(data, list) else []
    if not ok:
        flash('No fue posible cargar el catálogo de productos.', 'warning')

    return render_template('products.html', products=product_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # TODO: Implementar lógica de login
        # Enviar datos a la API de autenticación
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email y contraseña son obligatorios.', 'danger')
            return render_template('login.html', form_data={'email': email})

        ok, _, data = api_request(
            '/api/v1/users/login',
            method='POST',
            data={'email': email, 'password': password}
        )

        if not ok:
            flash(data.get('detail', 'No fue posible iniciar sesión.'), 'danger')
            return render_template('login.html', form_data={'email': email})

        user = data.get('user', {})
        session['user'] = {
            'id': user.get('id'),
            'username': user.get('username'),
            'email': user.get('email')
        }
        flash('Sesión iniciada correctamente.', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # TODO: Implementar lógica de registro
        # Enviar datos a la API de registro
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('register.html', form_data={'username': username, 'email': email})

        ok, _, data = api_request(
            '/api/v1/users/register',
            method='POST',
            data={'username': username, 'email': email, 'password': password}
        )

        if not ok:
            flash(data.get('detail', 'No fue posible registrar el usuario.'), 'danger')
            return render_template('register.html', form_data={'username': username, 'email': email})

        user = data.get('user', {})
        session['user'] = {
            'id': user.get('id'),
            'username': user.get('username'),
            'email': user.get('email')
        }
        flash('Registro exitoso. Bienvenido a la tienda.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/cart')
def cart():
    # TODO: Implementar página del carrito
    # Obtener carrito del usuario de la API
    if not is_logged_in():
        flash('Debes iniciar sesión para ver el carrito.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user']['id']
    ok, _, data = api_request('/api/v1/carts/', method='GET', params={'user_id': user_id})

    if not ok:
        flash(data.get('detail', 'No fue posible cargar el carrito.'), 'danger')
        return render_template('cart.html', items=[], total=0)

    return render_template(
        'cart.html',
        cart_id=data.get('cart_id'),
        items=data.get('items', []),
        total=data.get('total', 0)
    )

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    # TODO: Implementar agregar producto al carrito
    # Enviar request a la API
    if not is_logged_in():
        message = 'Debes iniciar sesión para agregar productos al carrito.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': message}), 401
        flash(message, 'warning')
        return redirect(url_for('login'))

    raw_quantity = request.form.get('quantity', '1')
    try:
        quantity = int(raw_quantity)
    except ValueError:
        quantity = 1
    quantity = max(1, quantity)

    user_id = session['user']['id']
    ok, _, data = api_request(
        '/api/v1/carts/items',
        method='POST',
        data={'user_id': user_id, 'product_id': product_id, 'quantity': quantity}
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': ok,
            'message': data.get('message', data.get('detail', 'Operación completada.'))
        }), (200 if ok else 400)

    if ok:
        flash('Producto agregado al carrito.', 'success')
    else:
        flash(data.get('detail', 'No fue posible agregar el producto.'), 'danger')

    return redirect(request.referrer or url_for('products'))


@app.route('/cart/items/<int:item_id>/update', methods=['POST'])
def update_cart_item(item_id):
    if not is_logged_in():
        flash('Debes iniciar sesión.', 'warning')
        return redirect(url_for('login'))

    raw_quantity = request.form.get('quantity', '1')
    try:
        quantity = int(raw_quantity)
    except ValueError:
        quantity = 1
    quantity = max(1, quantity)

    ok, _, data = api_request(
        f'/api/v1/carts/items/{item_id}',
        method='PUT',
        data={'quantity': quantity}
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': ok,
            'message': data.get('message', data.get('detail', 'Operación completada.'))
        }), (200 if ok else 400)

    flash('Cantidad actualizada.' if ok else data.get('detail', 'No fue posible actualizar el item.'), 'success' if ok else 'danger')
    return redirect(url_for('cart'))


@app.route('/cart/items/<int:item_id>/remove', methods=['POST'])
def remove_cart_item(item_id):
    if not is_logged_in():
        flash('Debes iniciar sesión.', 'warning')
        return redirect(url_for('login'))

    ok, _, data = api_request(f'/api/v1/carts/items/{item_id}', method='DELETE')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': ok,
            'message': data.get('message', data.get('detail', 'Operación completada.'))
        }), (200 if ok else 400)

    flash('Item removido del carrito.' if ok else data.get('detail', 'No fue posible remover el item.'), 'success' if ok else 'danger')
    return redirect(url_for('cart'))


@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    if not is_logged_in():
        flash('Debes iniciar sesión.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user']['id']
    ok, _, data = api_request('/api/v1/carts/', method='DELETE', params={'user_id': user_id})

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': ok,
            'message': data.get('message', data.get('detail', 'Operación completada.'))
        }), (200 if ok else 400)

    flash('Carrito limpiado.' if ok else data.get('detail', 'No fue posible limpiar el carrito.'), 'success' if ok else 'danger')
    return redirect(url_for('cart'))

@app.route('/logout')
def logout():
    # TODO: Implementar logout
    # Limpiar sesión
    session.pop('user', None)
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('index'))

# TODO: Función helper para hacer requests a la API
def api_request(endpoint, method='GET', data=None, headers=None, params=None):
    # TODO: Implementar función para hacer requests a la API
    url = f"{API_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    request_headers = headers or {}

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            json=data,
            params=params,
            headers=request_headers,
            timeout=10,
        )

        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            payload = response.json()
        else:
            payload = {'detail': response.text}

        return response.ok, response.status_code, payload
    except requests.RequestException as exc:
        return False, 503, {'detail': f'Error de conexión con la API: {str(exc)}'}

# TODO: Función para verificar si el usuario está logueado
def is_logged_in():
    # TODO: Verificar si hay sesión activa
    return bool(session.get('user') and session['user'].get('id') is not None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)