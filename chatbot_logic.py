from google.generativeai import configure, GenerativeModel

configure(api_key="AIzaSyBSJPdaz2kPVvh89gkPJ4IUpjFVvhD8VB0")

model = GenerativeModel("gemini-1.5-flash")

def get_chatbot_response(user_input, mode="serbest"):
    prompt = (
        f"{mode} konulu bir terapistsin. Kullanıcı şunu dedi: '{user_input}'\n"
        "Lütfen cevabını en fazla 5 cümle ile, kısa ve öz olarak ver.\n"
        "Senin cevabın:"
        )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini Hatası:", e)
        return "Şu anda yanıt veremiyorum. Lütfen sonra tekrar dene."






