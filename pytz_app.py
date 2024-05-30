from wsgiref.simple_server import make_server
import json
from datetime import datetime
import pytz

def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    method = environ['REQUEST_METHOD']
    content_length = int(environ.get('CONTENT_LENGTH', 0))
    request_body = environ['wsgi.input'].read(content_length) if content_length else b''
    
    if method == 'GET':
        # Обработка GET запроса для получения текущего времени в указанной временной зоне
        if path:
            try:
                tz = pytz.timezone(path)
            except pytz.UnknownTimeZoneError:
                start_response('400 Bad Request', [('Content-Type', 'text/html')])
                return [b'Unknown timezone']
        else:
            tz = pytz.utc
        
        now = datetime.now(tz)
        response_body = f"<html><body><h1>Current time in {tz.zone} is {now.strftime('%Y-%m-%d %H:%M:%S')}</h1></body></html>"
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [response_body.encode('utf-8')]

    elif method == 'POST':
        if path == 'api/v1/convert':
            # Обработка POST запроса для конвертации времени из одной временной зоны в другую
            data = json.loads(request_body)
            try:
                date_str = data['date']
                src_tz = pytz.timezone(data['tz'])
                target_tz = pytz.timezone(data['target_tz'])
                
                src_date = datetime.strptime(date_str, '%m.%d.%Y %H:%M:%S')
                src_date = src_tz.localize(src_date)
                target_date = src_date.astimezone(target_tz)
                
                response_body = json.dumps({"date": target_date.strftime('%Y-%m-%d %H:%M:%S'), "tz": target_tz.zone})
                start_response('200 OK', [('Content-Type', 'application/json')])
                return [response_body.encode('utf-8')]
            except Exception as e:
                start_response('400 Bad Request', [('Content-Type', 'application/json')])
                return [json.dumps({"error": str(e)}).encode('utf-8')]

        elif path == 'api/v1/datediff':
            # Обработка POST запроса для вычисления разницы между двумя датами в секундах
            data = json.loads(request_body)
            try:
                first_date_str = data['first_date']
                first_tz = pytz.timezone(data['first_tz'])
                second_date_str = data['second_date']
                second_tz = pytz.timezone(data['second_tz'])
                
                first_date = datetime.strptime(first_date_str, '%m.%d.%Y %H:%M:%S')
                first_date = first_tz.localize(first_date)
                
                second_date = datetime.strptime(second_date_str, '%I:%M%p %Y-%m-%d')
                second_date = second_tz.localize(second_date)
                
                diff_seconds = int((second_date - first_date).total_seconds())
                
                response_body = json.dumps({"difference_in_seconds": diff_seconds})
                start_response('200 OK', [('Content-Type', 'application/json')])
                return [response_body.encode('utf-8')]
            except Exception as e:
                start_response('400 Bad Request', [('Content-Type', 'application/json')])
                return [json.dumps({"error": str(e)}).encode('utf-8')]

    start_response('404 Not Found', [('Content-Type', 'text/html')])
    return [b'Not Found']

if __name__ == '__main__':
    # Запуск сервера на порту 5555
    with make_server('', 5555, application) as server:
        print("Serving on port 5555...")
        server.serve_forever()
