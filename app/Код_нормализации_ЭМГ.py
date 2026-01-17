"""
Модуль для нормализации ЭМГ-показателей между разными аппаратами
для использования в ИИ-модели выбора композита
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from enum import Enum


class EMGApparatus(Enum):
    """Типы ЭМГ-аппаратов"""
    BJOEMG2 = "BjoEMG II"
    SYNAPSYS = "Synapsys"
    KOLIBRI = "Kolibri"
    OTHER = "Other"


class MuscleType(Enum):
    """Типы мышц"""
    MASSETER = "masseter"
    TEMPORALIS = "temporalis"


class MeasurementCondition(Enum):
    """Условия измерения"""
    CHEWING = "chewing"  # акт жевания
    MAX_CLENCH = "max_clench"  # максимальное сжатие


class EMGNormalizer:
    """
    Класс для нормализации ЭМГ-показателей между разными аппаратами
    """
    
    # Контрольные значения (норма) для Synapsys
    CONTROL_VALUES_SYNAPSYS = {
        MeasurementCondition.CHEWING: {
            MuscleType.MASSETER: 352.5,  # среднее из диапазона 347-358
            MuscleType.TEMPORALIS: 224.0,  # среднее из диапазона 221-227
        },
        MeasurementCondition.MAX_CLENCH: {
            MuscleType.MASSETER: 355.0,  # среднее из диапазона 351-360
            MuscleType.TEMPORALIS: 262.0,  # среднее из диапазона 248-275
        }
    }
    
    # Контрольные значения (норма) для Колибри
    CONTROL_VALUES_KOLIBRI = {
        MeasurementCondition.CHEWING: {
            MuscleType.MASSETER: 111.0,
            MuscleType.TEMPORALIS: 138.0,
        },
        MeasurementCondition.MAX_CLENCH: {
            MuscleType.MASSETER: 278.0,
            MuscleType.TEMPORALIS: 558.0,
        }
    }
    
    # Контрольные значения (норма) для BjoEMG II (BioPAK Inc., США)
    # На основе научных статей: 
    # - В покое (rest): ~1.0-4.0 μV (среднее 2-3 μV) - порог патологии ≥1.5 μV
    # - При жевании (chewing): ~40-90 μV (среднее ~60 μV)
    # - При MVC (max clench): ~200-250 μV (среднее ~230 μV)
    # Источники: PubMed 28390127, PMC 10830968, и др.
    CONTROL_VALUES_BJOEMG2 = {
        MeasurementCondition.CHEWING: {
            MuscleType.MASSETER: 60.0,  # среднее из диапазона 40-90 μV (литература)
            MuscleType.TEMPORALIS: 60.0,  # среднее из диапазона 40-90 μV
        },
        MeasurementCondition.MAX_CLENCH: {
            MuscleType.MASSETER: 230.0,  # среднее из диапазона 200-250 μV (литература)
            MuscleType.TEMPORALIS: 230.0,  # среднее из диапазона 200-250 μV
        }
    }
    
    # Коэффициенты пересчета (экспериментальные, требуют валидации)
    CONVERSION_COEFFICIENTS = {
        MeasurementCondition.CHEWING: {
            MuscleType.MASSETER: 3.1,  # Synapsys / Колибри
            MuscleType.TEMPORALIS: 1.75,
        },
        MeasurementCondition.MAX_CLENCH: {
            MuscleType.MASSETER: 1.3,
            MuscleType.TEMPORALIS: 0.5,  # обратный коэффициент (Колибри > Synapsys)
        }
    }
    
    def __init__(self, reference_apparatus: EMGApparatus = EMGApparatus.SYNAPSYS):
        """
        Инициализация нормализатора
        
        Args:
            reference_apparatus: Референсный аппарат для нормализации
        """
        self.reference_apparatus = reference_apparatus
    
    def normalize_to_control(
        self,
        value: float,
        apparatus: EMGApparatus,
        muscle: MuscleType,
        condition: MeasurementCondition,
        side: str = "right"
    ) -> float:
        """
        Нормализация значения относительно контрольной группы
        
        Args:
            value: Измеренное значение ЭМГ (мкВ)
            apparatus: Тип аппарата
            muscle: Тип мышцы
            condition: Условие измерения
            side: Сторона (right/left)
            
        Returns:
            Нормализованное значение (процент от нормы)
        """
        if apparatus == EMGApparatus.SYNAPSYS:
            control = self.CONTROL_VALUES_SYNAPSYS[condition][muscle]
        elif apparatus == EMGApparatus.KOLIBRI:
            control = self.CONTROL_VALUES_KOLIBRI[condition][muscle]
        elif apparatus == EMGApparatus.BJOEMG2:
            control = self.CONTROL_VALUES_BJOEMG2[condition][muscle]
        else:
            # Для неизвестных аппаратов используем Synapsys как fallback
            control = self.CONTROL_VALUES_SYNAPSYS[condition][muscle]
        
        return (value / control) * 100
    
    def convert_between_apparatus(
        self,
        value: float,
        from_apparatus: EMGApparatus,
        to_apparatus: EMGApparatus,
        muscle: MuscleType,
        condition: MeasurementCondition
    ) -> float:
        """
        Конвертация значения между аппаратами
        
        Args:
            value: Исходное значение
            from_apparatus: Исходный аппарат
            to_apparatus: Целевой аппарат
            muscle: Тип мышцы
            condition: Условие измерения
            
        Returns:
            Конвертированное значение
        """
        if from_apparatus == to_apparatus:
            return value
        
        # Если конвертируем в Synapsys
        if to_apparatus == EMGApparatus.SYNAPSYS:
            if from_apparatus == EMGApparatus.KOLIBRI:
                coeff = self.CONVERSION_COEFFICIENTS[condition][muscle]
                return value * coeff
            else:
                raise ValueError(f"Конвертация из {from_apparatus} не поддерживается")
        
        # Если конвертируем из Synapsys
        elif from_apparatus == EMGApparatus.SYNAPSYS:
            if to_apparatus == EMGApparatus.KOLIBRI:
                coeff = self.CONVERSION_COEFFICIENTS[condition][muscle]
                return value / coeff
            else:
                raise ValueError(f"Конвертация в {to_apparatus} не поддерживается")
        
        else:
            raise ValueError("Конвертация между этими аппаратами не поддерживается")
    
    def calculate_relative_change(
        self,
        value_before: float,
        value_after: float
    ) -> float:
        """
        Расчет относительного изменения
        
        Args:
            value_before: Значение до лечения
            value_after: Значение после лечения
            
        Returns:
            Относительное изменение в процентах
        """
        if value_before == 0:
            return 0.0
        return ((value_after - value_before) / value_before) * 100
    
    def standardize_value(
        self,
        value: float,
        apparatus: EMGApparatus,
        muscle: MuscleType,
        condition: MeasurementCondition,
        mean: Optional[float] = None,
        std: Optional[float] = None
    ) -> float:
        """
        Стандартизация значения (z-score)
        
        Args:
            value: Исходное значение
            apparatus: Тип аппарата
            muscle: Тип мышцы
            condition: Условие измерения
            mean: Среднее значение (если None, используется контрольное)
            std: Стандартное отклонение (требуется для расчета)
            
        Returns:
            Стандартизированное значение (z-score)
        """
        if mean is None:
            if apparatus == EMGApparatus.SYNAPSYS:
                mean = self.CONTROL_VALUES_SYNAPSYS[condition][muscle]
            elif apparatus == EMGApparatus.KOLIBRI:
                mean = self.CONTROL_VALUES_KOLIBRI[condition][muscle]
            elif apparatus == EMGApparatus.BJOEMG2:
                mean = self.CONTROL_VALUES_BJOEMG2[condition][muscle]
            else:
                # Для неизвестных аппаратов используем Synapsys как fallback
                mean = self.CONTROL_VALUES_SYNAPSYS[condition][muscle]
        
        if std is None:
            # Использовать стандартное отклонение из литературных данных
            # Для Synapsys: ~6-9 мкВ, для Колибри: ~21-26 мкВ
            if apparatus == EMGApparatus.SYNAPSYS:
                std = 7.0  # примерное значение
            elif apparatus == EMGApparatus.KOLIBRI:
                std = 23.0  # примерное значение
            else:
                raise ValueError("Необходимо указать std для неизвестного аппарата")
        
        return (value - mean) / std


def create_emg_features(
    emg_data: Dict,
    normalizer: EMGNormalizer
) -> pd.DataFrame:
    """
    Создание признаков для ИИ-модели из ЭМГ-данных
    
    Args:
        emg_data: Словарь с ЭМГ-данными пациента
        normalizer: Объект нормализатора
        
    Returns:
        DataFrame с признаками
    """
    features = {}
    
    # Обработка аппарата с безопасной проверкой
    apparatus_str = emg_data.get('apparatus', 'Synapsys')
    try:
        apparatus = EMGApparatus(apparatus_str)
    except ValueError:
        # Если аппарат не найден в enum, пытаемся определить по подстроке
        apparatus_str_lower = apparatus_str.lower()
        if 'bjoemg' in apparatus_str_lower or 'biopak' in apparatus_str_lower:
            apparatus = EMGApparatus.BJOEMG2
        elif 'kolibri' in apparatus_str_lower or 'колибри' in apparatus_str_lower:
            apparatus = EMGApparatus.KOLIBRI
        elif 'synapsys' in apparatus_str_lower or 'синапсис' in apparatus_str_lower:
            apparatus = EMGApparatus.SYNAPSYS
        else:
            # По умолчанию используем Synapsys
            apparatus = EMGApparatus.SYNAPSYS
    
    # Исходные значения
    features['masseter_right_chewing_raw'] = emg_data.get('masseter_right_chewing', 0)
    features['masseter_left_chewing_raw'] = emg_data.get('masseter_left_chewing', 0)
    features['temporalis_right_chewing_raw'] = emg_data.get('temporalis_right_chewing', 0)
    features['temporalis_left_chewing_raw'] = emg_data.get('temporalis_left_chewing', 0)
    
    features['masseter_right_max_clench_raw'] = emg_data.get('masseter_right_max_clench', 0)
    features['masseter_left_max_clench_raw'] = emg_data.get('masseter_left_max_clench', 0)
    features['temporalis_right_max_clench_raw'] = emg_data.get('temporalis_right_max_clench', 0)
    features['temporalis_left_max_clench_raw'] = emg_data.get('temporalis_left_max_clench', 0)
    
    # Нормализованные значения (к контролю)
    for side in ['right', 'left']:
        for muscle_type in [MuscleType.MASSETER, MuscleType.TEMPORALIS]:
            muscle_name = muscle_type.value
            for condition in [MeasurementCondition.CHEWING, MeasurementCondition.MAX_CLENCH]:
                condition_name = 'chewing' if condition == MeasurementCondition.CHEWING else 'max_clench'
                key = f'{muscle_name}_{side}_{condition_name}'
                value = emg_data.get(key.replace('_', '_').replace('masseter', 'masseter'), 0)
                
                if value > 0:
                    normalized = normalizer.normalize_to_control(
                        value, apparatus, muscle_type, condition, side
                    )
                    features[f'{key}_normalized'] = normalized
    
    # Относительные изменения (если есть данные до и после)
    if 'before' in emg_data and 'after' in emg_data:
        for muscle_type in [MuscleType.MASSETER, MuscleType.TEMPORALIS]:
            for condition in [MeasurementCondition.CHEWING, MeasurementCondition.MAX_CLENCH]:
                # Расчет для правой и левой стороны
                pass  # Реализовать при необходимости
    
    # Симметрия (разница между правой и левой стороной)
    features['masseter_asymmetry_chewing'] = abs(
        features.get('masseter_right_chewing_raw', 0) - 
        features.get('masseter_left_chewing_raw', 0)
    )
    features['temporalis_asymmetry_chewing'] = abs(
        features.get('temporalis_right_chewing_raw', 0) - 
        features.get('temporalis_left_chewing_raw', 0)
    )
    
    # Тип аппарата (категориальный признак)
    features['apparatus_synapsys'] = 1 if apparatus == EMGApparatus.SYNAPSYS else 0
    features['apparatus_kolibri'] = 1 if apparatus == EMGApparatus.KOLIBRI else 0
    
    return pd.DataFrame([features])


# Пример использования
if __name__ == "__main__":
    # Инициализация нормализатора
    normalizer = EMGNormalizer(reference_apparatus=EMGApparatus.SYNAPSYS)
    
    # Пример данных пациента (Synapsys)
    patient_data = {
        'apparatus': 'Synapsys',
        'masseter_right_chewing': 350.5,
        'masseter_left_chewing': 339.25,
        'temporalis_right_chewing': 243.25,
        'temporalis_left_chewing': 234.8,
        'masseter_right_max_clench': 359.7,
        'masseter_left_max_clench': 351.25,
        'temporalis_right_max_clench': 274.8,
        'temporalis_left_max_clench': 248.45,
    }
    
    # Создание признаков
    features_df = create_emg_features(patient_data, normalizer)
    print("Признаки для ИИ-модели:")
    print(features_df)
    
    # Пример нормализации
    normalized_value = normalizer.normalize_to_control(
        350.5, EMGApparatus.SYNAPSYS, MuscleType.MASSETER, 
        MeasurementCondition.CHEWING
    )
    print(f"\nНормализованное значение: {normalized_value:.2f}% от нормы")

