"""
Примеры использования программы выбора композита
"""

from composite_selector import CompositeSelector, PatientData


def example_1_basic():
    """Пример 1: Базовое использование"""
    print("=" * 60)
    print("Пример 1: Базовое использование")
    print("=" * 60)
    
    selector = CompositeSelector()
    
    # Данные пациента с аномалией прикуса
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
        occlusion_anomaly_type="аномалия прикуса"
    )
    
    results = selector.select_composite(patient, top_n=3)
    
    print(f"\nНайдено {len(results)} рекомендаций:\n")
    for i, (composite, score, justification) in enumerate(results, 1):
        print(f"{i}. {composite['name']} (оценка: {score:.3f})")
        print(f"   Микротвердость: {composite['microhardness_KHN']:.1f} KHN")
        print(f"   Усадка: {composite['polymerization_shrinkage_percent']:.2f}%")
        print()


def example_2_with_wear_severity():
    """Пример 2: Пациент с патологической стираемостью"""
    print("=" * 60)
    print("Пример 2: Пациент с патологической стираемостью")
    print("=" * 60)
    
    selector = CompositeSelector()
    
    # Данные пациента с гиперфункцией (средняя/тяжелая стираемость)
    patient = PatientData(
        apparatus="Synapsys",
        masseter_right_chewing=380.0,  # повышенные значения
        masseter_left_chewing=370.0,
        temporalis_right_chewing=260.0,
        temporalis_left_chewing=250.0,
        masseter_right_max_clench=400.0,
        masseter_left_max_clench=390.0,
        temporalis_right_max_clench=300.0,
        temporalis_left_max_clench=280.0,
        occlusion_anomaly_type="аномалия прикуса",
        mvc_hyperfunction_percent=25.0,
        mvc_duration_sec_per_min=5.0  # 4-6 сек/мин = средняя/тяжелая
    )
    
    results = selector.select_composite(patient, top_n=3)
    
    print(f"\nНайдено {len(results)} рекомендаций:\n")
    for i, (composite, score, justification) in enumerate(results, 1):
        print(f"{i}. {composite['name']} (оценка: {score:.3f})")
        print(f"   Обоснование:")
        for reason in justification['reasons']:
            print(f"     - {reason}")
        print()


def example_3_kolibri_apparatus():
    """Пример 3: Данные с аппарата Колибри"""
    print("=" * 60)
    print("Пример 3: Данные с аппарата Колибри")
    print("=" * 60)
    
    selector = CompositeSelector()
    
    # Данные с аппарата Колибри (нормализация происходит автоматически)
    patient = PatientData(
        apparatus="Kolibri",
        masseter_right_chewing=111.0,  # значения Колибри
        masseter_left_chewing=111.0,
        temporalis_right_chewing=138.0,
        temporalis_left_chewing=138.0,
        masseter_right_max_clench=278.0,
        masseter_left_max_clench=278.0,
        temporalis_right_max_clench=558.0,
        temporalis_left_max_clench=558.0,
        occlusion_anomaly_type="аномалия прикуса"
    )
    
    results = selector.select_composite(patient, top_n=3)
    
    print(f"\nНайдено {len(results)} рекомендаций:\n")
    for i, (composite, score, justification) in enumerate(results, 1):
        print(f"{i}. {composite['name']} (оценка: {score:.3f})")
        print(f"   Категория: {composite['category']}")
        print(f"   Износостойкость: {composite['wear_resistance']}")
        print()


def example_4_comparison():
    """Пример 4: Сравнение разных пациентов"""
    print("=" * 60)
    print("Пример 4: Сравнение рекомендаций для разных пациентов")
    print("=" * 60)
    
    selector = CompositeSelector()
    
    # Пациент 1: Легкая стираемость
    patient1 = PatientData(
        apparatus="Synapsys",
        masseter_right_chewing=350.0,
        masseter_left_chewing=340.0,
        temporalis_right_chewing=240.0,
        temporalis_left_chewing=235.0,
        masseter_right_max_clench=360.0,
        masseter_left_max_clench=350.0,
        temporalis_right_max_clench=270.0,
        temporalis_left_max_clench=250.0,
        mvc_hyperfunction_percent=22.0,
        mvc_duration_sec_per_min=1.5  # легкая
    )
    
    # Пациент 2: Тяжелая стираемость
    patient2 = PatientData(
        apparatus="Synapsys",
        masseter_right_chewing=400.0,  # повышенные
        masseter_left_chewing=390.0,
        temporalis_right_chewing=280.0,
        temporalis_left_chewing=270.0,
        masseter_right_max_clench=420.0,
        masseter_left_max_clench=410.0,
        temporalis_right_max_clench=320.0,
        temporalis_left_max_clench=300.0,
        mvc_hyperfunction_percent=30.0,
        mvc_duration_sec_per_min=5.5  # тяжелая
    )
    
    print("\nПациент 1 (легкая стираемость):")
    results1 = selector.select_composite(patient1, top_n=2)
    for i, (composite, score, _) in enumerate(results1, 1):
        print(f"  {i}. {composite['name']} (оценка: {score:.3f})")
    
    print("\nПациент 2 (тяжелая стираемость):")
    results2 = selector.select_composite(patient2, top_n=2)
    for i, (composite, score, _) in enumerate(results2, 1):
        print(f"  {i}. {composite['name']} (оценка: {score:.3f})")
    
    print("\nВывод: Для тяжелой стираемости выбираются более прочные материалы")
    print()


if __name__ == "__main__":
    # Запуск всех примеров
    example_1_basic()
    print("\n")
    
    example_2_with_wear_severity()
    print("\n")
    
    example_3_kolibri_apparatus()
    print("\n")
    
    example_4_comparison()

