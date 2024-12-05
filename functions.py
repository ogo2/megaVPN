
import paramiko
import time
import os
import re
from config import *

def is_valid_client_name(name):
    return re.match(r'^[a-zA-Z0-9_]+$', name) is not None

def create_vpn_profile(client_name):
    if not is_valid_client_name(client_name):
        print("Недопустимое имя клиента.")
        return None

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Загрузка приватного ключа OpenSSH
        private_key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE_KEY_PATH)

        # Подключение по SSH
        ssh.connect(VPS_HOST, username=VPS_USERNAME, pkey=private_key)

        # Выполнение скрипта для создания клиента
        command = f"/USERNAME/auto_create_client.sh {client_name}"
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if error and not error.strip().startswith("spawn sudo ./openvpn-install.sh"):
            print(f"Ошибка при создании профиля VPN: {error}")
            ssh.close()
            return None

        

        # Поиск файла .ovpn на сервере
        transport = paramiko.Transport((VPS_HOST, 22))
        transport.connect(username=VPS_USERNAME, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Убедитесь, что путь к файлу правильный
        remote_file_path = f'/root/{client_name}.ovpn'  # Укажите правильный путь
        local_file_path = f'{client_name}.ovpn'
        local_file_path2 = '/openvpn'
        time.sleep(2)  # Ожидание 2 секунды перед проверкой файла
        
        try:
            sftp.stat(remote_file_path)  # Проверка существования файла
            sftp.get(remote_file_path, local_file_path)
            print(f"Файл {client_name}.ovpn успешно загружен.")
        except FileNotFoundError:
            print(f"Файл {remote_file_path} не найден на сервере.")
            return None
        
        
        sftp.close()
        transport.close()
        ssh.close()
        return local_file_path

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None
