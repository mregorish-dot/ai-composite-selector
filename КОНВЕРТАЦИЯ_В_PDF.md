# Инструкция по конвертации Markdown в PDF

## Вариант 1: Использование Pandoc (рекомендуется)

### Установка Pandoc

**macOS:**
```bash
brew install pandoc
brew install basictex  # или mactex для полной установки LaTeX
```

**Windows:**
Скачайте установщик с https://pandoc.org/installing.html

**Linux:**
```bash
sudo apt-get install pandoc texlive-latex-base
```

### Конвертация

```bash
pandoc ОПИСАНИЕ_РАЗРАБОТКИ.md -o ОПИСАНИЕ_РАЗРАБОТКИ.pdf --pdf-engine=xelatex -V mainfont="DejaVu Sans" -V geometry:margin=2cm
```

Или более простой вариант (без LaTeX):
```bash
pandoc ОПИСАНИЕ_РАЗРАБОТКИ.md -o ОПИСАНИЕ_РАЗРАБОТКИ.pdf
```

---

## Вариант 2: Использование Python скрипта

### Установка зависимостей

```bash
pip install markdown weasyprint
```

### Запуск

```bash
python3 convert_to_pdf.py ОПИСАНИЕ_РАЗРАБОТКИ.md
```

---

## Вариант 3: Онлайн конвертеры

1. **Markdown to PDF** - https://www.markdowntopdf.com/
2. **Dillinger** - https://dillinger.io/ (экспорт в PDF)
3. **StackEdit** - https://stackedit.io/ (экспорт в PDF)

---

## Вариант 4: VS Code расширение

Установите расширение "Markdown PDF" в VS Code и используйте команду "Markdown PDF: Export (pdf)".

---

## Рекомендация

Для лучшего качества используйте **Pandoc** с LaTeX движком.

