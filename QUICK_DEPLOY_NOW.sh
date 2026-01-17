#!/bin/bash

# Быстрое развертывание на Streamlit Cloud

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🚀 БЫСТРОЕ РАЗВЕРТЫВАНИЕ НА STREAMLIT CLOUD               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd "/Users/egorryzhkov/Desktop/AI Double" || exit 1

echo "📤 Обновление кода на GitHub..."
echo ""

# Добавление всех файлов
git add .

# Проверка изменений
if git diff --staged --quiet && git diff --quiet; then
    echo "ℹ️  Нет изменений для отправки"
else
    # Создание коммита
    git commit -m "Update: готово к развертыванию на Streamlit Cloud" || {
        echo "⚠️  Не удалось создать коммит"
    }
    
    # Отправка на GitHub
    echo ""
    echo "🚀 Отправка на GitHub..."
    if git push origin main; then
        echo "✅ Код успешно обновлен на GitHub!"
    else
        echo "⚠️  Не удалось отправить код. Проверьте аутентификацию."
        echo ""
        echo "💡 Если нужен Personal Access Token:"
        echo "   https://github.com/settings/tokens"
        exit 1
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     ✅ КОД ОБНОВЛЕН НА GITHUB!                               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 СЛЕДУЮЩИЙ ШАГ: РАЗВЕРТЫВАНИЕ НА STREAMLIT CLOUD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Откройте: https://share.streamlit.io/"
echo ""
echo "2. Войдите через GitHub"
echo ""
echo "3. Нажмите 'New app'"
echo ""
echo "4. Заполните форму:"
echo "   • Repository: mregorish-dot/ai-composite-selector"
echo "   • Branch: main"
echo "   • Main file path: app/app.py"
echo ""
echo "5. Нажмите 'Deploy'"
echo ""
echo "6. Подождите 1-2 минуты..."
echo ""
echo "✨ После деплоя вы получите публичную ссылку!"
echo ""
echo "🔗 Ссылка будет вида:"
echo "   https://mregorish-dot-ai-composite-selector-XXXXXX.streamlit.app"
echo ""
echo "✅ Эту ссылку можно отправлять друзьям и открывать на любом устройстве!"

