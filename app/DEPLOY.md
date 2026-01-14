# 🚀 Развертывание приложения

## Вариант 1: Streamlit Cloud (Рекомендуется - Бесплатно)

### Шаги:

1. **Создайте аккаунт на Streamlit Cloud:**
   - Перейдите на https://streamlit.io/cloud
   - Войдите через GitHub

2. **Загрузите код на GitHub:**
   ```bash
   cd "/Users/egorryzhkov/Desktop/AI Double"
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/github.com/ВАШ_РЕПОЗИТОРИЙ.git
   git push -u origin main
   ```

3. **Деплой на Streamlit Cloud:**
   - Перейдите на https://share.streamlit.io/
   - Нажмите "New app"
   - Выберите репозиторий
   - Main file path: `app/app.py`
   - Нажмите "Deploy"

4. **Получите ссылку:**
   - После деплоя вы получите ссылку вида: `https://ВАШ_ПОЛЬЗОВАТЕЛЬ-streamlit-app-XXXXXX.streamlit.app`
   - Эту ссылку можно отправлять друзьям!

---

## Вариант 2: Heroku

### Шаги:

1. **Создайте файл `Procfile`:**
   ```
   web: streamlit run app/app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Создайте `runtime.txt`:**
   ```
   python-3.11.0
   ```

3. **Деплой:**
   ```bash
   heroku create ваше-приложение
   git push heroku main
   ```

---

## Вариант 3: Локальный сервер (для тестирования)

### Запуск на локальной сети:

```bash
cd "/Users/egorryzhkov/Desktop/AI Double/app"
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

Затем откройте в браузере: `http://ВАШ_IP:8501`

---

## Мобильные и десктопные приложения

См. файлы:
- `mobile/` - для Android и iOS
- `desktop/` - для Windows

