import bcrypt
import psycopg2


def generate_hash(password):
    password_bytes = password.encode("utf-8")
    password_salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(password_bytes, password_salt)
    hash_str = hash_bytes.decode("utf-8")
    return hash_str


def authenticate(password, hash):
    password_bytes = password.encode("utf-8")
    hash_bytes = hash.encode("utf-8")
    result = bcrypt.checkpw(password_bytes, hash_bytes)
    return result


def save_user_to_db(username, password):
    hashed_password = generate_hash(password)

    # Initialize cursor to None
    cursor = None
    connection = None

    try:
        connection = psycopg2.connect(
            dbname='ALL',
            user='postgres',
            password='ssn23mzw',
            host='localhost',
            port='5432'
        )
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        ''')

        cursor.execute('''
            INSERT INTO users (username, password_hash) VALUES (%s, %s);
        ''', (username, hashed_password))

        connection.commit()
        print("Пользователь успешно добавлен.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        # Ensure cursor and connection are closed if they were created
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    username_input = input("Введите логин: ")
    password_input = input("Введите пароль: ")

    save_user_to_db(username_input, password_input)
