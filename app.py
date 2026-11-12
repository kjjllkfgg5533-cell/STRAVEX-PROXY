from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# ---------- صفحة رئيسية ----------
@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>خادم Flask</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: #f0f4f8; }
            h1 { color: #2c3e50; }
            a { display: block; margin: 10px; color: #3498db; }
        </style>
    </head>
    <body>
        <h1>مرحباً بك في خادم Flask 👋</h1>
        <p>الخادم يعمل بنجاح!</p>
        <a href="/api/hello">/api/hello</a>
        <a href="/api/users">/api/users</a>
    </body>
    </html>
    """)

# ---------- مسار JSON ----------
@app.route('/api/hello')
def hello():
    return jsonify({
        "message": "مرحباً بالعالم",
        "status": "success"
    })

# ---------- مسار مع بيانات ----------
@app.route('/api/users')
def get_users():
    users = [
        {"id": 1, "name": "أحمد", "age": 25},
        {"id": 2, "name": "سارة", "age": 30},
        {"id": 3, "name": "محمد", "age": 28},
    ]
    return jsonify(users)

# ---------- مسار مع معاملات ----------
@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    return jsonify({
        "id": user_id,
        "name": f"المستخدم رقم {user_id}"
    })

# ---------- مسار POST ----------
@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({
        "received": data,
        "status": "success"
    })

# ---------- تشغيل الخادم ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)