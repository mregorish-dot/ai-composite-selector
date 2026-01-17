"""
Автоматический поиск статей в интернете, загрузка в модель и обучение
Выполняется при запуске приложения для предварительного обучения модели
"""

import urllib.request
import urllib.parse
import json
import re
import time
import os
from pathlib import Path
from typing import List, Dict, Optional

# Путь к сохраненной модели
MODEL_PATH = os.path.join(Path(__file__).parent.absolute(), "trained_model.pkl")
ARTICLES_CACHE_PATH = os.path.join(Path(__file__).parent.absolute(), "auto_loaded_articles.json")


def search_pubmed_simple(query: str, max_results: int = 5) -> List[Dict]:
    """
    Простой поиск статей в PubMed через E-utilities API
    Использует только встроенные библиотеки Python (urllib)
    """
    articles = []
    
    try:
        # Шаг 1: Поиск статей
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        search_url = f"{base_url}esearch.fcgi"
        
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        url_with_params = f"{search_url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url_with_params, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            pmids = data.get('esearchresult', {}).get('idlist', [])
        
        if not pmids:
            return articles
        
        # Шаг 2: Получение детальной информации
        fetch_url = f"{base_url}efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml'
        }
        
        url_with_params = f"{fetch_url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url_with_params, timeout=15) as response:
            xml_content = response.read().decode('utf-8')
        
        # Простой парсинг XML (без внешних библиотек)
        for pmid in pmids:
            article_info = parse_pubmed_xml_simple(xml_content, pmid)
            if article_info:
                articles.append(article_info)
        
        time.sleep(0.5)  # Вежливость к API
        
    except Exception as e:
        print(f"Ошибка при поиске в PubMed: {e}")
    
    return articles


def parse_pubmed_xml_simple(xml_content: str, pmid: str) -> Optional[Dict]:
    """Простой парсинг XML ответа от PubMed"""
    try:
        article_info = {
            'pmid': pmid,
            'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            'source': 'PubMed'
        }
        
        # Извлечение заголовка
        title_match = re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml_content, re.DOTALL)
        if title_match:
            article_info['title'] = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        
        # Извлечение авторов
        authors = []
        author_matches = re.findall(
            r'<Author[^>]*>.*?<LastName>(.*?)</LastName>.*?<ForeName>(.*?)</ForeName>',
            xml_content, re.DOTALL
        )
        for last_name, first_name in author_matches:
            authors.append(f"{first_name.strip()} {last_name.strip()}")
        if authors:
            article_info['authors'] = ', '.join(authors[:5])
        
        # Извлечение года
        year_match = re.search(r'<PubDate>.*?<Year>(\d{4})</Year>', xml_content, re.DOTALL)
        if year_match:
            article_info['year'] = int(year_match.group(1))
        
        # Извлечение журнала
        journal_match = re.search(r'<Title>(.*?)</Title>', xml_content)
        if journal_match:
            article_info['journal'] = journal_match.group(1).strip()
        
        # Извлечение абстракта
        abstract_match = re.search(r'<AbstractText[^>]*>(.*?)</AbstractText>', xml_content, re.DOTALL)
        if abstract_match:
            abstract = re.sub(r'<[^>]+>', '', abstract_match.group(1)).strip()
            article_info['abstract'] = abstract
            article_info['text'] = abstract  # Для совместимости
        
        return article_info if article_info.get('title') else None
        
    except Exception as e:
        print(f"Ошибка при парсинге PubMed XML: {e}")
        return None


def search_arxiv_simple(query: str, max_results: int = 5) -> List[Dict]:
    """
    Простой поиск препринтов на arXiv через API
    Использует только встроенные библиотеки Python
    """
    articles = []
    
    try:
        base_url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        url_with_params = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url_with_params, timeout=10) as response:
            xml_content = response.read().decode('utf-8')
        
        # Простой парсинг Atom feed
        entries = re.findall(r'<entry>(.*?)</entry>', xml_content, re.DOTALL)
        
        for entry in entries:
            title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else ''
            
            link_match = re.search(r'<id>(.*?)</id>', entry)
            url = link_match.group(1).strip() if link_match else ''
            
            summary_match = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            abstract = re.sub(r'<[^>]+>', '', summary_match.group(1)).strip() if summary_match else ''
            
            authors = []
            author_matches = re.findall(r'<name>(.*?)</name>', entry)
            authors = ', '.join(author_matches[:5])
            
            published_match = re.search(r'<published>(\d{4})', entry)
            year = int(published_match.group(1)) if published_match else None
            
            if title:
                articles.append({
                    'title': title.replace('\n', ' ').strip(),
                    'authors': authors,
                    'year': year,
                    'url': url,
                    'abstract': abstract,
                    'text': abstract,
                    'source': 'arXiv'
                })
        
    except Exception as e:
        print(f"Ошибка при поиске в arXiv: {e}")
    
    return articles


