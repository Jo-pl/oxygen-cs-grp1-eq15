import json
import logging
import requests
import unittest
from unittest.mock import MagicMock, patch
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from main import Main

class MainTests(unittest.TestCase):
    def setUp(self):
        self.main = Main()
        

    def main_instance():
        return Main()

    def tearDown(self):
        del self.main

    '''
    def test_setSensorHub(self):
        # Create a MagicMock instance for HubConnectionBuilder
        hub_builder_mock = MagicMock()

        # Patch the HubConnectionBuilder class with the mock object
        with patch('main.HubConnectionBuilder', return_value=hub_builder_mock):
            # Create an instance of the Main class
            main_instance = Main()

            # Call the setSensorHub method
            main_instance.setSensorHub()

            # Assert that HubConnectionBuilder is called with the expected parameters
            hub_builder_mock.return_value.with_url.assert_called_once_with(f"{main_instance.HOST}/SensorHub?token={main_instance.TOKEN}")
            hub_builder_mock.return_value.configure_logging.assert_called_once_with(logging.INFO)
            hub_builder_mock.return_value.with_automatic_reconnect.assert_called_once_with({
                "type": "raw",
                "keep_alive_interval": 10,
                "reconnect_interval": 5,
                "max_attempts": 999,
            })
            hub_builder_mock.return_value.build.assert_called_once()

            # Assert the event handlers are registered
            main_instance._hub_connection.on.assert_called_once_with("ReceiveSensorData", main_instance.onSensorDataReceived)
            main_instance._hub_connection.on_open.assert_called_once()
            main_instance._hub_connection.on_close.assert_called_once()
            main_instance._hub_connection.on_error.assert_called_once()''' 
    
    def test_analyzeDatapoint_above_max(self):
        self.main.T_MAX = 30
        self.main.TICKETS = 5
        with patch('main.Main.sendActionToHvac') as mock_sendActionToHvac:
            self.main.analyzeDatapoint("2023-07-05", 35)
            mock_sendActionToHvac.assert_called_with("2023-07-05", "TurnOnAc", 5)

    def test_analyzeDatapoint_below_min(self):
        self.main.T_MIN = 10
        self.main.TICKETS = 3
        with patch('main.Main.sendActionToHvac') as mock_sendActionToHvac:
            self.main.analyzeDatapoint("2023-07-05", 5)
            mock_sendActionToHvac.assert_called_with("2023-07-05", "TurnOnHeater", 3)

    def test_sendActionToHvac(self):
        requests_mock = MagicMock()

        with patch('main.requests', requests_mock):
            mock_response = MagicMock()
            mock_response.text = '{"status": "success", "message": "Action sent"}'
            requests_mock.get.return_value = mock_response

            main_instance = Main()

            date = "2023-07-05"
            action = "cool"
            nbTick = 5
            main_instance.sendActionToHvac(date, action, nbTick)

            expected_url = f"{main_instance.HOST}/api/hvac/{main_instance.TOKEN}/{action}/{nbTick}"
            requests_mock.get.assert_called_once_with(expected_url, timeout=30)

            self.assertEqual(json.loads(mock_response.text), {"status": "success", "message": "Action sent"})

if __name__ == '__main__':
    unittest.main()