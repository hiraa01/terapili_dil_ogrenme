from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot_logic import get_chatbot_response

app = Flask(__name__)  
app.secret_key = 'gizli_anahtar'  # Session güvenliği

# Veritabanı bağlantısı
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='eD3fK64',  
        database='proje_db'
    )

# Ana sayfa → login yönlendirmesi
@app.route("/")
def home():
    # Giriş sonrası chat_page yerine dashboard’a yönlendir
    return redirect(url_for('dashboard'))

# Kullanıcı Kayıt
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Kullanıcı Giriş
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']

            # 🔹 Seviye kontrolü burada yapılır
            if user['level'] is None or user['level'] == '':
                return redirect(url_for('select_level'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return 'Geçersiz giriş!'
    return render_template('login.html')

#level select
@app.route('/select_level', methods=['GET', 'POST'])
def select_level():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_level = request.form['level']
        user_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET level = %s WHERE id = %s", (selected_level, user_id))
        conn.commit()
        conn.close()

        session['level'] = selected_level  # Menüde göstermek için session’a ekle

        return redirect(url_for('dashboard'))

    return render_template('level_select.html')

# Chat Sayfası (Sadece giriş yaptıysa)
@app.route("/chat")
def chat_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("chat.html", username=session['username'])

# Dashboard Sayfası (Giriş yaptıysa)
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], level=session.get('level', 'Belirtilmedi'))


# Chatbot API (chat.html bu endpoint’e mesaj gönderir)
@app.route("/get", methods=["POST"])
def chat():
    user_input = request.json.get("msg")
    mode = request.json.get("mode")
    response = get_chatbot_response(user_input, mode)
    return jsonify({"reply": response})

#çıkış yap
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# Uygulama başlat
if __name__ == "__main__":
    app.run(debug=True)
