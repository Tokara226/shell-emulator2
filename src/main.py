import sys
import os
import configparser
import argparse
import urllib.request
import gzip


def check_file_exists(file_path):
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit(1)


def load_config(config_path):
    check_file_exists(config_path)
    config = configparser.ConfigParser()
    try:
        config.read(config_path, encoding='utf-8')
    except configparser.Error as e:
        print(f"Ошибка парсинга INI: {e}")
        sys.exit(1)

    if 'Settings' not in config:
        print("Ошибка: Нет секции [Settings].")
        sys.exit(1)

    return validate_settings(config['Settings'])


def validate_settings(settings):
    pkg = settings.get('package_name', '').strip()
    url = settings.get('repo_url', '').strip()
    t_mode = settings.get('test_mode', '').strip().lower()

    errors = []
    if not pkg:
        errors.append("не задан 'package_name'")
    if not url:
        errors.append("не задан 'repo_url'")
    if not t_mode:
        errors.append("не задан 'test_mode'")

    if errors:
        print("Ошибка: " + ", ".join(errors) + ".")
        sys.exit(1)

    is_test = t_mode in ('true', '1', 'yes', 'on')
    return {'package_name': pkg, 'repo_url': url, 'test_mode': is_test}


def fetch_repo_data(url):
    print(f"Скачивание репозитория: {url} ...")
    try:
        '''Скачиваем архив и распаковываем без сохранения файла'''
        with urllib.request.urlopen(url) as response:
            with gzip.GzipFile(fileobj=response) as gz:
                return gz.read().decode('utf-8')
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        sys.exit(1)


def extract_dependencies(content, target_pkg):
    is_target = False
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("Package: "):
            current_pkg = line.split("Package: ")[1].strip()
            is_target = (current_pkg == target_pkg)
        elif is_target and line.startswith("Depends: "):
            deps_str = line.split("Depends: ")[1].strip()
            return clean_deps(deps_str)
    return []


def clean_deps(deps_str):
    cleaned = []
    for dep in deps_str.split(','):
        '''Отсекаем альтернативы и версии'''
        clean_name = dep.split('|')[0].strip().split()[0]
        if clean_name not in cleaned:
            cleaned.append(clean_name)
    return cleaned


def main():
    parser = argparse.ArgumentParser(description="Граф Ubuntu/apt")
    parser.add_argument('--config', default='config.ini')
    args = parser.parse_args()

    print("Загрузка конфигурации")
    cfg = load_config(args.config)
    for k, v in cfg.items():
        print(f"{k}: {v}")

    print(f"\nПрямые зависимости для '{cfg['package_name']}'")
    repo_data = fetch_repo_data(cfg['repo_url'])
    deps = extract_dependencies(repo_data, cfg['package_name'])

    if deps:
        for d in deps:
            print(f"- {d}")
    else:
        print("Пакет не найден или не имеет зависимостей.")


if __name__ == "__main__":
    main()