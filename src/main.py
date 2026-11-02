import sys
import os
import configparser
import argparse


def load_config(config_path):
    '''Проверка существования файла'''
    if not os.path.exists(config_path):
        print(f"Ошибка: Конфигурационный файл '{config_path}' не найден.")
        sys.exit(1)

    config = configparser.ConfigParser()

    try:
        config.read(config_path, encoding='utf-8')
    except configparser.Error as e:
        print(f"Ошибка парсинга INI-файла: {e}")
        sys.exit(1)

    '''Проверка наличия обязательной секции'''
    if 'Settings' not in config:
        print("Ошибка: В конфигурационном файле отсутствует секция [Settings].")
        sys.exit(1)

    settings = config['Settings']

    '''Извлечение параметров с проверкой их наличия'''
    package_name = settings.get('package_name')
    repo_url = settings.get('repo_url')
    test_mode_str = settings.get('test_mode')

    errors = []
    if not package_name:
        errors.append("не задан параметр 'package_name'")
    if not repo_url:
        errors.append("не задан параметр 'repo_url'")
    if not test_mode_str:
        errors.append("не задан параметр 'test_mode'")

    if errors:
        print("Ошибка конфигурации: " + ", ".join(errors) + ".")
        sys.exit(1)

    '''Преобразование строки test_mode в boolean'''
    test_mode = test_mode_str.strip().lower() in ('true', '1', 'yes', 'on')

    return {
        'package_name': package_name.strip(),
        'repo_url': repo_url.strip(),
        'test_mode': test_mode
    }


def main():
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей (Ubuntu/apt)")
    parser.add_argument('--config', type=str, default='config.ini', help='Путь к конфигурационному INI-файлу')
    args = parser.parse_args()

    config_params = load_config(args.config)

    '''Вывод всех настраиваемых параметров в формате ключ-значение (требование Этапа 1)'''
    for key, value in config_params.items():
        print(f"{key}: {value}")

    print("\nУспешно")


if __name__ == "__main__":
    main()