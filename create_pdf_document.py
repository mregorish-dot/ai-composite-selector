#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание PDF документа из научной версии статьи
"""

import markdown
from pathlib import Path
import re

def remove_black_highlights(text):
    """Удаляет черные выделения из текста"""
    pattern = r'<span style="color: black; background-color: black;">(.*?)</span>'
    text = re.sub(pattern, r'\1', text, flags=re.DOTALL)
    return text

def create_full_document():
    """Создает полный документ для PDF"""
    
    # Читаем научную версию статьи
    with open('Полная_статья_научная_версия.md', 'r', encoding='utf-8') as f:
        full_doc = f.read()
    
    return full_doc

def convert_to_html(md_text):
    """Конвертирует Markdown в HTML"""
    html = markdown.markdown(
        md_text,
        extensions=['extra', 'codehilite', 'tables'],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight'
            }
        }
    )
    
    # Добавляем стили
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Применение ИИ при выборе композита</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-size: 12pt;
        }}
        h1 {{
            font-size: 18pt;
            text-align: center;
            margin-bottom: 20px;
        }}
        h2 {{
            font-size: 14pt;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        h3 {{
            font-size: 12pt;
            margin-top: 15px;
            margin-bottom: 8px;
        }}
        p {{
            text-align: justify;
            margin-bottom: 10px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 10pt;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 10pt;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        @media print {{
            body {{
                max-width: 100%;
                padding: 0;
            }}
            h1 {{
                page-break-after: avoid;
            }}
            h2, h3 {{
                page-break-after: avoid;
            }}
        }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
    
    return full_html

if __name__ == "__main__":
    print("📄 Создание полного документа...")
    
    # Создаем полный документ
    full_doc = create_full_document()
    
    # Сохраняем Markdown версию
    with open('Полный_документ_статья.md', 'w', encoding='utf-8') as f:
        f.write(full_doc)
    print("✅ Markdown версия сохранена: Полный_документ_статья.md")
    
    # Конвертируем в HTML
    html = convert_to_html(full_doc)
    
    # Сохраняем HTML версию
    with open('Полный_документ_статья.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ HTML версия сохранена: Полный_документ_статья.html")
    
    print("\n💡 Для создания PDF:")
    print("   1. Откройте файл Полный_документ_статья.html в браузере")
    print("   2. Нажмите Cmd+P (или Ctrl+P)")
    print("   3. Выберите 'Сохранить как PDF'")
    print("   4. Сохраните файл")
