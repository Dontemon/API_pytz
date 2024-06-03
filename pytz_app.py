from wsgiref.simple_server import make_server
import json
from datetime import datetime
import pytz

def application(environ, start_response):
    try:
        # Получаем путь и метод запроса
        path = environ.get('PATH_INFO', '').lstrip('/')
        method = environ['REQUEST_METHOD']
        content_length = environ.get('CONTENT_LENGTH', '')

        try:
            # Получаем длину содержимого запроса
            content_length = int(content_length) if content_length else 0
        except ValueError:
            content_length = 0

        # Читаем тело запроса, если оно есть
        request_body = environ['wsgi.input'].read(content_length) if content_length else b''

        if method == 'GET':
            if path:
                try:
                    # Получаем временную зону из пути
                    tz = pytz.timezone(path)
                except pytz.UnknownTimeZoneError:
                    # Возвращаем ошибку, если временная зона неизвестна
                    start_response('400 Bad Request', [('Content-Type', 'text/html')])
                    return [b'Unknown timezone']
            else:
                # Если путь пустой, используем UTC
                tz = pytz.utc

            # Получаем текущее время в указанной временной зоне
            now = datetime.now(tz)
            response_body = f"<html><body><h1>Current time in {tz.zone} is {now.strftime('%Y-%m-%d %H:%M:%S')}</h1></body></html>"
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [response_body.encode('utf-8')]

        elif method == 'POST':
            if path == 'api/v1/convert':
                try:
                    # Разбираем тело запроса как JSON
                    data = json.loads(request_body)
                    date_str = data['date']
                    src_tz = pytz.timezone(data['tz'])
                    target_tz = pytz.timezone(data['target_tz'])

                    # Конвертируем дату/время из одной временной зоны в другую
                    src_date = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
                    src_date = src_tz.localize(src_date)
                    target_date = src_date.astimezone(target_tz)

                    response_body = json.dumps({"date": target_date.strftime('%Y-%m-%d %H:%M:%S'), "tz": target_tz.zone})
                    start_response('200 OK', [('Content-Type', 'application/json')])
                    return [response_body.encode('utf-8')]
                except Exception as e:
                    # Возвращаем ошибку при возникновении исключения
                    start_response('400 Bad Request', [('Content-Type', 'application/json')])
                    return [json.dumps({"error": str(e)}).encode('utf-8')]

            elif path == 'api/v1/datediff':
                try:
                    # Разбираем тело запроса как JSON
                    data = json.loads(request_body)
                    first_date_str = data['first_date']
                    first_tz = pytz.timezone(data['first_tz'])
                    second_date_str = data['second_date']
                    second_tz = pytz.timezone(data['second_tz'])

                    # Конвертируем даты/время в соответствующие временные зоны
                    first_date = first_tz.localize(datetime.strptime(first_date_str, '%d.%m.%Y %H:%M:%S'))

                    try:
                        # Пытаемся распарсить вторую дату в формате 'дд.мм.ГГГГ ЧЧ:ММ:СС'
                        second_date = second_tz.localize(datetime.strptime(second_date_str, '%d.%m.%Y %H:%M:%S'))
                    except ValueError:
                        # Если не удалось, пробуем распарсить в формате 'чч:ммпп ГГГГ-мм-дд'
                        second_date = second_tz.localize(datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d'))

                    # Вычисляем разницу в секундах между двумя датами
                    diff_seconds = int((second_date - first_date).total_seconds())

                    response_body = json.dumps({"difference_in_seconds": diff_seconds})
                    start_response('200 OK', [('Content-Type', 'application/json')])
                    return [response_body.encode('utf-8')]
                except Exception as e:
                    # Возвращаем ошибку при возникновении исключения
                    start_response('400 Bad Request', [('Content-Type', 'application/json')])
                    return [json.dumps({"error": str(e)}).encode('utf-8')]

        # Возвращаем 404, если запрашиваемый путь не найден
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'Not Found']
    except Exception as e:
        # Возвращаем ошибку сервера при возникновении неожиданного исключения
        start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
        return [f'Internal Server Error: {str(e)}'.encode('utf-8')]

if __name__ == '__main__':
    with make_server('', 5555, application) as server:
        print("Serving on port 5555...")
        server.serve_forever()