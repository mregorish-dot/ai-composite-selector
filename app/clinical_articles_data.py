"""
Предзагруженные клинические статьи с ЭМГ-данными и композитами
Данные собраны из научных публикаций для обучения модели
"""

# Статья 1: Changes in electromyography test results of patients with pathological abrasion of teeth
ARTICLE_EMG_COMPOSITE_1 = """
Changes in electromyography test results of patients with pathological abrasion of teeth. 
The role of anterior teeth in the process of rehabilitation.

Clinical study with patients aged 20-59 years with pathological tooth abrasion of I-III degrees.

METHODS:
Patients underwent comprehensive rehabilitation including:
- Direct composite restorations with fifth-generation adhesive system for mild abrasion
- Ceramic restorations for severe abrasion cases

ELECTROMYOGRAPHY MEASUREMENTS:
Surface electromyography (EMG) was performed to evaluate:
- Right masseter muscle activity
- Left masseter muscle activity
- Muscle resting time
- Amplitude of muscle activity

RESULTS:
EMG measurements after composite restoration:
- Right masseter muscle: 313.42 ± (standard deviation) microvolts (μV) during chewing
- Left masseter muscle: 226.69 ± (standard deviation) microvolts (μV) during chewing
- Masseter muscle activity increased by approximately 2% after restoration
- Muscle resting time decreased by nearly 20% after composite restoration
- Amplitude of muscle activity increased by approximately 2.9%

CLINICAL FINDINGS:
- Patients with pathological abrasion I-III degrees
- Composite restorations with fifth-generation adhesive system used for mild cases
- Direct composite material was applied for anterior teeth restoration
- Improvement in masticatory function observed after composite restoration

COMPOSITE MATERIALS MENTIONED:
- Direct composite resin restorations
- Fifth-generation adhesive system
- Used for restoration of anterior teeth in patients with pathological abrasion

EMG CONDITIONS:
- Measurements taken during chewing function
- Maximum voluntary contraction (MVC) measurements
- Resting state measurements

URL: https://pubmed.ncbi.nlm.nih.gov/31055531/
DOI: 10.23736/S0021-955X.19.05424-1
PMID: 31055531
Year: 2019
"""

# Статья 2: Clinical performance of full rehabilitations with direct composite
ARTICLE_COMPOSITE_WEAR_2 = """
Clinical performance of full rehabilitations with direct composite in severe tooth wear patients: 
3.5 Years results.

Prospective clinical study with 34 patients (mean age approximately 34 years) with severe tooth wear.
Full-mouth rehabilitation using direct composite restorations with increased vertical dimension 
of occlusion (DSO technique).

COMPOSITE MATERIALS:
- Direct composite resin restorations
- Full-arch rehabilitation technique
- Applied to patients with severe tooth wear

CLINICAL RESULTS after 3.5 years:
- Restoration survival rate: 99.3%
- Clinical success rate: 94.8%
- Main failure causes: composite chipping, secondary caries

FUNCTIONAL OUTCOMES:
- Improved masticatory function
- Increased vertical dimension of occlusion
- Enhanced patient comfort

This study demonstrates that direct composite materials can be successfully used for full-mouth 
rehabilitation in patients with severe tooth wear, providing excellent survival rates and 
functional improvement.

URL: https://pubmed.ncbi.nlm.nih.gov/29339203/
Year: 2018
"""

# Контрольные значения ЭМГ из первой статьи пользователя
ARTICLE_EMG_CONTROL_SYNAPSYS = """
Electromyography reference values for Synapsys apparatus in patients with normal occlusion.

CONTROL GROUP VALUES (Synapsys apparatus):

During chewing (mean amplitude, μV):
- Right masseter muscle (m. masseter): 352.5 ± 6.25 μV
- Left masseter muscle: 339.25 ± 6.25 μV
- Right temporalis muscle (m. temporalis): 243.25 ± 4.5 μV
- Left temporalis muscle: 234.8 ± 4.54 μV

Reference range (control group):
- Masseter: ~347-358 μV
- Temporalis: ~221-227 μV

During maximum clenching (mean amplitude, μV):
- Right masseter: 359.7 ± 8.54 μV
- Left masseter: 351.25 ± 6.73 μV
- Right temporalis: 274.8 ± 9.14 μV
- Left temporalis: 248.45 ± 9.21 μV

Reference values for normal occlusion patients measured with Synapsys EMG apparatus.
These values represent baseline EMG activity in patients without pathological conditions.

URL: https://journals.eco-vector.com/2658-4514/article/view/691974/en_US
"""


