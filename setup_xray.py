import subprocess
import json
import os
import sys

# --- Настройки ---
PORT = 3443
DEST = "ok.ru:443"
SNI = "ok.ru"
XHTTP_PATH = "/messages"
IMAGE = "teddysun/xray"
CONF_DIR = os.path.abspath("./xray_config")
DATA_FILE = os.path.join(CONF_DIR, "data.json")

def get_docker_output(cmd_list):
    try:
        base_cmd = ["docker", "run", "--rm", "--platform", "linux/amd64", IMAGE]
        result = subprocess.run(base_cmd + cmd_list, capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Ошибка Docker: {e}")
        return ""

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "private_key": "", "public_key": "", "short_id": ""}

def save_data(data):
    os.makedirs(CONF_DIR, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_new_keys(data):
    print("🔑 Генерация новых ключей REALITY...")
    raw_keys = get_docker_output(["xray", "x25519"])
    for line in raw_keys.split('\n'):
        line = line.strip()
        if "PrivateKey:" in line:
            data["private_key"] = line.split(":", 1)[1].strip()
        elif "PublicKey" in line:
            data["public_key"] = line.split(":")[-1].strip()
    data["short_id"] = os.urandom(8).hex()
    return data

def update_xray_config(data):
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "port": PORT,
            "protocol": "vless",
            "tag": "vless-xhttp-reality",
            "settings": {
                "clients": [{"id": uid, "email": name} for name, uid in data["users"].items()],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "xhttp",
                "security": "reality",
                "realitySettings": {
                    "show": False,
                    "dest": DEST,
                    "xver": 0,
                    "serverNames": [SNI],
                    "privateKey": data["private_key"],
                    "shortIds": [data["short_id"]]
                },
                "xhttpSettings": {"path": XHTTP_PATH, "host": SNI}
            },
            "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}
        }],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}]
    }
    with open(f"{CONF_DIR}/config.json", "w") as f:
        json.dump(config, f, indent=2)

def get_ip():
    try:
        return subprocess.run(["curl", "-s", "https://api.ipify.org"], capture_output=True, text=True).stdout.strip()
    except:
        return "ВАШ_IP"

def restart_container():
    print("🔄 Перезапуск контейнера...")
    old_id = subprocess.run(["docker", "ps", "-aqf", "name=xray-server"], capture_output=True, text=True).stdout.strip()
    if old_id:
        print(f"🗑 Останавливаем старый контейнер (ID: {old_id})")
        subprocess.run(["docker", "stop", "xray-server"], capture_output=True)
        subprocess.run(["docker", "rm", "xray-server"], capture_output=True)
    
    run_cmd = [
        "docker", "run", "-d", "--name", "xray-server", "--restart", "always",
        "-p", f"{PORT}:{PORT}",
        "-v", f"{CONF_DIR}:/etc/xray",
        IMAGE
    ]
    new_id = subprocess.run(run_cmd, capture_output=True, text=True).stdout.strip()
    print(f"🚀 Новый контейнер запущен! (ID: {new_id})")

def show_links(data):
    ip = get_ip()
    print("\n" + "="*50)
    print("🔗 СПИСОК КЛЮЧЕЙ (VLESS):")
    for name, uuid in data["users"].items():
        encoded_path = XHTTP_PATH.replace("/", "%2F")
        link = f"vless://{uuid}@{ip}:{PORT}?security=reality&sni={SNI}&fp=chrome&pbk={data['public_key']}&sid={data['short_id']}&type=xhttp&path={encoded_path}#{name}"
        print(f"\n👉 {name}:\n{link}")
    print("="*50)

def main():
    while True:
        data = load_data()
        print(f"\n--- МЕНЕДЖЕР XRAY (REALITY + XHTTP) ---")
        print("1. Показать список всех ключей (ссылок)")
        print("2. Добавить нового пользователя")
        print("3. Удалить пользователя")
        print("4. Перезапустить контейнер (применить настройки)")
        print("5. Создать с нуля (новые ключи, удаление старого)")
        print("6. Удалить текущий контейнер")
        print("0. Выход")
        
        choice = input("\nВыберите действие: ")

        if choice == "1":
            if not data["users"]:
                print("⚠️ Список пользователей пуст.")
            else:
                show_links(data)

        elif choice == "2":
            name = input("Введите имя нового пользователя: ")
            uuid = get_docker_output(["xray", "uuid"]).split('\n')[0].strip()
            data["users"][name] = uuid
            save_data(data)
            print(f"✅ Пользователь {name} добавлен. Не забудьте перезапустить (п. 4)")

        elif choice == "3":
            name = input("Введите имя для удаления: ")
            if name in data["users"]:
                del data["users"][name]
                save_data(data)
                print(f"✅ Пользователь {name} удален.")
            else:
                print("❌ Пользователь не найден.")

        elif choice == "4":
            update_xray_config(data)
            restart_container()

        elif choice == "5":
            confirm = input("⚠️ Это удалит старые ключи и создаст новые. Уверены? (y/n): ")
            if confirm.lower() == 'y':
                data = {"users": {}} 
                data = generate_new_keys(data)
                # Добавление админа
                admin_uuid = get_docker_output(["xray", "uuid"]).split('\n')[0].strip()
                data["users"]["Admin"] = admin_uuid
                save_data(data)
                update_xray_config(data)
                restart_container()
                show_links(data)

        elif choice == "6":
            old_id = subprocess.run(["docker", "ps", "-aqf", "name=xray-server"], capture_output=True, text=True).stdout.strip()
            if old_id:
                subprocess.run(["docker", "stop", "xray-server"], capture_output=True)
                subprocess.run(["docker", "rm", "xray-server"], capture_output=True)
                print(f"🛑 Контейнер {old_id} удален.")
            else:
                print("ℹ️ Контейнер не запущен.")

        elif choice == "0":
            sys.exit()
        else:
            print("❌ Неверный ввод.")

if __name__ == "__main__":
    main()
