"""
terminal üzerinden fastapi web sunucu ile sohbet gerçekleştir. (post request)
api endpoint: /chat
"""

import requests # api'ye istek atmak için

# api adresi
API_URL = "http://127.0.0.1:8000/chat" # fastapi sunucumuzun çalıştığı adres ve endpoint

# başlangıçta kullanılan bilgileri al

name=input("Lütfen adınızı girin: ")
age=int(input("Lütfen yaşınızı girin: "))

print("Sohbet başladı. Çıkmak için quit yazınız.")

# kullanıcıdan mesajı alıp sunucuya gönderen bir döngü oluşturalım

while True:
    user_msg=input(f"{name}: ")

    if user_msg.lower() in ["quit", "q"]:
        print("Sohbet sonlandırıldı.")
        break

    # api ye gönderielcek veri paketi
    payload = {
        "name": name,
        "age": age,
        "message": user_msg
    }

    try: 
        # api'ye post isteği at, timeout 30 saniye
        response = requests.post(API_URL, json=payload, timeout=15)

        if response.status_code == 200:
            data = response.json()
            print(f"Doktor Asistanı: {data['response']}")
        else:
            print(f"API hatası: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"İstek hatası: {e}")

