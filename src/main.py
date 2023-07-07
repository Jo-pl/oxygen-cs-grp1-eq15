"""
Manages the HVAC system
"""
import json
import time
import os
import logging
import requests
from signalrcore.hub_connection_builder import HubConnectionBuilder
import pymysql.cursors

class Main:
    """
    Main class to manage the HVAC system
    """
    def __init__(self):
        self._hub_connection = None
        self.HOST = os.environ.get('OXYGEN_HOST', 'http://34.95.34.5/')  # Setup your host here
        self.TOKEN = os.environ.get('OXYGEN_TOKEN', None)  # Setup your token here
        self.TICKETS = os.environ.get('OXYGEN_TICKETS', 5)  # Setup your tickets here
        self.T_MAX = os.environ.get('OXYGEN_T_MAX', 25)  # Setup your max temperature here
        self.T_MIN = os.environ.get('OXYGEN_T_MIN', 20)  # Setup your min temperature here
        self.DATABASE = os.environ.get('OXYGEN_DATABASE', 'localhost')  # Setup your database here
        self.DB_USER = os.environ.get('OXYGEN_DB_USER', 'oxygen')  # Setup your database here
        self.DB_PW = os.environ.get('OXYGEN_DB_PW', 'oxygen')  # Setup your database here
        self.DB_NAME = os.environ.get('OXYGEN_DB_NAME', 'oxygen')  # Setup your database here

        if self.TOKEN is None:
            raise Exception('Token missing')

        self.connection = pymysql.connect(host=self.DATABASE,
                                          user=self.DB_USER,
                                          password=self.DB_PW,
                                          database=self.DB_NAME,
                                          cursorclass=pymysql.cursors.DictCursor)

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def setup(self):
        self.setSensorHub()

    def start(self):
        self.setup()
        self._hub_connection.start()

        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setSensorHub(self):
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )

        self._hub_connection.on("ReceiveSensorData", self.onSensorDataReceived)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(lambda data: print(f"||| Connection errored: {data.error}"))

    def onSensorDataReceived(self, data):
        try:
            print(data[0]["date"] + " --> " + data[0]["data"])
            date = data[0]["date"]
            dp = float(data[0]["data"])
            #self.send_temperature_to_fastapi(date, dp) # No method "send_temperature_to_fastapi"?
            self.analyzeDatapoint(date, dp)
        except Exception as err:
            print(err)

    def analyzeDatapoint(self, date, data):
        if float(data) >= float(self.T_MAX):
            self.sendActionToHvac(date, "TurnOnAc", self.TICKETS)
        elif float(data) <= float(self.T_MIN):
            self.sendActionToHvac(date, "TurnOnHeater", self.TICKETS)

    def sendActionToHvac(self, date, action, nbTick):
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{nbTick}", timeout=30)
        details = json.loads(r.text)
        print(details)

    def send_event_to_database(self, timestamp, event):
        try:
            with self.connection:
                with self.connection.cursor() as cursor:
                    sql = "INSERT INTO sensordata (`data`) VALUES (%s)"
                    cursor.execute(sql, ('lorem ipsum'))

                self.connection.commit()
        except requests.exceptions.RequestException as e:
            print(e)


if __name__ == "__main__":
    main = Main()
    main.start()
