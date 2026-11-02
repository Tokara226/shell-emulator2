#!/bin/bash

echo "=== Тест 1: Успешная загрузка ==="
cat <<EOF > tests/test_ok.ini
[Settings]
package_name = wget
repo_url = http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
test_mode = false
EOF
python src/main.py --config tests/test_ok.ini
echo "-----------------------------------"

echo "=== Тест 2: Ошибка - Файл не найден ==="
python src/main.py --config tests/fake_config.ini
echo "-----------------------------------"

echo "=== Тест 3: Ошибка - Отсутствуют обязательные параметры ==="
cat <<EOF > tests/test_missing_params.ini
[Settings]
test_mode = false
EOF
python src/main.py --config tests/test_missing_params.ini
echo "-----------------------------------"

echo "=== Тест 4: Ошибка - Отсутствует секция [Settings] ==="
cat <<EOF > tests/test_no_section.ini
[WrongSection]
package_name = wget
EOF
python src/main.py --config tests/test_no_section.ini
echo "-----------------------------------"

echo "=== Тест 5: Ошибка - Поврежденный синтаксис INI ==="
cat <<EOF > tests/test_broken.ini
[Settings
package_name wget
EOF
python src/main.py --config tests/test_broken.ini
echo "-----------------------------------"

# Очистка временных файлов
rm tests/test_ok.ini tests/test_missing_params.ini tests/test_no_section.ini tests/test_broken.ini