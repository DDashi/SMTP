SMTP CLIENT 

This program helps to send emails via SMTP protocol using Yandex mail.

Usage

To send an email in the config file.In json, you can specify the subject of the message, the sender, the recipient and the name of the folder with all the attachments that you want to attach to the message.
But to send a message, you first need to get a password in the mail for sending via the SMTP protocol and specify this password in the password file.json. Also in the file msg.txt you can specify the text of the message in Russian or English.
Launch main.py to send.

Files
The repository contains the following files:

 - `main.py` : Contains code for sending a message.
 - `config.json` : Contains information for sending a message.
 - `password.json` : Contains sender's password.
 - `msg.txt` : Text to send.

This code was written by Емашова Анастасия КН-202.
