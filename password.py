import sys
import psycopg2
import bcrypt
import json
from PyQt5 import QtWidgets, QtGui, QtCore
from psycopg2 import sql


def connect_to_database(db_name, user, password, host="localhost", port="5432"):
    """Подключается к базе данных PostgreSQL."""
    try:
        conn = psycopg2.connect(database=db_name, user=user, password=password, host=host, port=port)
        print("Успешное подключение к базе данных.")
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def create_table(conn):
    """Создает таблицу users, если она не существует."""
    try:
        cursor = conn.cursor()
        cursor.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """))
        conn.commit()
        print("Таблица 'users' успешно создана или уже существует.")
    except psycopg2.Error as e:
        print(f"Ошибка создания таблицы: {e}")
        conn.rollback()


def load_users_from_json(conn, file_path):
    """Загружает пользователей из JSON файла в базу данных."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                user_data = json.loads(line.strip())
                save_user(conn, user_data['username'], user_data['password_hash'])
            print("Пользователи загружены из JSON!")
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")


def save_user(conn, username, password_hash):
    """Сохраняет пользователя в базу данных."""
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
        print(f"Пользователь '{username}' успешно добавлен в базу данных.")
        return True  # Успешное добавление пользователя
    except psycopg2.IntegrityError:
        conn.rollback()  # Пользователь уже существует
        print(f"Пользователь '{username}' уже существует.")
        return False  # Не удалось добавить пользователя
    except psycopg2.Error as e:
        print(f"Ошибка добавления пользователя: {e}")
        conn.rollback()
        return False  # Не удалось добавить пользователя
    finally:
        cursor.close()


def read_users_from_json(file_path):
    """Читает пользователей из JSON файла и возвращает их как множество уникальных имен пользователей."""
    users = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                user_data = json.loads(line.strip())
                users.add(user_data['username'])
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")

    return users


def write_user_to_json(file_path, username, password_hash):
    """Записывает нового пользователя в JSON файл только если он уникален."""
    existing_users = read_users_from_json(file_path)

    if username not in existing_users:
        with open(file_path, 'a', encoding='utf-8') as f:
            json.dump({"username": username, "password_hash": password_hash}, f)
            f.write('\n')
            print(f"Пользователь '{username}' успешно добавлен в JSON файл.")
            return True  # Успешное добавление в файл
    else:
        print(f"Пользователь '{username}' уже существует в JSON файле.")
        return False  # Не удалось добавить в файл


class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Подключение к базе данных и создание таблицы
        self.conn = connect_to_database('ALL', 'postgres', 'ssn23mzw')
        if self.conn:
            create_table(self.conn)
            load_users_from_json(self.conn, 'users.json')

    def initUI(self):
        # Установка размеров окна
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle('Авторизация')

        # Установка фона
        oImage = QtGui.QImage("Main.png")  # Замените на путь к вашей картинке
        sImage = oImage.scaled(self.size(), QtCore.Qt.KeepAspectRatioByExpanding)
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(sImage))
        self.setPalette(palette)

        # Создание полупрозрачного прямоугольника

        self.overlay = QtWidgets.QWidget(self)
        self.overlay.setGeometry(630, 230, 650, 350)  # Размеры и позиция прямоугольника
        self.overlay.setStyleSheet("background-color: rgba(150, 150, 150, 230);")

        # Создание элементов интерфейса
        self.username_label = QtWidgets.QLabel('Введите логин:', self)
        self.username_label.move(750, 270)
        self.username_label.setStyleSheet("font-size: 20px;")

        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setGeometry(755, 300, 400, 50)
        self.username_input.setStyleSheet("border-radius: 20px; padding: 10px; font-size: 17px;")

        self.password_label = QtWidgets.QLabel('Введите пароль:', self)
        self.password_label.move(750, 370)
        self.password_label.setStyleSheet("font-size: 20px;")

        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setGeometry(755, 400, 400, 50)
        self.password_input.setStyleSheet("border-radius: 20px; padding: 10px; font-size: 17px;")

        # Кнопка входа
        button_style = """
               QPushButton {
                   background-color: #c2c2c2; 
                   color: black;              
                   border: none;              
                   border-radius: 15px;       
                   font-size: 15px;           
               }
               QPushButton:hover {
                   background-color: #fdfdfd; 
               }
           """
        # Создание кнопки входа
        self.login_button = QtWidgets.QPushButton('Войти', self)
        self.login_button.setGeometry(1020, 500, 200, 35)
        # Применение стиля кнопки входа
        self.login_button.setStyleSheet(button_style)
        # Соединение с обработчиком входа
        self.login_button.clicked.connect(self.handle_login)

        # Кнопка создания аккаунта
        self.create_button = QtWidgets.QPushButton('Создать аккаунт', self)
        self.create_button.setGeometry(700, 500, 200, 35)
        # Применение стиля кнопки создания аккаунта
        self.create_button.setStyleSheet(button_style)
        # Соединение с обработчиком создания аккаунта
        self.create_button.clicked.connect(self.handle_create_account)


    def handle_create_account(self):
        """Создает новый аккаунт в базе данных и сохраняет его в JSON файл."""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Введите логин и пароль.')
            return

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        if save_user(self.conn, username, hashed.decode('utf-8')):
            if write_user_to_json('users.json', username, hashed.decode('utf-8')):
                QtWidgets.QMessageBox.information(self, 'Успех', 'Аккаунт создан!')
            else:
                QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Этот логин уже занят в JSON файле.')
        else:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Этот логин уже занят в базе данных.')


    def handle_login(self):
        """Обрабатывает вход пользователя в систему."""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Введите логин и пароль.')
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username=%s", (username,))

        result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            QtWidgets.QMessageBox.information(self, 'Успех', 'Вход выполнен успешно!')
        else:
            QtWidgets.QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль.')

        cursor.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
