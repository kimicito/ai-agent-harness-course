#!/usr/bin/env python3
"""
Humanizer Check — сканер AI-паттернов в переводах.
Запускать перед деплоем: python3 scripts/humanizer_check.py [lang]
Поддерживает: fr (default), en, es, zh, ru
"""
import os, glob, re, sys, argparse

def find_lang_dir(lang):
    """Find language directory in common locations."""
    for d in [f"site/{lang}", lang, "."]:
        if os.path.exists(d) and os.path.isdir(d):
            # Check if it has HTML files or subdirs
            if glob.glob(f"{d}/**/*.html", recursive=True):
                return d
    return lang

# Паттерны по языкам
PATTERNS = {
    "en": [
        (r'\bAdditionally,\b', "Additionally — filler"),
        (r'\bFurthermore,\b', "Furthermore — filler"),
        (r'\bMoreover,\b', "Moreover — filler"),
        (r'\bIt is important to note that\b', "It is important to note — filler"),
        (r'\bIn order to\b', "In order to → use 'To'"),
        (r'\bI hope this helps\b', "I hope this helps — chatbot artifact"),
        (r'\bLet me know if you need\b', "Let me know — chatbot artifact"),
        (r'\bOf course!?\b', "Of course — servile tone"),
        (r'\bGreat question!\b', "Great question — servile tone"),
        (r'\bCrucial\b', "Crucial — AI vocabulary"),
        (r'\bPivotal\b', "Pivotal — AI vocabulary"),
        (r'\bLandscape\b', "Landscape — AI vocab (abstract)"),
        (r'\bnot only\b.*\b but also\b', "Not only...but also — parallelism"),
        (r'\bstands as\b', "stands as — copula avoidance"),
        (r'\bserves as\b', "serves as — copula avoidance"),
        (r'\bmarking a\b', "marking a — inflated symbolism"),
        (r'\bsetting the stage\b', "setting the stage — inflated symbolism"),
        (r'\bgroundbreaking\b', "groundbreaking — promotional"),
        (r'\bRich cultural heritage\b', "Rich cultural heritage — promotional"),
    ],
    "fr": [
        (r'\bDe plus,\b', "De plus — filler"),
        (r'\bEn outre,\b', "En outre — filler"),
        (r'\bIl est important de noter que\b', "Il est important de noter — filler"),
        (r'\bAfin de\b', "Afin de — filler"),
        (r'\bBien sûr!?\b', "Bien sûr — servile tone"),
        (r'\bExcellente question!\b', "Excellente question — servile tone"),
        (r'\bJ\'espère que cela aide\b', "J'espère — chatbot artifact"),
        (r'\bN\'hésitez pas à me faire savoir\b', "N'hésitez pas — chatbot artifact"),
        (r'\bVoici un\b', "Voici un — chatbot artifact"),
        (r'\bCrucial\b', "Crucial — AI vocabulary"),
        (r'\bVital\b', "Vital — AI vocabulary"),
        (r'\bPivotal\b', "Pivotal — AI vocabulary"),
        (r'\bPaysage\b', "Paysage — AI vocab (abstract)"),
        (r'\bMet en lumière\b', "Met en lumière — superficial"),
        (r'\bSouligne\b', "Souligne — superficial"),
        (r'\bNon seulement\b.*\b mais aussi\b', "Non seulement...mais aussi — parallelism"),
        (r'\bse tient comme\b', "se tient comme — copula avoidance"),
        (r'\bsert de\b', "sert de — copula avoidance"),
        (r'\bmarquant un\b', "marquant un — inflated symbolism"),
        (r'\bpréparant la scène\b', "préparant la scène — inflated symbolism"),
        (r'\bRévolutionnaire\b', "Révolutionnaire — promotional"),
        (r'\bRiche patrimoine culturel\b', "Riche patrimoine culturel — promotional"),
        (r'\bAu cœur de\b', "Au cœur de — promotional"),
        (r'\bPartie intégrante\b', "Partie intégrante — inflated symbolism"),
    ],
    "ru": [
        (r'\bКроме того,\b', "Кроме того — filler"),
        (r'\bБолее того,\b', "Более того — filler"),
        (r'\bВажно отметить, что\b', "Важно отметить — filler"),
        (r'\bДля того чтобы\b', "Для того чтобы — filler"),
        (r'\bКонечно!?\b', "Конечно — servile tone"),
        (r'\bОтличный вопрос!\b', "Отличный вопрос — servile tone"),
        (r'\bНадеюсь, это поможет\b', "Надеюсь — chatbot artifact"),
        (r'\bВот обзор\b', "Вот обзор — chatbot artifact"),
        (r'\bКритически важный\b', "Критически важный — AI vocab"),
        (r'\bКлючевой\b', "Ключевой — AI vocab"),
        (r'\bЛандшафт\b', "Ландшафт — AI vocab (abstract)"),
        (r'\bПодчеркивает\b', "Подчеркивает — superficial"),
        (r'\bВыделяет\b', "Выделяет — superficial"),
        (r'\bНе только\b.*\b но и\b', "Не только...но и — parallelism"),
        (r'\bЭто не просто\b.*\b это\b', "Это не просто...это — parallelism"),
        (r'\bявляется\b.*\bсвидетельством\b', "является...свидетельством — inflated symbolism"),
        (r'\bиграет (важную|ключевую|решающую|критическую|значительную) роль\b', "играет роль — inflated symbolism"),
        (r'\bНеотъемлемая часть\b', "Неотъемлемая часть — inflated symbolism"),
        (r'\bЗакладывает основу\b', "Закладывает основу — inflated symbolism"),
        (r'\bФормирует\b', "Формирует — inflated symbolism"),
        (r'\bОказывает (значительное|существенное|огромное|колоссальное) влияние\b', "Оказывает влияние — inflated symbolism"),
        (r'\bПредставляет собой\b', "Представляет собой — copula avoidance"),
        (r'\bВыступает в качестве\b', "Выступает в качестве — copula avoidance"),
        (r'\bСлужит\b.*\bдля\b', "Служит для — copula avoidance"),
    ],
    "es": [
        (r'\bAdemás,\b', "Además — filler"),
        (r'\bPor supuesto!?\b', "Por supuesto — servile tone"),
        (r'\bEspero que esto ayude\b', "Espero — chatbot artifact"),
        (r'\bCrucial\b', "Crucial — AI vocabulary"),
        (r'\bPaisaje\b', "Paisaje — AI vocab (abstract)"),
    ],
    "zh": [
        (r'此外，', "此外 — filler"),
        (r'当然', "当然 — servile tone"),
        (r'希望这有帮助', "希望这有帮助 — chatbot artifact"),
        (r'至关重要', "至关重要 — AI vocabulary"),
    ]
}

