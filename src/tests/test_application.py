import paho.mqtt.client as mqtt
import time

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

def test_receieve_rate():
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