#!/bin/bash

# Скрипт для автоматического развертывания на Streamlit Cloud

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🚀 РАЗВЕРТЫВАНИЕ COMPOSEAI В ИНТЕРНЕТЕ                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Переход в директорию проекта
cd "/Users/egorryzhkov/Desktop/AI Double" || exit 1

# Проверка Git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Установите Git: https://git-scm.com/"
    exit 1
fi

# Проверка наличия .git
if [ ! -d ".git" ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
    git branch -M main
    echo "✅ Git репозиторий инициализирован"
    echo ""
fi

# Проверка remote репозитория
if ! git remote | grep -q origin; then
    echo "⚠️  Remote репозиторий не настроен!"
    echo ""
    echo "📋 Выполните следующие команды:"
    echo ""
    echo "1. Создайте репозиторий на GitHub:"
    echo "   https://github.com/new"
    echo "   Название: composeai-app"
    echo "   Видимость: Public"
    echo ""
    echo "2. Добавьте remote репозиторий:"
    echo "   git remote add origin https://github.com/ВАШ_USERNAME/composeai-app.git"
    echo ""
    echo "   (Замените ВАШ_USERNAME на ваш GitHub username)"
    echo ""
    read -p "Нажмите Enter после создания репозитория на GitHub..."
fi

# Добавление всех файлов
echo "📤 Добавление файлов..."
git add .

# Проверка изменений
if git diff --staged --quiet; then
    echo "ℹ️  Нет изменений для коммита"
else
    # Создание коммита
    echo "💾 Создание коммита..."
    git commit -m "Deploy ComposeAI application to Streamlit Cloud" || {
        echo "⚠️  Не удалось создать коммит. Возможно, нет изменений."
    }
fi

# Отправка на GitHub
echo ""
echo "🚀 Отправка кода на GitHub..."
if git push origin main 2>&1 | grep -q "fatal"; then
    echo "⚠️  Не удалось отправить код."
    echo ""
    echo "📋 Возможные причины:"
    echo "   1. Remote репозиторий не настроен"
    echo "   2. Проблемы с аутентификацией"
    echo ""
    echo "💡 Решение:"
    echo "   1. Проверьте remote: git remote -v"
    echo "   2. Если нужно, добавьте remote:"
    echo "      git remote add origin https://github.com/ВАШ_USERNAME/composeai-app.git"
    echo "   3. Для аутентификации используйте Personal Access Token:"
    echo "      https://github.com/settings/tokens"
else
    echo "✅ Код успешно отправлен на GitHub!"
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║     ✅ ГОТОВО К РАЗВЕРТЫВАНИЮ!                                ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📋 СЛЕДУЮЩИЕ ШАГИ:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Откройте: https://share.streamlit.io/"
    echo ""
    echo "2. Войдите через GitHub"
    echo ""
    echo "3. Нажмите 'New app'"
    echo ""
    echo "4. Заполните форму:"
    echo "   • Repository: ВАШ_USERNAME/composeai-app"
    echo "   • Branch: main"
    echo "   • Main file path: app/app.py"
    echo ""
    echo "5. Нажмите 'Deploy'"
    echo ""
    echo "6. Подождите 1-2 минуты..."
    echo ""
    echo "7. Получите публичную ссылку!"
    echo ""
    echo "🔗 Ссылка будет вида:"
    echo "   https://ВАШ_USERNAME-composeai-app-XXXXXX.streamlit.app"
    echo ""
    echo "✨ Эту ссылку можно отправлять друзьям и открывать на любом устройстве!"
    echo ""
fi

