import json
import time
import threading
import sys
import mosquitto

humidity = int(sys.argv[1])
rain = False if sys.argv[2] == "False" else True
time_to_dry = float(sys.argv[3])
mqqtc_server = sys.argv[4]
id = int(sys.argv[5])
sector_id = None
desired_humidity = None

working_sprinklers = []

mqttc = mosquitto.Mosquitto()

def on_connect(mqttc, obj, rc):
    print("rc: "+str(rc))

def on_message(mqttc, obj, msg):
    global sector_id, desired_humidity, rain
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    if msg.topic == "agh/iot/project9/config":
        try:
            msg_dict = json.loads(msg.payload)
            for sector in msg_dict["sectors"]:
                if sector["sensor_id"] == id:
                    sector_id = int(sector["id"])
                    desired_humidity = int(sector["desired_humidity"])
                    # mqttc.subscribe("agh/iot/project9/simulation/area/"+str(sector_id)+"/rain", 2)

        except Exception as e:
            print("json with incorrect format, "+str(e))

    elif msg.topic == "agh/iot/project9/sensor/request":
        mqttc.publish("agh/iot/project9/sensor/"+str(id)+"/humidity", str(humidity), 2, False)
    elif msg.topic == "agh/iot/project9/simulation/area/"+str(sector_id)+"/rain":
        try:
            sprinkling_data = json.loads(msg.payload)
            if str(sprinkling_data["rain"]).lower() != "none":
                rain = True if sprinkling_data["rain"].lower() == "true" else False
            else:
                sprinkler_id = int(sprinkling_data["sprinkler_id"])
                if str(sprinkling_data["is_watering"]).lower() == "true":
                    working_sprinklers.append(sprinkler_id)
                else:
                    working_sprinklers.remove(sprinkler_id)
        except Exception as e:
            print("json with incorrect format, " + str(e))




def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

def humidity_thread():
    global humidity, rain
    while True:
        if humidity > 0 and not rain and len(working_sprinklers) == 0:
            humidity -= 1
        if humidity < 100 and rain:
            humidity = humidity + 3 if humidity + 3 < 100 else 100
        if len(working_sprinklers) > 0 and humidity < 100:
            humidity = humidity + 2*len(working_sprinklers) if humidity + 2*len(working_sprinklers) < 100 else 100
        print("current humidity: "+str(humidity))
        print("is raining: "+str(rain))
        print("number of working sprinklers: "+str(len(working_sprinklers)))
        print("id: "+str(id))
        print("sector_id: "+str(sector_id))
        print("========================")
        time.sleep(time_to_dry)


mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_log = on_log
mqttc.connect(mqqtc_server, 1883, 60)

mqttc.subscribe("agh/iot/project9/sensor/request", 2)
mqttc.subscribe("agh/iot/project9/config", 2)
mqttc.subscribe("agh/iot/project9/simulation/area/+/rain", 2)

new_thread = threading.Thread(target=humidity_thread)

new_thread.start()

mqttc.loop_forever()
 