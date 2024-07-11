
#### `server.py`
```python
import select
import socket
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_ADDRESS = ('localhost', 8686)
MAX_CONNECTIONS = 10

INPUTS = []
OUTPUTS = []

def get_non_blocking_server_socket():
    """
    Создаем и возвращаем неблокирующий серверный сокет
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind(SERVER_ADDRESS)
    server.listen(MAX_CONNECTIONS)
    logging.info(f"Server started on {SERVER_ADDRESS}")
    return server

def handle_new_connection(server):
    """
    Обработка нового подключения к серверу
    """
    connection, client_address = server.accept()
    connection.setblocking(0)
    INPUTS.append(connection)
    logging.info(f"New connection from {client_address}")

def handle_readable(resource):
    """
    Обработка данных от клиента
    """
    try:
        data = resource.recv(1024)
        if data:
            logging.info(f"Received data: {data.decode('utf-8')}")
            if resource not in OUTPUTS:
                OUTPUTS.append(resource)
        else:
            clear_resource(resource)
    except ConnectionResetError:
        clear_resource(resource)

def clear_resource(resource):
    """
    Метод очистки ресурсов использования сокета
    """
    if resource in OUTPUTS:
        OUTPUTS.remove(resource)
    if resource in INPUTS:
        INPUTS.remove(resource)
    resource.close()
    logging.info(f"Closed connection {resource}")

def handle_writable(resource):
    """
    Обработка записи данных в сокет
    """
    try:
        resource.send(b'Hello from server!')
        OUTPUTS.remove(resource)
    except OSError:
        clear_resource(resource)

if __name__ == '__main__':
    server_socket = get_non_blocking_server_socket()
    INPUTS.append(server_socket)

    logging.info("Server is running, please, press Ctrl+C to stop")
    try:
        while INPUTS:
            readables, writables, exceptional = select.select(INPUTS, OUTPUTS, INPUTS)
            for resource in readables:
                if resource is server_socket:
                    handle_new_connection(server_socket)
                else:
                    handle_readable(resource)

            for resource in writables:
                handle_writable(resource)
                
            for resource in exceptional:
                clear_resource(resource)
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    finally:
        for resource in INPUTS:
            resource.close()
        logging.info("Server shutdown complete")
