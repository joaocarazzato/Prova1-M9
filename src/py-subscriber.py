import paho.mqtt.client as mqtt
from json import loads

# Callback quando uma mensagem é recebida do servidor.
def on_message(client, userdata, message):
    json_string = message.payload.decode()
    json_string = json_string.replace("'", '"')
    json_string = loads(json_string)

    temp_alta = "[ALERTA: TEMPERATURA ALTA]"
    temp_baixa = "[ALERTA: TEMPERATURA BAIXA]"

    if json_string['tipo'].lower() == 'freezer':
        if int(json_string['temperatura']) > -15:
            alert = temp_alta
        elif int(json_string['temperatura']) < -25:
            alert = temp_baixa
        else:
            alert = ""
    elif json_string['tipo'].lower() == 'geladeira':
        if int(json_string['temperatura']) > 10:
            alert = temp_alta
        elif int(json_string['temperatura']) < 2:
            alert = temp_baixa
        else:
            alert = ""
    print(f"{json_string['data']} - id: {json_string['id']} | {json_string['tipo']} | {str(json_string['temperatura'])} °C {alert}")

# Callback para quando o cliente recebe uma resposta CONNACK do servidor.
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker com código de resultado "+str(rc))
    # Inscreva no tópico aqui, ou se perder a conexão e se reconectar, então as
    # subscrições serão renovadas.
    client.subscribe("store/#")

# Configuração do cliente
client = mqtt.Client("python_subscriber")
client.on_connect = on_connect
client.on_message = on_message

# Conecte ao broker
client.connect("localhost", 1891, 60)

# Loop para manter o cliente executando e escutando por mensagens
client.loop_forever()