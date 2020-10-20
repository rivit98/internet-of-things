from VirtualCopernicusNG import TkCircuit

# initialize the circuit inside the

configuration = {
    "name": "CopernicusNG Weather Forecast",
    "sheet": "sheet_forecast.png",
    "width": 343,
    "height": 267,

    "servos": [
        {"x": 170, "y": 150, "length": 90, "name": "Servo 1", "pin": 17}
    ],
    "buttons": [
        {"x": 295, "y": 200, "name": "Button 1", "pin": 11},
        {"x": 295, "y": 170, "name": "Button 2", "pin": 12},
    ]
}

circuit = TkCircuit(configuration)


@circuit.run
def main():
    from time import sleep
    from gpiozero import AngularServo, Button
    import pyowm

    servo1 = AngularServo(17, min_angle=-90, max_angle=90)
    owm = pyowm.OWM('4526d487f12ef78b82b7a7d113faea64')
    weather_manager = owm.weather_manager()
    button1 = Button(11)
    button2 = Button(12)

    class CitySelector:
        def __init__(self):
            self._cities = [
                "Krakow,PL", "Istambul,TR", "Stockholm,SE", "Cairo,EG"
            ]
            self._current_city = 0

        def increment_iterator(self):
            self._current_city = self._current_city + 1
            self._current_city %= len(self._cities)

        def next_city(self):
            c = self._cities[self._current_city]
            self.increment_iterator()
            return c

        def reset_iterator(self):
            self._current_city = 0
            c = self._cities[self._current_city]
            self.increment_iterator()
            return c

    city_selector = CitySelector()

    def get_weather_status(city):
        weather = weather_manager.weather_at_place(city).weather
        return weather

    def status_to_angle(status: str):
        status = status.lower()
        try:
            return {
                "thunderstorm": 65,
                "drizzle": 30,
                "rain": 45,
                "snow": 50,
                "clear": -70,
                "clouds": 15,
                "fog": -5,
                "mist": 0
            }[status]
        except:
            print("Unknown status!")
            return -90

    def servo_update(angle):
        servo1.angle = angle

    def update(city):
        weather_status = get_weather_status(city)
        weather_desc = weather_status.status
        temperature = weather_status.temperature('celsius')['temp']
        angle = status_to_angle(weather_desc)
        print("{} - {}, {}°C - servo: {}deg".format(city, weather_desc, temperature, angle))
        servo_update(angle)

    button1.when_pressed = lambda: update(city_selector.next_city())
    button2.when_pressed = lambda: update(city_selector.reset_iterator())


    def test_servo():
        p = [
            "thunderstorm", "drizzle", "rain", "snow", "clear", "clouds", "fog"
        ]

        for s in p:
            a = status_to_angle(s)
            print("{} - {}".format(s, a))
            servo_update(a)
            sleep(3)

    # test_servo()

    button2.when_pressed()

    while True:
        sleep(0.1)
