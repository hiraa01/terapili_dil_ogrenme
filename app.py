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
            return redirect(url_for('chat_page'))
        else:
            return 'Geçersiz giriş!'
    return render_template('login.html')

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
    return render_template("dashboard.html", username=session['username'])


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
