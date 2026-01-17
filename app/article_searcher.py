"""
Модуль для автоматического поиска и загрузки научных статей из интернета
"""

import requests
import time
from typing import List, Dict, Optional
from urllib.parse import quote, urlparse
import json
import re

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False


class ArticleSearcher:
    """Класс для автоматического поиска статей в интернете"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_pubmed(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Поиск статей в PubMed
        
        Args:
            query: Поисковый запрос (например, "dental composite EMG")
            max_results: Максимальное количество результатов
            
        Returns:
            Список словарей с информацией о статьях
        """
        articles = []
        
        try:
            # PubMed E-utilities API
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
            
            # Шаг 1: Поиск статей
            search_url = f"{base_url}esearch.fcgi"
            params = {
                'db': 'pubmed',
                'term': query,
                'retmax': max_results,
                'retmode': 'json'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code != 200:
                return articles
            
            data = response.json()
            pmids = data.get('esearchresult', {}).get('idlist', [])
            
            if not pmids:
                return articles
            
            # Шаг 2: Получение детальной информации о статьях
            fetch_url = f"{base_url}efetch.fcgi"
            params = {
                'db': 'pubmed',
                'id': ','.join(pmids),
                'retmode': 'xml'
            }
            
            response = self.session.get(fetch_url, params=params, timeout=15)
            if response.status_code != 200:
                return articles
            
            # Парсинг XML (упрощенный)
            xml_content = response.text
            
            # Извлечение информации из XML
            for pmid in pmids:
                article_info = self._parse_pubmed_xml(xml_content, pmid)
                if article_info:
                    articles.append(article_info)
            
            # Задержка между запросами (вежливость к API)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Ошибка при поиске в PubMed: {e}")
        
        return articles
    
    def _parse_pubmed_xml(self, xml_content: str, pmid: str) -> Optional[Dict]:
        """Парсит XML ответ от PubMed для одной статьи"""
        try:
            # Упрощенный парсинг (можно улучшить с помощью xml.etree.ElementTree)
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
            author_matches = re.findall(r'<Author[^>]*>.*?<LastName>(.*?)</LastName>.*?<ForeName>(.*?)</ForeName>', xml_content, re.DOTALL)
            for last_name, first_name in author_matches:
                authors.append(f"{first_name.strip()} {last_name.strip()}")
            if authors:
                article_info['authors'] = ', '.join(authors[:5])  # Первые 5 авторов
            
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
                article_info['abstract'] = re.sub(r'<[^>]+>', '', abstract_match.group(1)).strip()
                article_info['text'] = article_info['abstract']  # Для совместимости
            
            return article_info if article_info.get('title') else None
            
        except Exception as e:
            print(f"Ошибка при парсинге PubMed XML: {e}")
            return None
    
    def search_pubmed_central(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Поиск статей в PubMed Central (открытый доступ)
        
        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов
            
        Returns:
            Список словарей с информацией о статьях
        """
        articles = []
        
        try:
            # PubMed Central API
            base_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
            
            # Сначала ищем через PubMed, затем проверяем доступность в PMC
            pubmed_articles = self.search_pubmed(query, max_results * 2)
            
            for article in pubmed_articles:
                pmid = article.get('pmid')
                if not pmid:
                    continue
                
                # Проверка доступности в PMC
                pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmid}/"
                
                # Попытка получить полный текст (упрощенная версия)
                try:
                    response = self.session.get(pmc_url, timeout=10)
                    if response.status_code == 200 and 'pmc' in response.url.lower():
                        article['pmc_url'] = pmc_url
                        article['source'] = 'PubMed Central'
                        
                        # Попытка извлечь текст статьи
                        if BS4_AVAILABLE:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            # Поиск основного текста статьи
                            main_content = soup.find('div', class_='tsec sec') or soup.find('div', id='maincontent')
                            if main_content:
                                # Извлечение текста из параграфов
                                paragraphs = main_content.find_all('p')
                                full_text = '\n\n'.join([p.get_text() for p in paragraphs])
                                if full_text:
                                    article['text'] = full_text
                                    article['has_full_text'] = True
                except:
                    pass
                
                if article.get('has_full_text'):
                    articles.append(article)
                    if len(articles) >= max_results:
                        break
                
                time.sleep(0.3)  # Задержка между запросами
            
        except Exception as e:
            print(f"Ошибка при поиске в PubMed Central: {e}")
        
        return articles
    
    def search_arxiv(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Поиск препринтов на arXiv
        
        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов
            
        Returns:
            Список словарей с информацией о статьях
        """
        articles = []
        
        if not FEEDPARSER_AVAILABLE:
            print("⚠️ feedparser не установлен. Установите: pip install feedparser")
            return articles
        
        try:
            # arXiv API
            base_url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            if response.status_code != 200:
                return articles
            
            feed = feedparser.parse(response.text)
            
            for entry in feed.entries:
                article_info = {
                    'title': entry.get('title', '').replace('\n', ' ').strip(),
                    'authors': ', '.join([author.get('name', '') for author in entry.get('authors', [])]),
                    'year': entry.get('published', '')[:4] if entry.get('published') else None,
                    'url': entry.get('link', ''),
                    'abstract': entry.get('summary', '').strip(),
                    'text': entry.get('summary', '').strip(),  # Для совместимости
                    'source': 'arXiv',
                    'doi': entry.get('arxiv_doi', '')
                }
                
                if article_info['title']:
                    articles.append(article_info)
            
        except Exception as e:
            print(f"Ошибка при поиске в arXiv: {e}")
        
        return articles
    
    def search_google_scholar_simple(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Упрощенный поиск в Google Scholar (без официального API)
        ВНИМАНИЕ: Может быть заблокирован при частых запросах
        
        Args:
            query: Поисковый запрос
            max_results: Максимальное количество результатов
            
        Returns:
            Список словарей с информацией о статьях
        """
        articles = []
        
        if not BS4_AVAILABLE:
            print("⚠️ BeautifulSoup не установлен. Установите: pip install beautifulsoup4")
            return articles
        
        try:
            # Google Scholar поиск
            search_url = "https://scholar.google.com/scholar"
            params = {
                'q': query,
                'hl': 'en'
            }
            
            response = self.session.get(search_url, params=params, timeout=10)
            if response.status_code != 200:
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Поиск результатов
            results = soup.find_all('div', class_='gs_ri')[:max_results]
            
            for result in results:
                # Заголовок
                title_elem = result.find('h3', class_='gs_rt')
                if not title_elem:
                    continue
                
                title = title_elem.get_text().strip()
                
                # Ссылка
                link_elem = title_elem.find('a')
                url = link_elem.get('href', '') if link_elem else ''
                
                # Авторы и информация
                authors_elem = result.find('div', class_='gs_a')
                authors_info = authors_elem.get_text().strip() if authors_elem else ''
                
                # Абстракт
                abstract_elem = result.find('div', class_='gs_rs')
                abstract = abstract_elem.get_text().strip() if abstract_elem else ''
                
                article_info = {
                    'title': title,
                    'authors': authors_info.split(' - ')[0] if ' - ' in authors_info else authors_info,
                    'url': url if url.startswith('http') else f"https://scholar.google.com{url}",
                    'abstract': abstract,
                    'text': abstract,  # Для совместимости
                    'source': 'Google Scholar'
                }
                
                # Извлечение года из информации об авторах
                year_match = re.search(r'\b(19|20)\d{2}\b', authors_info)
                if year_match:
                    article_info['year'] = int(year_match.group())
                
                if article_info['title']:
                    articles.append(article_info)
            
            # Задержка для вежливости
            time.sleep(2)
            
        except Exception as e:
            print(f"Ошибка при поиске в Google Scholar: {e}")
            print("⚠️ Google Scholar может блокировать автоматические запросы")
        
        return articles
    
    def search_all_sources(self, query: str, max_results_per_source: int = 5) -> List[Dict]:
        """
        Поиск во всех доступных источниках
        
        Args:
            query: Поисковый запрос
            max_results_per_source: Максимальное количество результатов на источник
            
        Returns:
            Объединенный список статей из всех источников
        """
        all_articles = []
        
        print(f"🔍 Поиск статей по запросу: '{query}'...")
        
        # PubMed
        print("📚 Поиск в PubMed...")
        pubmed_articles = self.search_pubmed(query, max_results_per_source)
        all_articles.extend(pubmed_articles)
        print(f"   Найдено: {len(pubmed_articles)} статей")
        
        # PubMed Central (открытый доступ)
        print("📖 Поиск в PubMed Central...")
        pmc_articles = self.search_pubmed_central(query, max_results_per_source)
        all_articles.extend(pmc_articles)
        print(f"   Найдено: {len(pmc_articles)} статей")
        
        # arXiv (препринты)
        print("📄 Поиск в arXiv...")
        arxiv_articles = self.search_arxiv(query, max_results_per_source)
        all_articles.extend(arxiv_articles)
        print(f"   Найдено: {len(arxiv_articles)} статей")
        
        # Google Scholar (опционально, может быть заблокирован)
        # print("🔬 Поиск в Google Scholar...")
        # scholar_articles = self.search_google_scholar_simple(query, max_results_per_source)
        # all_articles.extend(scholar_articles)
        # print(f"   Найдено: {len(scholar_articles)} статей")
        
        # Удаление дубликатов по заголовку
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        print(f"\n✅ Всего найдено уникальных статей: {len(unique_articles)}")
        
        return unique_articles
    
    def get_full_text_from_url(self, url: str) -> Optional[str]:
        """
        Попытка получить полный текст статьи по URL
        
        Args:
            url: URL статьи
            
        Returns:
            Текст статьи или None
        """
        if not BS4_AVAILABLE:
            return None
        
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Удаление скриптов и стилей
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Поиск основного контента
            main_content = (
                soup.find('article') or
                soup.find('div', class_='article-content') or
                soup.find('div', id='content') or
                soup.find('main') or
                soup.find('body')
            )
            
            if main_content:
                # Извлечение текста из параграфов
                paragraphs = main_content.find_all('p')
                text = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                return text if text else None
            
        except Exception as e:
            print(f"Ошибка при получении текста с {url}: {e}")
        
        return None


def get_recommended_queries() -> List[str]:
    """Возвращает список рекомендуемых поисковых запросов"""
    return [
        "dental composite EMG",
        "composite material chewing teeth",
        "EMG masticatory muscles composite",
        "dental restoration composite selection",
        "polymerization shrinkage composite",
        "composite filler content wear resistance",
        "pathological tooth wear composite",
        "occlusion anomaly composite restoration",
        "bulk fill composite properties",
        "nanofilled composite mechanical properties"
    ]

