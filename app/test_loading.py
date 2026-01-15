#!/usr/bin/env python3
"""
Тестовый скрипт для проверки загрузки статей и обучения модели
"""
import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

print("=" * 70)
print("🚀 ПОЛНАЯ ПРОВЕРКА СИСТЕМЫ ЗАГРУЗКИ И ОБУЧЕНИЯ")
print("=" * 70)

try:
    # 1. Импорт модулей
    print("\n1️⃣ Импорт модулей...")
    from knowledge_extractor import KnowledgeExtractor
    from preloaded_articles import get_preloaded_articles
    from clinical_articles_data import get_clinical_articles, get_emg_composite_pairs
    from model_trainer import EMGCompositePair, CompositeModelTrainer
    print("   ✅ Все модули импортированы")
    
    # 2. Загрузка статей
    print("\n2️⃣ Загрузка статей в KnowledgeExtractor...")
    extractor = KnowledgeExtractor()
    
    # Предзагруженные
    preloaded = get_preloaded_articles()
    for art in preloaded:
        extractor.add_article(**art)
        extractor.process_article(extractor.articles[-1])
    print(f"   ✅ Предзагруженных: {len(preloaded)}")
    
    # Клинические
    clinical = get_clinical_articles()
    for art in clinical:
        extractor.add_article(**art)
        extractor.process_article(extractor.articles[-1])
    print(f"   ✅ Клинических: {len(clinical)}")
    print(f"   ✅ Всего статей: {len(extractor.articles)}")
    
    # 3. Извлечение знаний
    print("\n3️⃣ Извлечение знаний из статей...")
    kb = extractor.get_knowledge_base()
    print(f"   ✅ Рекомендаций по композитам: {len(kb['composite_recommendations'])}")
    print(f"   ✅ ЭМГ-показателей: {len(kb['emg_guidelines'])}")
    print(f"   ✅ Клинических критериев: {len(kb['clinical_criteria'])}")
    
    # 4. Загрузка пар ЭМГ→композит
    print("\n4️⃣ Загрузка пар ЭМГ→композит...")
    pairs_data = get_emg_composite_pairs()
    pairs = [EMGCompositePair(**p) for p in pairs_data]
    pairs_with_comp = [p for p in pairs if p.composite_name]
    
    print(f"   ✅ Всего пар: {len(pairs)}")
    print(f"   ✅ С композитами: {len(pairs_with_comp)}")
    
    if pairs_with_comp:
        print("\n   📋 Примеры пар:")
        for i, p in enumerate(pairs_with_comp[:3], 1):
            print(f"      {i}. Композит: {p.composite_name}")
            print(f"         ЭМГ жевательная правая: {p.masseter_right_chewing} мкВ")
            print(f"         Источник: {p.source_article[:50]}...")
    
    # 5. Обучение модели
    print("\n5️⃣ Обучение модели...")
    if len(pairs_with_comp) >= 2:
        trainer = CompositeModelTrainer()
        results = trainer.train(pairs_with_comp, model_type='random_forest')
        
        print(f"   ✅ Модель обучена успешно!")
        print(f"   ✅ Тип: {results['model_type']}")
        print(f"   ✅ Примеров: {results['train_size']}")
        print(f"   ✅ Тестовых: {results['test_size']}")
        print(f"   ✅ Композитов: {results['unique_composites']}")
        if results.get('accuracy'):
            print(f"   ✅ Точность: {results['accuracy']:.1%}")
        
        # 6. Тест предсказания
        print("\n6️⃣ Тест предсказания модели...")
        test_cases = [
            {
                'name': 'Пациент с патологической стираемостью',
                'data': {
                    'masseter_right_chewing': 313.42,
                    'masseter_left_chewing': 226.69,
                    'temporalis_right_chewing': 260.0,
                    'temporalis_left_chewing': 250.0,
                    'masseter_right_max_clench': 350.0,
                    'masseter_left_max_clench': 340.0,
                    'temporalis_right_max_clench': 280.0,
                    'temporalis_left_max_clench': 270.0,
                    'age': 40,
                    'mvc_hyperfunction_percent': 2.0
                }
            },
            {
                'name': 'Молодой пациент, легкая стираемость',
                'data': {
                    'masseter_right_chewing': 330.0,
                    'masseter_left_chewing': 310.0,
                    'temporalis_right_chewing': 245.0,
                    'temporalis_left_chewing': 235.0,
                    'masseter_right_max_clench': 365.0,
                    'masseter_left_max_clench': 355.0,
                    'temporalis_right_max_clench': 285.0,
                    'temporalis_left_max_clench': 275.0,
                    'age': 28,
                    'mvc_hyperfunction_percent': 3.0
                }
            }
        ]
        
        for test in test_cases:
            pred, conf = trainer.predict(test['data'])
            print(f"   📊 {test['name']}:")
            print(f"      → Композит: {pred}")
            print(f"      → Уверенность: {conf:.1%}")
        
        # Сохранение
        trainer.save_model("trained_model.pkl")
        print(f"\n   💾 Модель сохранена: trained_model.pkl")
        
    else:
        print(f"   ❌ Недостаточно данных: {len(pairs_with_comp)} пар (нужно минимум 2)")
    
    # Итоги
    print("\n" + "=" * 70)
    print("✅ ВСЕ СИСТЕМЫ РАБОТАЮТ КОРРЕКТНО!")
    print("=" * 70)
    print(f"📚 Статей загружено: {len(extractor.articles)}")
    print(f"📊 Пар ЭМГ→композит: {len(pairs)} (с композитами: {len(pairs_with_comp)})")
    print(f"🤖 Модель: {'✅ Обучена' if len(pairs_with_comp) >= 2 else '❌ Не обучена'}")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