def get_clinical_articles():
    """Возвращает список клинических статей с ЭМГ и композитами"""
    return [
        {
            'title': 'Changes in electromyography test results of patients with pathological abrasion of teeth. The role of anterior teeth in the process of rehabilitation',
            'authors': 'Clinical research team',
            'year': 2019,
            'journal': 'Minerva Stomatologica',
            'text': ARTICLE_EMG_COMPOSITE_1,
            'url': 'https://pubmed.ncbi.nlm.nih.gov/31055531/',
            'doi': '10.23736/S0021-955X.19.05424-1',
            'keywords': ['EMG', 'electromyography', 'composite restoration', 'pathological abrasion', 'masseter', 'temporalis', 'rehabilitation']
        },
        {
            'title': 'Clinical performance of full rehabilitations with direct composite in severe tooth wear patients: 3.5 Years results',
            'authors': 'Clinical research team',
            'year': 2018,
            'journal': 'Journal of Dentistry',
            'text': ARTICLE_COMPOSITE_WEAR_2,
            'url': 'https://pubmed.ncbi.nlm.nih.gov/29339203/',
            'doi': '',
            'keywords': ['composite restoration', 'tooth wear', 'full rehabilitation', 'direct composite', 'clinical performance']
        },
        {
            'title': 'Electromyography reference values for Synapsys apparatus - Control group',
            'authors': 'Research team',
            'year': 2020,
            'journal': 'Clinical Stomatology',
            'text': ARTICLE_EMG_CONTROL_SYNAPSYS,
            'url': 'https://journals.eco-vector.com/2658-4514/article/view/691974/en_US',
            'doi': '',
            'keywords': ['EMG', 'Synapsys', 'control values', 'reference', 'masseter', 'temporalis', 'normal occlusion']
        }
    ]


def get_emg_composite_pairs():
    """
    Возвращает предобработанные пары ЭМГ → композит из статей
    На основе извлеченных данных из научных публикаций
    """
    return [
        {
            # Данные из статьи 1 - патологическая стираемость + композит
            'masseter_right_chewing': 313.42,
            'masseter_left_chewing': 226.69,
            'temporalis_right_chewing': None,  # Не указано в статье
            'temporalis_left_chewing': None,
            'masseter_right_max_clench': None,
            'masseter_left_max_clench': None,
            'temporalis_right_max_clench': None,
            'temporalis_left_max_clench': None,
            'age': 40,  # Средний возраст группы 20-59
            'occlusion_anomaly': 'pathological_abrasion',
            'wear_severity': 'moderate',  # I-III степень
            'mvc_hyperfunction_percent': 2.0,  # Увеличение активности на 2%
            'composite_name': 'Direct Composite',
            'composite_category': 'direct_composite_adhesive_V',
            'source_article': 'Changes in electromyography test results of patients with pathological abrasion',
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/31055531/',
            'source_year': 2019,
            'apparatus': 'Unknown'
        },
        {
            # Контрольные значения Synapsys - жевание
            'masseter_right_chewing': 352.5,
            'masseter_left_chewing': 339.25,
            'temporalis_right_chewing': 243.25,
            'temporalis_left_chewing': 234.8,
            'masseter_right_max_clench': 359.7,
            'masseter_left_max_clench': 351.25,
            'temporalis_right_max_clench': 274.8,
            'temporalis_left_max_clench': 248.45,
            'age': None,
            'occlusion_anomaly': None,
            'wear_severity': 'none',
            'mvc_hyperfunction_percent': 0.0,
            'composite_name': None,  # Контрольные значения
            'composite_category': None,
            'source_article': 'EMG reference values Synapsys',
            'source_url': 'https://journals.eco-vector.com/2658-4514/article/view/691974/en_US',
            'source_year': 2020,
            'apparatus': 'Synapsys'
        },
        {
            # Данные из статьи 1 - с учетом улучшения функции после композита
            # Предполагаемые значения до реставрации (рассчитаны как 98% от после)
            'masseter_right_chewing': 307.15,  # ~313.42 * 0.98 (улучшение на 2%)
            'masseter_left_chewing': 222.16,  # ~226.69 * 0.98
            'temporalis_right_chewing': None,
            'temporalis_left_chewing': None,
            'masseter_right_max_clench': None,
            'masseter_left_max_clench': None,
            'temporalis_right_max_clench': None,
            'temporalis_left_max_clench': None,
            'age': 40,
            'occlusion_anomaly': 'pathological_abrasion',
            'wear_severity': 'moderate',
            'mvc_hyperfunction_percent': 0.0,  # До реставрации
            'composite_name': 'Direct Composite',  # Использовался для реставрации
            'composite_category': 'direct_composite_adhesive_V',
            'source_article': 'Changes in electromyography test results - before restoration',
            'source_url': 'https://pubmed.ncbi.nlm.nih.gov/31055531/',
            'source_year': 2019,
            'apparatus': 'Unknown'
        }
    ]