def auto_load_and_train():
    """
    Автоматический поиск статей, загрузка в модель и обучение
    """
    print("🔍 Начинаю автоматический поиск статей...")
    
    # Расширенные поисковые запросы для максимального покрытия
    queries = [
        "dental composite EMG masticatory muscles",
        "composite material chewing teeth restoration",
        "polymerization shrinkage composite occlusal",
        "composite filler content wear resistance",
        "pathological tooth wear composite restoration",
        "EMG masseter temporalis composite selection",
        "resin composite occlusal restoration EMG",
        "bulk fill composite posterior teeth",
        "composite restoration masticatory function",
        "EMG activity composite material selection",
        "dental composite mechanical properties EMG",
        "occlusal composite restoration EMG analysis"
    ]
    
    all_articles = []
    
    # Поиск в PubMed (больше запросов, больше результатов)
    print("📚 Расширенный поиск в PubMed...")
    for query in queries[:8]:  # Первые 8 запросов в PubMed
        articles = search_pubmed_simple(query, max_results=5)  # Увеличено с 3 до 5
        all_articles.extend(articles)
        print(f"   Найдено {len(articles)} статей по запросу: {query}")
        time.sleep(0.8)  # Небольшая задержка между запросами
    
    # Поиск в arXiv
    print("📄 Поиск в arXiv...")
    for query in queries[8:]:  # Остальные в arXiv
        articles = search_arxiv_simple(query, max_results=3)  # Увеличено с 2 до 3
        all_articles.extend(articles)
        print(f"   Найдено {len(articles)} статей по запросу: {query}")
        time.sleep(0.8)
    
    # Удаление дубликатов
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        title = article.get('title', '').lower().strip()
        if title and title not in seen_titles:
            seen_titles.add(title)
            unique_articles.append(article)
    
    print(f"\n✅ Всего найдено уникальных статей: {len(unique_articles)}")
    
    # Сохранение статей в кэш
    try:
        with open(ARTICLES_CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, ensure_ascii=False, indent=2)
        print(f"💾 Статьи сохранены в {ARTICLES_CACHE_PATH}")
    except Exception as e:
        print(f"⚠️ Ошибка сохранения статей: {e}")
    
    return unique_articles


