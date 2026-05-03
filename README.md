# Xray Manager

Xray Manager is a simple command-line interactive Python script that automates the configuration and management of an Xray server running inside a Docker container. It sets up Xray with the **VLESS + REALITY + XHTTP** protocols.

## Features

- **Interactive CLI**: Easily manage your Xray server using a simple terminal menu.
- **Docker-based**: Automatically runs the `teddysun/xray` container, ensuring a clean and isolated environment.
- **User Management**: Add, remove, and list users effortlessly.
- **Auto-generate Links**: Automatically generates VLESS share links for your users.
- **Key Generation**: Built-in support for generating REALITY X25519 keys and client UUIDs.

## Prerequisites

- **Python 3.x**: Ensure Python is installed on your system.
- **Docker**: Docker must be installed and running, as the script uses it to run the Xray server and generate keys.

## Installation

1. Clone or download this repository.
2. Ensure you have Docker and Python installed.
3. No additional Python libraries are required (only standard libraries like `subprocess`, `json`, `os`, and `sys` are used).

## Usage

Run the script using Python:

```bash
python3 setup_xray.py
```

Upon running, you will see the following interactive menu:

```text
--- МЕНЕДЖЕР XRAY (REALITY + XHTTP) ---
1. Показать список всех ключей (ссылок)
2. Добавить нового пользователя
3. Удалить пользователя
4. Перезапустить контейнер (применить настройки)
5. Создать с нуля (новые ключи, удаление старого)
6. Удалить текущий контейнер
0. Выход
```

### Menu Options

- **1. Show all keys (links)**: Displays the VLESS connection links for all registered users. These links can be directly imported into clients like v2rayN, Nekobox, v2rayNG, or Shadowrocket.
- **2. Add a new user**: Prompts for a username, generates a new UUID, and adds the user. **Note:** You must restart the container (Option 4) for the changes to take effect.
- **3. Delete a user**: Removes an existing user by their username.
- **4. Restart container**: Updates the Xray `config.json` based on current user settings and restarts the Docker container to apply the changes.
- **5. Create from scratch**: Deletes the existing container and keys, generates new REALITY keys, creates a default "Admin" user, and starts a fresh instance.
- **6. Delete current container**: Stops and removes the running `xray-server` Docker container.
- **0. Exit**: Closes the script.

## Default Configuration

By default, the script uses the following network settings (these can be modified at the top of `setup_xray.py`):

- **Port**: `3443`
- **Destination (DEST)**: `ok.ru:443`
- **SNI**: `ok.ru`
- **XHTTP Path**: `/messages`

The generated configuration files and user data (`data.json`, `config.json`) are automatically saved in an `xray_config` directory located in the same directory as the script.

## License

This project is licensed under the terms of the included LICENSE file.
