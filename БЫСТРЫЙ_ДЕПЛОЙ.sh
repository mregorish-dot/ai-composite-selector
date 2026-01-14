#!/bin/bash

echo "🚀 БЫСТРЫЙ ДЕПЛОЙ НА STREAMLIT CLOUD"
echo "======================================"
echo ""

# Проверка Git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен!"
    echo "Установите Git: https://git-scm.com/downloads"
    exit 1
fi

# Проверка наличия GitHub аккаунта
echo "📋 ШАГ 1: Подготовка к деплою"
echo ""

# Инициализация Git (если нужно)
if [ ! -d ".git" ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
    git add .
    git commit -m "Initial commit: AI Composite Selector"
    git branch -M main
    echo "✅ Git репозиторий инициализирован"
    echo ""
else
    echo "✅ Git репозиторий уже существует"
    git add .
    git commit -m "Update: AI Composite Selector" || echo "Нет изменений"
    echo ""
fi

echo "📋 ШАГ 2: Создание GitHub репозитория"
echo ""
echo "⚠️  ВАЖНО: Выполните следующие шаги:"
echo ""
echo "1. Откройте в браузере: https://github.com/new"
echo "2. Название репозитория: ai-composite-selector"
echo "3. Выберите 'Public' или 'Private'"
echo "4. НЕ добавляйте README, .gitignore или лицензию"
echo "5. Нажмите 'Create repository'"
echo ""
read -p "Нажмите Enter после создания репозитория..."

echo ""
echo "📋 ШАГ 3: Подключение к GitHub"
echo ""
read -p "Введите ваш GitHub username: " GITHUB_USER

if [ -z "$GITHUB_USER" ]; then
    echo "❌ Username не может быть пустым!"
    exit 1
fi

# Проверка remote
if git remote | grep -q "origin"; then
    echo "⚠️  Remote 'origin' уже существует"
    read -p "Заменить? (y/n): " REPLACE
    if [ "$REPLACE" = "y" ]; then
        git remote remove origin
        git remote add origin "https://github.com/$GITHUB_USER/ai-composite-selector.git"
    fi
else
    git remote add origin "https://github.com/$GITHUB_USER/ai-composite-selector.git"
fi

echo ""
echo "📤 Загрузка кода на GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Код успешно загружен на GitHub!"
    echo ""
    echo "📋 ШАГ 4: Деплой на Streamlit Cloud"
    echo ""
    echo "1. Откройте: https://share.streamlit.io/"
    echo "2. Войдите через GitHub"
    echo "3. Нажмите 'New app'"
    echo "4. Заполните:"
    echo "   - Repository: $GITHUB_USER/ai-composite-selector"
    echo "   - Branch: main"
    echo "   - Main file path: app/app.py"
    echo "5. Нажмите 'Deploy'"
    echo ""
    echo "⏳ Подождите 1-2 минуты..."
    echo ""
    echo "✅ После деплоя вы получите ссылку:"
    echo "   https://$GITHUB_USER-ai-composite-selector-XXXXXX.streamlit.app"
    echo ""
    echo "🎉 Эту ссылку можно отправлять друзьям!"
else
    echo ""
    echo "❌ Ошибка при загрузке на GitHub"
    echo "Проверьте:"
    echo "1. Правильность username"
    echo "2. Существование репозитория"
    echo "3. Права доступа"
fi

