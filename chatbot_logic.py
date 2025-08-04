from google.generativeai import configure, GenerativeModel

configure(api_key="AIzaSyBSJPdaz2kPVvh89gkPJ4IUpjFVvhD8VB0")

model = GenerativeModel("gemini-1.5-flash")

def get_chatbot_response(user_input, mode="intermediate", selected_mode="serbest", language="english"):
    # Dil bazlı prompt'lar - seviyeye göre ayarlanmış
    language_instructions = {
        'simple': {
            'english': "Respond in English. Use simple words and short sentences. Keep your response supportive and understanding. Maximum 3 sentences, very simple language.",
            'spanish': "Responde en español. Usa palabras simples y oraciones cortas. Mantén tu respuesta de apoyo y comprensiva. Máximo 3 oraciones, lenguaje muy simple.",
            'french': "Répondez en français. Utilisez des mots simples et des phrases courtes. Gardez votre réponse de soutien et compréhensive. Maximum 3 phrases, langage très simple.",
            'korean': "한국어로 답변하세요. 간단한 단어와 짧은 문장을 사용하세요. 지원적이고 이해심 많은 답변을 유지하세요. 최대 3문장, 매우 간단한 언어.",
            'japanese': "日本語で答えてください。簡単な言葉と短い文を使用してください。支援的で理解力のある回答を保ってください。最大3文、非常に簡単な言語。",
            'arabic': "أجب باللغة العربية. استخدم كلمات بسيطة وجمل قصيرة. حافظ على إجابتك داعمة ومتفهمة. أقصى 3 جمل، لغة بسيطة جداً.",
            'turkish': "Türkçe yanıt verin. Basit kelimeler ve kısa cümleler kullanın. Yanıtınızı destekleyici ve anlayışlı tutun. En fazla 3 cümle, çok basit dil."
        },
        'intermediate': {
            'english': "Respond in English. Keep your response supportive, understanding, and constructive. Maximum 5 sentences, clear and helpful language.",
            'spanish': "Responde en español. Mantén tu respuesta de apoyo, comprensiva y constructiva. Máximo 5 oraciones, lenguaje claro y útil.",
            'french': "Répondez en français. Gardez votre réponse de soutien, compréhensive et constructive. Maximum 5 phrases, langage clair et utile.",
            'korean': "한국어로 답변하세요. 지원적이고 이해심 많으며 건설적인 답변을 유지하세요. 최대 5문장, 명확하고 도움이 되는 언어.",
            'japanese': "日本語で答えてください。支援的で理解力があり、建設的な回答を保ってください。最大5文、明確で役立つ言語。",
            'arabic': "أجب باللغة العربية. حافظ على إجابتك داعمة ومتفهمة وبناءة. أقصى 5 جمل، لغة واضحة ومفيدة.",
            'turkish': "Türkçe yanıt verin. Yanıtınızı destekleyici, anlayışlı ve yapıcı tutun. En fazla 5 cümle, açık ve yardımcı dil."
        },
        'advanced': {
            'english': "Respond in English. Provide detailed, insightful, and professional therapeutic guidance. Use sophisticated language while remaining supportive. Maximum 7 sentences with deeper analysis.",
            'spanish': "Responde en español. Proporciona orientación terapéutica detallada, perspicaz y profesional. Usa lenguaje sofisticado manteniendo el apoyo. Máximo 7 oraciones con análisis más profundo.",
            'french': "Répondez en français. Fournissez des conseils thérapeutiques détaillés, perspicaces et professionnels. Utilisez un langage sophistiqué tout en restant de soutien. Maximum 7 phrases avec analyse plus approfondie.",
            'korean': "한국어로 답변하세요. 상세하고 통찰력 있으며 전문적인 치료적 지도를 제공하세요. 지원적이면서도 정교한 언어를 사용하세요. 더 깊은 분석과 함께 최대 7문장.",
            'japanese': "日本語で答えてください。詳細で洞察力があり、専門的な治療的ガイダンスを提供してください。支援的でありながら洗練された言語を使用してください。より深い分析とともに最大7文。",
            'arabic': "أجب باللغة العربية. قدم إرشاداً علاجياً مفصلاً وثاقباً ومهنياً. استخدم لغة متطورة مع الحفاظ على الدعم. أقصى 7 جمل مع تحليل أعمق.",
            'turkish': "Türkçe yanıt verin. Detaylı, anlayışlı ve profesyonel terapötik rehberlik sağlayın. Destekleyici kalırken sofistike dil kullanın. Daha derin analizle en fazla 7 cümle."
        }
    }
    
    # Seviyeye göre dil talimatını seç
    level_instructions = language_instructions.get(mode, language_instructions['intermediate'])
    current_language_instruction = level_instructions.get(language, level_instructions['english'])
    
    # Mod bazlı prompt'lar
    mode_prompts = {
        'aile': {
            'english': f"You are a family therapist psychologist. You specialize in family relationships, parenting, sibling relationships, and family communication. The user said: '{user_input}'. Please provide a family-focused, supportive, and constructive response. {current_language_instruction}",
            'spanish': f"Eres un psicólogo terapeuta familiar. Te especializas en relaciones familiares, crianza, relaciones entre hermanos y comunicación familiar. El usuario dijo: '{user_input}'. Por favor proporciona una respuesta enfocada en la familia, de apoyo y constructiva. {current_language_instruction}",
            'french': f"Vous êtes un psychologue thérapeute familial. Vous vous spécialisez dans les relations familiales, la parentalité, les relations fraternelles et la communication familiale. L'utilisateur a dit: '{user_input}'. Veuillez fournir une réponse axée sur la famille, de soutien et constructive. {current_language_instruction}",
            'korean': f"당신은 가족 치료 심리학자입니다. 가족 관계, 육아, 형제 관계, 가족 소통에 전문가입니다. 사용자가 말했습니다: '{user_input}'. 가족 중심적이고 지원적이며 건설적인 답변을 제공해 주세요. {current_language_instruction}",
            'japanese': f"あなたは家族療法心理学者です。家族関係、子育て、兄弟関係、家族のコミュニケーションを専門としています。ユーザーは言いました：'{user_input}'。家族に焦点を当てた、支援的で建設的な回答を提供してください。{current_language_instruction}",
            'arabic': f"أنت طبيب نفساني معالج أسري. تتخصص في العلاقات الأسرية وتربية الأطفال والعلاقات بين الإخوة والتواصل الأسري. قال المستخدم: '{user_input}'. يرجى تقديم رد يركز على الأسرة وداعم وبناء. {current_language_instruction}",
            'turkish': f"Sen aile terapisti bir psikologsun. Aile ilişkileri, ebeveynlik, kardeş ilişkileri ve aile içi iletişim konularında uzmanlaşmışsın. Kullanıcı şunu dedi: '{user_input}'. Lütfen aile odaklı, destekleyici ve yapıcı bir yanıt ver. {current_language_instruction}"
        },
        'ask': {
            'english': f"You are a love and relationship therapist psychologist. You specialize in romantic relationships, love life, communication problems, and personal development. The user said: '{user_input}'. Please provide a relationship-focused, understanding, and supportive response. {current_language_instruction}",
            'spanish': f"Eres un psicólogo terapeuta de amor y relaciones. Te especializas en relaciones románticas, vida amorosa, problemas de comunicación y desarrollo personal. El usuario dijo: '{user_input}'. Por favor proporciona una respuesta enfocada en las relaciones, comprensiva y de apoyo. {current_language_instruction}",
            'french': f"Vous êtes un psychologue thérapeute de l'amour et des relations. Vous vous spécialisez dans les relations romantiques, la vie amoureuse, les problèmes de communication et le développement personnel. L'utilisateur a dit: '{user_input}'. Veuillez fournir une réponse axée sur les relations, compréhensive et de soutien. {current_language_instruction}",
            'korean': f"당신은 사랑과 관계 치료 심리학자입니다. 로맨틱한 관계, 연애 생활, 소통 문제, 개인 발전에 전문가입니다. 사용자가 말했습니다: '{user_input}'. 관계 중심적이고 이해심 많으며 지원적인 답변을 제공해 주세요. {current_language_instruction}",
            'japanese': f"あなたは愛と関係療法心理学者です。ロマンチックな関係、恋愛生活、コミュニケーションの問題、個人の成長を専門としています。ユーザーは言いました：'{user_input}'。関係に焦点を当てた、理解力があり支援的な回答を提供してください。{current_language_instruction}",
            'arabic': f"أنت طبيب نفساني معالج للحب والعلاقات. تتخصص في العلاقات الرومانسية والحياة العاطفية ومشاكل التواصل والتطور الشخصي. قال المستخدم: '{user_input}'. يرجى تقديم رد يركز على العلاقات ومتفهم وداعم. {current_language_instruction}",
            'turkish': f"Sen aşk ve ilişki terapisti bir psikologsun. Romantik ilişkiler, aşk hayatı, iletişim problemleri ve kişisel gelişim konularında uzmanlaşmışsın. Kullanıcı şunu dedi: '{user_input}'. Lütfen ilişki odaklı, anlayışlı ve destekleyici bir yanıt ver. {current_language_instruction}"
        },
        'akademik': {
            'english': f"You are an academic advisor and educational psychologist. You specialize in study techniques, exam stress, career planning, and student life. The user said: '{user_input}'. Please provide an academically focused, motivating, and practical response. {current_language_instruction}",
            'spanish': f"Eres un asesor académico y psicólogo educativo. Te especializas en técnicas de estudio, estrés de exámenes, planificación de carrera y vida estudiantil. El usuario dijo: '{user_input}'. Por favor proporciona una respuesta enfocada académicamente, motivadora y práctica. {current_language_instruction}",
            'french': f"Vous êtes un conseiller académique et psychologue de l'éducation. Vous vous spécialisez dans les techniques d'étude, le stress des examens, la planification de carrière et la vie étudiante. L'utilisateur a dit: '{user_input}'. Veuillez fournir une réponse axée sur l'académique, motivante et pratique. {current_language_instruction}",
            'korean': f"당신은 학업 상담사이자 교육 심리학자입니다. 공부 기법, 시험 스트레스, 진로 계획, 학생 생활에 전문가입니다. 사용자가 말했습니다: '{user_input}'. 학업 중심적이고 동기부여적이며 실용적인 답변을 제공해 주세요. {current_language_instruction}",
            'japanese': f"あなたは学術アドバイザー兼教育心理学者です。勉強法、試験ストレス、キャリアプランニング、学生生活を専門としています。ユーザーは言いました：'{user_input}'。学術に焦点を当てた、動機付けがあり実用的な回答を提供してください。{current_language_instruction}",
            'arabic': f"أنت مستشار أكاديمي وطبيب نفساني تربوي. تتخصص في تقنيات الدراسة وضغط الامتحانات والتخطيط المهني وحياة الطالب. قال المستخدم: '{user_input}'. يرجى تقديم رد يركز على الأكاديمية ومحفز وعملي. {current_language_instruction}",
            'turkish': f"Sen akademik danışman ve eğitim psikoloğusun. Ders çalışma teknikleri, sınav stresi, kariyer planlaması ve öğrenci yaşamı konularında uzmanlaşmışsın. Kullanıcı şunu dedi: '{user_input}'. Lütfen akademik odaklı, motive edici ve pratik bir yanıt ver. {current_language_instruction}"
        },
        'serbest': {
            'english': f"You are a general therapist. You can support the user with any type of problem. The user said: '{user_input}'. Please provide a supportive, understanding, and constructive response. {current_language_instruction}",
            'spanish': f"Eres un terapeuta general. Puedes apoyar al usuario con cualquier tipo de problema. El usuario dijo: '{user_input}'. Por favor proporciona una respuesta de apoyo, comprensiva y constructiva. {current_language_instruction}",
            'french': f"Vous êtes un thérapeute général. Vous pouvez soutenir l'utilisateur avec tout type de problème. L'utilisateur a dit: '{user_input}'. Veuillez fournir une réponse de soutien, compréhensive et constructive. {current_language_instruction}",
            'korean': f"당신은 일반 치료사입니다. 모든 종류의 문제로 사용자를 지원할 수 있습니다. 사용자가 말했습니다: '{user_input}'. 지원적이고 이해심 많으며 건설적인 답변을 제공해 주세요. {current_language_instruction}",
            'japanese': f"あなたは一般的なセラピストです。あらゆる種類の問題でユーザーをサポートできます。ユーザーは言いました：'{user_input}'。支援的で理解力があり建設的な回答を提供してください。{current_language_instruction}",
            'arabic': f"أنت معالج عام. يمكنك دعم المستخدم مع أي نوع من المشاكل. قال المستخدم: '{user_input}'. يرجى تقديم رد داعم ومتفهم وبناء. {current_language_instruction}",
            'turkish': f"Sen genel bir terapistsin. Kullanıcının her türlü sorununa destek olabilirsin. Kullanıcı şunu dedi: '{user_input}'. Lütfen destekleyici, anlayışlı ve yapıcı bir yanıt ver. {current_language_instruction}"
        }
    }
    
    mode_languages = mode_prompts.get(selected_mode, mode_prompts['serbest'])
    prompt = mode_languages.get(language, mode_languages['english'])
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini Hatası:", e)
        error_messages = {
            'english': "I can't respond right now. Please try again later.",
            'spanish': "No puedo responder ahora. Por favor inténtalo de nuevo más tarde.",
            'french': "Je ne peux pas répondre maintenant. Veuillez réessayer plus tard.",
            'korean': "지금 답변할 수 없습니다. 나중에 다시 시도해 주세요.",
            'japanese': "今は返信できません。後でもう一度お試しください。",
            'arabic': "لا يمكنني الرد الآن. يرجى المحاولة مرة أخرى لاحقاً.",
            'turkish': "Şu anda yanıt veremiyorum. Lütfen sonra tekrar dene."
        }
        return error_messages.get(language, error_messages['english'])

