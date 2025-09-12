#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TURAN Мебельный Магазин - Автоматизация создания рекламных видео
Генерация премиум видео из фотографий мебели с помощью Google Veo 3 API
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
        logging.FileHandler('turan_video_generator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VeoModel(Enum):
    """Доступные модели Veo API"""
    VEO_2_GENERATE = "veo-2.0-generate-001"
    VEO_2_GENERATE_EXP = "veo-2.0-generate-exp"
    VEO_3_GENERATE = "veo-3.0-generate-001"
    VEO_3_FAST_GENERATE = "veo-3.0-fast-generate-001"
    VEO_3_GENERATE_PREVIEW = "veo-3.0-generate-preview"
    VEO_3_FAST_GENERATE_PREVIEW = "veo-3.0-fast-generate-preview"

class AspectRatio(Enum):
    """Соотношения сторон для видео"""
    LANDSCAPE = "16:9"  # Горизонтальное для YouTube, Facebook
    PORTRAIT = "9:16"   # Вертикальное для TikTok, Instagram Stories

class Resolution(Enum):
    """Разрешения видео (только для Veo 3)"""
    HD = "720p"
    FULL_HD = "1080p"

@dataclass
class VideoGenerationConfig:
    """Конфигурация генерации видео"""
    model: VeoModel = VeoModel.VEO_3_GENERATE
    duration_seconds: int = 8
    aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE
    resolution: Resolution = Resolution.FULL_HD
    sample_count: int = 1
    generate_audio: bool = True
    enhance_prompt: bool = True
    compression_quality: str = "optimized"  # "optimized" или "lossless"
    person_generation: str = "allow_adult"  # "allow_adult" или "dont_allow"
    seed: Optional[int] = None

class TuranVideoGenerator:
    """Главный класс для генерации рекламных видео мебели TURAN"""
    
    def __init__(self, project_id: str = "turantt", location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.base_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models"
        
        # Настройка аутентификации
        self.credentials = None
        self._setup_authentication()
        
        # Промпты для разных типов мебели
        self.furniture_prompts = {
            'диван': [
                "Роскошная современная гостиная с элегантным диваном TURAN в центре, мягкое освещение, камера медленно приближается к дивану, подчеркивая качество ткани и комфорт",
                "Стильный диван TURAN в уютной домашней обстановке, семья отдыхает, теплая атмосфера, золотой час, кинематографическое освещение",
                "Премиум диван TURAN в минималистичном интерьере, камера вращается вокруг мебели, демонстрируя элегантные линии и превосходное качество"
            ],
            'кровать': [
                "Роскошная спальня с кроватью TURAN, утреннее солнце проникает через окна, мягкие тени, демонстрация комфорта и качества",
                "Элегантная кровать TURAN в современной спальне, камера показывает детали изголовья, высококачественные материалы, премиум атмосфера",
                "Кровать TURAN в уютной спальне, вечернее освещение, демонстрация удобства и стиля, кинематографическая подача"
            ],
            'стол': [
                "Обеденный стол TURAN в элегантной столовой, красивая сервировка, камера медленно скользит вокруг стола, подчеркивая качество древесины",
                "Стильный стол TURAN в современном интерьере, семейный ужин, теплое освещение, демонстрация функциональности и красоты",
                "Премиум стол TURAN, детали текстуры дерева, элегантные ножки, профессиональное освещение, демонстрация мастерства"
            ],
            'шкаф': [
                "Просторный шкаф TURAN в современной спальне, двери плавно открываются, показывая внутреннее пространство, организованное хранение",
                "Элегантный шкаф TURAN в гардеробной, красивое освещение, демонстрация вместительности и стильного дизайна",
                "Премиум шкаф TURAN, камера показывает качество фурнитуры, плавное закрывание дверей, внимание к деталям"
            ],
            'стул': [
                "Комфортные стулья TURAN вокруг обеденного стола, семья собирается за ужином, уютная атмосфера, демонстрация эргономики",
                "Стильные стулья TURAN в современной кухне, камера крупным планом показывает качество обивки и каркаса",
                "Элегантные стулья TURAN в гостиной, демонстрация комфорта и дизайна, мягкое освещение"
            ]
        }
    
    def _setup_authentication(self):
        """Настройка аутентификации Google Cloud"""
        try:
            # Попытка получить credentials по умолчанию
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
            
            # Определение MIME типа
            mime_type, _ = mimetypes.guess_type(image_path)
            if mime_type not in ['image/jpeg', 'image/png']:
                raise ValueError(f"Неподдерживаемый формат изображения: {mime_type}")
            
            return encoded_string, mime_type
        except Exception as e:
            logger.error(f"Ошибка кодирования изображения {image_path}: {e}")
            raise
    
    def _detect_furniture_type(self, image_path: str) -> str:
        """Определение типа мебели по названию файла"""
        filename = Path(image_path).stem.lower()
        
        furniture_keywords = {
            'диван': ['диван', 'sofa', 'couch'],
            'кровать': ['кровать', 'bed', 'bedroom'],
            'стол': ['стол', 'table', 'desk'],
            'шкаф': ['шкаф', 'wardrobe', 'closet', 'cabinet'],
            'стул': ['стул', 'chair', 'seat']
        }
        
        for furniture_type, keywords in furniture_keywords.items():
            if any(keyword in filename for keyword in keywords):
                return furniture_type
        
        return 'мебель'  # По умолчанию
    
    def _create_turan_prompt(self, furniture_type: str, custom_prompt: Optional[str] = None) -> str:
        """Создание промпта для рекламного видео TURAN"""
        if custom_prompt:
            return f"{custom_prompt}, бренд TURAN, премиум качество, стильный интерьер, профессиональное освещение, кинематографическая подача"
        
        import random
        base_prompts = self.furniture_prompts.get(furniture_type, self.furniture_prompts['диван'])
        selected_prompt = random.choice(base_prompts)
        
        return selected_prompt
    
    def _create_negative_prompt(self) -> str:
        """Создание негативного промпта"""
        return "плохое качество, размытость, искажения, неестественные цвета, плохое освещение, хаос, беспорядок"
    
    def generate_video_from_image(
        self, 
        image_path: str, 
        config: VideoGenerationConfig,
        custom_prompt: Optional[str] = None,
        storage_uri: Optional[str] = None
    ) -> str:
        """Генерация видео из изображения"""
        
        logger.info(f"Начало генерации видео из изображения: {image_path}")
        
        # Кодирование изображения
        image_base64, mime_type = self._encode_image_to_base64(image_path)
        
        # Определение типа мебели и создание промпта
        furniture_type = self._detect_furniture_type(image_path)
        prompt = self._create_turan_prompt(furniture_type, custom_prompt)
        negative_prompt = self._create_negative_prompt()
        
        logger.info(f"Тип мебели: {furniture_type}")
        logger.info(f"Промпт: {prompt}")
        
        # Подготовка данных запроса
        request_data = {
            "instances": [{
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": image_base64,
                    "mimeType": mime_type
                }
            }],
            "parameters": {
                "durationSeconds": config.duration_seconds,
                "aspectRatio": config.aspect_ratio.value,
                "sampleCount": config.sample_count,
                "enhancePrompt": config.enhance_prompt,
                "compressionQuality": config.compression_quality,
                "negativePrompt": negative_prompt,
                "personGeneration": config.person_generation
            }
        }
        
        # Добавление параметров для Veo 3
        if config.model.value.startswith("veo-3"):
            request_data["parameters"]["generateAudio"] = config.generate_audio
            request_data["parameters"]["resolution"] = config.resolution.value
        
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
            return operation_name
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке запроса: {e}")
            raise
    
    def poll_operation_status(self, operation_name: str, max_wait_time: int = 600) -> Dict:
        """Отслеживание статуса операции"""
        
        logger.info(f"Отслеживание операции: {operation_name}")
        
        # Извлечение model_id из operation_name
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
                    time.sleep(10)  # Ждем 10 секунд перед следующей проверкой
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Ошибка при проверке статуса: {e}")
                time.sleep(5)
        
        raise TimeoutError(f"Операция не завершилась за {max_wait_time} секунд")
    
    def download_video(self, gcs_uri: str, local_path: str) -> str:
        """Скачивание видео из Google Cloud Storage"""
        try:
            # Для простоты используем gsutil команду
            # В продакшене лучше использовать Google Cloud Storage client library
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
        """Обработка папки с изображениями"""
        
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
        
        logger.info(f"Найдено {len(image_files)} изображений для обработки")
        
        for image_file in image_files:
            try:
                logger.info(f"Обработка: {image_file.name}")
                
                # Генерация видео
                operation_name = self.generate_video_from_image(
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
                            "status": "success"
                        }
                        
                        if "gcsUri" in video:
                            # Скачивание из GCS
                            gcs_uri = video["gcsUri"]
                            local_filename = f"{image_file.stem}_video_{i}.mp4"
                            local_path = output_folder / local_filename
                            
                            self.download_video(gcs_uri, str(local_path))
                            video_result["local_path"] = str(local_path)
                            video_result["gcs_uri"] = gcs_uri
                            
                        elif "bytesBase64Encoded" in video:
                            # Сохранение из base64
                            video_data = base64.b64decode(video["bytesBase64Encoded"])
                            local_filename = f"{image_file.stem}_video_{i}.mp4"
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
    
    def create_batch_config_for_social_media(self) -> List[VideoGenerationConfig]:
        """Создание конфигураций для разных социальных сетей"""
        
        configs = []
        
        # YouTube/Facebook - горизонтальное HD
        configs.append(VideoGenerationConfig(
            model=VeoModel.VEO_3_GENERATE,
            duration_seconds=8,
            aspect_ratio=AspectRatio.LANDSCAPE,
            resolution=Resolution.FULL_HD,
            sample_count=1,
            generate_audio=True
        ))
        
        # Instagram Stories/TikTok - вертикальное HD
        configs.append(VideoGenerationConfig(
            model=VeoModel.VEO_3_GENERATE,
            duration_seconds=6,
            aspect_ratio=AspectRatio.PORTRAIT,
            resolution=Resolution.FULL_HD,
            sample_count=1,
            generate_audio=True
        ))
        
        # Быстрая версия для превью
        configs.append(VideoGenerationConfig(
            model=VeoModel.VEO_3_FAST_GENERATE,
            duration_seconds=4,
            aspect_ratio=AspectRatio.LANDSCAPE,
            resolution=Resolution.HD,
            sample_count=1,
            generate_audio=True
        ))
        
        return configs

def main():
    """Основная функция для демонстрации использования"""
    
    # Инициализация генератора
    generator = TuranVideoGenerator()
    
    # Настройки проекта
    config = VideoGenerationConfig(
        model=VeoModel.VEO_3_GENERATE,
        duration_seconds=8,
        aspect_ratio=AspectRatio.LANDSCAPE,
        resolution=Resolution.FULL_HD,
        generate_audio=True,
        sample_count=2  # Создаем 2 варианта
    )
    
    # Пути к файлам
    images_folder = "images/furniture"  # Папка с фотографиями мебели
    output_folder = "output/videos"     # Папка для готовых видео
    storage_bucket = "gs://turan-videos/generated/"  # GCS bucket для хранения
    
    try:
        # Создание папок
        Path(images_folder).mkdir(parents=True, exist_ok=True)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        logger.info("🎬 Запуск автоматизации видео для TURAN")
        logger.info(f"📁 Папка изображений: {images_folder}")
        logger.info(f"📁 Папка вывода: {output_folder}")
        
        # Обработка всех изображений в папке
        results = generator.process_image_folder(
            images_folder, 
            output_folder, 
            config,
            storage_uri=storage_bucket
        )
        
        # Сохранение отчета
        report_path = Path(output_folder) / "generation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Обработка завершена! Отчет сохранен: {report_path}")
        
        # Статистика
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = len(results) - successful
        
        print(f"\n🎉 СТАТИСТИКА ГЕНЕРАЦИИ:")
        print(f"✅ Успешно: {successful}")
        print(f"❌ Ошибки: {failed}")
        print(f"📊 Всего: {len(results)}")
        
        # Создание конфигураций для социальных сетей
        social_configs = generator.create_batch_config_for_social_media()
        print(f"📱 Доступно {len(social_configs)} конфигураций для соцсетей")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()