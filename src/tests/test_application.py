import paho.mqtt.client as mqtt
import time
from json import loads
from datetime import datetime

# O correto envio das mensagens com QoS = 1;
def test_message_rate_confirmation():
    # Configurações da taxa de disparo
    target_message_rate = 1  # mensagens por segundo
    duration = 60  # segundos
    acceptable_error_margin = 0.1  # 10%

    client_sub = mqtt.Client()
    client_sub.connect("localhost", 1891, 60)
    client_sub.subscribe("test/topic", qos=1)

    # Iniciar loop em segundo plano para o subscriber
    client_sub.loop_start()

    client_pub = mqtt.Client()
    client_pub.connect("localhost", 1891, 60)
    start_time = time.time()
    messages_sent = 0
    while time.time() - start_time < duration:
        messages_sent += 1
        time.sleep(1)
        client_pub.publish("test/topic", "Hello, MQTT!")

    client_pub.disconnect()
    client_sub.disconnect()
    actual_message_rate = messages_sent / duration

    lower_bound = target_message_rate * (1 - acceptable_error_margin)
    assert lower_bound <= actual_message_rate

# O correto recebimento das mensagens com QoS = 1;
def test_receieve_rate():
    message_count = 0
    def on_sub_message(client, userdata, message):
        global message_count
        message_count += 1

    client = mqtt.Client("python_subscriber")
    client.on_message = on_sub_message

    # Conecte ao broker
    client.connect("localhost", 1891, 60)

    # Configurações da taxa de disparo
    target_message_rate = 1  # mensagens por segundo
    duration = 60  # segundos
    acceptable_error_margin = 0.1  # 10%

    start_time = time.time()

    # Loop para manter o cliente executando e escutando por mensagens em segundo plano
    client.loop_start()

    client_pub = mqtt.Client()
    client_pub.connect("localhost", 1891, 60)

    while time.time() - start_time < duration:
        time.sleep(1)
        client_pub.publish("test/topic", "Hello, MQTT!")

    client_pub.disconnect()
    client.disconnect()

    actual_message_rate = message_count / duration
    lower_bound = target_message_rate * (1 - acceptable_error_margin)
    assert lower_bound <= actual_message_rate

# A integridade das mensagens recebidas, garantindo que o subscriber não distorce as informações recebidas;
def test_mqtt_integrity():
    received_messages = []

    def on_message(client, userdata, msg):
        received_messages.append(msg.payload.decode())

    # Configurar o subscriber
    client_sub = mqtt.Client()
    client_sub.on_message = on_message
    client_sub.connect("localhost", 1891, 60)
    client_sub.subscribe("test/topic", qos=1)

    # Iniciar loop em segundo plano para o subscriber
    client_sub.loop_start()

    # Enviar mensagem do Publisher
    client_pub = mqtt.Client()
    client_pub.connect("localhost", 1891, 60)
    client_pub.publish("test/topic", "Hello, MQTT!")

    # Esperar um pouco para a mensagem ser recebida
    time.sleep(2)

    # Verificar se a mensagem foi recebida corretamente
    assert received_messages[-1] == "Hello, MQTT!"

    # Desconectar os clientes
    client_pub.disconnect()
    client_sub.disconnect()


def test_payload_entirely_receieved():
    received_message = ""

    sensor_data = {
    "id": ["lj01f01", "lf01f01", "lf01f01", "lj02g01", "lj02g01", "lj02g01"], 
    "tipo": ["freezer", "freezer", "freezer", "geladeira", "geladeira", "geladeira"], 
    "temperatura": [-18, -27, -10, 11, -1, 5]
    }

    def on_message(client, userdata, message):
        global received_message
        json_string = message.payload.decode()
        json_string = json_string.replace("'", '"')
        json_string = loads(json_string)
        received_message = json_string
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
    client.loop_start()

    # Configuração do cliente
    client_pub = mqtt.Client("py-publisher")

    # Conecte ao broker
    client_pub.connect("localhost", 1891, 60)

    def show_sensor_data():
        global x
        x = 0
        if x < len(sensor_data["id"]):
            sensor_id = sensor_data["id"][x]
            sensor_type = sensor_data["tipo"][x]
            sensor_temp = sensor_data["temperatura"][x]
            x += 1

            sensor_info = {
                    "id": sensor_id,
                    "tipo": sensor_type,
                    "temperatura": sensor_temp,
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }

            return sensor_info
        
    sensor_info = show_sensor_data()
    message = "" + str(sensor_info)
    client.publish(f"store/test", message)

    assert received_message is not None


def program_alarms(input_wanted):
    sensor_data = {
    "id": ["lj01f01", "lf01f01", "lf01f01", "lj02g01", "lj02g01", "lj02g01"], 
    "tipo": ["freezer", "freezer", "freezer", "geladeira", "geladeira", "geladeira"], 
    "temperatura": [-18, -27, -10, 11, -1, 5]
    }
    sensor_id = sensor_data["id"][input_wanted]
    sensor_type = sensor_data["tipo"][input_wanted]
    sensor_temp = sensor_data["temperatura"][input_wanted]

    temp_alta = "[ALERTA: TEMPERATURA ALTA]"
    temp_baixa = "[ALERTA: TEMPERATURA BAIXA]"

    if sensor_type.lower() == 'freezer':
        if int(sensor_temp) > -15:
            alert = temp_alta
        elif int(sensor_temp) < -25:
            alert = temp_baixa
        else:
            alert = ""
    elif sensor_type.lower() == 'geladeira':
        if int(sensor_temp) > 10:
            alert = temp_alta
        elif int(sensor_temp) < 2:
            alert = temp_baixa
        else:
            alert = ""

    return sensor_id, sensor_type, sensor_temp, alert

def test_freezer_alert_down():
    sensor_id , sensor_type, sensor_temp, alert = program_alarms(1)

    assert alert == "[ALERTA: TEMPERATURA BAIXA]"

def test_freezer_alert_up():
    sensor_id , sensor_type, sensor_temp, alert = program_alarms(2)

    assert alert == "[ALERTA: TEMPERATURA ALTA]"

def test_freezer_alert_ok():
    sensor_id , sensor_type, sensor_temp, alert = program_alarms(0)

    assert alert == ""

def test_geladeira_alert_down():
    sensor_id , sensor_type, sensor_temp, alert = program_alarms(4)

    assert alert == "[ALERTA: TEMPERATURA BAIXA]"

def test_geladeira_alert_up():
    sensor_id , sensor_type, sensor_temp, alert = program_alarms(3)

    assert alert == "[ALERTA: TEMPERATURA ALTA]"

def test_geladeira_alert_ok():
    sensor_id , sensor_type, sensor_temp, alert = program_alarms(5)

    assert alert == ""