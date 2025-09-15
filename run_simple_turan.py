#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TURAN Simple Dressing Table Video Generator - Enhanced CLI Runner
Простой показ туалетных столиков с готовой русской озвучкой + Кинематографические улучшения
"""

import argparse
import sys
import yaml
import json
from pathlib import Path
from main import SimpleTuranGenerator, VideoGenerationConfig, VeoModel, AspectRatio, Resolution, CinematicStyle, LightingMood

def load_config(config_path: str = "simple_turan_config.yaml") -> dict:
    """Загрузка конфигурации из YAML файла"""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"⚠️ Файл конфигурации {config_path} не найден. Используются настройки по умолчанию.")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ Ошибка чтения конфигурации: {e}")
        sys.exit(1)

def create_config_from_args(args, config_data: dict) -> VideoGenerationConfig:
    """Создание конфигурации на основе аргументов CLI"""
    
    # Получение настроек по умолчанию
    defaults = config_data.get('video_defaults', {})
    enhanced_defaults = config_data.get('enhanced_settings', {})
    
    # Всегда используем VEO 3.0 и 8 секунд
    model = VeoModel.VEO_3_GENERATE
    duration = 8
    
    # Определение соотношения сторон
    aspect_ratio = AspectRatio.PORTRAIT if args.portrait else AspectRatio.LANDSCAPE
    
    # Определение разрешения
    resolution = Resolution.HD if args.hd else Resolution.FULL_HD
    
    # Кинематографические настройки
    cinematic_style_map = {
        'commercial': CinematicStyle.COMMERCIAL,
        'lifestyle': CinematicStyle.LIFESTYLE,
        'dramatic': CinematicStyle.DRAMATIC,
        'intimate': CinematicStyle.INTIMATE
    }
    
    lighting_mood_map = {
        'golden_hour': LightingMood.GOLDEN_HOUR,
        'morning_soft': LightingMood.MORNING_SOFT,
        'evening_warm': LightingMood.EVENING_WARM,
        'dramatic_contrast': LightingMood.DRAMATIC_CONTRAST,
        'natural_bright': LightingMood.NATURAL_BRIGHT
    }
    
    cinematic_style = cinematic_style_map.get(
        args.cinematic_style or enhanced_defaults.get('default_cinematic_style', 'commercial'),
        CinematicStyle.COMMERCIAL
    )
    
    lighting_mood = lighting_mood_map.get(
        args.lighting_mood or enhanced_defaults.get('default_lighting_mood', 'golden_hour'),
        LightingMood.GOLDEN_HOUR
    )
    
    return VideoGenerationConfig(
        model=model,
        duration_seconds=duration,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        sample_count=args.samples or defaults.get('sample_count', 1),
        generate_audio=not args.no_audio and defaults.get('generate_audio', True),
        enhance_prompt=not args.no_enhance and defaults.get('enhance_prompt', True),
        compression_quality=defaults.get('compression_quality', 'optimized'),
        person_generation=defaults.get('person_generation', 'allow_adult'),
        seed=args.seed,
        # Новые кинематографические параметры
        cinematic_style=cinematic_style,
        lighting_mood=lighting_mood,
        use_enhanced_prompts=not args.disable_enhanced and enhanced_defaults.get('enabled', True)
    )

def show_showcase_scenarios(generator: SimpleTuranGenerator):
    """Показать все доступные сценарии показа столиков"""
    print("🎥 Доступные кинематографические сценарии показа TURAN Lux:")
    print("=" * 70)
    
    scenarios = generator.get_all_scenarios()
    
    # Группировка по фокусам
    focus_groups = {}
    for scenario in scenarios:
        focus = scenario['focus']
        if focus not in focus_groups:
            focus_groups[focus] = []
        focus_groups[focus].append(scenario)
    
    # Эмодзи для фокусов
    focus_emojis = {
        'bedroom_setting': '🛏️',
        'morning_lighting': '🌅',
        'interior_design': '🏠',
        'evening_comfort': '🌆',
        'product_features': '✨',
        'family_lifestyle': '👨‍👩‍👧‍👦',
        'quality_premium': '💎',
        'daily_integration': '☀️',
        'space_efficiency': '📐',
        'brand_reliability': '🏆'
    }
    
    for focus, scenarios_list in focus_groups.items():
        emoji = focus_emojis.get(focus, '📝')
        print(f"\n{emoji} {focus.upper().replace('_', ' ')}")
        print("-" * 50)
        
        for scenario in scenarios_list:
            print(f"  🎬 ID: {scenario['id']}")
            print(f"     Стиль: {scenario.get('cinematic_style', 'Standard')}")
            print(f"     Освещение: {scenario.get('lighting_mood', 'Natural')}")
            print(f"     Озвучка: {scenario['russian_voiceover']}")
            print()

def show_enhancement_comparison():
    """Показать сравнение старых и новых промптов"""
    print("📊 СРАВНЕНИЕ ПРОМПТОВ - ДО И ПОСЛЕ УЛУЧШЕНИЙ:")
    print("=" * 70)
    
    print("\n❌ СТАРЫЙ ПРОМПТ (простой):")
    old_prompt = "Keep the dressing table exactly as shown in the image. Add: Elegant bedroom interior, warm morning light through window, camera slowly pans around the dressing table showing different angles, cozy atmosphere, soft lighting, modern home interior, 8-second elegant showcase"
    print(f"   {old_prompt}")
    print(f"   Длина: {len(old_prompt)} символов")
    
    print("\n✅ НОВЫЙ ПРОМПТ (кинематографический):")
    new_prompt = "Professional commercial shot on ARRI ALEXA 35 with 50mm Zeiss Master Prime lens. Keep the TURAN Lux dressing table exactly as shown in image - preserve white glass surface, 4 drawers, LED mirror, and metallic legs unchanged. Add: Elegant contemporary bedroom interior with warm oak flooring and floor-to-ceiling windows. Warm golden hour sunlight streaming through sheer curtains, creating ethereal atmosphere with dancing light particles and soft shadows highlighting the glass surface texture. Camera begins with wide establishing shot, then executes slow dolly movement forward with subtle downward tilt, ending in intimate close-up of LED mirror lighting. Audio: gentle morning ambiance, soft fabric sounds, warm contemporary piano score building subtly. Color palette: warm whites, brushed metallics, soft golden accents. Professional commercial cinematography. No subtitles."
    print(f"   {new_prompt[:200]}...")
    print(f"   Длина: {len(new_prompt)} символов")
    
    print(f"\n📈 УЛУЧШЕНИЯ:")
    print(f"   📐 Длина увеличена в {len(new_prompt) / len(old_prompt):.1f} раза")
    print(f"   🎥 Добавлены профессиональные камеры и объективы")
    print(f"   💡 Детальное описание освещения и атмосферы")
    print(f"   🎵 Интегрирован звуковой дизайн")
    print(f"   🎨 Определена цветовая палитра")
    print(f"   📱 Убраны субтитры и наложения")
    print(f"   🎬 Кинематографические движения камеры")

def main():
    """Главная функция CLI для улучшенного показа туалетных столиков"""
    parser = argparse.ArgumentParser(
        description="🪞 TURAN Enhanced Dressing Table Generator - Кинематографический показ с готовой озвучкой",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Базовое использование с улучшениями
  python run_simple_turan.py -i images/dressing_tables -o output/videos --enhanced

  # Коммерческий стиль с золотым освещением
  python run_simple_turan.py -i images/dressing_tables -o output/commercial \\
    --cinematic-style commercial --lighting-mood golden_hour

  # Lifestyle стиль для Instagram/TikTok
  python run_simple_turan.py -i images/dressing_tables -o output/instagram \\
    --portrait --cinematic-style lifestyle --lighting-mood morning_soft

  # Драматический стиль для премиум показа
  python run_simple_turan.py -i images/dressing_tables -o output/dramatic \\
    --cinematic-style dramatic --lighting-mood dramatic_contrast

  # Сравнение старых и новых промптов
  python run_simple_turan.py --compare-prompts

  # Показать все кинематографические сценарии
  python run_simple_turan.py --show-scenarios

  # A/B тестирование (старый vs новый подход)
  python run_simple_turan.py --single-image images/dressing_tables/столик.jpg \\
    -o output/ab_test --ab-test

  # Быстрое превью с улучшениями
  python run_simple_turan.py -i images/dressing_tables -o output/preview --hd --enhanced
        """
    )
    
    # Основные параметры
    parser.add_argument('-i', '--input', 
                       help='Папка с изображениями туалетных столиков', 
                       default='images/dressing_tables')
    
    parser.add_argument('-o', '--output', 
                       help='Папка для сохранения видео', 
                       default='output/dressing_table_enhanced')
    
    parser.add_argument('-c', '--config', 
                       help='Путь к файлу конфигурации', 
                       default='simple_turan_config.yaml')
    
    # Параметры видео
    parser.add_argument('--samples', type=int, 
                       choices=range(1, 4),
                       help='Количество вариантов видео для каждого изображения')
    
    parser.add_argument('--seed', type=int,
                       help='Seed для воспроизводимых результатов')
    
    # Форматы и качество
    parser.add_argument('--portrait', action='store_true',
                       help='Создать вертикальное видео (9:16) для Stories/TikTok')
    
    parser.add_argument('--hd', action='store_true',
                       help='Использовать 720p вместо 1080p (быстрее)')
    
    # НОВЫЕ КИНЕМАТОГРАФИЧЕСКИЕ ПАРАМЕТРЫ
    parser.add_argument('--cinematic-style', 
                       choices=['commercial', 'lifestyle', 'dramatic', 'intimate'],
                       help='Кинематографический стиль видео')
    
    parser.add_argument('--lighting-mood',
                       choices=['golden_hour', 'morning_soft', 'evening_warm', 'dramatic_contrast', 'natural_bright'],
                       help='Настроение освещения')
    
    parser.add_argument('--enhanced', action='store_true',
                       help='Включить все кинематографические улучшения (рекомендуется)')
    
    parser.add_argument('--disable-enhanced', action='store_true',
                       help='Отключить улучшенные промпты (использовать простые)')
    
    # Специальные режимы анализа
    parser.add_argument('--ab-test', action='store_true',
                       help='A/B тестирование: сравнить старые и новые промпты')
    
    parser.add_argument('--compare-prompts', action='store_true',
                       help='Показать сравнение старых и новых промптов')
    
    parser.add_argument('--export-analytics', action='store_true',
                       help='Экспортировать аналитику производительности')
    
    # Дополнительные опции
    parser.add_argument('--no-audio', action='store_true',
                       help='Отключить генерацию русской озвучки')
    
    parser.add_argument('--no-enhance', action='store_true',
                       help='Отключить улучшение промптов через Gemini')
    
    parser.add_argument('--storage-uri',
                       help='URI Google Cloud Storage для сохранения (gs://bucket/path/)')
    
    # Специальные режимы
    parser.add_argument('--batch-social-media', action='store_true',
                       help='Создать видео для всех соцсетей с оптимальными стилями')
    
    parser.add_argument('--single-image',
                       help='Обработать только одно изображение туалетного столика')
    
    parser.add_argument('--custom-prompt',
                       help='Кастомный промпт показа (на английском). Будет улучшен автоматически!')
    
    # Информационные команды
    parser.add_argument('--show-scenarios', action='store_true',
                       help='Показать все доступные кинематографические сценарии')
    
    # Утилиты
    parser.add_argument('--dry-run', action='store_true',
                       help='Показать что будет выполнено без реального запуска')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    
    args = parser.parse_args()
    
    # Информационные команды (выполняются без инициализации генератора)
    if args.compare_prompts:
        show_enhancement_comparison()
        return
    
    # Инициализация генератора
    try:
        generator = SimpleTuranGenerator()
    except Exception as e:
        if not args.show_scenarios:
            print(f"❌ Ошибка инициализации: {e}")
            sys.exit(1)
        else:
            print(f"⚠️ Ошибка инициализации, но показываем локальную информацию")
            generator = None
    
    # Информационные команды
    if args.show_scenarios:
        if generator:
            show_showcase_scenarios(generator)
        return
    
    # Загрузка конфигурации
    config_data = load_config(args.config)
    
    print("🪞 TURAN Enhanced Dressing Table Generator")
    print("Кинематографический показ столиков + Готовая русская озвучка")
    print("=" * 65)
    
    if args.verbose:
        print(f"📁 Входная папка: {args.input}")
        print(f"📁 Выходная папка: {args.output}")
        print(f"⚙️ Конфигурация: {args.config}")
        print("🎯 Модель: VEO 3.0 (фиксированная)")
        print("⏱️ Длительность: 8 секунд (фиксированная)")
        print("🔊 Озвучка: Готовые русские тексты")
        print("📸 Столик: Остается точно как на фото")
        enhancement_status = "ВКЛЮЧЕНЫ" if not args.disable_enhanced else "ОТКЛЮЧЕНЫ"
        print(f"🎬 Кинематографические улучшения: {enhancement_status}")
        if not args.disable_enhanced:
            print(f"🎥 Стиль: {args.cinematic_style or 'commercial'}")
            print(f"💡 Освещение: {args.lighting_mood or 'golden_hour'}")
        print("-" * 65)
    
    # Проверка инициализации генератора
    if not generator:
        print("❌ Генератор не инициализирован")
        sys.exit(1)
    
    print("✅ Улучшенный генератор показа туалетных столиков готов")
    
    # Создание конфигурации
    config = create_config_from_args(args, config_data)
    
    if args.verbose:
        print(f"📹 Модель: {config.model.value}")
        print(f"⏱️ Длительность: {config.duration_seconds} сек")
        print(f"📐 Соотношение: {config.aspect_ratio.value}")
        print(f"🎯 Разрешение: {config.resolution.value}")
        print(f"🔊 Русская озвучка: {'Да' if config.generate_audio else 'Нет'}")
        print(f"📊 Количество: {config.sample_count}")
        print(f"🎬 Кинематографический стиль: {config.cinematic_style.value}")
        print(f"💡 Настроение освещения: {config.lighting_mood.value}")
        print(f"✨ Улучшенные промпты: {'Да' if config.use_enhanced_prompts else 'Нет'}")
        
        # Показать примеры сценариев
        scenarios = generator.get_all_scenarios()
        print(f"🎥 Доступно кинематографических сценариев: {len(scenarios)}")
        print("Примеры улучшенных промптов:")
        for scenario in scenarios[:2]:
            print(f"  • {scenario['id']}: {scenario['russian_voiceover']}")
            print(f"    {scenario['enhanced_prompt'][:100]}...")
        print("-" * 65)
    
    # Dry run режим
    if args.dry_run:
        print("🔍 DRY RUN - план выполнения:")
        
        enhancement_note = " с кинематографическими улучшениями" if config.use_enhanced_prompts else " (простые промпты)"
        
        if args.single_image:
            print(f"📷 Обработка изображения: {args.single_image}")
            if args.custom_prompt:
                print(f"🎨 Кастомный промпт: {args.custom_prompt}")
                print("🎬 Промпт будет автоматически улучшен до кинематографического уровня!")
            else:
                scenarios = generator.get_all_scenarios()
                import random
                example_scenario = random.choice(scenarios)
                print(f"🎥 Пример сценария: {example_scenario['id']}")
                print(f"🎬 Стиль: {example_scenario.get('cinematic_style', 'Standard')}")
                print(f"🔊 Озвучка: {example_scenario['russian_voiceover']}")
            print(f"📸 Столик останется точно как на фото{enhancement_note}")
        else:
            input_path = Path(args.input)
            if input_path.exists():
                images = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png")) + list(input_path.glob("*.jpeg"))
                print(f"📷 Найдено изображений туалетных столиков: {len(images)}")
                for img in images[:3]:
                    print(f"  - {img.name}")
                if len(images) > 3:
                    print(f"  ... и еще {len(images) - 3}")
                
                scenarios = generator.get_all_scenarios()
                print(f"🎥 Каждое изображение получит случайный сценарий из {len(scenarios)} кинематографических")
                print(f"🎬 Сценарии включают профессиональные камеры, освещение и движения{enhancement_note}")
            else:
                print(f"❌ Папка {args.input} не найдена")
        
        print(f"💾 Результаты будут сохранены в: {args.output}")
        print(f"📄 JSON отчеты: enhanced_showcase_scenarios.json")
        if args.storage_uri:
            print(f"☁️ GCS URI: {args.storage_uri}")
        
        print("\n▶️ Для выполнения уберите флаг --dry-run")
        return
    
    # Создание выходной папки
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    try:
        # A/B тестирование
        if args.ab_test and args.single_image:
            print("🔬 A/B ТЕСТИРОВАНИЕ: Сравнение старых и новых промптов")
            
            # Создаем папки для сравнения
            ab_output = Path(args.output) / "ab_test"
            old_output = ab_output / "traditional_prompts"
            new_output = ab_output / "enhanced_prompts"
            old_output.mkdir(parents=True, exist_ok=True)
            new_output.mkdir(parents=True, exist_ok=True)
            
            # Тест со старыми промптами
            print("\n📹 Генерация с традиционными промптами...")
            config_old = config
            config_old.use_enhanced_prompts = False
            
            operation_old, scenario_old = generator.generate_video_from_image(
                args.single_image, config_old, custom_prompt=args.custom_prompt,
                storage_uri=f"{args.storage_uri}/traditional/" if args.storage_uri else None
            )
            
            # Тест с новыми промптами
            print("\n🎬 Генерация с кинематографическими промптами...")
            config_new = config
            config_new.use_enhanced_prompts = True
            
            operation_new, scenario_new = generator.generate_video_from_image(
                args.single_image, config_new, custom_prompt=args.custom_prompt,
                storage_uri=f"{args.storage_uri}/enhanced/" if args.storage_uri else None
            )
            
            print(f"\n📊 РЕЗУЛЬТАТЫ A/B ТЕСТИРОВАНИЯ:")
            print(f"📝 Традиционный сценарий: {scenario_old['id']}")
            print(f"🎬 Кинематографический сценарий: {scenario_new['id']}")
            print(f"⏳ Ожидайте завершения обеих генераций для сравнения...")
            
            # Дожидаемся результатов и сохраняем
            print("⏳ Ожидание завершения традиционной генерации...")
            result_old = generator.poll_operation_status(operation_old)
            
            print("⏳ Ожидание завершения кинематографической генерации...")
            result_new = generator.poll_operation_status(operation_new)
            
            print("✅ A/B тестирование завершено! Сравните результаты в папках.")
            return
        
        # Режим пакетной обработки для соцсетей
        if args.batch_social_media:
            print("📱 Режим пакетной обработки для социальных сетей с оптимальными стилями")
            
            social_configs = generator.create_social_media_configs()
            platforms = [
                ('youtube_facebook', 'Горизонтальное (YouTube/Facebook) - Commercial Style'),
                ('instagram_tiktok', 'Вертикальное (Instagram/TikTok) - Lifestyle Style')
            ]
            
            for i, (platform, description) in enumerate(platforms):
                platform_output = Path(args.output) / platform
                platform_output.mkdir(exist_ok=True)
                
                print(f"\n🎥 Создание видео: {description}")
                print(f"🎬 Стиль: {social_configs[i].cinematic_style.value}")
                print(f"💡 Освещение: {social_configs[i].lighting_mood.value}")
                
                results = generator.process_image_folder(
                    args.input,
                    str(platform_output),
                    social_configs[i],
                    storage_uri=args.storage_uri
                )
                
                successful = sum(1 for r in results if r.get("status") == "success")
                print(f"✅ {platform}: {successful}/{len(results)} успешно")
                
                # Показать использованные сценарии
                if args.verbose and successful > 0:
                    print("🎥 Использованные кинематографические сценарии:")
                    for result in results[:3]:  # Показать первые 3
                        if result.get("status") == "success" and "scenario" in result:
                            scenario = result["scenario"]
                            print(f"  • {scenario['id']}: {scenario['russian_voiceover'][:60]}...")
                            print(f"    Стиль: {scenario.get('cinematic_style', 'Standard')}")
        
        # Обработка одного изображения
        elif args.single_image:
            print(f"📷 Обработка изображения туалетного столика: {args.single_image}")
            
            operation_name, scenario = generator.generate_video_from_image(
                args.single_image,
                config,
                custom_prompt=args.custom_prompt,
                storage_uri=args.storage_uri
            )
            
            print(f"🎥 Выбранный кинематографический сценарий: {scenario['id']}")
            print(f"🎬 Стиль: {scenario.get('cinematic_style', 'Standard')}")
            print(f"💡 Освещение: {scenario.get('lighting_mood', 'Natural')}")
            print(f"🔊 Русская озвучка: {scenario['russian_voiceover']}")
            print(f"🎯 Фокус: {scenario['focus']}")
            
            print("⏳ Ожидание завершения генерации...")
            result = generator.poll_operation_status(operation_name)
            
            if "response" in result:
                videos = result["response"].get("videos", [])
                print(f"✅ Создано кинематографическое видео: {len(videos)} файлов")
                
                for i, video in enumerate(videos):
                    if "gcsUri" in video:
                        print(f"☁️ GCS: {video['gcsUri']}")
                    elif "bytesBase64Encoded" in video:
                        filename = f"turan_enhanced_{scenario['id']}_{Path(args.single_image).stem}_v{i}.mp4"
                        output_path = Path(args.output) / filename
                        
                        import base64
                        video_data = base64.b64decode(video["bytesBase64Encoded"])
                        with open(output_path, 'wb') as f:
                            f.write(video_data)
                        
                        print(f"💾 Сохранено: {output_path}")
        
        # Обработка папки с изображениями
        else:
            print(f"📁 Обработка папки с туалетными столиками: {args.input}")
            enhancement_note = " с кинематографическими улучшениями" if config.use_enhanced_prompts else ""
            print(f"🎬 Режим{enhancement_note}")
            
            results = generator.process_image_folder(
                args.input,
                args.output,
                config,
                storage_uri=args.storage_uri
            )
            
            # Сохранение подробного отчета
            report_path = Path(args.output) / "enhanced_showcase_generation_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # Экспорт аналитики если запрошено
            if args.export_analytics:
                generator.export_performance_report()
            
            # Статистика
            successful = sum(1 for r in results if r.get("status") == "success")
            failed = len(results) - successful
            
            print(f"\n🎉 КИНЕМАТОГРАФИЧЕСКАЯ ГЕНЕРАЦИЯ ВИДЕО ЗАВЕРШЕНА!")
            print(f"✅ Успешно: {successful}")
            print(f"❌ Ошибки: {failed}")
            print(f"📊 Всего: {len(results)}")
            print(f"📄 Отчет: {report_path}")
            print(f"🎥 Сценарии: generated_showcase_scenarios.json")
            
            # Показать статистику улучшений
            if args.verbose:
                analytics = generator.get_generation_analytics()
                print(f"\n📊 СТАТИСТИКА КИНЕМАТОГРАФИЧЕСКИХ УЛУЧШЕНИЙ:")
                print(f"   🎬 Улучшенных промптов: {analytics['enhancement_usage_percentage']:.1f}%")
                print(f"   📝 Традиционных промптов: {analytics['traditional_usage_percentage']:.1f}%")
                
                scenario_usage = {}
                for result in results:
                    if result.get("status") == "success" and "scenario" in result:
                        scenario_id = result["scenario"]["id"]
                        scenario_style = result.get("cinematic_style", "Standard")
                        key = f"{scenario_id} ({scenario_style})"
                        scenario_usage[key] = scenario_usage.get(key, 0) + 1
                
                print(f"\n🎥 Использованные кинематографические сценарии:")
                for scenario_key, count in sorted(scenario_usage.items())[:5]:
                    print(f"  • {scenario_key}: {count} раз")
            
            if failed > 0:
                print(f"\n❌ Изображения с ошибками:")
                for result in results:
                    if result.get("status") == "error":
                        print(f"  - {result['source_image']}: {result.get('error', 'Unknown error')}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Операция прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()