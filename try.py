import sys
import requests
import threading
import json
from concurrent.futures import ThreadPoolExecutor
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QHBoxLayout, QFrame
from PyQt5.QtGui import QPalette, QColor, QIcon, QMouseEvent
from PyQt5.QtCore import Qt, QPoint

# Fonction pour envoyer un message à Discord
def send_message(proxy, channel_ids, token, message):
    headers = {
        "Authorization": f"{token}",
        "Content-Type": "application/json"
    }
    data = {
        "content": message
    }
    proxy_dict = {
        "http": proxy,
        "https": proxy
    }
    for _ in range(10):
        for channel_id in channel_ids:
            url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
            try:
                response = requests.post(url, headers=headers, json=data, proxies=proxy_dict)
                if response.status_code == 200:
                    print(f"Message sent successfully to channel {channel_id} with proxy {proxy}")
                else:
                    print(f"Failed to send message to channel {channel_id} with proxy {proxy}: {response.status_code}")
            except Exception as e:
                print(f"Error with proxy {proxy} for channel {channel_id}: {e}")
        time.sleep(2)

def check_proxy(proxy):
    test_url = "https://httpbin.org/ip"
    proxy_dict = {
        "http": proxy,
        "https": proxy
    }
    try:
        response = requests.get(test_url, proxies=proxy_dict, timeout=5)
        if response.status_code == 200:
            print(f"Proxy {proxy} is working")
            return proxy
        else:
            print(f"Proxy {proxy} failed with status code {response.status_code}")
    except Exception as e:
        print(f"Proxy {proxy} failed: {e}")
    return None

# Fonction pour vérifier les proxys avec threading
def check_proxies(proxies, num_threads):
    valid_proxies = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = executor.map(check_proxy, proxies)
    for result in results:
        if result:
            valid_proxies.append(result)
    return valid_proxies

class TitleBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2E2E2E;
                border: none;
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        
        self.setFixedHeight(30)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.title = QLabel("Discord Message Sender")
        layout.addWidget(self.title)
        
        self.minimize_button = QPushButton("_")
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.minimize_button)
        
        self.close_button = QPushButton("X")
        self.close_button.clicked.connect(self.parent.close)
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.dragPos = event.globalPos()
            event.accept()
        
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(self.parent.pos() + event.globalPos() - self.parent.dragPos)
            self.parent.dragPos = event.globalPos()
            event.accept()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Discord Message Sender'
        self.proxies = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowOpacity(0.9)  # Set window transparency
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        self.dragPos = QPoint()
        
        layout = QVBoxLayout()
        
        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)
        
        self.token_label = QLabel('Entrez le token:')
        layout.addWidget(self.token_label)
        
        self.token_input = QLineEdit(self)
        layout.addWidget(self.token_input)
        
        self.message_label = QLabel('Entrez le message:')
        layout.addWidget(self.message_label)
        
        self.message_input = QLineEdit(self)
        layout.addWidget(self.message_input)
        
        self.channel_ids_label = QLabel('Entrez les channel_ids séparés par des virgules:')
        layout.addWidget(self.channel_ids_label)
        
        self.channel_ids_input = QLineEdit(self)
        layout.addWidget(self.channel_ids_input)
        
        self.threads_label = QLabel('Entrez le nombre de threads:')
        layout.addWidget(self.threads_label)
        
        self.threads_input = QLineEdit(self)
        layout.addWidget(self.threads_input)
        
        self.select_file_button = QPushButton('Sélectionner le fichier de proxys', self)
        self.select_file_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_file_button)
        
        self.check_proxies_button = QPushButton('Vérifier les proxys', self)
        self.check_proxies_button.clicked.connect(self.check_proxies)
        layout.addWidget(self.check_proxies_button)
        
        self.send_message_button = QPushButton('Envoyer le message', self)
        self.send_message_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_message_button)
        
        self.save_config_button = QPushButton('Sauvegarder la configuration', self)
        self.save_config_button.clicked.connect(self.save_config)
        layout.addWidget(self.save_config_button)
        
        self.load_config_button = QPushButton('Charger la configuration', self)
        self.load_config_button.clicked.connect(self.load_config)
        layout.addWidget(self.load_config_button)
        
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)
        
        self.setLayout(layout)
        self.apply_styles()
        self.show()
        
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(46, 46, 46, 200);
                color: #FFFFFF;
                font-family: Arial, sans-serif;
                font-size: 14px;
                border: 5px solid transparent;
                border-radius: 10px;
                background-clip: padding-box;
                border-image: linear-gradient(45deg, red, yellow, green, cyan, blue, magenta, red) 1;
            }
            QLineEdit, QTextEdit {
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: rgba(58, 58, 58, 200);
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: rgba(74, 74, 74, 200);
            }
            QPushButton:pressed {
                background-color: rgba(42, 42, 42, 200);
            }
            QLabel {
                color: #FFFFFF;
            }
        """)
        
    def select_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Sélectionner le fichier de proxys", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'r') as file:
                self.proxies = [line.strip() for line in file.readlines()]
            self.output.append(f"Fichier de proxys chargé: {file_name}")
        
    def check_proxies(self):
        if not self.proxies:
            self.output.append("Veuillez d'abord sélectionner un fichier de proxys.")
            return
        try:
            num_threads = int(self.threads_input.text())
        except ValueError:
            self.output.append("Veuillez entrer un nombre valide de threads.")
            return
        self.output.append("Vérification des proxys...")
        valid_proxies = check_proxies(self.proxies, num_threads)
        self.output.append(f"Proxys valides: {valid_proxies}")
        
    def send_message(self):
        token = self.token_input.text()
        message = self.message_input.text()
        channel_ids = self.channel_ids_input.text().split(',')
        if not self.proxies:
            self.output.append("Veuillez d'abord sélectionner un fichier de proxys.")
            return
        threads = []
        for proxy in self.proxies:
            thread = threading.Thread(target=send_message, args=(proxy, channel_ids, token, message))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.output.append("Messages envoyés.")
    
    def save_config(self):
        config = {
            "token": self.token_input.text(),
            "message": self.message_input.text(),
            "channel_ids": self.channel_ids_input.text(),
            "threads": self.threads_input.text(),
            "proxy_file": self.proxies
        }
        with open("config.json", "w") as config_file:
            json.dump(config, config_file)
        self.output.append("Configuration sauvegardée.")
    
    def load_config(self):
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.token_input.setText(config["token"])
                self.message_input.setText(config["message"])
                self.channel_ids_input.setText(config["channel_ids"])
                self.threads_input.setText(config["threads"])
                self.proxies = config["proxy_file"]
                self.output.append("Configuration chargée.")
        except FileNotFoundError:
            self.output.append("Aucune configuration trouvée.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())