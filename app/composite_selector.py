"""
Основная программа для выбора композита на основе ЭМГ-данных и технических характеристик
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
try:
    from Код_нормализации_ЭМГ import (
        EMGNormalizer, EMGApparatus, MuscleType, MeasurementCondition,
        create_emg_features
    )
except ImportError:
    # Альтернативный импорт если есть проблемы с кодировкой
    import sys
    import importlib.util
    spec = importlib.util.spec_from_file_location("emg_normalizer", "Код_нормализации_ЭМГ.py")
    emg_module = importlib.util.module_from_spec(spec)
    sys.modules["emg_normalizer"] = emg_module
    spec.loader.exec_module(emg_module)
    EMGNormalizer = emg_module.EMGNormalizer
    EMGApparatus = emg_module.EMGApparatus
    MuscleType = emg_module.MuscleType
    MeasurementCondition = emg_module.MeasurementCondition
    create_emg_features = emg_module.create_emg_features


@dataclass
class PatientData:
    """Данные пациента"""
    # ЭМГ-данные
    apparatus: str = "Synapsys"
    masseter_right_chewing: float = 0.0
    masseter_left_chewing: float = 0.0
    temporalis_right_chewing: float = 0.0
    temporalis_left_chewing: float = 0.0
    masseter_right_max_clench: float = 0.0
    masseter_left_max_clench: float = 0.0
    temporalis_right_max_clench: float = 0.0
    temporalis_left_max_clench: float = 0.0
    
    # Дополнительные данные
    age: Optional[int] = None
    occlusion_anomaly_type: Optional[str] = None
    wear_severity: Optional[str] = None  # none, mild, moderate, severe, bushan_I-IV, twes_0-4
    mvc_hyperfunction_percent: Optional[float] = None
    mvc_duration_sec_per_min: Optional[float] = None
    # Дополнительные фильтры
    region_filter: Optional[List[str]] = None
    manufacturer_filter: Optional[List[str]] = None
    year_min: Optional[int] = None
    price_max: Optional[float] = None


class CompositeDatabase:
    """База данных композитов"""
    
    def __init__(self, json_path: str = None):
        """Загрузка базы данных композитов"""
        if json_path is None:
            # Пробуем найти файл в текущей директории или родительской
            import os
            from pathlib import Path
            current_dir = Path(__file__).parent
            parent_dir = current_dir.parent
            for path in [current_dir / "База_композитов.json", parent_dir / "База_композитов.json"]:
                if path.exists():
                    json_path = str(path)
                    break
            if json_path is None:
                json_path = "База_композитов.json"
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл не найден: {json_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON файла {json_path}: {e}")
        
        # Безопасная загрузка данных с проверками
        if not isinstance(self.data, dict):
            raise ValueError("Файл База_композитов.json должен содержать словарь (JSON объект)")
        
        # Проверяем наличие обязательных ключей
        if 'composites' not in self.data:
            raise KeyError("Отсутствует обязательный ключ 'composites' в JSON файле")
        if 'selection_criteria' not in self.data:
            raise KeyError("Отсутствует обязательный ключ 'selection_criteria' в JSON файле")
        if 'emg_based_classification' not in self.data:
            raise KeyError("Отсутствует обязательный ключ 'emg_based_classification' в JSON файле")
        
        # Загружаем данные с безопасными значениями по умолчанию
        self.composites = pd.DataFrame(self.data['composites'])
        self.criteria = self.data.get('selection_criteria', {})
        self.emg_classification = self.data.get('emg_based_classification', {})
        self.bushan_classification = self.data.get('bushan_classification', {})
        self.twes2_classification = self.data.get('twes2_classification', {})
    
    def filter_composites(
        self,
        for_occlusal: bool = True,
        has_occlusion_anomaly: bool = False,
        wear_severity: Optional[str] = None,
        use_article_rules: bool = True,
        region_filter: Optional[List[str]] = None,
        manufacturer_filter: Optional[List[str]] = None,
        year_min: Optional[int] = None,
        price_max: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Фильтрация композитов по критериям
        
        Args:
            for_occlusal: Для окклюзионных реставраций
            has_occlusion_anomaly: Наличие аномалии прикуса
            wear_severity: Степень стираемости (none, mild, moderate, severe)
            use_article_rules: Использовать правила из научных статей
        """
        df = self.composites.copy()
        
        # Базовые критерии для окклюзионных реставраций
        if for_occlusal:
            required = self.criteria['for_occlusal_restorations']['required']
            
            # Фильтрация по обязательным критериям
            df = df[df['viscosity'] == required['viscosity']]
            df = df[df['polymerization_shrinkage_percent'] <= required['polymerization_shrinkage_percent_max']]
            df = df[df['microhardness_KHN'] >= required['microhardness_KHN_min']]
            df = df[df['suitable_for_occlusal'] == required['suitable_for_occlusal']]
            df = df[df['requires_capping'] == required['requires_capping']]
            
            # Исключение категорий
            excluded = self.criteria['for_occlusal_restorations']['excluded_categories']
            df = df[~df['category'].isin(excluded)]
        
        # ПРАВИЛА ИЗ НАУЧНЫХ СТАТЕЙ
        if use_article_rules:
            # Правило из статьи 1: Исключить композиты с усадкой >3%
            # Источник: RIZZANTE et al. 2019 - Dental Materials Journal
            initial_count = len(df)
            df = df[df['polymerization_shrinkage_percent'] <= 3.0]
            if len(df) < initial_count:
                excluded = initial_count - len(df)
                # Логирование исключенных композитов
                pass
            
            # Правило из статьи 2: Приоритет композитам с наполнителем 25-50%
            # Источник: PubMed 24909664 - Оптимальный диапазон 25-50%
            # Примечание: Расширяем диапазон до 20-55% для большей гибкости
            # Композиты с наполнителем 20-55% получают приоритет,
            # остальные предлагаются как альтернатива
            # НЕ исключаем композиты с наполнителем >55%, а помечаем их для альтернативного выбора
            df['filler_optimal'] = (
                (df['filler_content_percent'] >= 20.0) & 
                (df['filler_content_percent'] < 55.0)
            )
            
            # Исключаем только композиты с наполнителем <20%
            initial_count = len(df)
            df = df[df['filler_content_percent'] >= 20.0]
            if len(df) < initial_count:
                excluded = initial_count - len(df)
                # Логирование исключенных композитов
                pass
        
        # Дополнительные критерии для аномалий прикуса
        if has_occlusion_anomaly:
            additional = self.criteria['for_patients_with_occlusion_anomalies']['additional_requirements']
            df = df[df['wear_resistance'].isin(['high', 'very_high'])]
            df = df[df['microhardness_KHN'] >= additional['microhardness_KHN_min']]
            df = df[df['polymerization_shrinkage_percent'] <= additional['polymerization_shrinkage_percent_max']]
        
        # Критерии на основе классификации стираемости
        if wear_severity:
            # Классификация TWES 2.0
            if wear_severity.startswith('twes_'):
                grade = wear_severity.replace('twes_', '')
                if self.twes2_classification and 'grades' in self.twes2_classification:
                    if grade in self.twes2_classification['grades']:
                        criteria = self.twes2_classification['grades'][grade]
                        min_hardness = criteria.get('recommended_microhardness_min', 50)
                        df = df[df['microhardness_KHN'] >= min_hardness]
                        
                        recommended_wear = criteria.get('recommended_wear_resistance', 'high')
                        if recommended_wear == 'very_high':
                            df = df[df['wear_resistance'].isin(['very_high', 'high'])]
                        else:
                            df = df[df['wear_resistance'].isin(['high', 'very_high', 'medium'])]
                        
                        min_filler = criteria.get('recommended_filler_min', 60)
                        df = df[df['filler_content_percent'] >= min_filler]
            # Классификация по Бушану
            elif wear_severity.startswith('bushan_'):
                degree = wear_severity.replace('bushan_', '')
                if self.bushan_classification and 'degrees' in self.bushan_classification:
                    if degree in self.bushan_classification['degrees']:
                        criteria = self.bushan_classification['degrees'][degree]
                        min_hardness = criteria.get('recommended_microhardness_min', 50)
                        df = df[df['microhardness_KHN'] >= min_hardness]
                        
                        recommended_wear = criteria.get('recommended_wear_resistance', 'high')
                        if recommended_wear == 'very_high':
                            df = df[df['wear_resistance'].isin(['very_high', 'high'])]
                        else:
                            df = df[df['wear_resistance'].isin(['high', 'very_high', 'medium'])]
                        
                        min_filler = criteria.get('recommended_filler_min', 60)
                        df = df[df['filler_content_percent'] >= min_filler]
            # ЭМГ-классификация
            elif wear_severity in ['none', 'mild']:
                criteria = self.emg_classification['wear_severity_none_mild']
                min_hardness = criteria['recommended_microhardness_min']
                df = df[df['microhardness_KHN'] >= min_hardness]
            elif wear_severity in ['moderate', 'severe']:
                criteria = self.emg_classification['wear_severity_moderate_severe']
                min_hardness = criteria['recommended_microhardness_min']
                df = df[df['microhardness_KHN'] >= min_hardness]
                # Принимаем как "high", так и "very_high" износостойкость
                recommended_wear = criteria['recommended_wear_resistance']
                df = df[df['wear_resistance'].isin([recommended_wear, 'high'])]
        
        # Дополнительные фильтры
        if region_filter and 'Все' not in region_filter:
            df = df[df['region'].isin(region_filter)]
        
        if manufacturer_filter and 'Все' not in manufacturer_filter:
            df = df[df['manufacturer'].isin(manufacturer_filter)]
        
        if year_min:
            if 'year_released' in df.columns:
                df = df[df['year_released'] >= year_min]
        
        if price_max:
            if 'price_rub' in df.columns:
                df = df[df['price_rub'] <= price_max]
        
        return df
    
    def calculate_composite_score(
        self,
        composite: pd.Series,
        emg_features: pd.Series,
        patient_data: PatientData
    ) -> float:
        """
        Расчет оценки композита для пациента
        
        Args:
            composite: Данные композита
            emg_features: Признаки ЭМГ
            patient_data: Данные пациента
            
        Returns:
            Оценка композита (чем выше, тем лучше)
        """
        score = 0.0
        
        # Базовые характеристики (веса)
        weights = {
            'microhardness': 0.3,
            'wear_resistance': 0.25,
            'polymerization_shrinkage': 0.2,
            'filler_content': 0.15,
            'depth_of_cure': 0.1
        }
        
        # Микротвердость (чем выше, тем лучше)
        max_hardness = self.composites['microhardness_KHN'].max()
        hardness_score = composite['microhardness_KHN'] / max_hardness
        score += weights['microhardness'] * hardness_score
        
        # Износостойкость
        wear_map = {'low': 0.3, 'medium': 0.6, 'high': 0.9, 'very_high': 1.0}
        wear_score = wear_map.get(composite['wear_resistance'], 0.5)
        score += weights['wear_resistance'] * wear_score
        
        # Полимеризационная усадка (чем меньше, тем лучше)
        max_shrinkage = self.composites['polymerization_shrinkage_percent'].max()
        shrinkage_score = 1 - (composite['polymerization_shrinkage_percent'] / max_shrinkage)
        score += weights['polymerization_shrinkage'] * shrinkage_score
        
        # Концентрация наполнителя (оптимальный диапазон 25-50% согласно статье 2)
        # Расширяем оптимальный диапазон до 20-55% для большей гибкости
        filler = composite['filler_content_percent']
        if 20 <= filler < 55:
            # Оптимальный диапазон - максимальный балл
            filler_score = 1.0
            # Дополнительный бонус за соответствие правилу из статьи (строгий диапазон 25-50%)
            if 25 <= filler < 50:
                score += 0.15  # Максимальный бонус за строго оптимальный наполнитель
            else:
                score += 0.1  # Бонус за близкий к оптимальному наполнитель
        elif filler < 20:
            # Меньше оптимального - снижаем оценку
            filler_score = filler / 20
        else:
            # Больше 55% - предлагаем как альтернативу (снижаем оценку, но не исключаем)
            # Композиты с наполнителем 55-70% получают хорошую оценку
            # Композиты с наполнителем >70% получают сниженную оценку
            if 55 <= filler <= 70:
                filler_score = 0.8  # Хорошая альтернатива
            elif 70 < filler <= 85:
                filler_score = 0.6  # Приемлемая альтернатива
            else:
                filler_score = 0.4  # Альтернатива с замечанием
        score += weights['filler_content'] * filler_score
        
        # Глубина полимеризации (чем больше, тем лучше для bulk fill)
        if composite['category'] in ['high_viscosity_bulk_fill', 'low_viscosity_bulk_fill']:
            max_depth = 5.0  # максимальная глубина для bulk fill
            depth_score = composite['depth_of_cure_mm'] / max_depth
        else:
            depth_score = 0.7  # для традиционных композитов
        score += weights['depth_of_cure'] * depth_score
        
        # Учет ЭМГ-показателей
        # Если есть асимметрия, предпочитать более прочные материалы
        if 'masseter_asymmetry_chewing' in emg_features:
            asymmetry = emg_features['masseter_asymmetry_chewing']
            if asymmetry > 20:  # значительная асимметрия
                score += 0.1 * hardness_score  # бонус за прочность
        
        # Учет гиперфункции
        if patient_data.mvc_hyperfunction_percent and patient_data.mvc_hyperfunction_percent > 20:
            if patient_data.mvc_duration_sec_per_min:
                if patient_data.mvc_duration_sec_per_min >= 4:  # средняя/тяжелая стираемость
                    score += 0.15 * wear_score  # дополнительный бонус за износостойкость
        
        return score


