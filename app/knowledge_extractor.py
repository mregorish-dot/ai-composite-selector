"""
Модуль для извлечения знаний из научных статей и учебных материалов
"""

import re
import json
import io
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import pandas as pd

# Импорт для работы с PDF
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    try:
        import pdfplumber
        PDF_SUPPORT = True
    except ImportError:
        PDF_SUPPORT = False


@dataclass
class Article:
    """Структура статьи"""
    title: str
    authors: str = ""
    year: Optional[int] = None
    journal: str = ""
    url: str = ""
    text: str = ""
    doi: str = ""
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class ExtractedKnowledge:
    """Извлеченные знания из статьи"""
    article_title: str
    composite_recommendations: List[Dict] = None
    emg_guidelines: List[Dict] = None
    clinical_criteria: List[Dict] = None
    technical_specs: List[Dict] = None
    
    def __post_init__(self):
        if self.composite_recommendations is None:
            self.composite_recommendations = []
        if self.emg_guidelines is None:
            self.emg_guidelines = []
        if self.clinical_criteria is None:
            self.clinical_criteria = []
        if self.technical_specs is None:
            self.technical_specs = []


class KnowledgeExtractor:
    """Класс для извлечения знаний из научных статей"""
    
    def __init__(self):
        self.articles: List[Article] = []
        self.extracted_knowledge: List[ExtractedKnowledge] = []
        self.pdf_support = PDF_SUPPORT
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """
        Извлечение текста из PDF файла
        
        Args:
            pdf_file: Файловый объект или bytes PDF
            
        Returns:
            Извлеченный текст
        """
        if not self.pdf_support:
            raise ImportError("Для работы с PDF установите PyPDF2 или pdfplumber: pip install PyPDF2 pdfplumber")
        
        text = ""
        
        # Пробуем PyPDF2
        try:
            import PyPDF2
            if isinstance(pdf_file, bytes):
                pdf_file = io.BytesIO(pdf_file)
            
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num, page in enumerate(pdf_reader.pages):
                text += page.extract_text() + "\n"
            
            return text
        except:
            pass
        
        # Пробуем pdfplumber
        try:
            import pdfplumber
            if isinstance(pdf_file, bytes):
                pdf_file = io.BytesIO(pdf_file)
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text
        except Exception as e:
            raise ValueError(f"Ошибка при извлечении текста из PDF: {e}")
    
    def process_pdf_article(
        self,
        pdf_file,
        title: str = "",
        authors: str = "",
        year: Optional[int] = None,
        journal: str = "",
        url: str = "",
        doi: str = ""
    ) -> ExtractedKnowledge:
        """
        Обработка PDF файла и извлечение знаний
        
        Args:
            pdf_file: PDF файл (файловый объект или bytes)
            title: Название статьи (если не указано, попытается извлечь из PDF)
            authors: Авторы
            year: Год публикации
            journal: Журнал
            url: Ссылка на статью
            doi: DOI
            
        Returns:
            Извлеченные знания
        """
        # Извлечение текста из PDF
        text = self.extract_text_from_pdf(pdf_file)
        
        # Попытка извлечь метаданные из текста, если не указаны
        if not title:
            # Ищем название в начале текста (обычно первые несколько строк)
            lines = text.split('\n')[:10]
            for line in lines:
                if len(line) > 20 and len(line) < 200:
                    title = line.strip()
                    break
        
        if not title:
            title = "Статья из PDF"
        
        # Добавление статьи
        article = self.add_article(
            title=title,
            text=text,
            authors=authors,
            year=year,
            journal=journal,
            url=url,
            doi=doi
        )
        
        # Извлечение знаний
        knowledge = self.process_article(article)
        return knowledge
    
    def add_article(
        self,
        title: str,
        text: str = "",
        url: str = "",
        authors: str = "",
        year: Optional[int] = None,
        journal: str = "",
        doi: str = "",
        keywords: List[str] = None
    ):
        """Добавление статьи"""
        article = Article(
            title=title,
            text=text,
            url=url,
            authors=authors,
            year=year,
            journal=journal,
            doi=doi,
            keywords=keywords or []
        )
        self.articles.append(article)
        return article
    
    def extract_clinical_pairs(self, text: str, article_title: str = "", article_url: str = "", article_year: Optional[int] = None) -> List[Dict]:
        """
        Извлечение пар "ЭМГ-данные -> композит" из статьи
        
        Использует улучшенные паттерны для поиска клинических данных
        """
        from model_trainer import ClinicalDataExtractor
        
        extractor = ClinicalDataExtractor()
        pairs = extractor.extract_patient_data(text, article_title, article_url, article_year)
        
        # Конвертируем в словари для сохранения
        return [pair.to_dict() for pair in pairs]
    
    def extract_knowledge_from_text(self, text: str, article_title: str = "") -> ExtractedKnowledge:
        """
        Извлечение знаний из текста статьи
        
        Ищет:
        - Рекомендации по композитам
        - ЭМГ-показатели и нормальные значения
        - Клинические критерии выбора
        - Технические характеристики
        """
        knowledge = ExtractedKnowledge(article_title=article_title)
        
        text_lower = text.lower()
        
        # Извлечение рекомендаций по композитам
        composite_patterns = [
            r'(?:рекомендуется|рекомендуют|предпочтительно|подходит|оптимален).*?(?:композит|материал|composite|material)[\s\w,]*?([A-Z0-9]+(?:\s+[A-Z0-9]+)*)',
            r'([A-Z0-9]+(?:\s+[A-Z0-9]+)*).*?(?:для|при).*?(?:жевательных|окклюзионных|occlusal|molar)',
            r'(?:high viscosity|высоковязкий).*?([A-Z0-9]+)',
            r'([A-Z0-9]+).*?(?:микротвердость|microhardness).*?(\d+\.?\d*)\s*(?:KHN|кнн)',
        ]
        
        for pattern in composite_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                composite_name = match.group(1).strip()
                if len(composite_name) <= 10:  # Фильтр разумных названий
                    knowledge.composite_recommendations.append({
                        'composite': composite_name,
                        'context': match.group(0)[:200],
                        'source': article_title
                    })
        
        # Извлечение ЭМГ-показателей
        emg_patterns = [
            r'(?:жевательная|masseter).*?(?:мкв|μv|мкв|microvolt).*?(\d+\.?\d*)\s*[±±]\s*(\d+\.?\d*)',
            r'(?:височная|temporalis).*?(?:мкв|μv|мкв|microvolt).*?(\d+\.?\d*)\s*[±±]\s*(\d+\.?\d*)',
            r'эмг.*?(?:норма|контроль|control).*?(\d+\.?\d*)\s*[±±]\s*(\d+\.?\d*)',
            r'(?:при акте жевания|chewing).*?(\d+\.?\d*)\s*[±±]\s*(\d+\.?\d*)\s*(?:мкв|μv)',
        ]
        
        for pattern in emg_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = float(match.group(1))
                std = float(match.group(2)) if len(match.groups()) > 1 else 0
                knowledge.emg_guidelines.append({
                    'value': value,
                    'std': std,
                    'context': match.group(0)[:200],
                    'source': article_title
                })
        
        # Извлечение клинических критериев
        criteria_patterns = [
            r'(?:для|при).*?(?:жевательных|окклюзионных).*?(?:микротвердость|microhardness).*?(\d+\.?\d*)\s*(?:KHN|кнн|минимум|minimum)',
            r'(?:усадка|shrinkage).*?(\d+\.?\d*)\s*%',
            r'(?:наполнитель|filler).*?(\d+\.?\d*)\s*%',
            r'(?:износостойкость|wear resistance).*?(?:высокая|high|средняя|medium|низкая|low)',
        ]
        
        for pattern in criteria_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                knowledge.clinical_criteria.append({
                    'criterion': match.group(0)[:100],
                    'value': match.group(1) if len(match.groups()) > 0 else None,
                    'source': article_title
                })
        
        # Извлечение технических характеристик
        tech_patterns = [
            r'([A-Z0-9]+).*?(?:микротвердость|microhardness).*?(\d+\.?\d*)\s*(?:KHN|кнн)',
            r'([A-Z0-9]+).*?(?:усадка|shrinkage).*?(\d+\.?\d*)\s*%',
            r'([A-Z0-9]+).*?(?:наполнитель|filler).*?(\d+\.?\d*)\s*%',
        ]
        
        for pattern in tech_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                composite = match.group(1).strip()
                value = float(match.group(2))
                knowledge.technical_specs.append({
                    'composite': composite,
                    'property': 'unknown',
                    'value': value,
                    'source': article_title
                })
        
        return knowledge
    
    def process_article(self, article: Article) -> ExtractedKnowledge:
        """Обработка статьи и извлечение знаний"""
        knowledge = self.extract_knowledge_from_text(article.text, article.title)
        self.extracted_knowledge.append(knowledge)
        return knowledge
    
    def get_knowledge_base(self) -> Dict:
        """Получение базы знаний в структурированном виде"""
        return {
            'articles_count': len(self.articles),
            'knowledge_count': len(self.extracted_knowledge),
            'composite_recommendations': [
                rec for k in self.extracted_knowledge 
                for rec in k.composite_recommendations
            ],
            'emg_guidelines': [
                guide for k in self.extracted_knowledge 
                for guide in k.emg_guidelines
            ],
            'clinical_criteria': [
                crit for k in self.extracted_knowledge 
                for crit in k.clinical_criteria
            ],
            'technical_specs': [
                spec for k in self.extracted_knowledge 
                for spec in k.technical_specs
            ]
        }
    
    def save_knowledge_base(self, filepath: str):
        """Сохранение базы знаний в JSON"""
        kb = self.get_knowledge_base()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(kb, f, ensure_ascii=False, indent=2)
    
    def load_knowledge_base(self, filepath: str):
        """Загрузка базы знаний из JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            kb = json.load(f)
        return kb


# Пример использования
if __name__ == "__main__":
    extractor = KnowledgeExtractor()
    
    # Пример статьи
    article_text = """
    Исследование показало, что для реставрации жевательных зубов рекомендуется 
    использовать высоковязкие композиты с микротвердостью не менее 50 KHN.
    Композит XF показал микротвердость 74.34 KHN и усадку 2.5%.
    При акте жевания нормальные значения ЭМГ для жевательной мышцы составляют 
    350.5 ± 6.25 мкВ, для височной мышцы - 243.25 ± 4.5 мкВ.
    """
    
    article = extractor.add_article(
        title="Исследование композитов для жевательных зубов",
        text=article_text,
        year=2024
    )
    
    knowledge = extractor.process_article(article)
    print("Извлеченные знания:")
    print(f"Рекомендации по композитам: {knowledge.composite_recommendations}")
    print(f"ЭМГ-показатели: {knowledge.emg_guidelines}")
    print(f"Клинические критерии: {knowledge.clinical_criteria}")

