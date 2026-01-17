#!/usr/bin/env python3
"""
Скрипт для конвертации Markdown документа в PDF
"""

import sys
import os
from pathlib import Path

def convert_markdown_to_pdf(md_file: str, pdf_file: str = None):
    """
    Конвертирует Markdown файл в PDF
    
    Args:
        md_file: Путь к Markdown файлу
        pdf_file: Путь к выходному PDF файлу (опционально)
    """
    if pdf_file is None:
        pdf_file = md_file.replace('.md', '.pdf')
    
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"❌ Файл {md_file} не найден")
        return False
    
    print(f"📄 Конвертация {md_file} → {pdf_file}...")
    
    # Метод 1: Использование markdown + weasyprint
    try:
        import markdown
        from weasyprint import HTML, CSS
        
        # Читаем Markdown
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Конвертируем Markdown в HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'tables', 'toc']
        )
        
        # Добавляем стили
        html_with_styles = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: 'DejaVu Sans', Arial, sans-serif;
                    font-size: 11pt;
                    line-height: 1.6;
                    color: #333;
                }}
                h1 {{
                    font-size: 24pt;
                    color: #1a1a1a;
                    border-bottom: 3px solid #1a1a1a;
                    padding-bottom: 10px;
                    margin-top: 30px;
                }}
                h2 {{
                    font-size: 20pt;
                    color: #2c3e50;
                    border-bottom: 2px solid #2c3e50;
                    padding-bottom: 8px;
                    margin-top: 25px;
                }}
                h3 {{
                    font-size: 16pt;
                    color: #34495e;
                    margin-top: 20px;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 10pt;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    border-left: 4px solid #3498db;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
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
                    background-color: #3498db;
                    color: white;
                }}
                blockquote {{
                    border-left: 4px solid #3498db;
                    margin: 15px 0;
                    padding-left: 15px;
                    color: #555;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                hr {{
                    border: none;
                    border-top: 2px solid #ddd;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Конвертируем HTML в PDF
        HTML(string=html_with_styles).write_pdf(pdf_file)
        
        print(f"✅ PDF создан: {pdf_file}")
        return True
        
    except ImportError as e:
        print(f"❌ Не установлены необходимые библиотеки: {e}")
        print("\n📦 Установите зависимости:")
        print("   pip install markdown weasyprint")
        print("\n💡 Альтернатива: используйте pandoc")
        print("   pandoc ОПИСАНИЕ_РАЗРАБОТКИ.md -o ОПИСАНИЕ_РАЗРАБОТКИ.pdf")
        return False
    except Exception as e:
        print(f"❌ Ошибка при конвертации: {e}")
        return False


if __name__ == "__main__":
    md_file = "ОПИСАНИЕ_РАЗРАБОТКИ.md"
    
    if len(sys.argv) > 1:
        md_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        pdf_file = sys.argv[2]
    else:
        pdf_file = None
    
    convert_markdown_to_pdf(md_file, pdf_file)