class CompositeSelector:
    """Система выбора композита на основе ИИ"""
    
    def __init__(self, composite_db_path: str = None):
        """Инициализация селектора"""
        self.db = CompositeDatabase(composite_db_path)
        self.normalizer = EMGNormalizer()
    
    def select_composite(
        self,
        patient_data: PatientData,
        top_n: int = 3,
        include_alternatives: bool = True
    ) -> List[Tuple[pd.Series, float, Dict]]:
        """
        Выбор оптимального композита для пациента
        
        Args:
            patient_data: Данные пациента
            top_n: Количество лучших вариантов для возврата
            include_alternatives: Включать альтернативные варианты (с наполнителем >50%)
            
        Returns:
            Список кортежей (композит, оценка, обоснование)
        """
        # Определение степени стираемости на основе ЭМГ
        wear_severity = self._classify_wear_severity(patient_data)
        
        # Фильтрация композитов с применением правил из научных статей
        filtered = self.db.filter_composites(
            for_occlusal=True,
            has_occlusion_anomaly=patient_data.occlusion_anomaly_type is not None,
            wear_severity=wear_severity,
            use_article_rules=True  # Применяем правила из статей
        )
        
        if filtered.empty:
            return []
        
        # Создание ЭМГ-признаков
        emg_dict = {
            'apparatus': patient_data.apparatus,
            'masseter_right_chewing': patient_data.masseter_right_chewing,
            'masseter_left_chewing': patient_data.masseter_left_chewing,
            'temporalis_right_chewing': patient_data.temporalis_right_chewing,
            'temporalis_left_chewing': patient_data.temporalis_left_chewing,
            'masseter_right_max_clench': patient_data.masseter_right_max_clench,
            'masseter_left_max_clench': patient_data.masseter_left_max_clench,
            'temporalis_right_max_clench': patient_data.temporalis_right_max_clench,
            'temporalis_left_max_clench': patient_data.temporalis_left_max_clench,
        }
        emg_features = create_emg_features(emg_dict, self.normalizer)
        
        # Разделение на приоритетные (наполнитель 25-50%) и альтернативные (>50%)
        # Расширяем диапазон приоритетных до 20-55% для большей гибкости
        priority_composites = filtered[
            (filtered['filler_content_percent'] >= 20.0) & 
            (filtered['filler_content_percent'] < 55.0)
        ].copy()
        
        alternative_composites = filtered[
            filtered['filler_content_percent'] >= 55.0
        ].copy() if include_alternatives else pd.DataFrame()
        
        # Расчет оценок для приоритетных композитов
        priority_results = []
        for idx, composite in priority_composites.iterrows():
            score = self.db.calculate_composite_score(
                composite, emg_features.iloc[0], patient_data
            )
            justification = self._generate_justification(
                composite, score, patient_data, wear_severity, is_priority=True
            )
            priority_results.append((composite, score, justification))
        
        # Расчет оценок для альтернативных композитов
        alternative_results = []
        if include_alternatives and not alternative_composites.empty:
            for idx, composite in alternative_composites.iterrows():
                score = self.db.calculate_composite_score(
                    composite, emg_features.iloc[0], patient_data
                )
                justification = self._generate_justification(
                    composite, score, patient_data, wear_severity, is_priority=False
                )
                alternative_results.append((composite, score, justification))
        
        # Сортировка
        priority_results.sort(key=lambda x: x[1], reverse=True)
        alternative_results.sort(key=lambda x: x[1], reverse=True)
        
        # Объединение: сначала приоритетные, потом альтернативные
        all_results = priority_results + alternative_results
        
        return all_results[:top_n]
    
    def _classify_wear_severity(self, patient_data: PatientData) -> Optional[str]:
        """
        Классификация степени стираемости на основе ЭМГ или Бушан
        
        Returns:
            Степень стираемости: none, mild, moderate, severe, или bushan_I, bushan_II, bushan_III, bushan_IV
        """
        if patient_data.wear_severity:
            return patient_data.wear_severity
        
        if (patient_data.mvc_hyperfunction_percent and 
            patient_data.mvc_hyperfunction_percent > 20 and
            patient_data.mvc_duration_sec_per_min):
            
            if 1 <= patient_data.mvc_duration_sec_per_min <= 2:
                return 'mild'
            elif 4 <= patient_data.mvc_duration_sec_per_min <= 6:
                return 'moderate'
        
        return None
    
    def _generate_justification(
        self,
        composite: pd.Series,
        score: float,
        patient_data: PatientData,
        wear_severity: Optional[str],
        is_priority: bool = True
    ) -> Dict:
        """Генерация обоснования выбора"""
        reasons = []
        
        # Основные преимущества
        if composite['microhardness_KHN'] >= 70:
            reasons.append(f"Высокая микротвердость ({composite['microhardness_KHN']:.1f} KHN)")
        
        if composite['wear_resistance'] in ['high', 'very_high']:
            reasons.append(f"Высокая износостойкость ({composite['wear_resistance']})")
        
        if composite['polymerization_shrinkage_percent'] <= 2.5:
            reasons.append(f"Низкая усадка ({composite['polymerization_shrinkage_percent']:.1f}%)")
        
        # Информация о наполнителе
        filler = composite['filler_content_percent']
        if 25 <= filler < 50:
            reasons.append(f"✅ Оптимальный наполнитель ({filler:.0f}%) - соответствует статье 2")
        elif 20 <= filler < 55:
            reasons.append(f"✅ Хороший наполнитель ({filler:.0f}%) - близко к оптимальному диапазону 25-50%")
        elif filler >= 55:
            if is_priority:
                reasons.append(f"⚠️ Наполнитель {filler:.0f}% (оптимально 25-50% по статье 2)")
            else:
                reasons.append(f"Альтернативный вариант: наполнитель {filler:.0f}% (оптимально 25-50%)")
        
        # Специфические для пациента
        if wear_severity:
            if wear_severity.startswith('bushan_'):
                degree = wear_severity.replace('bushan_', '')
                if self.db.bushan_classification and 'degrees' in self.db.bushan_classification:
                    if degree in self.db.bushan_classification['degrees']:
                        bush_info = self.db.bushan_classification['degrees'][degree]
                        reasons.append(f"Рекомендован для {bush_info['name']} по Бушану: {bush_info['characteristics']}")
            elif wear_severity in ['moderate', 'severe']:
                reasons.append("Подходит для пациентов с патологической стираемостью")
        
        if patient_data.occlusion_anomaly_type:
            reasons.append("Оптимален для пациентов с аномалиями прикуса")
        
        # Метка приоритета
        priority_note = ""
        if not is_priority:
            priority_note = "Альтернативный вариант (наполнитель вне оптимального диапазона 25-50%)"
        
        return {
            'score': score,
            'reasons': reasons,
            'category': composite['category'],
            'notes': composite.get('notes', ''),
            'is_priority': is_priority,
            'priority_note': priority_note,
            'filler_content': filler
        }


