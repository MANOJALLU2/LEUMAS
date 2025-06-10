from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json, os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')


def load_json(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)
    with open(file) as f:
        return json.load(f)


def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)


def login_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('products_page'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_json(USERS_FILE)
        u = request.form['username']
        p = request.form['password']
        user = next((x for x in users if x['username'] == u), None)
        if user and check_password_hash(user['password'], p):
            session['user'] = u
            return redirect(url_for('products_page'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_json(USERS_FILE)
        u = request.form['username']
        if any(x['username'] == u for x in users):
            return render_template('register.html', error='User exists')
        users.append({
            'username':
            u,
            'password':
            generate_password_hash(request.form['password'])
        })
        save_json(USERS_FILE, users)
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/products')
@login_required
def products_page():
    return render_template('products.html')


@app.route('/product/<id>')
@login_required
def product_page(id):
    return render_template('transactions.html', product_id=id)


@app.route('/api/products', methods=['GET', 'POST'])
@login_required
def api_products():
    data = load_json(PRODUCTS_FILE)
    if request.method == 'GET':
        return jsonify(data)
    d = request.get_json()
    nid = str(max([int(x['id']) for x in data] + [0]) + 1)
    prod = {
        'id': nid,
        'name': d['name'],
        'sku': d['sku'],
        'category': d['category'],
        'current_stock': d['initial_stock']
    }
    data.append(prod)
    save_json(PRODUCTS_FILE, data)
    return jsonify(prod)


@app.route('/api/products/<id>', methods=['PUT'])
@login_required
def api_update_product(id):
    data = load_json(PRODUCTS_FILE)
    d = request.get_json()
    for x in data:
        if x['id'] == id:
            x['current_stock'] = d['current_stock']
            save_json(PRODUCTS_FILE, data)
            return jsonify(x)
    return jsonify({}), 404


@app.route('/api/transactions', methods=['POST'])
@login_required
def api_transactions():
    txns = load_json(TRANSACTIONS_FILE)
    d = request.get_json()
    nid = str(max([int(x['id']) for x in txns] + [0]) + 1)
    from datetime import datetime
    t = {
        'id': nid,
        'product_id': d['product_id'],
        'type': d['type'],
        'quantity': d['quantity'],
        'timestamp': datetime.utcnow().isoformat()
    }
    txns.append(t)
    save_json(TRANSACTIONS_FILE, txns)
    prods = load_json(PRODUCTS_FILE)
    for x in prods:
        if x['id'] == t['product_id']:
            x['current_stock'] += t['quantity'] if t[
                'type'] == 'IN' else -t['quantity']
    save_json(PRODUCTS_FILE, prods)
    return jsonify(t)


@app.route('/api/products/<id>/transactions', methods=['GET'])
@login_required
def api_product_transactions(id):
    txns = load_json(TRANSACTIONS_FILE)
    return jsonify([x for x in txns if x['product_id'] == id])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # default to 5000 if not set
    app.run(host="0.0.0.0", port=port, debug=True)
