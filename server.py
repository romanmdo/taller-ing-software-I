from wsgiref.simple_server import make_server
import json

d = {}
prox = 1

def web_app(environ, start_response):
    global d
    global prox

    status = '200 OK'
    method = environ["REQUEST_METHOD"]
    path = environ["PATH_INFO"].split("/")
    cuerpo_respuesta = b'' 

    if len(path) == 2 and path[1] == 'tasks':
        if method == 'GET':
            cuerpo_respuesta = json.dumps(d).encode("utf-8")

        elif method == 'POST':
            status = '201 Created'
            content_length = int(environ.get("CONTENT_LENGTH", 0))
            body = environ['wsgi.input'].read(content_length)

            data = json.loads(body)
            d[prox] = data
            data["id"] = prox
            prox += 1

            cuerpo_respuesta = json.dumps(data).encode("utf-8")

        else:
            status = '405 Method Not Allowed'

    elif len(path) == 3 and path[1] == 'tasks' and path[2].isdigit():
        tarea_id = int(path[2])
        
        if method == 'GET':
            if tarea_id in d:
                cuerpo_respuesta = json.dumps(d[tarea_id]).encode("utf-8")
            else:
                status = '404 Not Found'
        elif method == 'PATCH':
            if tarea_id in d:
                content_length = int(environ.get("CONTENT_LENGTH", 0))
                body = environ['wsgi.input'].read(content_length)
                data = json.loads(body)
                d[tarea_id].update(data)

                cuerpo_respuesta = json.dumps(d[tarea_id]).encode("utf-8")

            else:
                status = '404 Not Found'
        elif method == 'DELETE':
            if tarea_id in d:
                del d[tarea_id]
            else:
                status = '404 Not Found'
        else:
            status = '405 Method Not Allowed'

    else:
        status = '404 Not Found'

    headers = [("Content-Type", "application/json")]
    start_response(status, headers)
    
    return [cuerpo_respuesta]


with make_server("", 9292, web_app) as server:
    print("Listening on http://localhost:9292")
    server.serve_forever()