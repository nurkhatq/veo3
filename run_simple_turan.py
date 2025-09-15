#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TURAN Simple Dressing Table Video Generator - CLI Runner
Простой показ туалетных столиков с готовой русской озвучкой
"""

import argparse
import sys
import yaml
import json
from pathlib import Path
from main import SimpleTuranGenerator, VideoGenerationConfig, VeoModel, AspectRatio, Resolution

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
    
    # Всегда используем VEO 3.0 и 8 секунд
    model = VeoModel.VEO_3_GENERATE
    duration = 8
    
    # Определение соотношения сторон
    aspect_ratio = AspectRatio.PORTRAIT if args.portrait else AspectRatio.LANDSCAPE
    
    # Определение разрешения
    resolution = Resolution.HD if args.hd else Resolution.FULL_HD
    
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
        seed=args.seed
    )

def show_showcase_scenarios(generator: SimpleTuranGenerator):
    """Показать все доступные сценарии показа столиков"""
    print("🎥 Доступные сценарии показа туалетных столиков TURAN Lux:")
    print("=" * 65)
    
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
        print("-" * 45)
        
        for scenario in scenarios_list:
            print(f"  🎬 ID: {scenario['id']}")
            print(f"     Озвучка: {scenario['russian_voiceover']}")
            print()

def main():
    """Главная функция CLI для простого показа туалетных столиков"""
    parser = argparse.ArgumentParser(
        description="🪞 TURAN Simple Dressing Table Generator - Простой показ с готовой озвучкой",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Базовое использование - показ столиков в уютной обстановке
  python run_simple_turan.py -i images/dressing_tables -o output/videos

  # Быстрое превью
  python run_simple_turan.py -i images/dressing_tables -o output/preview --hd

  # Вертикальное для Instagram/TikTok
  python run_simple_turan.py -i images/dressing_tables -o output/instagram --portrait

  # Обработка одного изображения
  python run_simple_turan.py --single-image images/dressing_tables/столик.jpg -o output/single

  # Показать все сценарии показа
  python run_simple_turan.py --show-scenarios

  # Кастомный промпт для показа (столик остается неизменным)
  python run_simple_turan.py \
    --single-image images/dressing_tables/столик.jpg \
    --custom-prompt "Camera moves smoothly around furniture in cozy bedroom" \
    -o output/custom
        """
    )
    
    # Основные параметры
    parser.add_argument('-i', '--input', 
                       help='Папка с изображениями туалетных столиков', 
                       default='images/dressing_tables')
    
    parser.add_argument('-o', '--output', 
                       help='Папка для сохранения видео', 
                       default='output/dressing_table_showcase')
    
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
    
    # Дополнительные опции
    parser.add_argument('--no-audio', action='store_true',
                       help='Отключить генерацию русской озвучки')
    
    parser.add_argument('--no-enhance', action='store_true',
                       help='Отключить улучшение промптов через Gemini')
    
    parser.add_argument('--storage-uri',
                       help='URI Google Cloud Storage для сохранения (gs://bucket/path/)')
    
    # Специальные режимы
    parser.add_argument('--batch-social-media', action='store_true',
                       help='Создать видео для всех соцсетей (горизонтальное + вертикальное)')
    
    parser.add_argument('--single-image',
                       help='Обработать только одно изображение туалетного столика')
    
    parser.add_argument('--custom-prompt',
                       help='Кастомный промпт показа (на английском). Столик останется неизменным!')
    
    # Информационные команды
    parser.add_argument('--show-scenarios', action='store_true',
                       help='Показать все доступные сценарии показа')
    
    # Утилиты
    parser.add_argument('--dry-run', action='store_true',
                       help='Показать что будет выполнено без реального запуска')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    
    args = parser.parse_args()
    
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
    
    print("🪞 TURAN Simple Dressing Table Generator")
    print("Простой показ столиков + Готовая русская озвучка")
    print("=" * 55)
    
    if args.verbose:
        print(f"📁 Входная папка: {args.input}")
        print(f"📁 Выходная папка: {args.output}")
        print(f"⚙️ Конфигурация: {args.config}")
        print("🎯 Модель: VEO 3.0 (фиксированная)")
        print("⏱️ Длительность: 8 секунд (фиксированная)")
        print("🔊 Озвучка: Готовые русские тексты")
        print("📸 Столик: Остается точно как на фото")
        print("🎥 Режим: Показ в уютной обстановке")
        print("-" * 55)
    
    # Проверка инициализации генератора
    if not generator:
        print("❌ Генератор не инициализирован")
        sys.exit(1)
    
    print("✅ Простой генератор показа туалетных столиков готов")
    
    # Создание конфигурации
    config = create_config_from_args(args, config_data)
    
    if args.verbose:
        print(f"📹 Модель: {config.model.value}")
        print(f"⏱️ Длительность: {config.duration_seconds} сек")
        print(f"📐 Соотношение: {config.aspect_ratio.value}")
        print(f"🎯 Разрешение: {config.resolution.value}")
        print(f"🔊 Русская озвучка: {'Да' if config.generate_audio else 'Нет'}")
        print(f"📊 Количество: {config.sample_count}")
        
        # Показать примеры сценариев
        scenarios = generator.get_all_scenarios()
        print(f"🎥 Доступно сценариев показа: {len(scenarios)}")
        print("Примеры озвучки:")
        for scenario in scenarios[:2]:
            print(f"  • {scenario['russian_voiceover']}")
        print("-" * 55)
    
    # Dry run режим
    if args.dry_run:
        print("🔍 DRY RUN - план выполнения:")
        
        if args.single_image:
            print(f"📷 Обработка изображения: {args.single_image}")
            if args.custom_prompt:
                print(f"🎨 Кастомный промпт: {args.custom_prompt}")
                print("📸 Столик останется точно как на фото!")
            else:
                scenarios = generator.get_all_scenarios()
                import random
                example_scenario = random.choice(scenarios)
                print(f"🎥 Пример сценария: {example_scenario['id']}")
                print(f"🔊 Озвучка: {example_scenario['russian_voiceover']}")
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
                print(f"🎥 Каждое изображение получит случайный сценарий из {len(scenarios)} доступных")
                print("🎬 Сценарии фокусируются на уютном показе столика с разных ракурсов")
            else:
                print(f"❌ Папка {args.input} не найдена")
        
        print(f"💾 Результаты будут сохранены в: {args.output}")
        print(f"📄 JSON отчеты: generated_showcase_scenarios.json")
        if args.storage_uri:
            print(f"☁️ GCS URI: {args.storage_uri}")
        
        print("\n▶️ Для выполнения уберите флаг --dry-run")
        return
    
    # Создание выходной папки
    Path(args.output).mkdir(parents=True, exist_ok=True)
    
    try:
        # Режим пакетной обработки для соцсетей
        if args.batch_social_media:
            print("📱 Режим пакетной обработки для социальных сетей")
            
            social_configs = generator.create_social_media_configs()
            platforms = [
                ('youtube_facebook', 'Горизонтальное (YouTube/Facebook)'),
                ('instagram_tiktok', 'Вертикальное (Instagram/TikTok)')
            ]
            
            for i, (platform, description) in enumerate(platforms):
                platform_output = Path(args.output) / platform
                platform_output.mkdir(exist_ok=True)
                
                print(f"\n🎥 Создание видео: {description}")
                
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
                    print("🎥 Использованные сценарии показа:")
                    for result in results[:3]:  # Показать первые 3
                        if result.get("status") == "success" and "scenario" in result:
                            scenario = result["scenario"]
                            print(f"  • {scenario['id']}: {scenario['russian_voiceover'][:60]}...")
        
        # Обработка одного изображения
        elif args.single_image:
            print(f"📷 Обработка изображения туалетного столика: {args.single_image}")
            
            operation_name, scenario = generator.generate_video_from_image(
                args.single_image,
                config,
                custom_prompt=args.custom_prompt,
                storage_uri=args.storage_uri
            )
            
            print(f"🎥 Выбранный сценарий показа: {scenario['id']}")
            print(f"🔊 Русская озвучка: {scenario['russian_voiceover']}")
            print(f"🎬 Фокус: {scenario['focus']}")
            
            print("⏳ Ожидание завершения генерации...")
            result = generator.poll_operation_status(operation_name)
            
            if "response" in result:
                videos = result["response"].get("videos", [])
                print(f"✅ Создано видео показа: {len(videos)} файлов")
                
                for i, video in enumerate(videos):
                    if "gcsUri" in video:
                        print(f"☁️ GCS: {video['gcsUri']}")
                    elif "bytesBase64Encoded" in video:
                        filename = f"turan_{scenario['id']}_{Path(args.single_image).stem}_v{i}.mp4"
                        output_path = Path(args.output) / filename
                        
                        import base64
                        video_data = base64.b64decode(video["bytesBase64Encoded"])
                        with open(output_path, 'wb') as f:
                            f.write(video_data)
                        
                        print(f"💾 Сохранено: {output_path}")
        
        # Обработка папки с изображениями
        else:
            print(f"📁 Обработка папки с туалетными столиками: {args.input}")
            
            results = generator.process_image_folder(
                args.input,
                args.output,
                config,
                storage_uri=args.storage_uri
            )
            
            # Сохранение подробного отчета
            report_path = Path(args.output) / "showcase_generation_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # Статистика
            successful = sum(1 for r in results if r.get("status") == "success")
            failed = len(results) - successful
            
            print(f"\n🎉 ГЕНЕРАЦИЯ ВИДЕО ПОКАЗА ЗАВЕРШЕНА!")
            print(f"✅ Успешно: {successful}")
            print(f"❌ Ошибки: {failed}")
            print(f"📊 Всего: {len(results)}")
            print(f"📄 Отчет: {report_path}")
            print(f"🎥 Сценарии показа: generated_showcase_scenarios.json")
            
            # Показать статистику по сценариям
            if successful > 0 and args.verbose:
                scenario_usage = {}
                for result in results:
                    if result.get("status") == "success" and "scenario" in result:
                        scenario_id = result["scenario"]["id"]
                        scenario_usage[scenario_id] = scenario_usage.get(scenario_id, 0) + 1
                
                print(f"\n🎥 Использованные сценарии показа:")
                for scenario_id, count in sorted(scenario_usage.items()):
                    print(f"  • {scenario_id}: {count} раз")
            
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