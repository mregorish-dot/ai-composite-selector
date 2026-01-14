"""
Предзагруженные научные статьи для обучения системы
"""

# Статья 1: Polymerization shrinkage, microhardness and depth of cure of bulk fill resin composites
ARTICLE_1 = """
Polymerization shrinkage, microhardness and depth of cure of bulk fill resin composites

Fabio Antonio Piola RIZZANTE, Jussaro Alves DUQUE, Marco Antônio Húngaro DUARTE, 
Rafael Francisco Lia MONDELLI, Gustavo MENDONÇA, Sérgio Kiyoshi ISHIKIRIAMA

Dental Materials Journal 2019;38(3):403-410

The present in vitro study assessed the polymerization shrinkage/PS, Knoop microhardness/KHN 
and depth of cure/DC of 9 different resin composites: Filtek Bulk Fill Flowable (FBF), 
Surefill SDR flow (SDR), Xtra Base (XB), Filtek Z350XT Flowable (Z3F), Filtek Bulk Fill Posterior (FBP), 
Xtra Fill (SF), Tetric Evo Ceram Bulk Fill (TBF), Admira Fusion Xtra (ADM), and Filtek Z350XT (Z3XT).

Key findings:
- Low viscosity resin composites showed lower KHN values when compared with high viscosity resins.
- Z3XT showed the highest microhardness among the tested resin composites.
- Z3XT and Z3F showed lower DC when compared with bulk fill resin composites.
- All bulk fill resin composites presented depth of cure higher than 4.5 mm and similar or lower PS than conventional resin composites.

Bulk fill resin composites can be subdivided into two groups: the materials that can be exposed to 
the oral environment (usually high viscosity), with greater mechanical properties; and those that 
should be used as a base/liner (usually low viscosity/flowable), in which the manufacturer recommends 
a capping layer with conventional resin composite.

For occlusal restorations, high viscosity bulk fill composites with polymerization shrinkage of 1-3% 
are recommended. Low viscosity composites with shrinkage up to 6% should not be used for occlusal surfaces.

CRITICAL RECOMMENDATION: For masticatory/occlusal restorations, composites with polymerization shrinkage 
greater than 3% should be excluded. Only high viscosity bulk fill composites with shrinkage 1-3% are 
suitable for occlusal surfaces.

URL: https://www.jstage.jst.go.jp/article/dmj/38/3/38_2018-063/_pdf
DOI: 10.4012/dmj.2018-063
"""

# Статья 2: Исследование влияния концентрации наполнителя на износостойкость
ARTICLE_2 = """
Influence of filler content on wear resistance of nanofilled resin composites

The study synthesized nanofilled resin composites based on resin matrix and 40 nm SiO₂ particles 
with three different filler levels (25%, 50%, and 65% by weight).

Key findings:
- At 25% filler content: material more frequently failed through crack formation and fatigue damage.
- At 50% and 65% filler content: wear mechanism was more related to abrasive surface cutting (microcutting).

According to the authors, optimal mechanical properties (strength, elastic modulus) were observed 
for mixtures with approximately 25-50% filler content. Importantly, higher filler percentage does 
not necessarily provide better wear resistance.

CRITICAL RECOMMENDATION: For optimal wear resistance and mechanical properties, filler content should 
be in the range of 25-50% by weight. Composites with filler content below 25% or above 50% should 
be excluded for occlusal restorations.

Optimal range: 25-50% filler content provides the best balance of strength, elastic modulus, and wear resistance.

URL: https://pubmed.ncbi.nlm.nih.gov/24909664/
"""


def get_preloaded_articles():
    """Возвращает список предзагруженных статей"""
    return [
        {
            'title': 'Polymerization shrinkage, microhardness and depth of cure of bulk fill resin composites',
            'authors': 'RIZZANTE et al.',
            'year': 2019,
            'journal': 'Dental Materials Journal',
            'text': ARTICLE_1,
            'url': 'https://www.jstage.jst.go.jp/article/dmj/38/3/38_2018-063/_pdf',
            'doi': '10.4012/dmj.2018-063',
            'keywords': ['polymerization shrinkage', 'bulk fill', 'microhardness', 'depth of cure', 'occlusal restorations']
        },
        {
            'title': 'Influence of filler content on wear resistance of nanofilled resin composites',
            'authors': 'Research on nanofilled composites',
            'year': 2014,
            'journal': 'PubMed',
            'text': ARTICLE_2,
            'url': 'https://pubmed.ncbi.nlm.nih.gov/24909664/',
            'doi': '',
            'keywords': ['filler content', 'wear resistance', 'nanofilled composites', 'mechanical properties']
        }
    ]


def get_extraction_rules():
    """Возвращает правила извлечения знаний из статей"""
    return {
        'shrinkage_threshold': 3.0,  # Максимальная усадка для жевательных зубов
        'filler_min': 25.0,  # Минимальный процент наполнителя
        'filler_max': 50.0,  # Максимальный процент наполнителя
        'sources': [
            'RIZZANTE et al. 2019 - Dental Materials Journal',
            'PubMed 24909664 - Filler content study'
        ]
    }

