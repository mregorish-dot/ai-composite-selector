#!/bin/bash

# Скрипт для быстрого деплоя на Streamlit Cloud

echo "🚀 Подготовка к деплою на Streamlit Cloud..."
echo ""

# Проверка Git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Установите Git: https://git-scm.com/"
    exit 1
fi

# Проверка наличия .git
if [ ! -d ".git" ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    echo "✅ Git репозиторий инициализирован"
    echo ""
    echo "⚠️  ВАЖНО: Добавьте remote репозиторий:"
    echo "   git remote add origin https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/ai-composite-selector.git"
    echo "   git push -u origin main"
else
    echo "✅ Git репозиторий уже инициализирован"
    echo ""
    echo "📤 Загрузка изменений на GitHub..."
    git add .
    git commit -m "Update application" || echo "Нет изменений для коммита"
    git push origin main || echo "⚠️  Не удалось отправить. Проверьте remote репозиторий"
fi

echo ""
echo "✅ Готово!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Перейдите на https://share.streamlit.io/"
echo "2. Войдите через GitHub"
echo "3. Нажмите 'New app'"
echo "4. Выберите репозиторий и укажите Main file path: app/app.py"
echo "5. Нажмите 'Deploy'"
echo ""
echo "🔗 После деплоя вы получите ссылку, которую можно отправлять друзьям!"

