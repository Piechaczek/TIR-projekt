from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import json
import mosquitto
import ssl
import certifi
import geopy.geocoders
from geopy.geocoders import Nominatim


class IrrigationSystem(App):
    def build(self):
        self.window = GridLayout()
        self.window.cols = 1
        self.window.size_hint = (0.6, 0.4)
        self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        self.projectName = Label(
            text="SYSTEM NAWADNIAJĄCY TIR 2021/22",
            font_size=24,
            color='#10a164'
        )
        self.window.add_widget(self.projectName)

        self.handle_sectors_no()

        return self.window

    def handle_sectors_no(self):
        self.query = Label(
            text="Podaj liczbę sektorów do nawadniania:",
            font_size=20,
            color='#10a164'
        )

        self.window.add_widget(self.query)

        self.input = TextInput(
            multiline=False,
            padding_x=(10, 2),
            padding_y=(10, 2),
            size_hint=(0.5, 0.5)
        )
        self.window.add_widget(self.input)

        self.button = Button(
            text="Zatwierdź",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#10a164',
            background_normal=""
        )
        self.button.bind(on_press=self.handle_sectors_no_callback)
        self.window.add_widget(self.button)

    def handle_sectors_no_callback(self, instance):
        sectors.append(int(self.input.text))
        sectors.append(0)

        for i in range(sectors[0]):
            sprinklers.append([])

        self.window.remove_widget(self.query)
        self.window.remove_widget(self.input)
        self.window.remove_widget(self.button)

        self.handle_sensors(sectors[1])

    def handle_sensors(self, sector):
        self.query = Label(
            text=f"Podaj ID sensora w sektorze {sector + 1}:",
            font_size=20,
            color='#10a164'
        )
        self.window.add_widget(self.query)

        self.input = TextInput(
            multiline=False,
            padding_x=(10, 2),
            padding_y=(10, 2),
            size_hint=(0.5, 0.5)
        )
        self.window.add_widget(self.input)

        self.button = Button(
            text="Zatwierdź",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#10a164',
            background_normal=""
        )
        self.button.bind(on_press=self.handle_sensor_callback)
        self.window.add_widget(self.button)

    def handle_sensor_callback(self, instance):
        if sectors[0] > sectors[1] + 1:
            sensors.append(self.input.text)

            self.window.remove_widget(self.query)
            self.window.remove_widget(self.input)
            self.window.remove_widget(self.button)

            sectors[1] += 1
            self.handle_sensors(sectors[1])
        else:
            sensors.append(self.input.text)
            self.window.remove_widget(self.query)
            self.window.remove_widget(self.input)
            self.window.remove_widget(self.button)

            sectors[1] = 0
            self.handle_sprinklers_no(sectors[1])

    def handle_sprinklers_no(self, sector):
        self.query = Label(
            text=f"Podaj liczbę zraszaczy w sektorze nr.{sector + 1}:",
            font_size=20,
            color='#10a164'
        )
        self.window.add_widget(self.query)

        self.input = TextInput(
            multiline=False,
            padding_x=(10, 2),
            padding_y=(10, 2),
            size_hint=(0.5, 0.5)
        )
        self.window.add_widget(self.input)

        self.button = Button(
            text="Zatwierdź",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#10a164',
            background_normal=""
        )
        self.button.bind(on_press=self.handle_sprinklers_no_callback)
        self.window.add_widget(self.button)

    def handle_sprinklers_no_callback(self, instance):
        sprinklersNo.append([int(self.input.text), 0])

        self.window.remove_widget(self.query)
        self.window.remove_widget(self.input)
        self.window.remove_widget(self.button)

        if sprinklersNo[sectors[1]][0] >= sprinklersNo[sectors[1]][1] + 1:
            sprinklersNo[sectors[1]][1] += 1
            self.handle_sprinkler(sectors[1], sprinklersNo[sectors[1]][1])
        elif sectors[0] > sectors[1] + 1:
            sectors[1] += 1
            self.handle_sprinklers_no(sectors[1])

    def handle_sprinkler(self, sector, sprinkler):
        self.query = Label(
            text=f"Podaj ID zraszacza nr.{sprinkler} w sektorze nr.{sector + 1}:",
            font_size=20,
            color='#10a164'
        )
        self.window.add_widget(self.query)

        self.input = TextInput(
            multiline=False,
            padding_x=(10, 2),
            padding_y=(10, 2),
            size_hint=(0.5, 0.5)
        )

        self.window.add_widget(self.input)

        self.button = Button(
            text="Zatwierdź",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#10a164',
            background_normal=""
        )
        self.button.bind(on_press=self.handle_sprinkler_callback)
        self.window.add_widget(self.button)

    def handle_sprinkler_callback(self, instance):
        sprinklers[sectors[1]].append(self.input.text)

        self.window.remove_widget(self.query)
        self.window.remove_widget(self.input)
        self.window.remove_widget(self.button)

        if sprinklersNo[sectors[1]][0] > sprinklersNo[sectors[1]][1]:
            sprinklersNo[sectors[1]][1] += 1
            self.handle_sprinkler(sectors[1], sprinklersNo[sectors[1]][1])
        elif sectors[0] > sectors[1] + 1:
            sectors[1] += 1
            self.handle_sprinklers_no(sectors[1])
        else:
            sectors[1] = 0
            self.handle_humidity(sectors[1])

    def handle_humidity(self, sector):
        self.query = Label(
            text=f"Podaj pożądaną wilgotność w sektorze nr.{sector + 1} [%]:",
            font_size=20,
            color='#10a164'
        )
        self.window.add_widget(self.query)

        self.input = TextInput(
            multiline=False,
            padding_x=(10, 2),
            padding_y=(10, 2),
            size_hint=(0.5, 0.5)
        )

        self.window.add_widget(self.input)

        self.button = Button(
            text="Zatwierdź",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#10a164',
            background_normal=""
        )
        self.button.bind(on_press=self.handle_humidity_callback)
        self.window.add_widget(self.button)

    def handle_humidity_callback(self, instance):
        desiredHumidity.append(int(self.input.text))

        self.window.remove_widget(self.query)
        self.window.remove_widget(self.input)
        self.window.remove_widget(self.button)

        if sectors[0] > sectors[1] + 1:
            sectors[1] += 1
            self.handle_humidity(sectors[1])
        else:
            self.handle_weather()

    def handle_weather(self):
        self.query = Label(
            text=f"Podaj miasto dla którego ma zostać sprawdzona prognoza pogody:",
            font_size=20,
            color='#10a164'
        )
        self.window.add_widget(self.query)

        self.input = TextInput(
            multiline=False,
            padding_x=(10, 2),
            padding_y=(10, 2),
            size_hint=(0.5, 0.5)
        )

        self.window.add_widget(self.input)

        self.button = Button(
            text="Zatwierdź",
            size_hint=(1, 0.5),
            bold=True,
            background_color='#10a164',
            background_normal=""
        )
        self.button.bind(on_press=self.handle_weather_callback)
        self.window.add_widget(self.button)

    def handle_weather_callback(self, instance):
        city.append(self.input.text)

        self.window.remove_widget(self.query)
        self.window.remove_widget(self.input)
        self.window.remove_widget(self.button)

        self.handle_data();

    def handle_data(self):
        data = send_data()

        self.info2 = Label(
            text=f"Wysłano dane:\n{data}",
            text_size=[600, 100],
            font_size=18,
            color='#10a164'
        )
        self.window.add_widget(self.info2)


def handle_weather_forecast(data, city):
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    geolocator = Nominatim(user_agent="irrigation_system")
    location = geolocator.geocode(city)
    data["lat"] = location.latitude
    data["lon"] = location.longitude


def send_data():
    mqttc = mosquitto.Mosquitto()
    mqttc.connect("broker.emqx.io", 1883, 60)

    data = {"sectors": []}

    for i in range(1, sectors[0] + 1):
        sectorObject = {
            "id": i,
            "sensor_id": sensors[i - 1],
            "desired_humidity": desiredHumidity[i - 1],
            "sprinklers": sprinklers[i - 1]
        }

        data["sectors"].append(sectorObject)

    handle_weather_forecast(data, city[0])

    mqttc.publish("agh/iot/project9/config", json.dumps(data), retain=True)

    return data


if __name__ == "__main__":
    sensors = []
    sprinklersNo = []
    sprinklers = []
    desiredHumidity = []
    sectors = []
    city = []

    IrrigationSystem().run()
