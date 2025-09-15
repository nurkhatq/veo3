#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TURAN Dressing Table Video Generator - Простая версия
Показ туалетных столиков в уютной обстановке с готовой русской озвучкой
"""

import os
import json
import time
import base64
import requests
import logging
from typing import List, Dict, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import mimetypes
from google.auth import default
from google.auth.transport.requests import Request

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('turan_simple_generator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VeoModel(Enum):
    """Только VEO 3.0 модель"""
    VEO_3_GENERATE = "veo-3.0-generate-001"

class AspectRatio(Enum):
    """Соотношения сторон для видео"""
    LANDSCAPE = "16:9"  # Горизонтальное для YouTube, Facebook
    PORTRAIT = "9:16"   # Вертикальное для TikTok, Instagram Stories

class Resolution(Enum):
    """Разрешения видео"""
    HD = "720p"
    FULL_HD = "1080p"

@dataclass
class VideoGenerationConfig:
    """Конфигурация генерации видео для туалетных столиков"""
    model: VeoModel = VeoModel.VEO_3_GENERATE
    duration_seconds: int = 8  # Всегда 8 секунд
    aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE
    resolution: Resolution = Resolution.FULL_HD
    sample_count: int = 1
    generate_audio: bool = True
    enhance_prompt: bool = True
    compression_quality: str = "optimized"
    person_generation: str = "allow_adult"
    seed: Optional[int] = None

class SimpleTuranGenerator:
    """Простой генератор видео туалетных столиков TURAN с готовой озвучкой"""
    
    def __init__(self, project_id: str = "turantt", location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.base_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models"
        
        # Настройка аутентификации
        self.credentials = None
        self._setup_authentication()
        
        # Простые сценарии показа столика с готовой озвучкой
        self.showcase_scenarios = [
            {
                "id": "cozy_bedroom_view",
                "english_prompt": "Keep the dressing table exactly as shown in the image. Add: Elegant bedroom interior, warm morning light through window, camera slowly pans around the dressing table showing different angles, cozy atmosphere, soft lighting, modern home interior, 8-second elegant showcase",
                "russian_voiceover": "Туалетный столик TURAN Lux - идеальное решение для вашей спальни. Стильный дизайн и функциональность в одном.",
                "focus": "bedroom_setting"
            },
            {
                "id": "morning_light_showcase",
                "english_prompt": "Preserve the dressing table from image unchanged. Add: Beautiful morning sunlight illuminating the dressing table, camera moves in smooth arc around the furniture, highlighting glass surface and LED mirror, warm cozy home atmosphere, 8-second gentle movement",
                "russian_voiceover": "Начните утро с красоты! Столик TURAN с LED-подсветкой и стеклянной столешницей - ваш ежедневный помощник.",
                "focus": "morning_lighting"
            },
            {
                "id": "modern_interior_tour",
                "english_prompt": "Keep dressing table design identical to image. Add: Modern stylish bedroom, camera touring around the dressing table from multiple angles, showcasing contemporary interior design, comfortable home setting, soft ambient lighting, 8-second smooth camera movement",
                "russian_voiceover": "TURAN Lux гармонично впишется в любой современный интерьер. Качество и стиль для вашего дома.",
                "focus": "interior_design"
            },
            {
                "id": "evening_ambiance",
                "english_prompt": "Maintain dressing table appearance from image. Add: Cozy evening atmosphere, warm lamplight, camera gently circles the dressing table, showing comfortable bedroom setting, relaxing home environment, soft shadows, 8-second peaceful showcase",
                "russian_voiceover": "Вечерний уют с туалетным столиком TURAN. Расслабьтесь и наслаждайтесь моментами красоты каждый день.",
                "focus": "evening_comfort"
            },
            {
                "id": "feature_highlight",
                "english_prompt": "Keep the dressing table exactly as in image. Add: Close-up shots transitioning to wide angle, highlighting 4 drawers, LED mirror lighting, glass surface details, premium furniture quality, modern home interior, 8-second detailed showcase",
                "russian_voiceover": "4 вместительных ящика, зеркало с LED-подсветкой, стеклянная столешница. TURAN Lux - продуманно до мелочей.",
                "focus": "product_features"
            },
            {
                "id": "lifestyle_comfort",
                "english_prompt": "Preserve dressing table unchanged from image. Add: Comfortable family home atmosphere, natural daylight, camera smoothly moves showing the dressing table in lived-in bedroom space, cozy lifestyle setting, 8-second warm presentation",
                "russian_voiceover": "Сделайте свой дом уютнее с мебелью TURAN. Качество, которому доверяют тысячи семей в Казахстане.",
                "focus": "family_lifestyle"
            },
            {
                "id": "premium_quality",
                "english_prompt": "Keep dressing table design from image intact. Add: Luxury bedroom setting, elegant camera movement showcasing the furniture's premium build quality, sophisticated home interior, refined lighting, 8-second quality demonstration",
                "russian_voiceover": "Премиум качество по доступной цене. Туалетный столик TURAN Lux - инвестиция в ваш комфорт на годы.",
                "focus": "quality_premium"
            },
            {
                "id": "daily_routine",
                "english_prompt": "Maintain the dressing table appearance unchanged. Add: Peaceful morning bedroom scene, camera flows around the dressing table showing how it fits into daily life, comfortable home routine setting, 8-second lifestyle integration",
                "russian_voiceover": "Каждое утро начинается с вас. Туалетный столик TURAN - ваш персональный уголок красоты и вдохновения.",
                "focus": "daily_integration"
            },
            {
                "id": "space_solution", 
                "english_prompt": "Keep dressing table identical to image shown. Add: Smart bedroom layout, camera demonstrates how the dressing table optimizes space, organized storage solutions visible, efficient home design, 8-second space showcase",
                "russian_voiceover": "Умное использование пространства с TURAN Lux. Стиль, функциональность и порядок в вашей спальне.",
                "focus": "space_efficiency"
            },
            {
                "id": "brand_trust",
                "english_prompt": "Preserve original dressing table design from image. Add: Reliable home furniture setting, stable and trustworthy appearance, quality family home environment, dependable furniture showcase, 8-second trust building",
                "russian_voiceover": "TURAN - казахстанский бренд, которому доверяют. Надежная мебель для вашего дома уже более 10 лет.",
                "focus": "brand_reliability"
            }
        ]
    
    def _setup_authentication(self):
        """Настройка аутентификации Google Cloud"""
        try:
            credentials, project = default()
            credentials.refresh(Request())
            self.credentials = credentials
            logger.info(f"Аутентификация успешна для проекта: {project}")
        except Exception as e:
            logger.error(f"Ошибка аутентификации: {e}")
            logger.info("Убедитесь, что выполнена команда: gcloud auth application-default login")
            raise
    
    def _get_auth_token(self) -> str:
        """Получение токена доступа"""
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        return self.credentials.token
    
    def _encode_image_to_base64(self, image_path: str) -> tuple[str, str]:
        """Кодирование изображения в base64"""
        try:
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            mime_type, _ = mimetypes.guess_type(image_path)
            if mime_type not in ['image/jpeg', 'image/png']:
                raise ValueError(f"Неподдерживаемый формат изображения: {mime_type}")
            
            return encoded_string, mime_type
        except Exception as e:
            logger.error(f"Ошибка кодирования изображения {image_path}: {e}")
            raise
    
    def _select_scenario(self, custom_prompt: Optional[str] = None) -> dict:
        """Выбор сценария показа столика"""
        if custom_prompt:
            return {
                "id": "custom",
                "english_prompt": f"Keep the dressing table exactly as shown in image. Add: {custom_prompt}",
                "russian_voiceover": "Туалетный столик TURAN Lux - качество и стиль для вашего дома.",
                "focus": "custom_scene"
            }
        
        import random
        scenario = random.choice(self.showcase_scenarios)
        logger.info(f"Выбран сценарий: {scenario['id']} - {scenario['focus']}")
        return scenario
    
    def _create_negative_prompt(self) -> str:
        """Создание негативного промпта"""
        return "changing the dressing table design, removing furniture, altering furniture color, different furniture style, poor quality, blurry, distorted, unnatural colors, bad lighting, chaotic scene"
    
    def generate_video_from_image(
        self, 
        image_path: str, 
        config: VideoGenerationConfig,
        custom_prompt: Optional[str] = None,
        storage_uri: Optional[str] = None
    ) -> tuple[str, dict]:
        """Генерация видео показа туалетного столика"""
        
        logger.info(f"Начало генерации видео показа: {image_path}")
        
        # Кодирование изображения
        image_base64, mime_type = self._encode_image_to_base64(image_path)
        
        # Выбор сценария
        scenario = self._select_scenario(custom_prompt)
        english_prompt = scenario['english_prompt']
        negative_prompt = self._create_negative_prompt()
        
        logger.info(f"Сценарий: {scenario['id']}")
        logger.info(f"Английский промпт: {english_prompt}")
        logger.info(f"Русская озвучка: {scenario['russian_voiceover']}")
        
        # Подготовка данных запроса
        request_data = {
            "instances": [{
                "prompt": english_prompt,
                "image": {
                    "bytesBase64Encoded": image_base64,
                    "mimeType": mime_type
                }
            }],
            "parameters": {
                "durationSeconds": 8,  # Всегда 8 секунд
                "aspectRatio": config.aspect_ratio.value,
                "sampleCount": config.sample_count,
                "enhancePrompt": config.enhance_prompt,
                "compressionQuality": config.compression_quality,
                "negativePrompt": negative_prompt,
                "personGeneration": config.person_generation,
                "generateAudio": config.generate_audio,
                "resolution": config.resolution.value
            }
        }
        
        if config.seed is not None:
            request_data["parameters"]["seed"] = config.seed
        
        if storage_uri:
            request_data["parameters"]["storageUri"] = storage_uri
        
        # Отправка запроса
        url = f"{self.base_url}/{config.model.value}:predictLongRunning"
        headers = {
            "Authorization": f"Bearer {self._get_auth_token()}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=request_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            operation_name = result.get("name")
            
            logger.info(f"Операция создана: {operation_name}")
            
            # Сохраняем информацию о сценарии
            self._save_scenario_info(image_path, scenario)
            
            return operation_name, scenario
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке запроса: {e}")
            raise
    
    def _save_scenario_info(self, image_path: str, scenario: dict):
        """Сохранение информации о сценарии"""
        scenarios_file = Path("generated_showcase_scenarios.json")
        
        if scenarios_file.exists():
            with open(scenarios_file, 'r', encoding='utf-8') as f:
                scenarios = json.load(f)
        else:
            scenarios = {}
        
        scenarios[str(Path(image_path).name)] = {
            "scenario_id": scenario['id'],
            "focus": scenario['focus'],
            "english_prompt": scenario['english_prompt'],
            "russian_voiceover": scenario['russian_voiceover'],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(scenarios_file, 'w', encoding='utf-8') as f:
            json.dump(scenarios, f, ensure_ascii=False, indent=2)
    
    def poll_operation_status(self, operation_name: str, max_wait_time: int = 600) -> Dict:
        """Отслеживание статуса операции"""
        
        logger.info(f"Отслеживание операции: {operation_name}")
        
        model_id = operation_name.split("/models/")[1].split("/operations/")[0]
        
        url = f"{self.base_url}/{model_id}:fetchPredictOperation"
        headers = {
            "Authorization": f"Bearer {self._get_auth_token()}",
            "Content-Type": "application/json"
        }
        
        request_data = {
            "operationName": operation_name
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.post(url, headers=headers, json=request_data, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("done"):
                    logger.info("Операция завершена успешно!")
                    return result
                else:
                    logger.info("Операция в процессе выполнения...")
                    time.sleep(10)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка при проверке статуса: {e}")
                time.sleep(5)
        
        raise TimeoutError(f"Операция не завершилась за {max_wait_time} секунд")
    
    def download_video(self, gcs_uri: str, local_path: str) -> str:
        """Скачивание видео из Google Cloud Storage"""
        try:
            import subprocess
            
            result = subprocess.run(
                ["gsutil", "cp", gcs_uri, local_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Видео скачано: {local_path}")
            return local_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка скачивания видео: {e}")
            raise
    
    def process_image_folder(
        self, 
        folder_path: str, 
        output_folder: str,
        config: VideoGenerationConfig,
        storage_uri: Optional[str] = None
    ) -> List[Dict]:
        """Обработка папки с изображениями туалетных столиков"""
        
        folder = Path(folder_path)
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)
        
        results = []
        
        # Поддерживаемые форматы
        supported_formats = {'.jpg', '.jpeg', '.png'}
        
        image_files = [
            f for f in folder.iterdir() 
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        
        logger.info(f"Найдено {len(image_files)} изображений туалетных столиков для обработки")
        
        for image_file in image_files:
            try:
                logger.info(f"Создание видео показа для: {image_file.name}")
                
                # Генерация видео
                operation_name, scenario = self.generate_video_from_image(
                    str(image_file), 
                    config, 
                    storage_uri=storage_uri
                )
                
                # Ожидание завершения
                operation_result = self.poll_operation_status(operation_name)
                
                # Обработка результата
                if "response" in operation_result:
                    response_data = operation_result["response"]
                    videos = response_data.get("videos", [])
                    
                    for i, video in enumerate(videos):
                        video_result = {
                            "source_image": str(image_file),
                            "operation_name": operation_name,
                            "video_index": i,
                            "status": "success",
                            "product": "TURAN Lux Dressing Table",
                            "scenario": scenario,
                            "russian_text": scenario['russian_voiceover']
                        }
                        
                        if "gcsUri" in video:
                            gcs_uri = video["gcsUri"]
                            local_filename = f"turan_{scenario['id']}_{image_file.stem}_v{i}.mp4"
                            local_path = output_folder / local_filename
                            
                            self.download_video(gcs_uri, str(local_path))
                            video_result["local_path"] = str(local_path)
                            video_result["gcs_uri"] = gcs_uri
                            
                        elif "bytesBase64Encoded" in video:
                            video_data = base64.b64decode(video["bytesBase64Encoded"])
                            local_filename = f"turan_{scenario['id']}_{image_file.stem}_v{i}.mp4"
                            local_path = output_folder / local_filename
                            
                            with open(local_path, 'wb') as f:
                                f.write(video_data)
                            
                            video_result["local_path"] = str(local_path)
                        
                        results.append(video_result)
                
            except Exception as e:
                logger.error(f"Ошибка обработки {image_file.name}: {e}")
                results.append({
                    "source_image": str(image_file),
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def create_social_media_configs(self) -> List[VideoGenerationConfig]:
        """Создание конфигураций для разных социальных сетей"""
        
        configs = []
        
        # YouTube/Facebook - горизонтальное
        configs.append(VideoGenerationConfig(
            model=VeoModel.VEO_3_GENERATE,
            duration_seconds=8,
            aspect_ratio=AspectRatio.LANDSCAPE,
            resolution=Resolution.FULL_HD,
            sample_count=1,
            generate_audio=True
        ))
        
        # Instagram Stories/TikTok - вертикальное
        configs.append(VideoGenerationConfig(
            model=VeoModel.VEO_3_GENERATE,
            duration_seconds=8,
            aspect_ratio=AspectRatio.PORTRAIT,
            resolution=Resolution.FULL_HD,
            sample_count=1,
            generate_audio=True
        ))
        
        return configs
    
    def get_all_scenarios(self) -> List[dict]:
        """Получить все доступные сценарии показа"""
        return self.showcase_scenarios
    
    def get_scenarios_by_focus(self, focus: str) -> List[dict]:
        """Получить сценарии по фокусу"""
        return [s for s in self.showcase_scenarios if s['focus'] == focus]

def main():
    """Основная функция для демонстрации"""
    
    # Инициализация генератора
    generator = SimpleTuranGenerator()
    
    # Конфигурация (всегда 8 секунд, только VEO 3.0)
    config = VideoGenerationConfig(
        model=VeoModel.VEO_3_GENERATE,
        duration_seconds=8,
        aspect_ratio=AspectRatio.LANDSCAPE,
        resolution=Resolution.FULL_HD,
        generate_audio=True,
        sample_count=1
    )
    
    # Пути к файлам
    images_folder = "images/dressing_tables"
    output_folder = "output/dressing_table_showcase"
    storage_bucket = "gs://turan-videos/dressing-tables/"
    
    try:
        Path(images_folder).mkdir(parents=True, exist_ok=True)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        logger.info("🎬 Запуск простого генератора видео показа туалетных столиков TURAN Lux")
        logger.info(f"📁 Папка изображений: {images_folder}")
        logger.info(f"📁 Папка вывода: {output_folder}")
        
        # Показать доступные сценарии
        scenarios = generator.get_all_scenarios()
        print(f"🎥 Доступно {len(scenarios)} сценариев показа:")
        for scenario in scenarios[:3]:  # Показать первые 3
            print(f"  • {scenario['id']}: {scenario['russian_voiceover']}")
        
        # Обработка всех изображений
        results = generator.process_image_folder(
            images_folder, 
            output_folder, 
            config,
            storage_uri=storage_bucket
        )
        
        # Сохранение отчета
        report_path = Path(output_folder) / "showcase_generation_report.json"
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
        print(f"🎭 Сценарии сохранены в: generated_showcase_scenarios.json")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()