#!/usr/bin/expect -f

set timeout -1

# Устанавливаем терминал как "dumb" для отключения лишних управляющих символов
set ::env(TERM) dumb

# Получение имени клиента из аргументов
set client_name [lindex $argv 0]

if {$client_name == ""} {
    puts "Usage: ./auto_create_client.sh <client_name>"
    exit 1
}

# Переходим в директорию, где находится openvpn-install.sh
cd /root

spawn sudo ./openvpn-install.sh

# Ожидание меню опций
expect {
    -re {What do you want to do.*\?.*Select an option \[1-4\]:} {
        send -- "1\r"
    }
    timeout {
        puts "Ошибка: Таймаут при ожидании меню опций."
        exit 1
    }
}

# Ожидание запроса имени клиента
expect {
    -re {Tell me a name for the client.*Client name:} {
        send -- "$client_name\r"
    }
    timeout {
        puts "Ошибка: Таймаут при ожидании запроса имени клиента."
        exit 1
    }
}

# Добавляем небольшую задержку перед следующей командой
sleep 1

# Ожидание запроса пароля для клиента
expect {
    -re {Do you want to protect the configuration file with a password.*Select an option \[1-2\]:} {
        send -- "\r"
    }
    timeout {
        puts "Ошибка: Таймаут при ожидании запроса о пароле."
        exit 1
    }
}

# Добавляем задержку, чтобы дать скрипту время обработать запрос
sleep 1

# Ожидание подтверждения добавления клиента
expect {
    -re {Client .* added.*} {
        puts "Клиент $client_name успешно добавлен."
    }
    -re {Client configuration for .* created.*} {
        puts "Клиент $client_name успешно добавлен."
    }
    -re {A client with the specified name already exists.*} {
        puts "Клиент с таким именем уже существует."
        exit 1
    }
    timeout {
        puts "Ошибка: Таймаут при ожидании подтверждения добавления клиента."
        exit 1
    }
}

expect eof