def train_model_with_articles(articles: List[Dict]):
    """
    Обучение модели на найденных статьях и предзагруженных клинических данных
    """
    try:
        from knowledge_extractor import KnowledgeExtractor
        from model_trainer import ClinicalDataExtractor, CompositeModelTrainer, EMGCompositePair
        
        print("\n🤖 Начинаю обучение модели...")
        
        # Создаем экстрактор знаний
        knowledge_extractor = KnowledgeExtractor()
        
        # Загружаем найденные статьи в knowledge_extractor
        for article_data in articles:
            try:
                article = knowledge_extractor.add_article(
                    title=article_data.get('title', ''),
                    text=article_data.get('text', article_data.get('abstract', '')),
                    url=article_data.get('url', ''),
                    authors=article_data.get('authors', ''),
                    year=article_data.get('year'),
                    journal=article_data.get('journal', '')
                )
                knowledge_extractor.process_article(article)
            except Exception as e:
                print(f"⚠️ Ошибка при обработке статьи '{article_data.get('title', 'Unknown')}': {e}")
                continue
        
        print(f"📚 Обработано найденных статей: {len(knowledge_extractor.articles)}")
        
        # Загружаем предзагруженные клинические статьи
        try:
            from clinical_articles_data import get_clinical_articles, get_emg_composite_pairs
            clinical_articles = get_clinical_articles()
            clinical_pairs_dicts = get_emg_composite_pairs()
            
            print(f"📚 Загружено клинических статей: {len(clinical_articles)}")
            print(f"📊 Предзагружено пар ЭМГ-композит (словари): {len(clinical_pairs_dicts)}")
            
            # Загружаем клинические статьи в knowledge_extractor
            for article_data in clinical_articles:
                try:
                    article = knowledge_extractor.add_article(**article_data)
                    knowledge_extractor.process_article(article)
                except Exception as e:
                    continue
        except ImportError:
            clinical_pairs_dicts = []
            print("⚠️ Модуль clinical_articles_data не найден")
        
        # Извлекаем клинические данные из найденных статей
        extractor = ClinicalDataExtractor()
        
        # Конвертируем словари в объекты EMGCompositePair и добавляем
        base_pairs = []
        if clinical_pairs_dicts:
            for pair_dict in clinical_pairs_dicts:
                try:
                    pair = EMGCompositePair(**pair_dict)
                    base_pairs.append(pair)
                    extractor.extracted_pairs.append(pair)
                except Exception as e:
                    print(f"⚠️ Ошибка конвертации пары: {e}")
                    continue
            print(f"✅ Добавлено {len(extractor.extracted_pairs)} предзагруженных пар")
        
        # Генерация синтетических данных для повышения точности
        try:
            from generate_synthetic_training_data import get_all_synthetic_pairs
            print("\n🔬 Генерация синтетических обучающих данных...")
            synthetic_pairs = get_all_synthetic_pairs(base_pairs)
            extractor.extracted_pairs.extend(synthetic_pairs)
            print(f"✅ Добавлено {len(synthetic_pairs)} синтетических пар")
        except ImportError as e:
            print(f"⚠️ Модуль generate_synthetic_training_data не найден: {e}")
        except Exception as e:
            print(f"⚠️ Ошибка генерации синтетических данных: {e}")
            import traceback
            traceback.print_exc()
        
        # Извлекаем данные из найденных статей
        for article_data in articles:
            text = article_data.get('text', article_data.get('abstract', ''))
            if text:
                try:
                    extractor.extract_patient_data(
                        text,
                        article_title=article_data.get('title', ''),
                        article_url=article_data.get('url', ''),
                        article_year=article_data.get('year')
                    )
                except Exception as e:
                    continue
        
        # Извлекаем данные из клинических статей
        for article_data in clinical_articles:
            text = article_data.get('text', '')
            if text:
                try:
                    extractor.extract_patient_data(
                        text,
                        article_title=article_data.get('title', ''),
                        article_url=article_data.get('url', ''),
                        article_year=article_data.get('year')
                    )
                except Exception as e:
                    continue
        
        print(f"📊 Всего извлечено пар ЭМГ-композит: {len(extractor.extracted_pairs)}")
        
        # Обучение модели
        if len(extractor.extracted_pairs) > 0:
            trainer = CompositeModelTrainer()
            
            print("🎓 Обучаю модель с ансамблем для максимальной точности...")
            try:
                results = trainer.train(extractor.extracted_pairs, model_type='random_forest', use_ensemble=True)
                
                if trainer.model is not None:
                    # Сохранение модели
                    trainer.save_model(MODEL_PATH)
                    print(f"✅ Модель обучена и сохранена в {MODEL_PATH}")
                    if results.get('accuracy'):
                        print(f"📈 Точность модели: {results['accuracy']:.2%}")
                    print(f"📊 Примеров для обучения: {results.get('train_size', 0)}")
                    print(f"🔢 Уникальных композитов: {results.get('unique_composites', 0)}")
                    return True
                else:
                    print("⚠️ Не удалось обучить модель (недостаточно данных)")
                    return False
            except ValueError as e:
                print(f"⚠️ Ошибка обучения: {e}")
                return False
        else:
            print("⚠️ Не найдено пар ЭМГ-композит для обучения")
            return False
            
    except ImportError as e:
        print(f"⚠️ Ошибка импорта модулей: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Ошибка при обучении модели: {e}")
        import traceback
        traceback.print_exc()
        return False


def auto_train_on_startup():
    """
    Автоматическое обучение модели при запуске приложения
    Проверяет, есть ли уже обученная модель, и если нет - обучает
    """
    # Проверяем, есть ли уже обученная модель
    if os.path.exists(MODEL_PATH):
        print(f"✅ Обученная модель уже существует: {MODEL_PATH}")
        return True
    
    print("🔄 Обученной модели не найдено. Начинаю автоматическое обучение...")
    
    # Проверяем кэш статей
    articles = []
    if os.path.exists(ARTICLES_CACHE_PATH):
        try:
            with open(ARTICLES_CACHE_PATH, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            print(f"📚 Загружено {len(articles)} статей из кэша")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки кэша статей: {e}")
    
    # Если статей нет, ищем в интернете
    if not articles:
        articles = auto_load_and_train()
    
    # Обучаем модель
    if articles:
        success = train_model_with_articles(articles)
        return success
    else:
        print("⚠️ Не найдено статей для обучения")
        return False


if __name__ == "__main__":
    # Запуск автоматического обучения
    auto_train_on_startup()