def scan_file(path, patterns):
    """Сканирует один файл на наличие AI-паттернов."""
    issues = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [(path, 0, f"ERROR: {e}")]
    
    for pattern, label in patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_num = content[:match.start()].count('\n') + 1
            context = content[max(0, match.start()-40):match.end()+40].replace('\n', ' ')
            issues.append((path, line_num, f"{label}\n  → ...{context}..."))
    
    return issues

def main():
    parser = argparse.ArgumentParser(description='Check translations for AI patterns')
    parser.add_argument('lang', nargs='?', default='fr', choices=['en', 'fr', 'es', 'zh', 'ru'],
                        help='Language to check (default: fr)')
    parser.add_argument('--dir', default=None, help='Directory to scan (default: site/LANG/)')
    args = parser.parse_args()
    
    # Определяем директорию
    scan_dir = args.dir if args.dir else find_lang_dir(args.lang)
    
    if not os.path.exists(scan_dir):
        print(f"❌ Directory not found: {scan_dir}")
        sys.exit(1)
    
    # Получаем паттерны
    patterns = PATTERNS.get(args.lang, PATTERNS["en"])
    
    # Сканируем все HTML файлы
    files = glob.glob(f"{scan_dir}/**/*.html", recursive=True)
    print(f"🔍 Scanning {len(files)} files in {scan_dir} for AI patterns...")
    
    all_issues = []
    for filepath in files:
        issues = scan_file(filepath, patterns)
        all_issues.extend(issues)
    
    # Выводим результаты
    if all_issues:
        print(f"\n⚠️  Found {len(all_issues)} AI pattern(s):\n")
        for filepath, line, desc in all_issues:
            print(f"  📁 {filepath}:{line}")
            print(f"     {desc}\n")
        print(f"\n❌ FAILED: {len(all_issues)} AI pattern(s) found")
        sys.exit(1)
    else:
        print(f"\n✅ PASSED: No AI patterns found in {len(files)} files")
        sys.exit(0)

if __name__ == "__main__":
    main()
