#!/bin/bash
cd "$(dirname "$0")/.."

echo "Тест 1: Ошибка - Файл не найден"
python src/main.py --config tests/fake_config.ini
echo "-----------------------------------"

echo "Тест 2: Ошибка - Отсутствуют обязательные параметры"
cat <<EOF > tests/test_missing_params.ini
[Settings]
test_mode = false
EOF
python src/main.py --config tests/test_missing_params.ini
echo "-----------------------------------"

echo "Тест 3: Ошибка - Отсутствует секция [Settings]"
cat <<EOF > tests/test_no_section.ini
[WrongSection]
package_name = wget
EOF
python src/main.py --config tests/test_no_section.ini
echo "-----------------------------------"

echo "Тест 4: Ошибка - Поврежденный синтаксис INI"
cat <<EOF > tests/test_broken.ini
[Settings
package_name wget
EOF
python src/main.py --config tests/test_broken.ini
echo "-----------------------------------"

rm tests/test_ok.ini tests/test_missing_params.ini tests/test_no_section.ini tests/test_broken.ini