def analyze_mood_and_extract_words(text, language="english"):
    # Dil bazlı duygu analizi kelimeleri
    mood_words = {
        'english': {
            'positive': ['good', 'great', 'wonderful', 'excellent', 'happy', 'glad', 'proud', 'successful', 'amazing', 'fantastic'],
            'negative': ['bad', 'sad', 'stressed', 'worried', 'afraid', 'angry', 'tired', 'depressed', 'terrible', 'awful']
        },
        'spanish': {
            'positive': ['bueno', 'excelente', 'maravilloso', 'feliz', 'contento', 'orgulloso', 'exitoso', 'increíble', 'fantástico'],
            'negative': ['malo', 'triste', 'estresado', 'preocupado', 'asustado', 'enojado', 'cansado', 'deprimido', 'terrible']
        },
        'french': {
            'positive': ['bon', 'excellent', 'merveilleux', 'heureux', 'content', 'fier', 'réussi', 'incroyable', 'fantastique'],
            'negative': ['mauvais', 'triste', 'stressé', 'inquiet', 'effrayé', 'fâché', 'fatigué', 'déprimé', 'terrible']
        },
        'korean': {
            'positive': ['좋다', '훌륭하다', '멋지다', '행복하다', '기쁘다', '자랑스럽다', '성공적이다', '놀랍다', '환상적이다'],
            'negative': ['나쁘다', '슬프다', '스트레스받다', '걱정하다', '무섭다', '화나다', '피곤하다', '우울하다', '끔찍하다']
        },
        'japanese': {
            'positive': ['良い', '素晴らしい', '素敵', '幸せ', '嬉しい', '誇り', '成功', '驚く', '素晴らしい'],
            'negative': ['悪い', '悲しい', 'ストレス', '心配', '怖い', '怒る', '疲れる', '落ち込む', 'ひどい']
        },
        'arabic': {
            'positive': ['جيد', 'ممتاز', 'رائع', 'سعيد', 'مسرور', 'فخور', 'ناجح', 'مذهل', 'رائع'],
            'negative': ['سيء', 'حزين', 'متوتر', 'قلق', 'خائف', 'غاضب', 'متعب', 'مكتئب', 'فظيع']
        },
        'turkish': {
            'positive': ['iyi', 'güzel', 'harika', 'mükemmel', 'mutlu', 'sevindim', 'gururlu', 'başarılı', 'inanılmaz', 'fantastik'],
            'negative': ['kötü', 'üzgün', 'stresli', 'endişeli', 'korkuyorum', 'sinirli', 'yorgun', 'bunalım', 'berbat', 'korkunç']
        }
    }
    
    text_lower = text.lower()
    current_mood_words = mood_words.get(language, mood_words['english'])
    
    # Duygu analizi
    positive_count = sum(1 for word in current_mood_words['positive'] if word in text_lower)
    negative_count = sum(1 for word in current_mood_words['negative'] if word in text_lower)
    
    # Dil bazlı duygu sonuçları
    mood_results = {
        'english': {'positive': 'happy', 'negative': 'sad', 'neutral': 'neutral'},
        'spanish': {'positive': 'feliz', 'negative': 'triste', 'neutral': 'neutral'},
        'french': {'positive': 'heureux', 'negative': 'triste', 'neutral': 'neutre'},
        'korean': {'positive': '행복', 'negative': '슬픔', 'neutral': '중립'},
        'japanese': {'positive': '幸せ', 'negative': '悲しい', 'neutral': '中立'},
        'arabic': {'positive': 'سعيد', 'negative': 'حزين', 'neutral': 'محايد'},
        'turkish': {'positive': 'mutlu', 'negative': 'üzgün', 'neutral': 'nötr'}
    }
    
    current_mood_results = mood_results.get(language, mood_results['english'])
    
    if positive_count > negative_count:
        mood = current_mood_results['positive']
    elif negative_count > positive_count:
        mood = current_mood_results['negative']
    else:
        mood = current_mood_results['neutral']
    
    # Kelime çıkarımı - 4 karakterden uzun kelimeler
    words = [w for w in text.split() if len(w) > 4 and w.isalpha()]
    
    return mood, words[:5]  # ilk 5 kelime öner





