"""
Fast API ile gemini 2.5 falsh doktor asistanını bir web servise çevir
Her kullanıcı için ayrı bir memory yani sohbet geçmişi tutalım

"""

# gerekli kütüphaneler
import os
from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel # istek ve yanıt şemaları için
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory # hafıza saklamak için
from langchain.chains import ConversationChain # llm ve memory'i birleştirmek için

# ortam değişkenlerini yükleme
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set it in the .env file.")

# fast api tanımla
app = FastAPI(title="Doktor Asistanı API", description="Google Gemini 2.5 Flash ile çalışan bir doktor asistanı API'si")

# llm tanımla
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7, # cevap çeşitliliği 0-garantici 1-yaratıcı
    google_api_key=api_key 
)

# her kullanıcı için memory yapılandırması
user_memories: Dict[str, ConversationBufferMemory] = {}

# istek ve yanıt şemalarını tanımla
class ChatRequest(BaseModel): # kullanıcının gönderdiği mesaj
    name: str
    age: int
    message: str

class ChatResponse(BaseModel): # asistanın vereceği cevap
    response: str


# sohbet endpoint'i oluştur

@app.post("/chat", response_model=ChatResponse)
async def chat_with_doctor(request: ChatRequest):
    try:
        # kullanııcya özel hafıza oluştur
        if request.name not in user_memories: # kullanıcı yoksa oluştur
            user_memories[request.name] = ConversationBufferMemory(return_messages=True)

        memory = user_memories[request.name] # kullanıcı varsa getir

        # ilk konuşma eğer memory boşsa giriş bağlamı ekle
        if len(memory.chat_memory.messages) == 0:
            intro = (
                f"Sen bir doktor asistanısın. Kullanıcının adı {request.name}, yaşı {request.age}. "
                "Sağlık sorunları hakkında konuşmak istiyor. "
                "Yaşına uygun, dikkatli ve nazik tavsiyeler ver; ismiyle hitap et, maksimum 3-5 cümle ile cevap ver. "
            )
            memory.chat_memory.add_user_message(intro)

        # llm + memory ile chain oluştur (sohbet zinciri)
        conversation = ConversationChain(
            llm=llm,
            memory=memory,
            verbose=True # arka plandaki işlemleri terminalde görmek istemiyoruz
        )

        # modelden yanıt al
        reply = conversation.predict(input=request.message)

        # terminale hafızayı yazdır (isteğe bağlı, debug için)
        print(f"Memory for {request.name}")
        for idx, msg in enumerate(memory.chat_memory.messages,start=1):
            print(f"{idx:02d}. {msg.type.upper()}: {msg.content}")
        print("-" * 50)

        # api yanıtını döndür
        return ChatResponse(response=reply)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
              