def main():
    """Пример использования программы"""
    print("=" * 60)
    print("Система выбора композита на основе ИИ и ЭМГ-данных")
    print("=" * 60)
    print()
    
    # Создание селектора
    selector = CompositeSelector()
    
    # Пример данных пациента
    patient = PatientData(
        apparatus="Synapsys",
        masseter_right_chewing=350.5,
        masseter_left_chewing=339.25,
        temporalis_right_chewing=243.25,
        temporalis_left_chewing=234.8,
        masseter_right_max_clench=359.7,
        masseter_left_max_clench=351.25,
        temporalis_right_max_clench=274.8,
        temporalis_left_max_clench=248.45,
        occlusion_anomaly_type="аномалия прикуса",
        mvc_hyperfunction_percent=25.0,
        mvc_duration_sec_per_min=3.0
    )
    
    # Выбор композита
    results = selector.select_composite(patient, top_n=3)
    
    if not results:
        print("❌ Не найдено подходящих композитов")
        return
    
    print(f"✅ Найдено {len(results)} рекомендуемых композита(ов):\n")
    
    for i, (composite, score, justification) in enumerate(results, 1):
        print(f"{'=' * 60}")
        print(f"Вариант {i}: {composite['name']}")
        print(f"Оценка: {score:.3f} (максимум 1.0)")
        print(f"{'=' * 60}")
        print(f"Категория: {composite['category']}")
        print(f"Вязкость: {composite['viscosity']}")
        print(f"Микротвердость: {composite['microhardness_KHN']:.2f} KHN")
        print(f"Полимеризационная усадка: {composite['polymerization_shrinkage_percent']:.2f}%")
        print(f"Концентрация наполнителя: {composite['filler_content_percent']:.1f}%")
        print(f"Износостойкость: {composite['wear_resistance']}")
        print(f"Глубина полимеризации: {composite['depth_of_cure_mm']:.2f} мм")
        print()
        print("Обоснование:")
        for reason in justification['reasons']:
            print(f"  ✓ {reason}")
        if justification['notes']:
            print(f"\nПримечание: {justification['notes']}")
        print()


if __name__ == "__main__":
    main()

