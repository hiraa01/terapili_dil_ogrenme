from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot_logic import get_chatbot_response, analyze_mood_and_extract_words
import json
from datetime import datetime

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
    # Giriş sonrası chat_page yerine dashboard'a yönlendir
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
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Otomatik giriş yap ve seviye seçim sayfasına yönlendir
        session['user_id'] = user_id
        session['username'] = username
        session['level'] = None  # Yeni kullanıcı için seviye seçimi gerekli
        session['language'] = 'english'  # Varsayılan dil
        
        return redirect(url_for('select_level'))
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
            session['level'] = user.get('level', 'A1')
            session['language'] = user.get('language', 'english')

            # 🔹 Seviye kontrolü burada yapılır
            if user['level'] is None or user['level'] == '':
                return redirect(url_for('select_level'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return 'Geçersiz giriş!'
    return render_template('login.html')

# Chatbot API
@app.route("/get", methods=["POST"])
def chat():
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    user_input = request.json.get("msg")
    chat_id = request.json.get("chat_id")
    selected_mode = request.json.get("mode", "serbest")
    user_level = session.get('level', 'A1')
    user_language = session.get('language', 'english')

    if user_level in ["A1", "A2"]:
        mode = "simple"
    elif user_level in ["B1", "B2"]:
        mode = "intermediate"
    else:
        mode = "advanced"

    # Mod bazlı yanıt oluştur
    response = get_chatbot_response(user_input, mode, selected_mode, user_language)
    mood, words = analyze_mood_and_extract_words(user_input, user_language)

    # Chat kelimelerini kullanıcı ilerlemesine ekle
    words_count = update_user_word_count_from_text(session['user_id'], user_input, "chat")

    # Mesajları veritabanına kaydet
    if chat_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Kullanıcı mesajını kaydet
        cursor.execute("""
            INSERT INTO chat_messages (chat_id, message_type, message_text) 
            VALUES (%s, 'user', %s)
        """, (chat_id, user_input))
        
        # Bot mesajını kaydet
        cursor.execute("""
            INSERT INTO chat_messages (chat_id, message_type, message_text) 
            VALUES (%s, 'bot', %s)
        """, (chat_id, response))
        
        conn.commit()
        conn.close()

    return jsonify({
        "reply": response,
        "mood": mood,
        "words": words,
        "words_count": words_count
    })

# Mod değişikliği için otomatik mesaj
@app.route("/api/chat/<int:chat_id>/mode-change", methods=["POST"])
def mode_change_message(chat_id):
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    data = request.json
    new_mode = data.get('mode', 'serbest')
    user_language = session.get('language', 'english')
    
    # Mod bazlı başlangıç mesajları - çok dilli
    mode_messages = {
        'aile': {
            'english': "👨‍👩‍👧‍👦 Hello! How can I help you with family matters? Would you like to talk about family relationships, parenting, sibling relationships, or family communication?",
            'spanish': "👨‍👩‍👧‍👦 ¡Hola! ¿Cómo puedo ayudarte con asuntos familiares? ¿Te gustaría hablar sobre relaciones familiares, crianza, relaciones entre hermanos o comunicación familiar?",
            'french': "👨‍👩‍👧‍👦 Bonjour! Comment puis-je vous aider avec les questions familiales? Voulez-vous parler des relations familiales, de la parentalité, des relations fraternelles ou de la communication familiale?",
            'korean': "👨‍👩‍👧‍👦 안녕하세요! 가족 문제에 대해 어떻게 도와드릴까요? 가족 관계, 육아, 형제 관계 또는 가족 소통에 대해 이야기하고 싶으신가요?",
            'japanese': "👨‍👩‍👧‍👦 こんにちは！家族の問題についてどのようにお手伝いできますか？家族関係、子育て、兄弟関係、家族のコミュニケーションについて話したいですか？",
            'arabic': "👨‍👩‍👧‍👦 مرحباً! كيف يمكنني مساعدتك في المسائل الأسرية؟ هل تريد التحدث عن العلاقات الأسرية أو تربية الأطفال أو العلاقات بين الإخوة أو التواصل الأسري؟",
            'turkish': "👨‍👩‍👧‍👦 Merhaba! Aile konularında size nasıl yardımcı olabilirim? Aile ilişkileriniz, ebeveynlik, kardeş ilişkileri veya aile içi iletişim hakkında konuşmak ister misiniz?"
        },
        'ask': {
            'english': "💕 Hello! Would you like to talk about your love life? I can support you with relationship issues, romantic feelings, communication problems, or personal development.",
            'spanish': "💕 ¡Hola! ¿Te gustaría hablar sobre tu vida amorosa? Puedo apoyarte con problemas de relación, sentimientos románticos, problemas de comunicación o desarrollo personal.",
            'french': "💕 Bonjour! Voulez-vous parler de votre vie amoureuse? Je peux vous soutenir avec les problèmes de relation, les sentiments romantiques, les problèmes de communication ou le développement personnel.",
            'korean': "💕 안녕하세요! 연애 생활에 대해 이야기하고 싶으신가요? 관계 문제, 로맨틱한 감정, 소통 문제 또는 개인 발전에 대해 도와드릴 수 있습니다.",
            'japanese': "💕 こんにちは！恋愛生活について話したいですか？関係の問題、ロマンチックな感情、コミュニケーションの問題、個人の成長についてサポートできます。",
            'arabic': "💕 مرحباً! هل تريد التحدث عن حياتك العاطفية؟ يمكنني دعمك في مشاكل العلاقات والمشاعر الرومانسية ومشاكل التواصل أو التطور الشخصي.",
            'turkish': "💕 Merhaba! Aşk hayatınız hakkında konuşmak ister misiniz? İlişki sorunları, romantik duygular, iletişim problemleri veya kişisel gelişim konularında size destek olabilirim."
        },
        'akademik': {
            'english': "📚 Hello! How can I help you with your academic life? Let's talk about study techniques, exam stress, career planning, or student life.",
            'spanish': "📚 ¡Hola! ¿Cómo puedo ayudarte con tu vida académica? Hablemos de técnicas de estudio, estrés de exámenes, planificación de carrera o vida estudiantil.",
            'french': "📚 Bonjour! Comment puis-je vous aider avec votre vie académique? Parlons des techniques d'étude, du stress des examens, de la planification de carrière ou de la vie étudiante.",
            'korean': "📚 안녕하세요! 학업 생활에 대해 어떻게 도와드릴까요? 공부 기법, 시험 스트레스, 진로 계획 또는 학생 생활에 대해 이야기해보겠습니다.",
            'japanese': "📚 こんにちは！学業生活についてどのようにお手伝いできますか？勉強法、試験ストレス、キャリアプランニング、学生生活について話しましょう。",
            'arabic': "📚 مرحباً! كيف يمكنني مساعدتك في حياتك الأكاديمية؟ دعنا نتحدث عن تقنيات الدراسة وضغط الامتحانات والتخطيط المهني أو حياة الطالب.",
            'turkish': "📚 Merhaba! Akademik hayatınızda nasıl yardımcı olabilirim? Ders çalışma teknikleri, sınav stresi, kariyer planlaması veya öğrenci yaşamı hakkında konuşalım."
        },
        'serbest': {
            'english': "🌟 Hello! How are you? What did you experience today? How can I help you?",
            'spanish': "🌟 ¡Hola! ¿Cómo estás? ¿Qué experimentaste hoy? ¿Cómo puedo ayudarte?",
            'french': "🌟 Bonjour! Comment allez-vous? Qu'avez-vous vécu aujourd'hui? Comment puis-je vous aider?",
            'korean': "🌟 안녕하세요! 어떻게 지내세요? 오늘 무엇을 경험하셨나요? 어떻게 도와드릴까요?",
            'japanese': "🌟 こんにちは！お元気ですか？今日何を経験しましたか？どのようにお手伝いできますか？",
            'arabic': "🌟 مرحباً! كيف حالك؟ ماذا عشت اليوم؟ كيف يمكنني مساعدتك؟",
            'turkish': "🌟 Merhaba! Nasılsınız? Bugün neler yaşadınız? Size nasıl yardımcı olabilirim?"
        }
    }
    
    mode_languages = mode_messages.get(new_mode, mode_messages['serbest'])
    welcome_message = mode_languages.get(user_language, mode_languages['english'])
    
    # Veritabanına kaydet
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_messages (chat_id, message_type, message_text) 
        VALUES (%s, 'bot', %s)
    """, (chat_id, welcome_message))
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": welcome_message,
        "mode": new_mode
    })

# Kelime oyunu API
@app.route("/api/game", methods=["GET", "POST"])
def word_game():
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    if request.method == "GET":
        # Yeni oyun başlat
        user_level = session.get('level', 'A1')
        user_language = session.get('language', 'english')
        game_type = request.args.get('type', 'daily')  # daily, challenge, review
        
        game_data = generate_advanced_word_game(user_level, user_language, game_type, session['user_id'])
        return jsonify(game_data)
    
    elif request.method == "POST":
        # Cevap kontrolü
        data = request.json
        answer = data.get('answer', '').lower().strip()
        correct_answers = data.get('correct_answers', [])
        word = data.get('word', '')
        game_type = data.get('game_type', 'daily')
        user_language = session.get('language', 'english')
        
        # Çoklu doğru cevap kontrolü
        is_correct = answer in [ans.lower().strip() for ans in correct_answers]
        
        # Dil bazlı mesajlar
        success_messages = {
            'english': "🎉 Correct! Great job!",
            'spanish': "🎉 ¡Correcto! ¡Excelente trabajo!",
            'french': "🎉 Correct! Excellent travail!",
            'korean': "🎉 맞습니다! 훌륭한 일입니다!",
            'japanese': "🎉 正解です！素晴らしい仕事です！",
            'arabic': "🎉 صحيح! عمل رائع!",
            'turkish': "🎉 Doğru! Harika bir iş çıkardınız!"
        }
        
        error_messages = {
            'english': "❌ Wrong. Correct answers: ",
            'spanish': "❌ Incorrecto. Respuestas correctas: ",
            'french': "❌ Incorrect. Réponses correctes: ",
            'korean': "❌ 틀렸습니다. 정답: ",
            'japanese': "❌ 間違いです。正解: ",
            'arabic': "❌ خطأ. الإجابات الصحيحة: ",
            'turkish': "❌ Yanlış. Doğru cevaplar: "
        }
        
        if is_correct:
            # Doğru cevap - puan ekle ve seviye kontrolü yap
            add_word_score(session['user_id'], word, game_type)
            level_up = check_advanced_level_upgrade(session['user_id'])
            
            return jsonify({
                "correct": True,
                "message": success_messages.get(user_language, success_messages['english']),
                "level_up": level_up,
                "new_level": session.get('level') if level_up else None,
                "points_earned": get_points_for_game_type(game_type)
            })
        else:
            return jsonify({
                "correct": False,
                "message": error_messages.get(user_language, error_messages['english']) + ", ".join(correct_answers),
                "level_up": False,
                "points_earned": 0
            })

# Gelişmiş kelime oyunu oluştur
def generate_advanced_word_game(level, language="english", game_type="daily", user_id=None):
    import random
    from datetime import datetime, timedelta
    
    # Yapay zeka ile kelime üretimi
    if game_type == "daily":
        return generate_daily_words(level, language, user_id)
    elif game_type == "challenge":
        return generate_challenge_words(level, language)
    elif game_type == "review":
        return generate_review_words(level, language, user_id)
    else:
        return generate_daily_words(level, language, user_id)

# Günlük kelimeler oluştur
def generate_daily_words(level, language, user_id):
    import random
    from datetime import datetime
    
    # Bugünün tarihini al
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Veritabanından bugünün kelimelerini kontrol et
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT word, translations, hint, difficulty 
        FROM daily_words 
        WHERE language = %s AND level = %s AND date = %s
    """, (language, level, today))
    
    existing_words = cursor.fetchall()
    
    if not existing_words:
        # Bugün için yeni kelimeler oluştur
        new_words = create_daily_words_with_ai(level, language, today)
        
        # Veritabanına kaydet
        for word_data in new_words:
            cursor.execute("""
                INSERT INTO daily_words (language, level, date, word, translations, hint, difficulty)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (language, level, today, word_data['word'], 
                  json.dumps(word_data['translations']), word_data['hint'], word_data['difficulty']))
        
        conn.commit()
        existing_words = new_words
    else:
        # JSON'dan çevirileri parse et
        for word in existing_words:
            word['translations'] = json.loads(word['translations'])
    
    conn.close()
    
    # Rastgele bir kelime seç
    selected_word = random.choice(existing_words)
    
    return {
        "word": selected_word['word'],
        "hint": selected_word['hint'],
        "correct_answers": selected_word['translations'],
        "level": level,
        "game_type": "daily",
        "difficulty": selected_word['difficulty']
    }

# Yapay zeka ile günlük kelimeler oluştur
def create_daily_words_with_ai(level, language, date):
    from chatbot_logic import model
    
    # Seviyeye göre kelime sayısı
    word_counts = {'A1': 5, 'A2': 7, 'B1': 10, 'B2': 12}
    word_count = word_counts.get(level, 5)
    
    # Dil bazlı prompt'lar
    language_prompts = {
        'english': f"Generate {word_count} English words for {level} level. Each word should have multiple Turkish translations and a hint. Format as JSON array with 'word', 'translations' (array), 'hint', 'difficulty' (1-5). Focus on daily use words.",
        'spanish': f"Generate {word_count} Spanish words for {level} level. Each word should have multiple Turkish translations and a hint. Format as JSON array with 'word', 'translations' (array), 'hint', 'difficulty' (1-5). Focus on daily use words.",
        'french': f"Generate {word_count} French words for {level} level. Each word should have multiple Turkish translations and a hint. Format as JSON array with 'word', 'translations' (array), 'hint', 'difficulty' (1-5). Focus on daily use words.",
        'korean': f"Generate {word_count} Korean words for {level} level. Each word should have multiple Turkish translations and a hint. Format as JSON array with 'word', 'translations' (array), 'hint', 'difficulty' (1-5). Focus on daily use words.",
        'japanese': f"Generate {word_count} Japanese words for {level} level. Each word should have multiple Turkish translations and a hint. Format as JSON array with 'word', 'translations' (array), 'hint', 'difficulty' (1-5). Focus on daily use words.",
        'arabic': f"Generate {word_count} Arabic words for {level} level. Each word should have multiple Turkish translations and a hint. Format as JSON array with 'word', 'translations' (array), 'hint', 'difficulty' (1-5). Focus on daily use words.",
        'turkish': f"Generate {word_count} Turkish words for {level} level. Each word should have multiple meanings and a hint. Format as JSON array with 'word', 'translations' (array), 'hint', 'difficulty' (1-5). Focus on daily use words."
    }
    
    prompt = language_prompts.get(language, language_prompts['english'])
    
    try:
        response = model.generate_content(prompt)
        words_data = json.loads(response.text.strip())
        return words_data
    except Exception as e:
        print(f"AI kelime üretimi hatası: {e}")
        # Fallback kelimeler
        return get_fallback_words(level, language)

# Fallback kelimeler
def get_fallback_words(level, language):
    fallback_words = {
        'english': {
            'A1': [
                {'word': 'hello', 'translations': ['merhaba', 'selam'], 'hint': 'Greeting', 'difficulty': 1},
                {'word': 'good', 'translations': ['iyi', 'güzel'], 'hint': 'Positive state', 'difficulty': 1},
                {'word': 'house', 'translations': ['ev', 'konut'], 'hint': 'Living place', 'difficulty': 1},
                {'word': 'book', 'translations': ['kitap', 'eser'], 'hint': 'Reading material', 'difficulty': 1},
                {'word': 'water', 'translations': ['su', 'akarsu'], 'hint': 'Beverage', 'difficulty': 1}
            ],
            'A2': [
                {'word': 'beautiful', 'translations': ['güzel', 'hoş'], 'hint': 'Visual beauty', 'difficulty': 2},
                {'word': 'important', 'translations': ['önemli', 'mühim'], 'hint': 'Valuable', 'difficulty': 2},
                {'word': 'difficult', 'translations': ['zor', 'güç'], 'hint': 'Not easy', 'difficulty': 2},
                {'word': 'interesting', 'translations': ['ilginç', 'enteresan'], 'hint': 'Attention-grabbing', 'difficulty': 2},
                {'word': 'necessary', 'translations': ['gerekli', 'zorunlu'], 'hint': 'Needed', 'difficulty': 2}
            ]
        }
    }
    
    return fallback_words.get(language, fallback_words['english']).get(level, fallback_words['english']['A1'])

# Challenge kelimeleri oluştur
def generate_challenge_words(level, language):
    # Daha zorlu kelimeler
    challenge_words = {
        'english': {
            'A1': [
                {'word': 'accomplish', 'translations': ['başarmak', 'tamamlamak'], 'hint': 'Complete goal', 'difficulty': 3},
                {'word': 'determine', 'translations': ['belirlemek', 'kararlaştırmak'], 'hint': 'Make decision', 'difficulty': 3},
                {'word': 'establish', 'translations': ['kurmak', 'oluşturmak'], 'hint': 'Create', 'difficulty': 3}
            ],
            'A2': [
                {'word': 'sophisticated', 'translations': ['sofistike', 'karmaşık'], 'hint': 'Advanced', 'difficulty': 4},
                {'word': 'accomplishment', 'translations': ['başarı', 'eser'], 'hint': 'Achieved result', 'difficulty': 4},
                {'word': 'perspective', 'translations': ['bakış açısı', 'görüş'], 'hint': 'Viewpoint', 'difficulty': 4}
            ]
        }
    }
    
    import random
    words = challenge_words.get(language, challenge_words['english']).get(level, challenge_words['english']['A1'])
    selected_word = random.choice(words)
    
    return {
        "word": selected_word['word'],
        "hint": selected_word['hint'],
        "correct_answers": selected_word['translations'],
        "level": level,
        "game_type": "challenge",
        "difficulty": selected_word['difficulty']
    }

# Review kelimeleri oluştur
def generate_review_words(level, language, user_id):
    # Kullanıcının öğrendiği kelimelerden rastgele seç
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT word, score, last_played 
        FROM word_scores 
        WHERE user_id = %s 
        ORDER BY last_played ASC 
        LIMIT 10
    """, (user_id,))
    
    learned_words = cursor.fetchall()
    conn.close()
    
    if learned_words:
        import random
        selected_word_data = random.choice(learned_words)
        
        # Kelime çevirilerini al
        word_translations = get_word_translations(selected_word_data['word'], language)
        
        return {
            "word": selected_word_data['word'],
            "hint": f"Review word (Score: {selected_word_data['score']})",
            "correct_answers": word_translations,
            "level": level,
            "game_type": "review",
            "difficulty": 2
        }
    else:
        # Hiç kelime yoksa günlük kelime döndür
        return generate_daily_words(level, language, user_id)

# Kelime çevirilerini al
def get_word_translations(word, language):
    # Basit çeviri sözlüğü
    translations = {
        'hello': ['merhaba', 'selam'],
        'good': ['iyi', 'güzel'],
        'house': ['ev', 'konut'],
        'book': ['kitap', 'eser'],
        'water': ['su', 'akarsu'],
        'beautiful': ['güzel', 'hoş'],
        'important': ['önemli', 'mühim'],
        'difficult': ['zor', 'güç'],
        'interesting': ['ilginç', 'enteresan'],
        'necessary': ['gerekli', 'zorunlu']
    }
    
    return translations.get(word.lower(), [word])

# Gelişmiş kelime puanı ekle
def add_word_score(user_id, word, game_type="daily"):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Kelime puanlarını takip etmek için tablo oluştur (eğer yoksa)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS word_scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            word VARCHAR(100) NOT NULL,
            score INT DEFAULT 1,
            game_type VARCHAR(20) DEFAULT 'daily',
            last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Günlük kelimeler tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_words (
            id INT AUTO_INCREMENT PRIMARY KEY,
            language VARCHAR(20) NOT NULL,
            level VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            word VARCHAR(100) NOT NULL,
            translations JSON NOT NULL,
            hint TEXT NOT NULL,
            difficulty INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Kullanıcı ilerleme tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            total_points INT DEFAULT 0,
            daily_streak INT DEFAULT 0,
            last_daily_date DATE,
            level_progress JSON DEFAULT '{}',
            chat_words_count INT DEFAULT 0,
            diary_words_count INT DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Kelime puanını güncelle veya ekle
    points = get_points_for_game_type(game_type)
    
    cursor.execute("""
        INSERT INTO word_scores (user_id, word, score, game_type) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        score = score + %s,
        game_type = %s,
        last_played = CURRENT_TIMESTAMP
    """, (user_id, word, points, game_type, points, game_type))
    
    # Kullanıcı ilerlemesini güncelle
    cursor.execute("""
        INSERT INTO user_progress (user_id, total_points) 
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE 
        total_points = total_points + %s
    """, (user_id, points, points))
    
    conn.commit()
    conn.close()

# Oyun türüne göre puan hesapla
def get_points_for_game_type(game_type):
    points = {
        'daily': 1,
        'challenge': 3,
        'review': 2
    }
    return points.get(game_type, 1)

# Gelişmiş seviye yükseltme kontrolü
def check_advanced_level_upgrade(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Kullanıcının toplam puanını hesapla
    cursor.execute("""
        SELECT total_points, chat_words_count, diary_words_count 
        FROM user_progress 
        WHERE user_id = %s
    """, (user_id,))
    
    progress = cursor.fetchone()
    if not progress:
        conn.close()
        return False
    
    total_points = progress['total_points'] or 0
    chat_words = progress['chat_words_count'] or 0
    diary_words = progress['diary_words_count'] or 0
    
    # Mevcut seviyeyi al
    cursor.execute("SELECT level FROM users WHERE id = %s", (user_id,))
    current_level = cursor.fetchone()['level']
    
    # Gelişmiş seviye yükseltme kriterleri
    level_thresholds = {
        'A1': {'points': 50, 'chat_words': 20, 'diary_words': 10},   # A1 -> A2
        'A2': {'points': 120, 'chat_words': 50, 'diary_words': 25},  # A2 -> B1
        'B1': {'points': 250, 'chat_words': 100, 'diary_words': 50}, # B1 -> B2
        'B2': {'points': 500, 'chat_words': 200, 'diary_words': 100} # B2 -> C1
    }
    
    new_level = None
    if current_level in level_thresholds:
        threshold = level_thresholds[current_level]
        
        if (total_points >= threshold['points'] and 
            chat_words >= threshold['chat_words'] and 
            diary_words >= threshold['diary_words']):
            
            level_progression = {'A1': 'A2', 'A2': 'B1', 'B1': 'B2', 'B2': 'C1'}
            new_level = level_progression.get(current_level)
            
            if new_level:
                # Seviyeyi güncelle
                cursor.execute("UPDATE users SET level = %s WHERE id = %s", (new_level, user_id))
                conn.commit()
                
                # Session'ı güncelle
                session['level'] = new_level
    
    conn.close()
    return new_level is not None

# Chat ve günlük analizi ile kelime sayısını güncelle
def update_user_word_count_from_text(user_id, text, source="chat"):
    from chatbot_logic import analyze_mood_and_extract_words
    
    # Metinden kelimeleri çıkar
    mood, words = analyze_mood_and_extract_words(text, session.get('language', 'english'))
    
    if words:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Kullanıcı ilerlemesini güncelle
        if source == "chat":
            cursor.execute("""
                UPDATE user_progress 
                SET chat_words_count = chat_words_count + %s 
                WHERE user_id = %s
            """, (len(words), user_id))
        elif source == "diary":
            cursor.execute("""
                UPDATE user_progress 
                SET diary_words_count = diary_words_count + %s 
                WHERE user_id = %s
            """, (len(words), user_id))
        
        conn.commit()
        conn.close()
    
    return len(words)

# Gelişmiş kelime oyunu istatistikleri
@app.route("/api/game/stats", methods=["GET"])
def get_game_stats():
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Kullanıcı ilerlemesi
    cursor.execute("""
        SELECT total_points, chat_words_count, diary_words_count, daily_streak
        FROM user_progress 
        WHERE user_id = %s
    """, (session['user_id'],))
    
    progress = cursor.fetchone()
    if not progress:
        progress = {'total_points': 0, 'chat_words_count': 0, 'diary_words_count': 0, 'daily_streak': 0}
    
    # Toplam kelime sayısı
    cursor.execute("""
        SELECT COUNT(DISTINCT word) as total_words 
        FROM word_scores 
        WHERE user_id = %s
    """, (session['user_id'],))
    total_words = cursor.fetchone()['total_words']
    
    # Oyun türüne göre puanlar
    cursor.execute("""
        SELECT game_type, SUM(score) as type_score
        FROM word_scores 
        WHERE user_id = %s
        GROUP BY game_type
    """, (session['user_id'],))
    
    game_scores = cursor.fetchall()
    daily_score = next((score['type_score'] for score in game_scores if score['game_type'] == 'daily'), 0)
    challenge_score = next((score['type_score'] for score in game_scores if score['game_type'] == 'challenge'), 0)
    review_score = next((score['type_score'] for score in game_scores if score['game_type'] == 'review'), 0)
    
    # Seviye ilerleme bilgisi
    current_level = session.get('level', 'A1')
    level_thresholds = {
        'A1': {'points': 50, 'chat_words': 20, 'diary_words': 10},
        'A2': {'points': 120, 'chat_words': 50, 'diary_words': 25},
        'B1': {'points': 250, 'chat_words': 100, 'diary_words': 50},
        'B2': {'points': 500, 'chat_words': 200, 'diary_words': 100}
    }
    
    next_level_progress = {}
    if current_level in level_thresholds:
        threshold = level_thresholds[current_level]
        next_level_progress = {
            'points_progress': min(100, (progress['total_points'] / threshold['points']) * 100),
            'chat_progress': min(100, (progress['chat_words_count'] / threshold['chat_words']) * 100),
            'diary_progress': min(100, (progress['diary_words_count'] / threshold['diary_words']) * 100)
        }
    
    conn.close()
    
    return jsonify({
        "totalWords": total_words,
        "totalPoints": progress['total_points'],
        "dailyScore": daily_score,
        "challengeScore": challenge_score,
        "reviewScore": review_score,
        "chatWordsCount": progress['chat_words_count'],
        "diaryWordsCount": progress['diary_words_count'],
        "dailyStreak": progress['daily_streak'],
        "currentLevel": current_level,
        "nextLevelProgress": next_level_progress
    })

# Sohbet oluştur
@app.route("/api/chats", methods=["POST"])
def create_chat():
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    data = request.json
    title = data.get('title', 'Yeni Sohbet')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chats (user_id, title) VALUES (%s, %s)
    """, (session['user_id'], title))
    
    chat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        "id": chat_id,
        "title": title,
        "created_at": datetime.now().isoformat()
    })

# Sohbetleri getir
@app.route("/api/chats", methods=["GET"])
def get_chats():
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, title, created_at, updated_at 
        FROM chats 
        WHERE user_id = %s 
        ORDER BY updated_at DESC
    """, (session['user_id'],))
    
    chats = cursor.fetchall()
    conn.close()
    
    # Datetime objelerini string'e çevir
    for chat in chats:
        chat['created_at'] = chat['created_at'].isoformat()
        chat['updated_at'] = chat['updated_at'].isoformat()
    
    return jsonify(chats)

# Sohbet mesajlarını getir
@app.route("/api/chats/<int:chat_id>/messages", methods=["GET"])
def get_chat_messages(chat_id):
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Sohbetin kullanıcıya ait olduğunu kontrol et
    cursor.execute("""
        SELECT id FROM chats WHERE id = %s AND user_id = %s
    """, (chat_id, session['user_id']))
    
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Sohbet bulunamadı"}), 404
    
    # Mesajları getir
    cursor.execute("""
        SELECT message_type, message_text, created_at 
        FROM chat_messages 
        WHERE chat_id = %s 
        ORDER BY created_at ASC
    """, (chat_id,))
    
    messages = cursor.fetchall()
    conn.close()
    
    # Datetime objelerini string'e çevir
    for msg in messages:
        msg['created_at'] = msg['created_at'].isoformat()
    
    return jsonify(messages)

# Sohbet başlığını güncelle
@app.route("/api/chats/<int:chat_id>", methods=["PUT"])
def update_chat(chat_id):
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    data = request.json
    title = data.get('title')
    
    if not title:
        return jsonify({"error": "Başlık gerekli"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sohbetin kullanıcıya ait olduğunu kontrol et ve güncelle
    cursor.execute("""
        UPDATE chats SET title = %s WHERE id = %s AND user_id = %s
    """, (title, chat_id, session['user_id']))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Sohbet bulunamadı"}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Sohbet güncellendi"})

# Sohbet sil
@app.route("/api/chats/<int:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sohbetin kullanıcıya ait olduğunu kontrol et ve sil
    cursor.execute("""
        DELETE FROM chats WHERE id = %s AND user_id = %s
    """, (chat_id, session['user_id']))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Sohbet bulunamadı"}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Sohbet silindi"})

# GÜNLÜK YAZMA Sayfası 
@app.route('/gunluk', methods=['GET', 'POST'])
def gunluk():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        text = request.form['gunluk_text']
        user_language = session.get('language', 'english')
        mood, words = analyze_mood_and_extract_words(text, user_language)
        response = get_chatbot_response(text, mode="intermediate", selected_mode="serbest", language=user_language)
        
        # Günlük kelimelerini kullanıcı ilerlemesine ekle
        words_count = update_user_word_count_from_text(session['user_id'], text, "diary")
        
        # Veritabanına kaydet
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO diary_entries (user_id, text, mood, words, bot_response) 
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_id'], text, mood, json.dumps(words), response))
        conn.commit()
        conn.close()
        
        return render_template('gunluk.html', username=session['username'], 
                               text=text, mood=mood, words=words, response=response, words_count=words_count)

    return render_template('gunluk.html', username=session['username'])

# Günlük yazılarını getir
@app.route("/api/diary", methods=["GET"])
def get_diary_entries():
    if 'user_id' not in session:
        return jsonify({"error": "Giriş yapılmamış"}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, text, mood, words, bot_response, created_at 
        FROM diary_entries 
        WHERE user_id = %s 
        ORDER BY created_at DESC
    """, (session['user_id'],))
    
    entries = cursor.fetchall()
    conn.close()
    
    # Datetime objelerini string'e çevir ve JSON'ı parse et
    for entry in entries:
        entry['created_at'] = entry['created_at'].isoformat()
        if entry['words']:
            entry['words'] = json.loads(entry['words'])
    
    return jsonify(entries)

#level select
@app.route('/select_level', methods=['GET', 'POST'])
def select_level():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_level = request.form['level']
        selected_language = request.form.get('language', 'english')
        user_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET level = %s, language = %s WHERE id = %s", (selected_level, selected_language, user_id))
        conn.commit()
        conn.close()

        session['level'] = selected_level  # Menüde göstermek için session'a ekle
        session['language'] = selected_language

        return redirect(url_for('dashboard'))

    return render_template('level_select.html')

@app.route('/change_language', methods=['GET', 'POST'])
def change_language():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        language = request.form['language']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET language = %s WHERE id = %s", (language, session['user_id']))
        conn.commit()
        conn.close()
        
        session['language'] = language
        return redirect(url_for('dashboard'))
    
    return render_template('change_language.html', current_language=session.get('language', 'english'))

# Chat Sayfası (Sadece giriş yaptıysa)
@app.route("/chat")
def chat_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("chat.html", username=session['username'])

# Kelime Oyunu Sayfası
@app.route("/game")
def game_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("game.html", username=session['username'])

# Dashboard Sayfası (Giriş yaptıysa)
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Dil adını çevir
    language_names = {
        'english': 'İngilizce',
        'spanish': 'İspanyolca',
        'french': 'Fransızca',
        'korean': 'Korece',
        'japanese': 'Japonca',
        'arabic': 'Arapça',
        'turkish': 'Türkçe'
    }
    
    user_language = session.get('language', 'english')
    language_name = language_names.get(user_language, 'İngilizce')
    
    return render_template('dashboard.html', 
                         username=session['username'], 
                         level=session.get('level', 'Belirtilmedi'),
                         language_name=language_name)

#çıkış yap
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# Uygulama başlat
if __name__ == "__main__":
    app.run(debug=True)
