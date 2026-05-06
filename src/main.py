import socket
import os

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем TCP пакет
server.bind(("localhost", 8080)) # привязываем к localhost и порту
server.listen(1) # указываем сколько подключений одновременно может ожидать

print("Server started on http://localhost:8080")

while True:
    base_dir = os.path.dirname(os.path.abspath(__file__)) # определяем директорию текущего файла
    site_dir = os.path.join(base_dir, "..", "site") # определяем директорию сайта
    client_socket, address = server.accept() # принимаем подключение от клиента

    request = client_socket.recv(1024).decode() # получаем HTTP запрос и декодируем

    lines = request.split("\n") # разбиваем запрос на строки
    first_line = lines[0] # первая строка содержит метод, путь и версию

    method, path, version = first_line.split() # разделяем на GET /index.html HTTP/1.1

    if path == "/":
        response = (
        "HTTP/1.1 302 Found\r\n"
        "Location: /index.html\r\n"
        "\r\n"
        ) 
        client_socket.send(response.encode()) # отправляем редирект

    elif os.path.isfile(os.path.join(site_dir, path[1:])): # проверяем существует ли файл
        file_path = os.path.join(site_dir, path[1:]) # формируем путь к файлу

        if file_path.endswith(".html"):
            content_type = "text/html; charset=utf-8" # тип контента html
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read() # читаем файл как текст
            body = content.encode() # переводим в байты

        elif file_path.endswith(".css"):
            content_type = "text/css" # тип контента css
            with open(file_path, "r", encoding="utf-8") as f:
                body = f.read().encode() # читаем и сразу кодируем

        else:
            content_type = "application/octet-stream" # бинарные файлы (картинки и тд)
            with open(file_path, "rb") as f:
                body = f.read() # читаем как байты

        response = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"\r\n"
        ).encode() + body # соединяем заголовки и тело ответа

        client_socket.send(response) # отправляем файл клиенту

    else:
        response = (
        "HTTP/1.1 404 Not Found\r\n"
        "\r\n"
        "404"
        )
        client_socket.send(response.encode()) # отправляем 404 если файл не найден

    if method == "POST":
        body_data = request.split("\r\n\r\n")[1] # берем тело POST запроса
        print("POST data:", body_data) # выводим данные в консоль

    client_socket.close() # закрываем соединение