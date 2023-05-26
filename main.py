import base64
import os
import socket
import ssl
import json
from datetime import datetime
import imghdr

SMTP_HOST = 'smtp.yandex.ru'
SMTP_PORT = 465


class Picture:
    def __init__(self, encoded: str, filename: str, filetype: str):
        self.encoded = encoded
        self.filename = filename
        self.filetype = filetype


with open('password.json', 'r', encoding='utf-8') as f1,\
        open("config.json", 'r', encoding='utf-8') as f2:
    password = json.load(f1)
    config = json.load(f2)
    SUBJECT_MESSAGE = config['Subject']
    USER_NAME_FROM = config['From']
    USER_NAME_TO = config['To']
    DIRECTORY = config['Directory']
    PASSWORD = password['password']


def request(user_socket, msg_request):  # передача данных по сокету и получение ответа
    user_socket.send((msg_request + '\n').encode('utf-8'))
    recv_data = user_socket.recv(65535)
    return recv_data


def build_message(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    current = datetime.now()
    boundary = "divide"
    headers = [
        f'Date: {current.strftime("%d/%m/%y")}',
        f'From: {USER_NAME_FROM}',
        f'To: {USER_NAME_TO}',
        f'Subject: {SUBJECT_MESSAGE}',
        "MIME-Version: 1.0",
        "Content-Type: multipart/mixed;",
        f"  boundary={boundary}",
        '',
    ]

    pictures = []
    for file in os.listdir(DIRECTORY):  # получаем все документы
        filetype = imghdr.what(f"{DIRECTORY}\\{file}")

        with open(f"{DIRECTORY}\\{file}", "rb") as pic:  # добовляем все докменты
            pictures.append(Picture(base64.b64encode(pic.read()).decode(), file, filetype))

    message_body = [  # тело сообщения
        f"--{boundary}",
        "Content-Type: text/html",
        '',
        f"{content}",
        f"--{boundary}"
    ]

    for i, picture in enumerate(pictures):  # для каждого докмента добавляем нужные заголовки для протокола
        message_body.append("Content-Disposition: attachment;")
        message_body.append(f"  filename=\"{picture.filename}\"")
        message_body.append("Content-Transfer-Encoding: base64")
        message_body.append(f"Content-Type: image/{picture.filetype};")
        message_body.append(f"	name=\"{picture.filename}\"")
        message_body.append("")
        message_body.append(f"{picture.encoded}")
        if i != len(pictures) - 1:
            message_body.append(f"--{boundary}")
            continue
        message_body.append(f"--{boundary}--")

    headers_str = '\n'.join(headers)
    message_str = '\n'.join(message_body)
    message = f"{headers_str}\n{message_str}\n.\n"
    print(message)
    return message


ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)  # для защищённого подключения
ssl_contex.check_hostname = False
ssl_contex.verify_mode = ssl.CERT_NONE

with socket.create_connection((SMTP_HOST, SMTP_PORT)) as sock:  # создаём подключение к серверу яндекса
    with ssl_contex.wrap_socket(sock, server_hostname=SMTP_HOST) as client:  # подключение протокола
        print(client.recv(1024))  # подключение по SMTP

        print(request(client, f'EHLO {USER_NAME_FROM}'))  #

        base64login = base64.b64encode(USER_NAME_FROM.encode()).decode()  # передаём логин и пароль
        base64password = base64.b64encode(PASSWORD.encode()).decode()

        print(request(client, 'AUTH LOGIN'))  # передача
        print(request(client, base64login))
        print(request(client, base64password))

        print(request(client, f'MAIL FROM:{USER_NAME_FROM}'))  # от кого кому
        print(request(client, f"RCPT TO:{USER_NAME_TO}"))

        print(request(client, 'DATA'))  # данные
        print(request(client, build_message("msg.txt")))
