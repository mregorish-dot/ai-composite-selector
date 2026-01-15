#!/bin/bash

echo "🚀 Автоматическая загрузка кода на GitHub"
echo "=========================================="
echo ""

# Проверка что мы в правильной директории
if [ ! -f "app/app.py" ]; then
    echo "❌ Ошибка: файл app/app.py не найден"
    echo "Перейдите в директорию проекта"
    exit 1
fi

echo "📋 ШАГ 1: Создание Personal Access Token"
echo ""
echo "1. Откройте в браузере: https://github.com/settings/tokens"
echo "2. Нажмите 'Generate new token' → 'Generate new token (classic)'"
echo "3. Название: ai-composite-selector"
echo "4. Выберите scope: repo (галочка)"
echo "5. Нажмите 'Generate token'"
echo "6. СКОПИРУЙТЕ ТОКЕН (он показывается только один раз!)"
echo ""
read -p "Вставьте токен сюда и нажмите Enter: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ Токен не может быть пустым!"
    exit 1
fi

echo ""
echo "📤 Загрузка кода на GitHub..."
echo ""

# Используем токен для авторизации
git push https://mregorish-dot:${TOKEN}@github.com/mregorish-dot/ai-composite-selector.git main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Код успешно загружен на GitHub!"
    echo ""
    echo "🔗 Ваш репозиторий:"
    echo "   https://github.com/mregorish-dot/ai-composite-selector"
    echo ""
    echo "📋 СЛЕДУЮЩИЙ ШАГ:"
    echo "1. Перейдите на: https://share.streamlit.io/"
    echo "2. Войдите через GitHub"
    echo "3. New app → Repository: mregorish-dot/ai-composite-selector"
    echo "4. Main file path: app/app.py"
    echo "5. Deploy"
    echo ""
else
    echo ""
    echo "❌ Ошибка при загрузке"
    echo "Проверьте:"
    echo "1. Правильность токена"
    echo "2. Что репозиторий создан на GitHub"
    echo "3. Что токен имеет права 'repo'"
fi

