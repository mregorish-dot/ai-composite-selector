"""
Веб-приложение для выбора композита на основе ИИ и ЭМГ-данных
Использует Streamlit для простого и красивого интерфейса
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sys
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта модулей
current_dir = Path(__file__).parent.absolute()
parent_dir = str(current_dir.parent)
current_dir_str = str(current_dir)

# ВАЖНО: Сначала добавляем текущую директорию (app/), чтобы использовать локальные версии модулей
# Затем добавляем родительскую директорию как резерв
for path in [current_dir_str, parent_dir]:
    if path in sys.path:
        sys.path.remove(path)  # Удаляем если уже есть
    sys.path.insert(0, path)  # Вставляем в начало

# Очистка кэша модулей для принудительной перезагрузки (важно для Streamlit)
if 'composite_selector' in sys.modules:
    del sys.modules['composite_selector']
if 'Код_нормализации_ЭМГ' in sys.modules:
    del sys.modules['Код_нормализации_ЭМГ']

# Импорт модулей
try:
    from composite_selector import CompositeSelector, PatientData
    from Код_нормализации_ЭМГ import EMGNormalizer, EMGApparatus
    from knowledge_extractor import KnowledgeExtractor, Article
    from preloaded_articles import get_preloaded_articles, get_extraction_rules
except ImportError as e:
    st.error(f"❌ Ошибка импорта модулей: {e}")
    st.error(f"Текущая директория: {current_dir_str}")
    st.error(f"Родительская директория: {parent_dir}")
    st.error("Убедитесь, что файлы composite_selector.py и Код_нормализации_ЭМГ.py находятся в правильной директории")
    st.stop()

# Настройка страницы
st.set_page_config(
    page_title="ComposeAI",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили отключены - используется стандартный интерфейс Streamlit

# Заголовок
st.title("🦷 ComposeAI")
st.markdown("---")

# Путь к файлу для сохранения статей
ARTICLES_SAVE_FILE = os.path.join(current_dir_str, "saved_articles.json")
PDF_DIR = os.path.join(current_dir_str, "saved_pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

def load_saved_articles():
    """Загрузка сохраненных статей из файла"""
    if os.path.exists(ARTICLES_SAVE_FILE):
        try:
            with open(ARTICLES_SAVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_articles(articles):
    """Сохранение статей в файл"""
    try:
        with open(ARTICLES_SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Ошибка сохранения статей: {e}")

# Инициализация сессионных переменных
if 'composite_selector' not in st.session_state:
    st.session_state.composite_selector = CompositeSelector()
if 'knowledge_extractor' not in st.session_state:
    st.session_state.knowledge_extractor = KnowledgeExtractor()
    # Предзагрузка статей
    preloaded = get_preloaded_articles()
    for article_data in preloaded:
        article = st.session_state.knowledge_extractor.add_article(**article_data)
        st.session_state.knowledge_extractor.process_article(article)
    
    # Загрузка клинических статей с ЭМГ и композитами
    try:
        from clinical_articles_data import get_clinical_articles
        clinical_articles = get_clinical_articles()
        for article_data in clinical_articles:
            article = st.session_state.knowledge_extractor.add_article(**article_data)
            st.session_state.knowledge_extractor.process_article(article)
    except ImportError:
        pass  # Модуль не найден, пропускаем
    
    # Загрузка сохраненных статей
    saved_articles = load_saved_articles()
    for article_data in saved_articles:
        if 'text' in article_data and article_data['text']:
            # Фильтруем только допустимые ключи для add_article
            allowed_keys = ['title', 'text', 'url', 'authors', 'year', 'journal', 'doi', 'keywords']
            filtered_data = {k: v for k, v in article_data.items() if k in allowed_keys}
            try:
                article = st.session_state.knowledge_extractor.add_article(**filtered_data)
                st.session_state.knowledge_extractor.process_article(article)
            except Exception as e:
                # Пропускаем статьи с ошибками, чтобы не блокировать запуск приложения
                print(f"Ошибка при загрузке статьи '{article_data.get('title', 'Unknown')}': {e}")
                continue

if 'articles' not in st.session_state:
    # Загружаем предзагруженные + клинические + сохраненные статьи
    preloaded = get_preloaded_articles()
    saved = load_saved_articles()
    # Добавляем клинические статьи
    try:
        from clinical_articles_data import get_clinical_articles
        clinical = get_clinical_articles()
    except ImportError:
        clinical = []
    # Объединяем, фильтруя некорректные данные
    all_articles = []
    for art in preloaded + clinical + saved:
        if isinstance(art, dict) and 'title' in art:
            all_articles.append(art)
    st.session_state.articles = all_articles

if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = st.session_state.knowledge_extractor.get_knowledge_base()
if 'article_rules' not in st.session_state:
    st.session_state.article_rules = get_extraction_rules()
if 'ml_model' not in st.session_state:
    st.session_state.ml_model = None  # ML модель для предсказания
if 'clinical_pairs' not in st.session_state:
    # Предзагружаем пары из клинических статей
    try:
        from clinical_articles_data import get_emg_composite_pairs
        from model_trainer import EMGCompositePair
        preloaded_pairs_data = get_emg_composite_pairs()
        preloaded_pairs = []
        for pair_data in preloaded_pairs_data:
            pair = EMGCompositePair(**pair_data)
            preloaded_pairs.append(pair)
        st.session_state.clinical_pairs = preloaded_pairs
    except (ImportError, Exception) as e:
        st.session_state.clinical_pairs = []  # Пары ЭМГ -> композит

# АВТОМАТИЧЕСКОЕ ОБУЧЕНИЕ МОДЕЛИ ПРИ ЗАПУСКЕ
if 'model_trained' not in st.session_state or not st.session_state.model_trained:
    # Автоматически обучаем модель на предзагруженных данных
    try:
        if 'clinical_pairs' in st.session_state and len(st.session_state.clinical_pairs) > 0:
            pairs_with_composites = [p for p in st.session_state.clinical_pairs if p.composite_name]
            if len(pairs_with_composites) >= 2:
                from model_trainer import CompositeModelTrainer
                trainer = CompositeModelTrainer()
                results = trainer.train(pairs_with_composites, model_type='random_forest')
                st.session_state.ml_model = trainer
                st.session_state.model_trained = True
                # Логируем успешное обучение (не отображаем в UI при автоматическом обучении)
                print(f"✅ Модель автоматически обучена при запуске приложения")
                print(f"   Точность: {results.get('accuracy', 'N/A')}")
                print(f"   Примеров для обучения: {results.get('train_size', 'N/A')}")
                print(f"   Уникальных композитов: {results.get('unique_composites', 'N/A')}")
            else:
                st.session_state.model_trained = False
                print(f"⚠️ Недостаточно пар с композитами для обучения: {len(pairs_with_composites)} (нужно минимум 2)")
        else:
            st.session_state.model_trained = False
            print("⚠️ Нет клинических пар для автоматического обучения модели")
    except Exception as e:
        st.session_state.model_trained = False
        print(f"❌ Ошибка при автоматическом обучении модели: {e}")
        import traceback
        traceback.print_exc()

# Боковое меню
st.sidebar.title("📋 Меню")
page = st.sidebar.radio(
    "Выберите раздел:",
    ["🏠 Главная", "📊 Выбор композита", "📥 Загрузка данных", "🤖 Обучение модели", "📈 Статистика"]
)

# ==================== ГЛАВНАЯ СТРАНИЦА ====================
if page == "🏠 Главная":
    st.header("Добро пожаловать!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Композитов в базе", len(st.session_state.composite_selector.db.composites))
    
    with col2:
        st.metric("Загружено статей", len(st.session_state.articles))
    
    with col3:
        status = "✅ Обучена" if st.session_state.model_trained else "⏳ Не обучена"
        # Используем обычную метрику, но с дополнительными стилями через CSS
        st.metric("Модель", status)
    
    # Показываем примененные правила
    if st.session_state.article_rules:
        st.markdown("---")
        st.info(f"""
        📚 **Применены правила из научных статей:**
        - Усадка ≤ {st.session_state.article_rules['shrinkage_threshold']}% (статья 1)
        - Наполнитель {st.session_state.article_rules['filler_min']}-{st.session_state.article_rules['filler_max']}% (статья 2)
        """)
    
    st.markdown("---")
    
    st.subheader("📖 Описание системы")
    st.markdown("""
    **ComposeAI** использует искусственный интеллект для выбора оптимального композитного материала 
    для реставрации жевательных зубов на основе:
    
    - **ЭМГ-данных** (электромиография жевательных и височных мышц)
    - **Технических характеристик** композитов
    - **Клинических особенностей** пациента (аномалии прикуса, стираемость)
    - **Знаний из научных статей** и учебных материалов
    
    ### Как использовать:
    1. Перейдите в раздел **"Выбор композита"**
    2. Введите ЭМГ-данные пациента
    3. Получите рекомендации с обоснованием на основе научных данных
    
    ### Для обучения модели:
    1. Загрузите научные статьи и учебные материалы в разделе **"Загрузка данных"**
    2. Система автоматически извлечет знания из статей:
       - Рекомендации по композитам
       - ЭМГ-показатели и нормальные значения
       - Клинические критерии выбора
       - Технические характеристики материалов
    3. Обучите модель в разделе **"Обучение модели"**
    4. Модель будет использовать актуальные данные из литературы
    """)
    
    st.markdown("---")
    st.subheader("🔬 Исследование")
    st.info("""
    **Тема:** Применение ИИ и цифровых технологий для выбора композита и проведения 
    реставраций жевательных зубов прямым методом с учётом данных ЭМГ и технических 
    характеристик композита у пациентов с аномалиями прикуса.
    
    **Цель:** Разработка автоматизированной системы выбора оптимального композитного 
    материала на основе объективных данных.
    """)

# ==================== ВЫБОР КОМПОЗИТА ====================
elif page == "📊 Выбор композита":
    st.header("Выбор композита на основе ЭМГ-данных")
    
    with st.expander("ℹ️ Инструкция", expanded=False):
        st.markdown("""
        Введите ЭМГ-данные пациента в покое. Система автоматически:
        - Проверит патологию при показателях ≥ 1.5 мкВ у всех 4 мышц
        - Вычислит MVC гиперфункцию (%) и MVC длительность из анализа
        - Выберет оптимальные композиты с обоснованием на основе клинической классификации стираемости (Бушан М.Г. или TWES 2.0)
        """)
    
    # Дополнительные фильтры (перед формой)
    with st.expander("🔧 Дополнительные фильтры", expanded=False):
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            filter_region = st.multiselect(
                "Страна/Регион производителя",
                ["Все", "USA", "Russia", "Italy", "Asia", "International"],
                default=["Все"]
            )
        
        with filter_col2:
            filter_manufacturer = st.multiselect(
                "Компания производитель",
                ["Все", "3M ESPE", "Ivoclar Vivadent", "Dentsply Sirona", "Kulzer", "Voco", "Kerr", "Ultradent", "DMG", "Schütz Dental", "COLTENE", "Septodont", "Heraeus", "Micerium", "Другие"],
                default=["Все"]
            )
        
        with filter_col3:
            filter_year_min = st.number_input(
                "Год выпуска (от)",
                min_value=1990,
                max_value=2025,
                value=2000,
                help="Минимальный год выпуска композита на рынок"
            )
        
        with filter_col4:
            filter_price_max = st.number_input(
                "Макс. цена (руб)",
                min_value=0,
                max_value=50000,
                value=50000,
                step=500,
                help="Максимальная цена на российском рынке"
            )
    
    # Выбор классификации ВЫНЕСЕН ИЗ ФОРМЫ для мгновенной синхронизации
    st.subheader("Классификация стираемости")
    
    # Отслеживание изменения классификации для автоматической синхронизации
    if 'previous_wear_severity_type' not in st.session_state:
        st.session_state.previous_wear_severity_type = None
    
    col_class1, col_class2 = st.columns(2)
    
    with col_class1:
        wear_severity_type = st.radio(
            "Тип классификации стираемости",
            ["TWES 2.0 (современная)", "По Бушану М.Г. (классическая)"],
            help="TWES 2.0 - современная классификация (2020), Бушан - классическая клиническая (на основании клинического обследования)",
            key="wear_severity_type_radio"
        )
        
        # Сброс выбранной степени при изменении классификации
        if st.session_state.previous_wear_severity_type is not None and st.session_state.previous_wear_severity_type != wear_severity_type:
            # Классификация изменилась - сбрасываем степень
            if 'wear_severity_twes' in st.session_state:
                st.session_state.wear_severity_twes = "Не указана"
            if 'wear_severity_bushan' in st.session_state:
                st.session_state.wear_severity_bushan = "Не указана"
        
        st.session_state.previous_wear_severity_type = wear_severity_type
    
    with col_class2:
        if wear_severity_type == "TWES 2.0 (современная)":
            col_wear1, col_wear2 = st.columns([2, 1])
            with col_wear1:
                wear_severity = st.selectbox(
                    "Степень стираемости (TWES 2.0)",
                    ["Не указана", "Grade 0", "Grade 1", "Grade 2", "Grade 3", "Grade 4"],
                    help="Grade 0-4 по TWES 2.0",
                    key="wear_severity_twes"
                )
            with col_wear2:
                if wear_severity != "Не указана":
                    twes_descriptions = {
                        "Grade 0": "0 - Не наблюдается стираемость",
                        "Grade 1": "1 - Лёгкая степень до 1/3 коронки",
                        "Grade 2": "2 - Лёгкая степень до 1/3 коронки",
                        "Grade 3": "3 - Средняя степень от 1/3 до 2/3 коронки",
                        "Grade 4": "4 - Тяжёлая степень более 2/3 коронки"
                    }
                    st.markdown(f"**{twes_descriptions.get(wear_severity, '')}**")
            
            # Конвертация для системы
            twes_map = {
                "Не указана": None,
                "Grade 0": "twes_0",
                "Grade 1": "twes_1",
                "Grade 2": "twes_2",
                "Grade 3": "twes_3",
                "Grade 4": "twes_4"
            }
            wear_severity = twes_map[wear_severity]
        else:  # По Бушану М.Г.
            col_wear1, col_wear2 = st.columns([2, 1])
            with col_wear1:
                wear_severity = st.selectbox(
                    "Степень патологической стираемости по Бушану",
                    ["Не указана", "I степень", "II степень", "III степень", "IV степень"],
                    help="Определяется на основании клинического обследования (не по ЭМГ)",
                    key="wear_severity_bushan"
                )
            with col_wear2:
                if wear_severity != "Не указана":
                    bush_descriptions = {
                        "I степень": "1 - Не наблюдается стираемость (в пределах эмали)",
                        "II степень": "2 - Лёгкая степень до 1/3 коронки",
                        "III степень": "3 - Средняя степень от 1/3 до 2/3 коронки",
                        "IV степень": "4 - Тяжёлая степень более 2/3 коронки"
                    }
                    st.markdown(f"**{bush_descriptions.get(wear_severity, '')}**")
            
            # Конвертация для системы
            bush_map = {
                "Не указана": None,
                "I степень": "bushan_I",
                "II степень": "bushan_II", 
                "III степень": "bushan_III",
                "IV степень": "bushan_IV"
            }
            wear_severity = bush_map[wear_severity]
    
    st.markdown("---")
    
    # Форма ввода данных
    with st.form("patient_data_form"):
        st.subheader("ЭМГ-данные")
        
        col1, col2 = st.columns(2)
        
        with col1:
            apparatus = st.selectbox(
                "Тип ЭМГ-аппарата",
                ["BjoEMG II", "Synapsys", "Kolibri", "Other"],
                help="Выберите аппарат, которым были получены данные"
            )
            
            st.markdown("**В покое (средняя амплитуда, мкВ):**")
            
            # Динамические пометки о патологии в зависимости от аппарата
            if apparatus == "BjoEMG II":
                st.caption("⚠️ Патология определяется при показателях ≥ 1.5 мкВ у всех 4 мышц")
            elif apparatus == "Synapsys":
                st.caption("⚠️ Патология при жевании: жевательная правая ≥ 350.5 мкВ, левая ≥ 339.25 мкВ; височная правая ≥ 243.25 мкВ, левая ≥ 234.8 мкВ")
            elif apparatus == "Kolibri":
                st.caption("⚠️ Патология: жевательная средняя ≥ 111 мкВ; височная средняя ≥ 427 мкВ")
            else:
                st.caption("⚠️ Патология определяется по нормативным значениям для выбранного аппарата")
            # Динамические подсказки в зависимости от аппарата
            if apparatus == "BjoEMG II":
                help_masseter_r = "Патология при ≥ 1.5 мкВ"
                help_masseter_l = "Патология при ≥ 1.5 мкВ"
                help_temporalis_r = "Патология при ≥ 1.5 мкВ"
                help_temporalis_l = "Патология при ≥ 1.5 мкВ"
            elif apparatus == "Synapsys":
                help_masseter_r = "Патология при жевании ≥ 350.5 мкВ"
                help_masseter_l = "Патология при жевании ≥ 339.25 мкВ"
                help_temporalis_r = "Патология при жевании ≥ 243.25 мкВ"
                help_temporalis_l = "Патология при жевании ≥ 234.8 мкВ"
            elif apparatus == "Kolibri":
                help_masseter_r = "Патология: средняя ≥ 111 мкВ"
                help_masseter_l = "Патология: средняя ≥ 111 мкВ"
                help_temporalis_r = "Патология: средняя ≥ 427 мкВ"
                help_temporalis_l = "Патология: средняя ≥ 427 мкВ"
            else:
                help_masseter_r = "Введите значение в покое"
                help_masseter_l = "Введите значение в покое"
                help_temporalis_r = "Введите значение в покое"
                help_temporalis_l = "Введите значение в покое"
            
            masseter_r_rest = st.number_input(
                "Жевательная мышца, правая", 
                min_value=0.0, 
                value=0.0,
                step=0.1,
                help=help_masseter_r
            )
            masseter_l_rest = st.number_input(
                "Жевательная мышца, левая", 
                min_value=0.0, 
                value=0.0,
                step=0.1,
                help=help_masseter_l
            )
            temporalis_r_rest = st.number_input(
                "Височная мышца, правая", 
                min_value=0.0, 
                value=0.0,
                step=0.1,
                help=help_temporalis_r
            )
            temporalis_l_rest = st.number_input(
                "Височная мышца, левая", 
                min_value=0.0, 
                value=0.0,
                step=0.1,
                help=help_temporalis_l
            )
        
        with col2:
            # Параметры максимального сжатия убраны из UI (правка 3)
            # Оставлены в коде для будущего использования (правка 4)
            # Установлены значения по умолчанию
            masseter_r_max = 0.0
            masseter_l_max = 0.0
            temporalis_r_max = 0.0
            temporalis_l_max = 0.0
        
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            age = st.number_input("Возраст пациента", min_value=0, max_value=120, value=None)
            occlusion_anomaly = st.text_input(
                "Тип аномалии прикуса (если есть)", 
                value="",
                help="Например: открытый прикус, глубокий прикус и т.д."
            )
        
        with col4:
            # Классификация уже выбрана выше, здесь только показываем информацию
            st.info(f"**Выбрана классификация:** {wear_severity_type}")
            if wear_severity and wear_severity is not None:
                if wear_severity.startswith('twes_'):
                    grade = wear_severity.replace('twes_', '')
                    st.info(f"**Степень (TWES 2.0):** Grade {grade}")
                elif wear_severity.startswith('bushan_'):
                    degree = wear_severity.replace('bushan_', '')
                    st.info(f"**Степень (Бушан М.Г.):** {degree} степень")
        
        submitted = st.form_submit_button("🔍 Найти оптимальный композит", use_container_width=True)
    
    # Обработка формы
    if submitted:
        # Подготовка данных
        # wear_severity уже обработан выше (может быть bushan_I, bushan_II и т.д. или none, mild и т.д.)
        wear_sev = wear_severity
        
        # Подготовка фильтров
        region_filt = None if "Все" in filter_region else filter_region
        manufacturer_filt = None if "Все" in filter_manufacturer else filter_manufacturer
        
        patient = PatientData(
            apparatus=apparatus,
            masseter_right_chewing=masseter_r_rest,  # Правка 2: в покое, не при жевании
            masseter_left_chewing=masseter_l_rest,
            temporalis_right_chewing=temporalis_r_rest,
            temporalis_left_chewing=temporalis_l_rest,
            masseter_right_max_clench=masseter_r_max,  # Правка 3: скрыто в UI, но остаётся в коде для будущего
            masseter_left_max_clench=masseter_l_max,
            temporalis_right_max_clench=temporalis_r_max,
            temporalis_left_max_clench=temporalis_l_max,
            age=age if age else None,
            occlusion_anomaly_type=occlusion_anomaly if occlusion_anomaly else None,
            wear_severity=wear_sev,
            mvc_hyperfunction_percent=None,  # Правка 6: вычисляется и выводится из анализа
            mvc_duration_sec_per_min=None,   # Правка 6: вычисляется и выводится из анализа
            region_filter=region_filt,
            manufacturer_filter=manufacturer_filt,
            year_min=filter_year_min if filter_year_min > 1990 else None,
            price_max=filter_price_max if filter_price_max < 50000 else None
        )
        
        # Поиск композитов с применением правил из статей
        with st.spinner("Анализ данных и выбор композита с учетом научных статей..."):
            results = st.session_state.composite_selector.select_composite(
                patient, 
                top_n=5,
                include_alternatives=True  # Включаем альтернативные варианты
            )
            
            # Показываем примененные правила из статей
            if st.session_state.article_rules:
                with st.expander("📚 Применены правила из научных статей", expanded=False):
                    rules = st.session_state.article_rules
                    st.markdown(f"""
                    **📄 Статья 1 (RIZZANTE et al. 2019):**
                    - ✅ Исключены композиты с усадкой >{rules['shrinkage_threshold']}%
                    - Источник: [Dental Materials Journal]({get_preloaded_articles()[0]['url']})
                    
                    **📄 Статья 2 (PubMed 24909664):**
                    - ✅ **Приоритет:** Композиты с наполнителем {rules['filler_min']}-{rules['filler_max']}%
                    - ⚠️ **Альтернатива:** Композиты с наполнителем ≥{rules['filler_max']}% (предлагаются во вторую очередь)
                    - ❌ **Исключены:** Композиты с наполнителем <{rules['filler_min']}%
                    - Источник: [PubMed]({get_preloaded_articles()[1]['url']})
                    """)
                    
                    # Статистика результатов
                    if results:
                        priority_count = sum(1 for _, _, j in results if j.get('is_priority', True))
                        alternative_count = len(results) - priority_count
                        st.info(f"""
                        📊 **Результаты:**
                        - Приоритетных вариантов (наполнитель 25-50%): {priority_count}
                        - Альтернативных вариантов (наполнитель >50%): {alternative_count}
                        """)
                    
                    # Информация о классификации
                    if wear_sev:
                        if wear_sev.startswith('twes_'):
                            grade = wear_sev.replace('twes_', '')
                            twes_data = st.session_state.composite_selector.db.twes2_classification
                            if twes_data and 'grades' in twes_data and grade in twes_data['grades']:
                                twes_info = twes_data['grades'][grade]
                                with st.expander("📚 Информация о классификации TWES 2.0", expanded=False):
                                    st.markdown(f"""
                                    **{twes_info['name']} - {twes_info['description']}**
                                    
                                    - **Глубина:** {twes_info['depth']}
                                    - **Ткани:** {twes_info['tissues']}
                                    - **Характеристика:** {twes_info['characteristics']}
                                    - **Клиническое значение:** {twes_info['clinical_significance']}
                                    
                                    **Рекомендации для композита:**
                                    - Микротвердость: ≥{twes_info['recommended_microhardness_min']} KHN
                                    - Износостойкость: {twes_info['recommended_wear_resistance']}
                                    - Наполнитель: ≥{twes_info['recommended_filler_min']}%
                                    
                                    *Источник: Wetselaar et al. 2020, Journal of Oral Rehabilitation*
                                    *[Ссылка на статью]({twes_data.get('url', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC7384115/')})*
                                    """)
                        elif wear_sev.startswith('bushan_'):
                            degree = wear_sev.replace('bushan_', '')
                            bush_data = st.session_state.composite_selector.db.bushan_classification
                            if bush_data and 'degrees' in bush_data and degree in bush_data['degrees']:
                                bush_info = bush_data['degrees'][degree]
                                with st.expander("📚 Информация о классификации по Бушану", expanded=False):
                                    st.markdown(f"""
                                    **{bush_info['name']} патологической стираемости:**
                                    
                                    - **Глубина:** {bush_info['depth']}
                                    - **Ткани:** {bush_info['tissues']}
                                    - **Характеристика:** {bush_info['characteristics']}
                                    - **Клиническое значение:** {bush_info['clinical_significance']}
                                    
                                    **Рекомендации для композита:**
                                    - Микротвердость: ≥{bush_info['recommended_microhardness_min']} KHN
                                    - Износостойкость: {bush_info['recommended_wear_resistance']}
                                    - Наполнитель: ≥{bush_info['recommended_filler_min']}%
                                    """)
        
        if results:
            st.success(f"✅ Найдено {len(results)} рекомендуемых композита(ов)")
            
            # Правка 6: Вывод MVC показателей из анализа (в покое)
            # Расчет MVC гиперфункции (%) и длительности на основе данных в покое
            if masseter_r_rest and masseter_l_rest and temporalis_r_rest and temporalis_l_rest:
                # Проверка патологии: ≥ 1.5 мкВ у всех 4 мышц (правка 2)
                rest_values = [masseter_r_rest, masseter_l_rest, temporalis_r_rest, temporalis_l_rest]
                all_above_threshold = all(val >= 1.5 for val in rest_values)
                
                if all_above_threshold:
                    # Расчет MVC гиперфункции (%)
                    # Референсные значения в покое из литературы: ~2.5 мкВ (среднее из 1.0-4.0 мкВ)
                    avg_masseter_rest = (masseter_r_rest + masseter_l_rest) / 2
                    avg_temporalis_rest = (temporalis_r_rest + temporalis_l_rest) / 2
                    ref_rest_normal = 2.5  # Нормальное значение в покое (литература)
                    mvc_hyperfunction_percent_masseter = ((avg_masseter_rest - ref_rest_normal) / ref_rest_normal) * 100
                    mvc_hyperfunction_percent_temporalis = ((avg_temporalis_rest - ref_rest_normal) / ref_rest_normal) * 100
                    mvc_hyperfunction_avg = (mvc_hyperfunction_percent_masseter + mvc_hyperfunction_percent_temporalis) / 2
                    
                    # Расчет MVC длительности (сек/мин) на основе степени отклонения от нормы
                    # Основано на литературе: при гиперфункции 5-20% = 1-2 сек/мин, 20%+ = 4-6 сек/мин
                    max_deviation = max(abs(mvc_hyperfunction_percent_masseter), abs(mvc_hyperfunction_percent_temporalis))
                    if max_deviation <= 5:
                        mvc_duration_sec_per_min = 1.0
                    elif max_deviation <= 20:
                        mvc_duration_sec_per_min = 1.0 + ((max_deviation - 5) / 15) * 1.0  # От 1 до 2
                    else:
                        mvc_duration_sec_per_min = 2.0 + min(((max_deviation - 20) / 30) * 4.0, 4.0)  # От 2 до 6
                    
                    # Ограничиваем значения до разумных пределов
                    mvc_hyperfunction_avg = max(0, min(mvc_hyperfunction_avg, 500))  # Максимум 500%
                    mvc_duration_sec_per_min = max(1.0, min(mvc_duration_sec_per_min, 6.0))  # От 1 до 6 сек/мин
                    
                    # Аккуратное отображение MVC показателей в карточках
                    st.markdown("#### 📊 Анализ MVC показателей")
                    col_mvc1, col_mvc2 = st.columns(2)
                    with col_mvc1:
                        st.metric(
                            "MVC гиперфункция (%)",
                            f"{mvc_hyperfunction_avg:.1f}%",
                            delta=f"Мас: {mvc_hyperfunction_percent_masseter:.1f}%, Вис: {mvc_hyperfunction_percent_temporalis:.1f}%"
                        )
                    with col_mvc2:
                        st.metric(
                            "MVC длительность (сек/мин)",
                            f"{mvc_duration_sec_per_min:.2f}",
                            delta="Расчётная"
                        )
                    st.markdown("---")
                else:
                    st.info("ℹ️ Патология не выявлена: показатели в покое < 1.5 мкВ (норма)")
                    st.markdown("---")
            
            # Отображение результатов
            for i, (composite, score, justification) in enumerate(results, 1):
                with st.container():
                    # Определяем, приоритетный это вариант или альтернативный
                    is_priority = justification.get('is_priority', True)
                    
                    # Заголовок и оценка - аккуратный формат
                    with st.container():
                        if is_priority:
                            st.markdown(f"### ✅ Вариант {i}: {composite['name']}")
                            st.caption("**Приоритетный вариант**")
                        else:
                            st.markdown(f"### ⚠️ Вариант {i}: {composite['name']}")
                            filler_pct = justification.get('filler_content', 0)
                            st.caption(f"**Альтернативный вариант** • Наполнитель: {filler_pct:.0f}% (оптимально 25-50%)")
                        st.markdown(f"**Оценка:** `{score:.3f} / 1.000`")
                    
                    # Используется стандартный интерфейс Streamlit без кастомных стилей
                    
                    # CSS для убирания троеточий БЕЗ переносов слов
                    st.markdown("""
                    <style>
                    /* Убираем троеточия но запрещаем переносы слов в метриках */
                    [data-testid="stMetricValue"],
                    [data-testid="stMetricValue"] * {
                        white-space: nowrap !important; /* Запрещаем перенос */
                        overflow: visible !important;
                        text-overflow: clip !important;
                        word-wrap: normal !important;
                        word-break: keep-all !important; /* Не разрываем слова */
                        max-width: 100% !important;
                        font-size: 0.9rem !important; /* Уменьшаем шрифт чтобы поместилось */
                    }
                    [data-testid="stMetricLabel"],
                    [data-testid="stMetricLabel"] * {
                        white-space: nowrap !important; /* Запрещаем перенос */
                        overflow: visible !important;
                        text-overflow: clip !important;
                        word-wrap: normal !important;
                        word-break: keep-all !important;
                        font-size: 0.7rem !important; /* Уменьшаем шрифт метки */
                    }
                    [data-testid="stMetricContainer"] {
                        overflow: visible !important;
                        min-width: 180px !important; /* Увеличиваем минимальную ширину */
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # Все метрики в одном ряду - 5 колонок (микротвердость + 4 остальные)
                    cols = st.columns(5)
                    with cols[0]:
                        st.metric("Микротвердость", f"{composite['microhardness_KHN']:.1f} KHN")
                    with cols[1]:
                        st.metric("Усадка", f"{composite['polymerization_shrinkage_percent']:.2f}%")
                    
                    # Наполнитель с индикацией в метке - сокращаем для помещается в рамку
                    filler = composite['filler_content_percent']
                    with cols[2]:
                        if 25 <= filler < 50:
                            st.metric("Наполнитель (опт.)", f"{filler:.0f}%")
                        elif filler >= 50:
                            st.metric("Наполнитель (альт.)", f"{filler:.0f}%")
                        else:
                            st.metric("Наполнитель", f"{filler:.0f}%")
                    
                    with cols[3]:
                        # Переводим износостойкость на русский для читаемости - сокращаем
                        wear_ru = {
                            'low': 'Низкая',
                            'medium': 'Средняя',
                            'high': 'Высокая',
                            'very_high': 'Оч.высокая'  # Без пробела для компактности
                        }
                        wear_display = wear_ru.get(composite['wear_resistance'], composite['wear_resistance'])
                        st.metric("Износостойкость", wear_display)
                    
                    with cols[4]:
                        st.metric("Глубина", f"{composite['depth_of_cure_mm']:.2f} мм")
                    
                    # Обоснование
                    st.markdown("**Обоснование выбора:**")
                    for reason in justification['reasons']:
                        st.markdown(f"  ✓ {reason}")
                    
                    if justification.get('notes'):
                        st.info(f"💡 {justification['notes']}")
                    
                    if justification.get('priority_note'):
                        st.warning(f"📌 {justification['priority_note']}")
                    
                    st.markdown("---")
        else:
            st.warning("⚠️ Не найдено подходящих композитов. Попробуйте изменить критерии поиска.")

# ==================== ЗАГРУЗКА ДАННЫХ ====================
elif page == "📥 Загрузка данных":
    st.header("📚 Загрузка научных статей и учебных материалов")
    
    st.info("""
    Загрузите научные статьи, учебные материалы и ссылки на публикации для обучения модели.
    Система автоматически извлечет знания о:
    - Рекомендациях по выбору композитов
    - ЭМГ-показателях и нормальных значениях
    - Клинических критериях выбора
    - Технических характеристиках материалов
    """)
    
    # Вкладки для разных способов загрузки
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Загрузка текста статьи", "📑 Загрузка PDF", "🔗 Добавление ссылки", "📋 Список статей"])
    
    with tab1:
        st.subheader("Загрузка текста статьи")
        
        with st.form("article_text_form"):
            title = st.text_input("Название статьи *", placeholder="Например: Исследование композитов для жевательных зубов")
            authors = st.text_input("Авторы", placeholder="Иванов И.И., Петров П.П.")
            journal = st.text_input("Журнал", placeholder="Клиническая стоматология")
            year = st.number_input("Год публикации", min_value=1900, max_value=2030, value=2024)
            doi = st.text_input("DOI", placeholder="10.1234/example")
            url = st.text_input("Ссылка на статью", placeholder="https://...")
            
            text = st.text_area(
                "Текст статьи *",
                height=300,
                placeholder="Вставьте текст статьи или скопируйте из PDF. Система автоматически извлечет информацию о композитах, ЭМГ-показателях и рекомендациях..."
            )
            
            keywords = st.text_input("Ключевые слова (через запятую)", placeholder="композит, ЭМГ, жевательные зубы")
            
            submitted = st.form_submit_button("📥 Добавить статью и извлечь знания", use_container_width=True)
            
            if submitted:
                if not title or not text:
                    st.error("❌ Заполните обязательные поля: название и текст статьи")
                else:
                    with st.spinner("Обработка статьи и извлечение знаний..."):
                        kw_list = [k.strip() for k in keywords.split(",")] if keywords else []
                        
                        article = st.session_state.knowledge_extractor.add_article(
                            title=title,
                            text=text,
                            authors=authors,
                            year=int(year) if year else None,
                            journal=journal,
                            doi=doi,
                            url=url,
                            keywords=kw_list
                        )
                        
                        knowledge = st.session_state.knowledge_extractor.process_article(article)
                        article_data = {
                            'title': title,
                            'authors': authors,
                            'year': year,
                            'journal': journal,
                            'text': text,  # Сохраняем текст
                            'url': url,
                            'doi': doi,
                            'keywords': kw_list,
                            'source': 'text_input'
                        }
                        st.session_state.articles.append(article_data)
                        save_articles(st.session_state.articles)  # Автосохранение
                        
                        st.success(f"✅ Статья добавлена! Извлечено знаний:")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Рекомендации", len(knowledge.composite_recommendations))
                        col2.metric("ЭМГ-показатели", len(knowledge.emg_guidelines))
                        col3.metric("Критерии", len(knowledge.clinical_criteria))
                        col4.metric("Характеристики", len(knowledge.technical_specs))
                        
                        if knowledge.composite_recommendations:
                            st.markdown("**Найденные рекомендации по композитам:**")
                            for rec in knowledge.composite_recommendations[:5]:
                                st.write(f"- {rec['composite']}: {rec['context'][:100]}...")
    
    with tab2:
        st.subheader("Загрузка PDF файла")
        
        st.info("""
        Загрузите PDF файл научной статьи. Система автоматически:
        - Извлечет текст из PDF
        - Найдет название статьи
        - Извлечет знания о композитах, ЭМГ-показателях и рекомендациях
        """)
        
        uploaded_pdf = st.file_uploader(
            "Выберите PDF файл",
            type=['pdf'],
            help="Поддерживаются PDF файлы научных статей"
        )
        
        if uploaded_pdf is not None:
            with st.form("pdf_article_form"):
                st.markdown("**Метаданные статьи (опционально, можно заполнить позже):**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    pdf_title = st.text_input("Название статьи", placeholder="Автоматически определится из PDF")
                    pdf_authors = st.text_input("Авторы", placeholder="Иванов И.И., Петров П.П.")
                    pdf_journal = st.text_input("Журнал", placeholder="Клиническая стоматология")
                
                with col2:
                    pdf_year = st.number_input("Год публикации", min_value=1900, max_value=2030, value=None)
                    pdf_doi = st.text_input("DOI", placeholder="10.1234/example")
                    pdf_url = st.text_input("Ссылка на статью", placeholder="https://...")
                
                submitted_pdf = st.form_submit_button("📥 Обработать PDF и извлечь знания", use_container_width=True)
                
                if submitted_pdf:
                    try:
                        with st.spinner("Извлечение текста из PDF и обработка..."):
                            # Чтение PDF
                            pdf_bytes = uploaded_pdf.read()
                            
                            # Сохранение PDF файла на диск
                            pdf_filename = uploaded_pdf.name
                            if not pdf_filename:
                                pdf_filename = f"article_{len(st.session_state.articles) + 1}.pdf"
                            pdf_path = os.path.join(PDF_DIR, pdf_filename)
                            with open(pdf_path, 'wb') as f:
                                f.write(pdf_bytes)
                            
                            # Обработка PDF
                            knowledge = st.session_state.knowledge_extractor.process_pdf_article(
                                pdf_file=pdf_bytes,
                                title=pdf_title if pdf_title else "",
                                authors=pdf_authors,
                                year=int(pdf_year) if pdf_year else None,
                                journal=pdf_journal,
                                url=pdf_url,
                                doi=pdf_doi
                            )
                            
                            # Получение названия из обработанной статьи
                            article_title = knowledge.article_title
                            
                            # Извлечение текста из PDF для сохранения
                            pdf_text = st.session_state.knowledge_extractor.extract_text_from_pdf(pdf_bytes)
                            
                            # Добавление в список статей
                            article_data = {
                                'title': article_title,
                                'authors': pdf_authors,
                                'year': pdf_year,
                                'journal': pdf_journal,
                                'url': pdf_url,
                                'doi': pdf_doi,
                                'text': pdf_text,  # Сохраняем извлеченный текст
                                'pdf_filename': pdf_filename,  # Имя сохраненного PDF
                                'pdf_path': pdf_path,  # Путь к PDF
                                'source': 'PDF'
                            }
                            st.session_state.articles.append(article_data)
                            save_articles(st.session_state.articles)  # Автосохранение
                            
                            st.success(f"✅ PDF обработан! Статья: {article_title}")
                            
                            # Показываем извлеченные знания
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Рекомендации", len(knowledge.composite_recommendations))
                            col2.metric("ЭМГ-показатели", len(knowledge.emg_guidelines))
                            col3.metric("Критерии", len(knowledge.clinical_criteria))
                            col4.metric("Характеристики", len(knowledge.technical_specs))
                            
                            if knowledge.composite_recommendations:
                                st.markdown("**Найденные рекомендации по композитам:**")
                                for rec in knowledge.composite_recommendations[:5]:
                                    st.write(f"- **{rec['composite']}**: {rec['context'][:150]}...")
                            
                            if knowledge.emg_guidelines:
                                st.markdown("**Найденные ЭМГ-показатели:**")
                                for guide in knowledge.emg_guidelines[:5]:
                                    st.write(f"- {guide['value']} ± {guide['std']} мкВ: {guide['context'][:100]}...")
                            
                            # Обновление базы знаний
                            st.session_state.knowledge_base = st.session_state.knowledge_extractor.get_knowledge_base()
                            
                    except ImportError as e:
                        st.error(f"❌ Ошибка: {e}")
                        st.info("""
                        **Установите библиотеку для работы с PDF:**
                        ```bash
                        pip install PyPDF2
                        ```
                        или
                        ```bash
                        pip install pdfplumber
                        ```
                        """)
                    except Exception as e:
                        st.error(f"❌ Ошибка при обработке PDF: {str(e)}")
                        st.info("Убедитесь, что файл является корректным PDF документом")
    
    with tab3:
        st.subheader("Добавление ссылки на статью")
        
        with st.form("article_url_form"):
            url = st.text_input("URL статьи *", placeholder="https://journals.eco-vector.com/...")
            title = st.text_input("Название статьи", placeholder="Автоматически определится или введите вручную")
            note = st.text_area("Примечания", placeholder="Дополнительная информация о статье")
            
            if st.form_submit_button("🔗 Добавить ссылку", use_container_width=True):
                if url:
                    article = st.session_state.knowledge_extractor.add_article(
                        title=title or "Статья по ссылке",
                        url=url,
                        text=note or ""
                    )
                    st.session_state.articles.append({
                        'title': title or "Статья по ссылке",
                        'url': url
                    })
                    st.success(f"✅ Ссылка добавлена! Всего статей: {len(st.session_state.articles)}")
                    st.info("💡 Для извлечения знаний загрузите текст статьи в первой вкладке")
                else:
                    st.error("❌ Введите URL статьи")
    
    with tab4:
        st.subheader("Загруженные статьи")
        
        # Кнопка для экспорта всех статей
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📚 Всего статей в системе: {len(st.session_state.articles)}")
        with col2:
            if st.button("💾 Сохранить все статьи", use_container_width=True):
                save_articles(st.session_state.articles)
                st.success("✅ Статьи сохранены!")
        
        if len(st.session_state.articles) == 0:
            st.info("📚 Пока нет загруженных статей. Добавьте статьи во вкладках выше.")
        else:
            # Разделение на предзагруженные и загруженные пользователем
            preloaded = get_preloaded_articles()
            preloaded_titles = {a['title'] for a in preloaded}
            user_articles = [a for a in st.session_state.articles if a.get('title') not in preloaded_titles]
            
            if user_articles:
                st.success(f"✅ Загружено пользователем: {len(user_articles)} статей")
                st.markdown("---")
            
            for i, article in enumerate(st.session_state.articles, 1):
                is_preloaded = article.get('title') in preloaded_titles
                source_badge = "🔵 Предзагружена" if is_preloaded else "📥 Загружена пользователем"
                
                with st.expander(f"📄 {i}. {article.get('title', 'Без названия')} {source_badge}"):
                    if article.get('authors'):
                        st.write(f"**Авторы:** {article['authors']}")
                    if article.get('year'):
                        st.write(f"**Год:** {article['year']}")
                    if article.get('journal'):
                        st.write(f"**Журнал:** {article['journal']}")
                    if article.get('url'):
                        st.write(f"**Ссылка:** [{article['url']}]({article['url']})")
                    if article.get('doi'):
                        st.write(f"**DOI:** {article['doi']}")
                    if article.get('source') == 'PDF' and article.get('pdf_filename'):
                        st.write(f"**PDF файл:** {article['pdf_filename']}")
                        # Кнопка для скачивания PDF
                        if os.path.exists(article.get('pdf_path', '')):
                            with open(article['pdf_path'], 'rb') as pdf_file:
                                st.download_button(
                                    label="📥 Скачать PDF",
                                    data=pdf_file.read(),
                                    file_name=article['pdf_filename'],
                                    mime="application/pdf"
                                )
                    if article.get('text'):
                        with st.expander("📝 Просмотр текста статьи"):
                            st.text_area("Текст", article['text'], height=200, disabled=True, key=f"text_{i}")
            
            # Обновление базы знаний
            if st.button("🔄 Обновить базу знаний", use_container_width=True):
                st.session_state.knowledge_base = st.session_state.knowledge_extractor.get_knowledge_base()
                st.success("✅ База знаний обновлена!")
                
                if st.session_state.knowledge_base:
                    st.json(st.session_state.knowledge_base)

# ==================== ОБУЧЕНИЕ МОДЕЛИ ====================
elif page == "🤖 Обучение модели":
    st.header("🤖 Обучение модели на основе научных статей")
    
    if len(st.session_state.articles) == 0:
        st.warning("⚠️ Нет загруженных статей. Загрузите статьи в разделе 'Загрузка данных'.")
    else:
        # Статистика базы знаний
        kb = st.session_state.knowledge_extractor.get_knowledge_base()
        
        st.info(f"""
        📊 **База знаний:**
        - Загружено статей: {kb['articles_count']}
        - Рекомендаций по композитам: {len(kb['composite_recommendations'])}
        - ЭМГ-показателей: {len(kb['emg_guidelines'])}
        - Клинических критериев: {len(kb['clinical_criteria'])}
        - Технических характеристик: {len(kb['technical_specs'])}
        """)
        
        # Просмотр извлеченных знаний
        with st.expander("📋 Просмотр извлеченных знаний", expanded=False):
            if kb['composite_recommendations']:
                st.subheader("Рекомендации по композитам")
                for rec in kb['composite_recommendations'][:10]:
                    st.write(f"- **{rec['composite']}** (из: {rec['source']})")
                    st.caption(rec['context'][:150])
            
            if kb['emg_guidelines']:
                st.subheader("ЭМГ-показатели")
                for guide in kb['emg_guidelines'][:10]:
                    st.write(f"- Значение: {guide['value']} ± {guide['std']} мкВ")
                    st.caption(guide['context'][:150])
        
        st.markdown("---")
        
        # Извлечение клинических пар (ЭМГ -> композит)
        st.subheader("🔬 Извлечение клинических данных")
        
        if 'clinical_pairs' not in st.session_state:
            st.session_state.clinical_pairs = []
        
        if st.button("🔍 Извлечь пары 'ЭМГ-показатели -> композит' из статей", use_container_width=True):
            with st.spinner("Извлечение клинических данных из статей..."):
                try:
                    try:
                        from model_trainer import ClinicalDataExtractor
                    except ImportError:
                        # Если модуль не найден, создаем заглушку
                        st.warning("⚠️ Модуль model_trainer не найден. Установите зависимости: pip install scikit-learn")
                        st.stop()
                    
                    extractor = ClinicalDataExtractor()
                    total_pairs = 0
                    
                    # Обрабатываем все статьи
                    for article_data in st.session_state.articles:
                        if 'text' in article_data and article_data['text']:
                            pairs = extractor.extract_patient_data(
                                article_data['text'],
                                article_title=article_data.get('title', ''),
                                article_url=article_data.get('url', ''),
                                article_year=article_data.get('year')
                            )
                            total_pairs += len(pairs)
                    
                    st.session_state.clinical_pairs = extractor.extracted_pairs
                    
                    st.success(f"✅ Извлечено {total_pairs} пар 'ЭМГ-показатели -> композит'")
                    
                    if total_pairs > 0:
                        # Показываем примеры
                        st.markdown("**Примеры извлеченных пар:**")
                        for i, pair in enumerate(st.session_state.clinical_pairs[:5], 1):
                            with st.expander(f"Пара {i}: {pair.composite_name or 'Контрольные значения'}"):
                                st.write(f"**Источник:** {pair.source_article}")
                                if pair.masseter_right_chewing:
                                    st.write(f"Жевательная правая (жевание): {pair.masseter_right_chewing} мкВ")
                                if pair.composite_name:
                                    st.write(f"**Композит:** {pair.composite_name}")
                                else:
                                    st.write("**Тип:** Контрольные ЭМГ-значения")
                except Exception as e:
                    st.error(f"❌ Ошибка извлечения: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # Обучение модели
        st.markdown("---")
        st.subheader("🤖 Обучение модели")
        
        if len(st.session_state.clinical_pairs) == 0:
            st.warning("⚠️ Сначала извлеките клинические данные из статей")
        else:
            pairs_with_composites = [p for p in st.session_state.clinical_pairs if p.composite_name]
            st.info(f"""
            📊 **Доступно для обучения:**
            - Всего пар: {len(st.session_state.clinical_pairs)}
            - Пар с композитами: {len(pairs_with_composites)}
            - Контрольных значений: {len(st.session_state.clinical_pairs) - len(pairs_with_composites)}
            """)
            
            model_type = st.radio(
                "Тип модели",
                ["Random Forest", "Gradient Boosting"],
                help="Random Forest - быстрее, Gradient Boosting - точнее"
            )
            
            if st.button("🚀 Обучить модель на клинических данных", use_container_width=True):
                with st.spinner("Обучение модели..."):
                    try:
                        from model_trainer import CompositeModelTrainer
                        
                        trainer = CompositeModelTrainer()
                        model_type_lower = model_type.lower().replace(" ", "_")
                        
                        results = trainer.train(
                            st.session_state.clinical_pairs,
                            model_type=model_type_lower
                        )
                        
                        # Сохраняем модель в session state
                        st.session_state.ml_model = trainer
                        st.session_state.model_trained = True
                        
                        st.success("✅ Модель успешно обучена!")
                        
                        st.markdown("---")
                        st.subheader("📊 Результаты обучения")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Примеров для обучения", results['train_size'])
                        col2.metric("Примеров для теста", results['test_size'])
                        col3.metric("Уникальных композитов", results['unique_composites'])
                        if results['accuracy']:
                            col4.metric("Точность", f"{results['accuracy']:.1%}")
                        
                        st.markdown("---")
                        st.info("""
                        ✅ **Модель обучена!** Теперь система может использовать машинное обучение 
                        для предсказания композита на основе ЭМГ-данных из научных статей.
                        """)
                        
                        # Сохранение модели
                        if st.button("💾 Сохранить модель", use_container_width=True):
                            try:
                                model_path = "trained_model.pkl"
                                trainer.save_model(model_path)
                                st.success(f"✅ Модель сохранена в {model_path}")
                            except Exception as e:
                                st.error(f"❌ Ошибка сохранения: {e}")
                                
                    except ValueError as e:
                        st.warning(f"⚠️ {e}")
                        st.info("💡 Добавьте больше статей с данными 'ЭМГ-показатели -> композит' для обучения модели")
                    except Exception as e:
                        st.error(f"❌ Ошибка обучения: {e}")
                        import traceback
                        st.code(traceback.format_exc())
        
        # Сохранение базы знаний
        st.markdown("---")
        st.subheader("💾 Сохранение данных")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Сохранить базу знаний", use_container_width=True):
                try:
                    st.session_state.knowledge_extractor.save_knowledge_base("knowledge_base.json")
                    st.success("✅ База знаний сохранена в файл knowledge_base.json")
                except Exception as e:
                    st.error(f"❌ Ошибка сохранения: {e}")
        
        with col2:
            if st.button("💾 Сохранить клинические пары", use_container_width=True):
                try:
                    pairs_data = [pair.to_dict() for pair in st.session_state.clinical_pairs]
                    with open("clinical_pairs.json", 'w', encoding='utf-8') as f:
                        json.dump(pairs_data, f, ensure_ascii=False, indent=2)
                    st.success("✅ Клинические пары сохранены в файл clinical_pairs.json")
                except Exception as e:
                    st.error(f"❌ Ошибка сохранения: {e}")

# ==================== СТАТИСТИКА ====================
elif page == "📈 Статистика":
    st.header("Статистика и аналитика")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Загруженные статьи")
        if len(st.session_state.articles) > 0:
            articles_df = pd.DataFrame(st.session_state.articles)
            if 'year' in articles_df.columns:
                year_counts = articles_df['year'].value_counts().sort_index()
                st.bar_chart(year_counts)
            st.metric("Всего статей", len(st.session_state.articles))
        else:
            st.info("Загрузите статьи для отображения статистики")
    
    with col2:
        st.subheader("Извлеченные знания")
        if st.session_state.knowledge_base:
            kb = st.session_state.knowledge_base
            st.metric("Рекомендаций", len(kb.get('composite_recommendations', [])))
            st.metric("ЭМГ-показателей", len(kb.get('emg_guidelines', [])))
            st.metric("Критериев", len(kb.get('clinical_criteria', [])))
        else:
            st.info("Обновите базу знаний в разделе 'Загрузка данных'")
    
    # Экспорт базы знаний
    st.markdown("---")
    if st.session_state.knowledge_base:
        kb_json = json.dumps(st.session_state.knowledge_base, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 Скачать базу знаний (JSON)",
            data=kb_json,
            file_name="knowledge_base.json",
            mime="application/json"
        )

# Футер
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>ComposeAI | Исследовательский проект | 2025</small>
</div>
""", unsafe_allow_html=True)

