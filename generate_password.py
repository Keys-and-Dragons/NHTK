import random
import string


# Функция для генерации пароля
def generate_password(length, use_uppercase, use_symbols):
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase if use_uppercase else ''
    num = string.digits
    symbols = string.punctuation if use_symbols else ''

    # Собираем все возможные символы для пароля
    all_characters = lower + upper + num + symbols

    # Проверка на наличие символов для генерации пароля
    if not all_characters:
        raise ValueError("Необходимо выбрать хотя бы один тип символов для генерации пароля.")

    # Генерация пароля
    temp = random.sample(all_characters, length)
    password = "".join(temp)

    return password


# Получение пользовательского ввода
length = int(input('Введите длину пароля: '))
use_uppercase = input('Использовать заглавные буквы? (да/нет): ').strip().lower() == 'да'
use_symbols = input('Использовать знаки препинания? (да/нет): ').strip().lower() == 'да'

# Генерация и вывод пароля
try:
    password = generate_password(length, use_uppercase, use_symbols)
    print(f'Сгенерированный пароль: {password}')
except ValueError as e:
    print(e)
