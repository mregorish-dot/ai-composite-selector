#!/bin/bash
# Автоматическое исправление новой версии приложения

echo "🔧 Проверка и исправление новой версии приложения..."
echo ""

cd "/Users/egorryzhkov/Desktop/AI Double"

# Проверка текущей ветки
echo "📋 Текущая ветка:"
git branch | grep "*"

# Проверка файлов
echo ""
echo "✅ Проверка файлов app/app.py и app/composite_selector.py..."

# Проверка наличия полей defect_volume и localization в composite_selector.py
if grep -q "defect_volume: Optional\[str\]" app/composite_selector.py && \
   grep -q "localization: Optional\[str\]" app/composite_selector.py; then
    echo "✅ composite_selector.py содержит правильные поля"
else
    echo "❌ ОШИБКА: composite_selector.py не содержит нужные поля!"
    exit 1
fi

# Проверка использования полей в app.py
if grep -q "defect_volume=defect_volume" app/app.py && \
   grep -q "localization=localization" app/app.py; then
    echo "✅ app.py правильно использует поля"
else
    echo "❌ ОШИБКА: app.py не использует поля правильно!"
    exit 1
fi

echo ""
echo "✅ Локальные файлы правильные!"
echo ""

# Проверка статуса Git
echo "📊 Статус Git:"
git status --short app/app.py app/composite_selector.py

# Если есть изменения, коммитим
if git diff --quiet app/app.py app/composite_selector.py; then
    echo ""
    echo "✅ Файлы уже синхронизированы с GitHub"
else
    echo ""
    echo "📝 Обнаружены изменения, коммитим..."
    git add app/app.py app/composite_selector.py
    git commit -m "Fix: Обновление PatientData с полями defect_volume и localization"
    echo "✅ Изменения закоммичены"
fi

echo ""
echo "🚀 Инструкции для обновления на Streamlit Cloud:"
echo ""
echo "1. Открой https://share.streamlit.io/"
echo "2. Найди приложение с ссылкой:"
echo "   https://ai-composite-selector-xscarydc3oexc6jj57dex2.streamlit.app/"
echo "3. Нажми 'Manage app'"
echo "4. Убедись, что выбрана ветка: new-version"
echo "5. Нажми 'Redeploy' или 'Reboot app'"
echo "6. Подожди 1-2 минуты"
echo ""
echo "✅ После этого приложение должно заработать!"
echo ""
