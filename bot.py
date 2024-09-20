
import requests 
import time
import re

# Configuración de Telegram
BOTS = [
    {
        'token': '8166977073:AAHnvl_SXz73f2lpQqIFtiR_vYfSLzSdsMs',
        'chat_id': '6887146335'
    },
    {
        'token': '8166977073:AAHnvl_SXz73f2lpQqIFtiR_vYfSLzSdsMs',
        'chat_id': '6557898799'  # Asegúrate de usar un chat_id diferente si es necesario
    }
]

mensaje = '¡Este es un mensaje de prueba!'
SOURCE_CHAT_IDS = [-1002137354432, 6557898799, 6887146335]  # Lista de chat IDs


# Enviar mensaje de prueba a cada bot
for bot in BOTS:
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{bot["token"]}/sendMessage'
    payload = {
        'chat_id': bot['chat_id'],
        'text': mensaje
    }
    response = requests.post(TELEGRAM_API_URL, data=payload)
    print(f'Mensaje enviado a {bot["chat_id"]} con bot {bot["token"]}: {response.status_code}, {response.json()}')

def formatear_ciudad(text):
    ciudades = {
        "MAT": "Matamoros][",
        "TIJ": "Tijuana][",
        "CJZ": "Ciudad Juarez][",  
        "GDL": "Guadalajara][",
        "HMO": "Hermosillo][",
        "MER": "Merida][",
        "MEX": "Mexico City][",
        "MTY": "Monterrey][",
        "NOG": "[Nogales][",
        "PVI": "PI ● ",
        "PV2": "P6 ● ",
        "PV3": "P3 ● ",
        "PV4": "P4 ● ",
        "PV5": "P5 ● ",
        "PV6": "P6 ● ",
        "● Cita Personal": "PI ● "
    }

    palabras = text.split()
    for i, palabra in enumerate(palabras):
        if palabra in ciudades:
            palabras[i] = ciudades[palabra]

    text = " ".join(palabras)
    text = re.sub(r'\d{1,2}:\d{2}\s?(AM|PM)', '', text)
    text = re.sub(r'Cazador Citas SARU|● Cita', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(\sPersonal)\d+', r'\1', text)
    text = text.strip()
    return text

def send_telegram_message(text, chat_id):
    formatted_text = formatear_ciudad(text)
    final_text = f"🇲🇽 [{formatted_text}]"
    
    for bot in BOTS:
        TELEGRAM_API_URL = f'https://api.telegram.org/bot{bot["token"]}/sendMessage'
        data = {
            'chat_id': bot['chat_id'],
            'text': final_text,
        }
        response = requests.post(TELEGRAM_API_URL, data=data)
        if response.status_code != 200:
            print(f"Error al enviar el mensaje a Telegram: {response.text}")

def get_updates(offset=None):
    url = f'https://api.telegram.org/bot{BOTS[0]["token"]}/getUpdates'
    params = {'timeout': 346, 'offset': offset}
    response = requests.get(url, params=params)
    return response.json()

def main():
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if updates.get('ok'):
                for update in updates.get('result', []):
                    message = update.get('message')
                    chat_id = message['chat']['id']
                    text = message.get('text')
                    
                    if message and chat_id in SOURCE_CHAT_IDS:
                        # Lógica para decidir qué bot recibir mensajes
                        if chat_id in [-1002137354432, 6557898799]:
                            send_telegram_message(text, '6557898799')  # Este bot recibe solo estos chats
                        if chat_id in SOURCE_CHAT_IDS:
                            send_telegram_message(text, '6887146335')  # Este bot recibe todos los chats
                            
                        offset = update['update_id'] + 1  # Actualiza el offset
            else:
                print(f"Error en la respuesta: {updates}")

        except requests.exceptions.RequestException as e:
            print(f"Error en la conexión: {e}")

        time.sleep(5)  # Espera antes de la próxima solicitud

if __name__ == '__main__':
    main()
