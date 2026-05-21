"""
Problem: 
    - Akıllı doktor asistanı: kullanıcının sağlık ile ilgili sorularını anlayan ve yanıtlayan bir  LLM tabanlı doktor asistanı (chatbot)
    - LLM: Google Gemini API 
    - Kişiselleştirme: kullanıcının adını ve yaşını bilerek ona göre cevap üretmeli 
    - Hafıza (Memory: Mesaj geçişini hatırlayarak diyaloğu ona göre sürdürmeli 

Çalışma ortamı:
    - ilk olarak terminal üzerinden çalıştır: doktor_asistani_terminal.py
        - tesst edebilmek için terminal üzerinden sorgu oluştur
    - Fastapi ile bir web servii oluştur: doktor_asistani_api.py
        - swagger ile test et

Veri Seti:
    - RAG yok, onun yerine prompt engineering ile LLM'yi yönlendireceğiz

Model Tanıtımı: Google Gemini: google gemini 2.5 flash
    - API üzerinden iletişimkuralım ve gerçek zamanlı sağlık önerileri alalım.

Kütüphaneler:
    - langchain: llm kütüphanesi, prompt yönetimi, memory, chain yapısı
    - FastAPI: web servisi oluşturmak için
    - uvicorn: FastAPI uygulamasını çalıştırmak için sunucu

Kurulumlar:
    pip install langchain-google-genai python-dotenv fastapi uvicorn


API KEY** 

"""

# gerekli kütüphaneler
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory # hafıza saklamak için
from langchain.chains import ConversationChain # llm ve memory'i birleştirmek için

import warnings
warnings.filterwarnings("ignore")

# ortam değişkenlerini yükleme
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it in the .env file.")

# llm tanımla
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7, # cevap çeşitliliği 0-garantici 1-yaratıcı
    google_api_key=api_key
)

# memory tanımla
memory = ConversationBufferMemory(return_messages=True)

# llm + memory ile chain oluştur
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True # arka plandaki işlemleri terminalde görmek için
)

# kullanıcı bilgileri ile kişiselleştirme
name=input("Lütfen adınızı girin: ")
age=input("Lütfen yaşınızı girin: ")
history= input("Geçmiş sağlık sorunlarınız var mı? Varsa kısaca yazın, yoksa 'yok' yazın: ")

"""
history = Yaklaşık 5 yıldır astım hastasıyım. Mevsim geçişlerinde nefes darlığım artıyor. Daha önce bronşit geçirdim ve düzenli olarak alerji ilacı kullanıyorum. Bunun dışında bilinen kronik bir hastalığım yok.
"""

# prompt tanımlama 
intro = (
    f"Sen bir doktor asistanısın. Kullanıcının adı {name}, yaşı {age} ve sağlık geçmişi: {history}. "
    "Sağlık sorunları hakkında konuşmak istiyor. "
    "Yaşına uygun, dikkatli ve nazik tavsiyeler ver; ismiyle hitap et, maksimum 3-5 cümle ile cevap ver. "
)

# başlangıç mesajını hafızaya kaydet
memory.chat_memory.add_user_message(intro)
print("Merhaba! Ben doktor asistanınızım. Size nasıl yardımcı olabilirim?")

# chatbot diyalog döngüsü

while True:
    # kullanıcı mesajı al
    user_msg = input(f"{name}: ")

    if user_msg.lower() in ["quit", "q"]:
        print("Görüşmek üzere! Sağlıklı günler dilerim.")
        break

    # chatbot cevabı üret
    reply = conversation.predict(input=user_msg)

    # cevabı yazdır
    print(f"Doktor Asistanı: {reply}")