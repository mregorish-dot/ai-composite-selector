#!/usr/bin/env python3
"""
Скрипт для конвертации Markdown документа в HTML
(HTML можно открыть в браузере и сохранить как PDF)
"""

import sys
from pathlib import Path

def convert_markdown_to_html(md_file: str, html_file: str = None):
    """
    Конвертирует Markdown файл в HTML
    
    Args:
        md_file: Путь к Markdown файлу
        html_file: Путь к выходному HTML файлу (опционально)
    """
    if html_file is None:
        html_file = md_file.replace('.md', '.html')
    
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"❌ Файл {md_file} не найден")
        return False
    
    print(f"📄 Конвертация {md_file} → {html_file}...")
    
    try:
        import markdown
        
        # Читаем Markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Конвертируем Markdown в HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'tables', 'toc']
        )
        
        # Добавляем стили и структуру HTML
        html_with_styles = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Описание разработки ИИ-системы выбора композита</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 20px;
            }}
            h1 {{
                page-break-after: avoid;
            }}
            h2, h3 {{
                page-break-after: avoid;
            }}
            pre {{
                page-break-inside: avoid;
            }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.8;
            color: #2c3e50;
            background-color: #ffffff;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        h1 {{
            font-size: 28pt;
            color: #1a1a1a;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-top: 40px;
            margin-bottom: 30px;
            page-break-after: avoid;
        }}
        
        h2 {{
            font-size: 22pt;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 35px;
            margin-bottom: 20px;
            page-break-after: avoid;
        }}
        
        h3 {{
            font-size: 18pt;
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 15px;
            page-break-after: avoid;
        }}
        
        h4 {{
            font-size: 14pt;
            color: #555;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Courier New', 'Monaco', monospace;
            font-size: 11pt;
            color: #e83e8c;
            border: 1px solid #e9ecef;
        }}
        
        pre {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            border-left: 5px solid #3498db;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            border: none;
            color: #333;
            font-size: 10pt;
            line-height: 1.6;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 11pt;
        }}
        
        th, td {{
            border: 1px solid #dee2e6;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        blockquote {{
            border-left: 5px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            color: #555;
            font-style: italic;
            background-color: #f8f9fa;
            padding: 15px 20px;
            border-radius: 4px;
        }}
        
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        hr {{
            border: none;
            border-top: 3px solid #dee2e6;
            margin: 30px 0;
        }}
        
        ul, ol {{
            margin-left: 30px;
            margin-bottom: 15px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: bold;
        }}
        
        em {{
            color: #555;
            font-style: italic;
        }}
        
        .toc {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin: 30px 0;
            border-left: 5px solid #3498db;
        }}
        
        .toc ul {{
            list-style-type: none;
            margin-left: 0;
        }}
        
        .toc li {{
            margin-bottom: 5px;
        }}
        
        .toc a {{
            color: #2c3e50;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #dee2e6;
            text-align: center;
            color: #6c757d;
            font-size: 10pt;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
        
        # Сохраняем HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_with_styles)
        
        print(f"✅ HTML создан: {html_file}")
        print(f"\n💡 Откройте файл в браузере и сохраните как PDF:")
        print(f"   - Chrome/Edge: Cmd+P (Mac) или Ctrl+P (Windows) → Сохранить как PDF")
        print(f"   - Safari: Файл → Экспортировать как PDF")
        print(f"   - Firefox: Файл → Печать → Сохранить как PDF")
        
        return True
        
    except ImportError as e:
        print(f"❌ Не установлены необходимые библиотеки: {e}")
        print("\n📦 Установите зависимости:")
        print("   pip3 install markdown")
        return False
    except Exception as e:
        print(f"❌ Ошибка при конвертации: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    md_file = "ОПИСАНИЕ_РАЗРАБОТКИ.md"
    
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        html_file = sys.argv[2]
    else:
        html_file = None
    
    convert_markdown_to_html(md_file, html_file)

