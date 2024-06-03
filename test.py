import unittest
import json
from urllib import request, parse
import threading
import time
from wsgiref.simple_server import make_server
from pytz_app import application

class TestApp(unittest.TestCase):
    BASE_URL = 'http://localhost:5555'
    server_thread = None

    @classmethod
    def setUpClass(cls):
        # Запуск сервера в отдельном потоке
        def start_server():
            with make_server('', 5555, application) as httpd:
                cls.server = httpd
                print("Serving on port 5555...")
                httpd.serve_forever()

        cls.server_thread = threading.Thread(target=start_server)
        cls.server_thread.setDaemon(True)
        cls.server_thread.start()
        time.sleep(1)  # Даем серверу время для запуска

    @classmethod
    def tearDownClass(cls):
        # Остановка сервера
        if cls.server:
            cls.server.shutdown()
            cls.server.server_close()
            cls.server_thread.join()

    def test_get_gmt(self):
        # Тестирование GET запроса для получения текущего времени в UTC
        print("Testing GET /")
        try:
            response = request.urlopen(self.BASE_URL)
            self.assertEqual(response.status, 200)
            response_body = response.read()
            print(f"Response body: {response_body}")
            self.assertIn(b'Current time in UTC', response_body)
        except Exception as e:
            print(f"Error during test_get_gmt: {e}")
            self.fail(f"test_get_gmt failed: {e}")

    def test_get_specific_timezone(self):
        # Тестирование GET запроса для получения текущего времени в указанной временной зоне
        print("Testing GET /Europe/Moscow")
        try:
            response = request.urlopen(f"{self.BASE_URL}/Europe/Moscow")
            self.assertEqual(response.status, 200)
            response_body = response.read()
            print(f"Response body: {response_body}")
            self.assertIn(b'Current time in Europe/Moscow', response_body)
        except Exception as e:
            print(f"Error during test_get_specific_timezone: {e}")
            self.fail(f"test_get_specific_timezone failed: {e}")

    def test_post_convert(self):
        # Тестирование POST запроса для конвертации времени из одной временной зоны в другую
        print("Testing POST /api/v1/convert")
        try:
            data = {
                "date": "20.12.2024 22:21:05",
                "tz": "EST",
                "target_tz": "Europe/Moscow"
            }
            req = request.Request(f"{self.BASE_URL}/api/v1/convert", method="POST")
            req.add_header('Content-Type', 'application/json')
            response = request.urlopen(req, data=json.dumps(data).encode('utf-8'))
            self.assertEqual(response.status, 200)
            response_body = response.read()
            print(f"Response body: {response_body}")
            self.assertIn(b'date', response_body)
        except Exception as e:
            print(f"Error during test_post_convert: {e}")
            self.fail(f"test_post_convert failed: {e}")

    def test_post_datediff(self):
        # Тестирование POST запроса для вычисления разницы между двумя датами в секундах
        print("Testing POST /api/v1/datediff")
        try:
            data = {
                "first_date": "12.06.2024 22:21:05",
                "first_tz": "EST",
                "second_date": "12:30pm 2024-02-01",
                "second_tz": "Europe/Moscow"
            }
            req = request.Request(f"{self.BASE_URL}/api/v1/datediff", method="POST")
            req.add_header('Content-Type', 'application/json')
            response = request.urlopen(req, data=json.dumps(data).encode('utf-8'))
            self.assertEqual(response.status, 200)
            response_body = response.read()
            print(f"Response body: {response_body}")
            self.assertIn(b'difference_in_seconds', response_body)
        except Exception as e:
            print(f"Error during test_post_datediff: {e}")
            self.fail(f"test_post_datediff failed: {e}")

if __name__ == '__main__':
    # Запуск тестов
    unittest.main()
