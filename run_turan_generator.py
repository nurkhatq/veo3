#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TURAN Video Generator - CLI Runner
Скрипт для запуска генератора видео из командной строки с различными параметрами
"""

import argparse
import sys
import yaml
import json
from pathlib import Path
from main import TuranVideoGenerator, VideoGenerationConfig, VeoModel, AspectRatio, Resolution

def load_config(config_path: str = "config.yaml") -> dict:
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
    """Создание конфигурации на основе аргументов CLI и файла config.yaml"""
    
    # Получение настроек по умолчанию
    defaults = config_data.get('video_defaults', {})
    
    # Определение модели
    model_name = args.model or defaults.get('default_model', 'veo-3.0-generate-001')
    model_map = {
        'veo-2.0': VeoModel.VEO_2_GENERATE,
        'veo-2.0-exp': VeoModel.VEO_2_GENERATE_EXP,
        'veo-3.0': VeoModel.VEO_3_GENERATE,
        'veo-3.0-fast': VeoModel.VEO_3_FAST_GENERATE,
        'veo-3.0-preview': VeoModel.VEO_3_GENERATE_PREVIEW,
        'veo-3.0-fast-preview': VeoModel.VEO_3_FAST_GENERATE_PREVIEW,
    }
    
    model = model_map.get(model_name, VeoModel.VEO_3_GENERATE)
    
    # Определение соотношения сторон
    aspect_ratio = AspectRatio.PORTRAIT if args.portrait else AspectRatio.LANDSCAPE
    
    # Определение разрешения
    resolution = Resolution.HD if args.hd else Resolution.FULL_HD
    
    return VideoGenerationConfig(
        model=model,
        duration_seconds=args.duration or defaults.get('duration_seconds', 8),
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        sample_count=args.samples or defaults.get('sample_count', 1),
        generate_audio=not args.no_audio and defaults.get('generate_audio', True),
        enhance_prompt=not args.no_enhance and defaults.get('enhance_prompt', True),
        compression_quality=args.quality or defaults.get('compression_quality', 'optimized'),
        person_generation=defaults.get('person_generation', 'allow_adult'),
        seed=args.seed
    )

def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        description="🎬 TURAN Video Generator - Создание рекламных видео для мебели",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Базовое использование
  python run_turan_generator.py -i images/furniture -o output/videos

  # Быстрое превью
  python run_turan_generator.py -i images/furniture -o output/preview --preview

  # Instagram Stories (вертикальное видео)
  python run_turan_generator.py -i images/furniture -o output/instagram --portrait

  # Высокое качество для YouTube
  python run_turan_generator.py -i images/furniture -o output/youtube --model veo-3.0 --duration 8 --quality lossless

  # Пакетная обработка для всех соцсетей
  python run_turan_generator.py -i images/furniture -o output --batch-social-media
        """
    )
    
    # Основные параметры
    parser.add_argument('-i', '--input', 
                       help='Папка с изображениями мебели', 
                       default='images/furniture')
    
    parser.add_argument('-o', '--output', 
                       help='Папка для сохранения видео', 
                       default='output/videos')
    
    parser.add_argument('-c', '--config', 
                       help='Путь к файлу конфигурации', 
                       default='config.yaml')
    
    # Параметры видео
    parser.add_argument('--model', 
                       choices=['veo-2.0', 'veo-2.0-exp', 'veo-3.0', 'veo-3.0-fast', 
                               'veo-3.0-preview', 'veo-3.0-fast-preview'],
                       help='Модель Veo для генерации')
    
    parser.add_argument('--duration', type=int, 
                       choices=[4, 5, 6, 7, 8],
                       help='Длительность видео в секундах')
    
    parser.add_argument('--samples', type=int, 
                       choices=range(1, 5),
                       help='Количество вариантов видео для каждого изображения')
    
    parser.add_argument('--seed', type=int,
                       help='Seed для воспроизводимых результатов')
    
    # Форматы и качество
    parser.add_argument('--portrait', action='store_true',
                       help='Создать вертикальное видео (9:16) для Stories/TikTok')
    
    parser.add_argument('--hd', action='store_true',
                       help='Использовать 720p вместо 1080p')
    
    parser.add_argument('--quality', 
                       choices=['optimized', 'lossless'],
                       help='Качество сжатия видео')
    
    # Дополнительные опции
    parser.add_argument('--no-audio', action='store_true',
                       help='Отключить генерацию звука')
    
    parser.add_argument('--no-enhance', action='store_true',
                       help='Отключить улучшение промптов через Gemini')
    
    parser.add_argument('--preview', action='store_true',
                       help='Режим быстрого превью (4 сек, 720p, без звука)')
    
    parser.add_argument('--storage-uri',
                       help='URI Google Cloud Storage для сохранения (gs://bucket/path/)')
    
    # Специальные режимы
    parser.add_argument('--batch-social-media', action='store_true',
                       help='Создать видео для всех соцсетей (YouTube, Instagram, TikTok)')
    
    parser.add_argument('--single-image',
                       help='Обработать только одно изображение')
    
    parser.add_argument('--custom-prompt',
                       help='Кастомный промпт для генерации')
    
    # Утилиты
    parser.add_argument('--dry-run', action='store_true',
                       help='Показать что будет выполнено без реального запуска')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    
    args = parser.parse_args()
    
    # Загрузка конфигурации
    config_data = load_config(args.config)
    
    print("🎬 TURAN Video Generator")
    print("=" * 50)
    
    if args.verbose:
        print(f"📁 Входная папка: {args.input}")
        print(f"📁 Выходная папка: {args.output}")
        print(f"⚙️ Конфигурация: {args.config}")
        print("-" * 50)
    
    # Инициализация генератора
    try:
        generator = TuranVideoGenerator()
        print("✅ Генератор инициализирован успешно")
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        sys.exit(1)
    
    # Режим быстрого превью
    if args.preview:
        print("🚀 Режим быстрого превью")
        config = VideoGenerationConfig(
            model=VeoModel.VEO_3_FAST_GENERATE,
            duration_seconds=4,
            aspect_ratio=AspectRatio.LANDSCAPE,
            resolution=Resolution.HD,
            generate_audio=True,
            sample_count=1
        )
    else:
        config = create_config_from_args(args, config_data)
    
    if args.verbose:
        print(f"📹 Модель: {config.model.value}")
        print(f"⏱️ Длительность: {config.duration_seconds} сек")
        print(f"📐 Соотношение: {config.aspect_ratio.value}")
        print(f"🎯 Разрешение: {config.resolution.value}")
        print(f"🔊 Звук: {'Да' if config.generate_audio else 'Нет'}")
        print(f"📊 Количество: {config.sample_count}")
        print("-" * 50)
    
    # Dry run режим
    if args.dry_run:
        print("🔍 DRY RUN - показать план без выполнения:")
        
        if args.single_image:
            print(f"📷 Обработка изображения: {args.single_image}")
        else:
            input_path = Path(args.input)
            if input_path.exists():
                images = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png")) + list(input_path.glob("*.jpeg"))
                print(f"📷 Найдено изображений: {len(images)}")
                for img in images[:5]:  # Показать первые 5
                    print(f"  - {img.name}")
                if len(images) > 5:
                    print(f"  ... и еще {len(images) - 5}")
            else:
                print(f"❌ Папка {args.input} не найдена")
        
        print(f"💾 Результаты будут сохранены в: {args.output}")
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
            
            social_configs = generator.create_batch_config_for_social_media()
            platforms = ['youtube', 'instagram_stories', 'tiktok']
            
            for platform in platforms:
                platform_output = Path(args.output) / platform
                platform_output.mkdir(exist_ok=True)
                
                print(f"\n🎥 Создание видео для {platform.upper()}")
                
                # Выбор соответствующей конфигурации
                if platform == 'youtube':
                    platform_config = social_configs[0]  # Горизонтальное
                elif platform in ['instagram_stories', 'tiktok']:
                    platform_config = social_configs[1]  # Вертикальное
                
                results = generator.process_image_folder(
                    args.input,
                    str(platform_output),
                    platform_config,
                    storage_uri=args.storage_uri
                )
                
                # Статистика для платформы
                successful = sum(1 for r in results if r.get("status") == "success")
                print(f"✅ {platform}: {successful}/{len(results)} успешно")
        
        # Обработка одного изображения
        elif args.single_image:
            print(f"📷 Обработка изображения: {args.single_image}")
            
            operation_name = generator.generate_video_from_image(
                args.single_image,
                config,
                custom_prompt=args.custom_prompt,
                storage_uri=args.storage_uri
            )
            
            print("⏳ Ожидание завершения генерации...")
            result = generator.poll_operation_status(operation_name)
            
            if "response" in result:
                videos = result["response"].get("videos", [])
                print(f"✅ Создано видео: {len(videos)} файлов")
                
                for i, video in enumerate(videos):
                    if "gcsUri" in video:
                        print(f"☁️ GCS: {video['gcsUri']}")
                    elif "bytesBase64Encoded" in video:
                        filename = f"{Path(args.single_image).stem}_video_{i}.mp4"
                        output_path = Path(args.output) / filename
                        
                        import base64
                        video_data = base64.b64decode(video["bytesBase64Encoded"])
                        with open(output_path, 'wb') as f:
                            f.write(video_data)
                        
                        print(f"💾 Сохранено: {output_path}")
        
        # Обработка папки с изображениями
        else:
            print(f"📁 Обработка папки: {args.input}")
            
            results = generator.process_image_folder(
                args.input,
                args.output,
                config,
                storage_uri=args.storage_uri
            )
            
            # Сохранение подробного отчета
            report_path = Path(args.output) / "generation_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # Статистика
            successful = sum(1 for r in results if r.get("status") == "success")
            failed = len(results) - successful
            
            print(f"\n🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
            print(f"✅ Успешно: {successful}")
            print(f"❌ Ошибки: {failed}")
            print(f"📊 Всего: {len(results)}")
            print(f"📄 Отчет: {report_path}")
            
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