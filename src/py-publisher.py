import paho.mqtt.client as mqtt
import time
from datetime import datetime


sensor_data = {
    "id": ["lj01f01", "lf01f01", "lf01f01", "lj02g01", "lj02g01", "lj02g01"], 
    "tipo": ["freezer", "freezer", "freezer", "geladeira", "geladeira", "geladeira"], 
    "temperatura": [-18, -27, -10, 11, -1, 5]
    }
update_time = 1
x = 0

def publish_broker():
    # Configuração do cliente
    client = mqtt.Client("py-publisher")

    # Conecte ao broker
    client.connect("localhost", 1891, 60)
    # Loop para publicar mensagens continuamente
    try:
        while True:
            sensor_info = show_sensor_data()
            message = "" + str(sensor_info)
            if message == "nan":
                client.disconnect()
                print("Publicação encerrada.")
                quit()
            client.publish(f"store/test", message)
            print(f"Publicado: '{message}' no tópico: 'store/test'")
            time.sleep(float(update_time))
    except KeyboardInterrupt:
        print("Publicação encerrada.")

    client.disconnect()


def show_sensor_data():
    global x
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
        
    else:
        print("Publicação de dados finalizada.")
        return "nan"

def main():
    publish_broker()

if __name__ == "__main__":
    main()