import sys
import os
import configparser
import argparse
import urllib.request
import gzip


def check_file(file_path):
    ''' Проверяет существование файла. Завершает программу, если его нет. '''
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit(1)


def load_config(config_path):
    ''' Читает INI-файл, проверяет секцию и передает на валидацию. '''
    check_file(config_path)
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
    ''' Проверяет обязательные параметры и преобразует test_mode. '''
    pkg = settings.get('package_name', '').strip()
    url = settings.get('repo_url', '').strip()
    t_mode = settings.get('test_mode', '').strip().lower()

    errors = []
    if not pkg: errors.append("нет 'package_name'")
    if not url: errors.append("нет 'repo_url'")
    if not t_mode: errors.append("нет 'test_mode'")

    if errors:
        print("Ошибка: " + ", ".join(errors))
        sys.exit(1)

    is_test = t_mode in ('true', '1', 'yes', 'on')
    return {'package_name': pkg, 'repo_url': url, 'test_mode': is_test}


def fetch_data(url, is_test):
    ''' Получает данные (читает локальный файл или качает gz-архив). '''
    if is_test:
        print(f"Тестовый режим. Чтение файла: {url}")
        check_file(url)
        with open(url, 'r', encoding='utf-8') as f:
            return f.read()
    print(f"Скачивание репозитория: {url} ...")
    try:
        with urllib.request.urlopen(url) as resp:
            with gzip.GzipFile(fileobj=resp) as gz:
                return gz.read().decode('utf-8')
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        sys.exit(1)


def parse_repo(content):
    ''' Собирает репозиторий в словарь: ключ - пакет, значение - зависимости. '''
    graph = {}
    current_pkg = None
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("Package: "):
            current_pkg = line.split("Package: ")[1].strip()
            if current_pkg not in graph:
                graph[current_pkg] = []
        elif current_pkg and line.startswith("Depends: "):
            deps_str = line.split("Depends: ")[1].strip()
            graph[current_pkg] = clean_deps(deps_str)
    return graph


def clean_deps(deps_str):
    ''' Очищает зависимости от версий и альтернатив. '''
    cleaned = []
    for dep in deps_str.split(','):
        clean_name = dep.split('|')[0].strip().split()[0]
        if clean_name not in cleaned:
            cleaned.append(clean_name)
    return cleaned


def dfs(graph, pkg, visited, edges, load_order):
    ''' Обходит граф в глубину, собирая связи и порядок загрузки. '''
    if pkg in visited:
        return
    visited.add(pkg)
    for dep in graph.get(pkg, []):
        edges.append((pkg, dep))
        dfs(graph, dep, visited, edges, load_order)

    # Добавляем пакет в порядок загрузки после обработки всех его зависимостей
    load_order.append(pkg)


def main():
    ''' Главная функция: связывает загрузку, парсинг и построение графа. '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.ini')
    args = parser.parse_args()

    print("=== Загрузка конфигурации ===")
    cfg = load_config(args.config)
    for k, v in cfg.items():
        print(f"{k}: {v}")
    print()

    content = fetch_data(cfg['repo_url'], cfg['test_mode'])
    full_graph = parse_repo(content)

    visited = set()
    edges = []
    load_order = []
    dfs(full_graph, cfg['package_name'], visited, edges, load_order)

    print(f"\nГраф зависимостей для '{cfg['package_name']}")
    if not edges:
        print("Зависимостей не найдено.")
    else:
        for parent, child in edges:
            print(f"{parent} -> {child}")

    print(f"\nПорядок загрузки зависимостей")
    for p in load_order:
        print(f"- {p}")


if __name__ == "__main__":
    main()