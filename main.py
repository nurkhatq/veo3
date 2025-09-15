#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TURAN Dressing Table Video Generator - Улучшенная версия с исправлением JSON ошибки
Показ туалетных столиков в уютной обстановке с профессиональными кинематографическими промптами
"""

import os
import json
import time
import base64
import requests
import logging
import random
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
        logging.FileHandler('turan_enhanced_generator.log', encoding='utf-8'),
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

class CinematicStyle(Enum):
    """Кинематографические стили"""
    COMMERCIAL = "commercial"
    LIFESTYLE = "lifestyle"
    DRAMATIC = "dramatic"
    INTIMATE = "intimate"

class LightingMood(Enum):
    """Настроения освещения"""
    GOLDEN_HOUR = "golden_hour"
    MORNING_SOFT = "morning_soft" 
    EVENING_WARM = "evening_warm"
    DRAMATIC_CONTRAST = "dramatic_contrast"
    NATURAL_BRIGHT = "natural_bright"

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
    # Новые параметры для кинематографии
    cinematic_style: CinematicStyle = CinematicStyle.COMMERCIAL
    lighting_mood: LightingMood = LightingMood.GOLDEN_HOUR
    use_enhanced_prompts: bool = True

class SimpleTuranGenerator:
    """Улучшенный генератор видео туалетных столиков TURAN с кинематографическими промптами"""
    
    def __init__(self, project_id: str = "turantt", location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.base_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models"
        
        # Настройка аутентификации
        self.credentials = None
        self._setup_authentication()
        
        # Статистика для анализа
        self.generation_stats = {
            "total_generated": 0,
            "enhanced_prompts_used": 0,
            "traditional_prompts_used": 0,
            "scenarios_used": {}
        }
        
        # Кинематографические компоненты
        self.camera_setups = {
            CinematicStyle.COMMERCIAL: [
                "Professional commercial shot on ARRI ALEXA 35 with 50mm Zeiss Master Prime lens",
                "High-end advertising setup using Sony FX9 with Sigma 24-70mm f/2.8 cine lens",
                "Luxury brand commercial shot on RED KOMODO 6K with 35mm vintage glass",
                "Premium furniture showcase using ARRI MINI LF with 75mm Master Macro lens"
            ],
            CinematicStyle.LIFESTYLE: [
                "Authentic lifestyle shot with handheld Sony A7S III, 85mm f/1.4 GM lens",
                "Natural documentary style using Canon R5 with 50mm f/1.2 RF lens",
                "Intimate home cinematography with Panasonic GH6, 25mm f/1.7 lens"
            ],
            CinematicStyle.DRAMATIC: [
                "Dramatic cinema setup using RED MONSTRO 8K with anamorphic 50mm lens",
                "High contrast commercial shot on ARRI ALEXA LF with 65mm Master Prime",
                "Cinematic furniture showcase with Blackmagic URSA 12K, 35mm cine lens"
            ]
        }
        
        self.lighting_descriptions = {
            LightingMood.GOLDEN_HOUR: [
                "Warm golden hour sunlight streaming through floor-to-ceiling windows, creating ethereal atmosphere with dancing light particles and soft shadows on the glass surface",
                "Magic hour lighting with honey-colored rays filtering through sheer curtains, painting warm gradients across the LED mirror and white surfaces",
                "Late afternoon sun creating dramatic rim lighting on the metallic legs and warm, inviting glow across the entire dressing table setup"
            ],
            LightingMood.MORNING_SOFT: [
                "Gentle morning sunlight diffused through translucent curtains, creating soft, even illumination that highlights the glass surface without harsh reflections",
                "Fresh daybreak lighting with cool-warm balance, emphasizing the clean lines and functional beauty of the TURAN Lux design",
                "Peaceful morning ambiance with natural north-facing window light, perfectly suited for beauty routines and intimate moments"
            ],
            LightingMood.EVENING_WARM: [
                "Cozy evening atmosphere with warm LED practicals and soft lamplight, creating intimate shadows and highlighting the mirror's illumination features",
                "Romantic twilight setting with warm tungsten lighting, emphasizing comfort and relaxation at the end of the day",
                "Evening sanctuary lighting with multiple warm sources, showcasing the dressing table as a personal retreat space"
            ]
        }
        
        self.camera_movements = [
            "Camera begins with wide establishing shot, then executes slow dolly movement forward with subtle downward tilt, revealing intricate details of the glass surface and LED lighting",
            "Smooth tracking shot starting from left side, gracefully orbiting around the dressing table to showcase all angles and the four-drawer storage system",
            "Elegant crane movement descending from high angle to intimate eye-level perspective, emphasizing the table's proportions and premium materials",
            "Gentle push-in movement from medium shot to close-up, highlighting the LED mirror functionality and glass surface reflections",
            "Sophisticated lateral tracking combined with slow zoom, revealing the relationship between the dressing table and its bedroom environment"
        ]
        
        self.audio_designs = [
            "Audio: gentle morning ambiance with soft fabric sounds, warm contemporary piano score building subtly, distant birds chirping",
            "Audio: intimate room tone with delicate material interactions, minimalist ambient music, subtle LED lighting hum",
            "Audio: peaceful bedroom atmosphere, soft drawer sliding sounds, elegant instrumental score with warm reverb",
            "Audio: natural environmental sounds blended with refined background music, authentic furniture interaction acoustics",
            "Audio: sophisticated commercial audio landscape with premium material sounds and contemporary orchestral arrangement"
        ]
        
        self.color_palettes = [
            "Color palette: warm whites, brushed metallics, soft golden accents with natural wood tones",
            "Color grading: pristine whites, cool silver metallic highlights, gentle cream undertones",
            "Color scheme: elegant white glass dominance, warm brass accents, soft beige environmental tones",
            "Color temperature: balanced daylight whites, subtle warm highlights, sophisticated neutral palette",
            "Visual palette: premium white surfaces, polished metal details, warm ambient color temperature"
        ]
        
        # Улучшенные кинематографические сценарии показа столика
        self.showcase_scenarios = [
            {
                "id": "golden_hour_elegance",
                "cinematic_style": "commercial",  # Изменено: строка вместо Enum
                "lighting_mood": "golden_hour",   # Изменено: строка вместо Enum
                "enhanced_prompt": "Professional commercial shot on ARRI ALEXA 35 with 50mm Zeiss Master Prime lens. Keep the TURAN Lux dressing table exactly as shown in image - preserve white glass surface, 4 drawers, LED mirror, and metallic legs unchanged. Add: Elegant contemporary bedroom interior with warm oak flooring and floor-to-ceiling windows. Warm golden hour sunlight streaming through sheer curtains, creating ethereal atmosphere with dancing light particles and soft shadows highlighting the glass surface texture. Camera begins with wide establishing shot, then executes slow dolly movement forward with subtle downward tilt, ending in intimate close-up of LED mirror lighting. Audio: gentle morning ambiance, soft fabric sounds, warm contemporary piano score building subtly. Color palette: warm whites, brushed metallics, soft golden accents. Professional commercial cinematography. No subtitles.",
                "russian_voiceover": "Туалетный столик TURAN Lux - идеальное решение для вашей спальни. Стильный дизайн и функциональность в одном.",
                "focus": "bedroom_setting"
            },
            {
                "id": "morning_beauty_ritual",
                "cinematic_style": "lifestyle",    # Изменено: строка вместо Enum
                "lighting_mood": "morning_soft",   # Изменено: строка вместо Enum
                "enhanced_prompt": "Authentic lifestyle shot with Sony A7S III, 85mm f/1.4 GM lens. Preserve the TURAN Lux dressing table from image unchanged - maintain white glass top, four-drawer configuration, LED mirror system, and metal frame intact. Add: Serene morning bedroom scene with natural diffused lighting through large windows. Gentle morning sunlight creating soft, even illumination that highlights the LED mirror's three lighting modes and glass surface clarity. Smooth tracking shot from left side, gracefully orbiting around the dressing table showcasing the functional drawer system and elegant proportions. Audio: peaceful morning atmosphere with soft drawer sliding sounds, minimalist ambient music, subtle environmental sounds. Color grading: pristine whites, gentle cream undertones, natural daylight balance. Intimate home cinematography aesthetic. No subtitles.",
                "russian_voiceover": "Начните утро с красоты! Столик TURAN с LED-подсветкой и стеклянной столешницей - ваш ежедневный помощник.",
                "focus": "morning_lighting"
            },
            {
                "id": "sophisticated_interior",
                "cinematic_style": "commercial",   # Изменено: строка вместо Enum
                "lighting_mood": "natural_bright", # Изменено: строка вместо Enum
                "enhanced_prompt": "High-end advertising setup using Sony FX9 with Sigma 24-70mm f/2.8 cine lens. Keep TURAN Lux dressing table design identical to image - preserve glass surface transparency, integrated drawer system, LED-illuminated mirror, and sleek metallic base. Add: Modern minimalist bedroom with concrete accent wall and designer pendant lighting fixtures. Bright natural daylight from multiple windows creating crisp, clean illumination that emphasizes the table's contemporary design elements. Elegant crane movement descending from high angle to intimate eye-level perspective, revealing the sophisticated storage solutions and premium build quality. Audio: sophisticated commercial audio with premium material interaction sounds, contemporary orchestral arrangement. Color scheme: elegant white glass dominance, cool silver metallic highlights, modern neutral palette. Luxury furniture advertising cinematography. No subtitles.",
                "russian_voiceover": "TURAN Lux гармонично впишется в любой современный интерьер. Качество и стиль для вашего дома.",
                "focus": "interior_design"
            },
            {
                "id": "evening_sanctuary",
                "cinematic_style": "intimate",      # Изменено: строка вместо Enum
                "lighting_mood": "evening_warm",    # Изменено: строка вместо Enum
                "enhanced_prompt": "Intimate cinematography with Canon R5, 50mm f/1.2 RF lens. Maintain TURAN Lux dressing table appearance from image unchanged - keep white tempered glass top, four-drawer configuration, LED mirror with adjustable lighting, and metal leg structure intact. Add: Cozy evening bedroom setting with warm tungsten practicals and soft bedside lighting. Romantic twilight atmosphere with warm LED practicals creating intimate shadows that highlight the mirror's illumination features and glass surface reflections. Gentle push-in movement from medium shot to close-up, emphasizing the personal, intimate nature of the beauty space. Audio: peaceful evening ambiance with delicate material sounds, warm ambient music with soft reverb. Color temperature: warm whites with golden highlights, intimate cozy atmosphere. Personal sanctuary cinematography style. No subtitles.",
                "russian_voiceover": "Вечерний уют с туалетным столиком TURAN. Расслабьтесь и наслаждайтесь моментами красоты каждый день.",
                "focus": "evening_comfort"
            },
            {
                "id": "premium_features_showcase",
                "cinematic_style": "commercial",        # Изменено: строка вместо Enum
                "lighting_mood": "dramatic_contrast",   # Изменено: строка вместо Enum
                "enhanced_prompt": "Premium furniture showcase using ARRI MINI LF with 75mm Master Macro lens. Preserve TURAN Lux dressing table exactly as shown - maintain glass surface clarity, four-drawer system (2 built-in + 2 removable), LED mirror with three light settings, and metallic leg design unchanged. Add: High-contrast studio environment with dramatic directional lighting emphasizing product features. Professional lighting setup with strong key light creating sculptural depth, highlighting the white tempered glass surface, drawer mechanisms, and LED mirror functionality. Dynamic camera sequence: close-up product details transitioning to wide contextual shots, showcasing storage capacity and build quality. Audio: sophisticated product demonstration audio with precise mechanical sounds, building contemporary score. Color palette: pristine commercial whites, dramatic shadows, metallic accent highlights. Premium product advertising cinematography. No subtitles.",
                "russian_voiceover": "4 вместительных ящика, зеркало с LED-подсветкой, стеклянная столешница. TURAN Lux - продуманно до мелочей.",
                "focus": "product_features"
            },
            {
                "id": "family_lifestyle_comfort",
                "cinematic_style": "lifestyle",         # Изменено: строка вместо Enum
                "lighting_mood": "natural_bright",      # Изменено: строка вместо Enum
                "enhanced_prompt": "Natural documentary style using Panasonic GH6 with 25mm f/1.7 lens. Keep TURAN Lux dressing table unchanged from image - preserve white glass top, integrated storage system, LED mirror assembly, and metal frame structure. Add: Comfortable family bedroom with lived-in warmth and natural daylight from multiple sources. Bright, welcoming atmosphere showcasing the dressing table in real home environment. Authentic handheld camera movement with subtle organic motion, demonstrating how the furniture integrates into daily family life. Audio: natural home environment sounds with warm, family-friendly background music, authentic lifestyle ambiance. Color grading: natural daylight whites, warm family home atmosphere, comfortable living tones. Documentary lifestyle cinematography approach. No subtitles.",
                "russian_voiceover": "Сделайте свой дом уютнее с мебелью TURAN. Качество, которому доверяют тысячи семей в Казахстане.",
                "focus": "family_lifestyle"
            },
            {
                "id": "luxury_investment_quality",
                "cinematic_style": "dramatic",         # Изменено: строка вместо Enum
                "lighting_mood": "dramatic_contrast",  # Изменено: строка вместо Enum
                "enhanced_prompt": "Dramatic cinema setup using RED MONSTRO 8K with anamorphic 50mm lens. Preserve TURAN Lux dressing table design from image intact - maintain glass surface premium quality, drawer system functionality, LED mirror technology, and metallic base construction. Add: Luxury bedroom setting with high-end interior design elements and sophisticated ambient lighting. Cinematic lighting with dramatic contrast emphasizing the furniture's premium build quality and attention to detail. Professional product cinematography with multiple camera angles revealing craftsmanship, material quality, and design sophistication. Audio: premium commercial audio design with refined material sounds, orchestral score building to emotional crescendo. Color grading: luxury whites with dramatic shadows, premium metallic accents, sophisticated commercial palette. High-end furniture advertising cinematography. No subtitles.",
                "russian_voiceover": "Премиум качество по доступной цене. Туалетный столик TURAN Lux - инвестиция в ваш комфорт на годы.",
                "focus": "quality_premium"
            },
            {
                "id": "daily_beauty_integration",
                "cinematic_style": "lifestyle",     # Изменено: строка вместо Enum
                "lighting_mood": "morning_soft",    # Изменено: строка вместо Enum
                "enhanced_prompt": "Intimate home cinematography with Sony A7S III, 85mm f/1.4 lens. Maintain TURAN Lux dressing table appearance unchanged from image - keep white tempered glass surface, four-drawer storage, LED mirror with lighting controls, and leg structure identical. Add: Peaceful morning bedroom routine setting with soft natural lighting and personal touches. Gentle morning sunlight creating serene atmosphere perfect for daily beauty rituals and personal care moments. Smooth flowing camera movement demonstrating how the dressing table integrates seamlessly into morning routines. Audio: intimate personal space ambiance with soft music, natural morning sounds, gentle product interaction audio. Color temperature: soft morning whites, natural skin-flattering lighting, personal sanctuary atmosphere. Personal lifestyle cinematography style. No subtitles.",
                "russian_voiceover": "Каждое утро начинается с вас. Туалетный столик TURAN - ваш персональный уголок красоты и вдохновения.",
                "focus": "daily_integration"
            },
            {
                "id": "space_optimization_smart",
                "cinematic_style": "commercial",    # Изменено: строка вместо Enum
                "lighting_mood": "natural_bright",  # Изменено: строка вместо Enum
                "enhanced_prompt": "Professional commercial shot on ARRI ALEXA LF with 65mm Master Prime lens. Keep TURAN Lux dressing table identical to image shown - preserve glass top dimensions, storage drawer configuration, LED mirror assembly, and base frame design unchanged. Add: Smart contemporary bedroom layout demonstrating efficient space utilization and organization solutions. Bright architectural lighting emphasizing the table's compact footprint and maximum storage efficiency. Sophisticated camera movement showcasing spatial relationships and functional design elements. Audio: modern home environment sounds with contemporary instrumental score, organized storage interaction sounds. Color palette: clean architectural whites, modern metallic accents, efficient living space tones. Smart home furniture advertising style. No subtitles.",
                "russian_voiceover": "Умное использование пространства с TURAN Lux. Стиль, функциональность и порядок в вашей спальне.",
                "focus": "space_efficiency"
            },
            {
                "id": "brand_heritage_trust",
                "cinematic_style": "commercial",   # Изменено: строка вместо Enum
                "lighting_mood": "golden_hour",    # Изменено: строка вместо Enum
                "enhanced_prompt": "Luxury brand commercial shot on RED KOMODO 6K with 35mm vintage glass. Preserve original TURAN Lux dressing table design from image - maintain white glass surface integrity, drawer system design, LED mirror functionality, and metallic leg construction. Add: Established family home environment with warm traditional and modern elements blend. Warm golden lighting creating trustworthy, established atmosphere that speaks to brand heritage and reliability. Classic commercial cinematography with stable, confident camera movements building trust and showcasing longevity. Audio: reliable, established brand atmosphere with warm family home sounds, traditional yet contemporary musical arrangement. Color grading: trustworthy whites, established metallic tones, heritage brand color palette. Brand heritage commercial cinematography. No subtitles.",
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
    
    def _select_scenario(self, custom_prompt: Optional[str] = None, config: Optional[VideoGenerationConfig] = None) -> dict:
        """Выбор сценария показа столика с учетом конфигурации"""
        if custom_prompt:
            # Создаем кинематографический кастомный сценарий
            return self._create_enhanced_custom_scenario(custom_prompt, config)
        
        if config and config.use_enhanced_prompts:
            # Используем улучшенные кинематографические сценарии
            scenario = random.choice(self.showcase_scenarios)
            self.generation_stats["enhanced_prompts_used"] += 1
            logger.info(f"Выбран улучшенный сценарий: {scenario['id']} - {scenario['focus']}")
            return scenario
        else:
            # Fallback к простым сценариям для совместимости
            return self._create_simple_scenario()
    
    def _create_enhanced_custom_scenario(self, custom_prompt: str, config: Optional[VideoGenerationConfig] = None) -> dict:
        """Создание улучшенного кастомного сценария"""
        style = config.cinematic_style.value if config else "commercial"  # Исправлено: получаем строку
        lighting = config.lighting_mood.value if config else "golden_hour"  # Исправлено: получаем строку
        
        # Выбираем компоненты на основе стиля
        style_enum = CinematicStyle(style)
        lighting_enum = LightingMood(lighting)
        
        camera_setup = random.choice(self.camera_setups[style_enum])
        lighting_desc = random.choice(self.lighting_descriptions[lighting_enum])
        camera_movement = random.choice(self.camera_movements)
        audio_design = random.choice(self.audio_designs)
        color_palette = random.choice(self.color_palettes)
        
        enhanced_prompt = f"""
        {camera_setup}. Keep the TURAN Lux dressing table exactly as shown in image - preserve white glass surface, 4 drawers, LED mirror, and metallic legs unchanged. Add: {custom_prompt}. {lighting_desc}. {camera_movement}. {audio_design}. {color_palette}. Professional commercial cinematography. No subtitles.
        """.strip()
        
        return {
            "id": "enhanced_custom",
            "enhanced_prompt": enhanced_prompt,
            "russian_voiceover": "Туалетный столик TURAN Lux - качество и стиль для вашего дома.",
            "focus": "custom_enhanced_scene",
            "cinematic_style": style,      # Строка, а не Enum
            "lighting_mood": lighting      # Строка, а не Enum
        }
    
    def _create_simple_scenario(self) -> dict:
        """Создание простого сценария для обратной совместимости"""
        simple_scenarios = [
            {
                "id": "simple_bedroom_view",
                "enhanced_prompt": "Keep the dressing table exactly as shown in the image. Add: Elegant bedroom interior, warm morning light through window, camera slowly pans around the dressing table showing different angles, cozy atmosphere, soft lighting, modern home interior, 8-second elegant showcase",
                "russian_voiceover": "Туалетный столик TURAN Lux - идеальное решение для вашей спальни. Стильный дизайн и функциональность в одном.",
                "focus": "bedroom_setting",
                "cinematic_style": "standard",  # Строка для совместимости
                "lighting_mood": "natural"      # Строка для совместимости
            }
        ]
        scenario = random.choice(simple_scenarios)
        self.generation_stats["traditional_prompts_used"] += 1
        return scenario
    
    def _create_enhanced_negative_prompt(self) -> str:
        """Создание улучшенного негативного промпта"""
        return "changing the TURAN dressing table design, removing original furniture, altering glass surface, modifying drawer configuration, changing LED mirror, different furniture style, poor quality, blurry, distorted, unnatural colors, bad lighting, amateur cinematography, unprofessional setup, subtitles, text overlay, watermarks, low resolution, pixelated, grainy, overexposed, underexposed, harsh shadows, flat lighting"
    
    def generate_video_from_image(
        self, 
        image_path: str, 
        config: VideoGenerationConfig,
        custom_prompt: Optional[str] = None,
        storage_uri: Optional[str] = None
    ) -> tuple[str, dict]:
        """Генерация видео показа туалетного столика с улучшенными промптами"""
        
        logger.info(f"Начало генерации видео показа: {image_path}")
        
        # Кодирование изображения
        image_base64, mime_type = self._encode_image_to_base64(image_path)
        
        # Выбор сценария
        scenario = self._select_scenario(custom_prompt, config)
        english_prompt = scenario['enhanced_prompt']
        negative_prompt = self._create_enhanced_negative_prompt()
        
        # Обновляем статистику
        self.generation_stats["total_generated"] += 1
        scenario_id = scenario['id']
        self.generation_stats["scenarios_used"][scenario_id] = self.generation_stats["scenarios_used"].get(scenario_id, 0) + 1
        
        logger.info(f"Сценарий: {scenario['id']}")
        logger.info(f"Стиль: {scenario.get('cinematic_style', 'Standard')}")
        logger.info(f"Английский промпт: {english_prompt[:200]}...")
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
            
            # Сохраняем информацию о сценарии (ИСПРАВЛЕНО)
            self._save_scenario_info(image_path, scenario)
            
            return operation_name, scenario
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке запроса: {e}")
            raise
    
    def _save_scenario_info(self, image_path: str, scenario: dict):
        """Сохранение информации о сценарии (ИСПРАВЛЕНО для JSON сериализации)"""
        scenarios_file = Path("generated_showcase_scenarios.json")
        
        if scenarios_file.exists():
            with open(scenarios_file, 'r', encoding='utf-8') as f:
                scenarios = json.load(f)
        else:
            scenarios = {}
        
        # ИСПРАВЛЕНИЕ: Конвертируем все значения в строки для JSON
        scenario_info = {
            "scenario_id": scenario['id'],
            "focus": scenario['focus'],
            "enhanced_prompt": scenario['enhanced_prompt'],
            "russian_voiceover": scenario['russian_voiceover'],
            "cinematic_style": str(scenario.get('cinematic_style', 'standard')),  # Всегда строка
            "lighting_mood": str(scenario.get('lighting_mood', 'natural')),      # Всегда строка
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "prompt_type": "enhanced" if self.generation_stats["enhanced_prompts_used"] > 0 else "traditional"
        }
        
        scenarios[str(Path(image_path).name)] = scenario_info
        
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
                    elapsed = int(time.time() - start_time)
                    logger.info(f"Операция в процессе выполнения... ({elapsed}s)")
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
                            "russian_text": scenario['russian_voiceover'],
                            "cinematic_style": str(scenario.get('cinematic_style', 'standard')),  # ИСПРАВЛЕНО
                            "lighting_mood": str(scenario.get('lighting_mood', 'natural')),        # ИСПРАВЛЕНО
                            "prompt_enhancement": "enhanced" if config.use_enhanced_prompts else "traditional"
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
        
        # YouTube/Facebook - горизонтальное с коммерческим стилем
        configs.append(VideoGenerationConfig(
            model=VeoModel.VEO_3_GENERATE,
            duration_seconds=8,
            aspect_ratio=AspectRatio.LANDSCAPE,
            resolution=Resolution.FULL_HD,
            sample_count=1,
            generate_audio=True,
            cinematic_style=CinematicStyle.COMMERCIAL,
            lighting_mood=LightingMood.GOLDEN_HOUR,
            use_enhanced_prompts=True
        ))
        
        # Instagram Stories/TikTok - вертикальное с lifestyle стилем
        configs.append(VideoGenerationConfig(
            model=VeoModel.VEO_3_GENERATE,
            duration_seconds=8,
            aspect_ratio=AspectRatio.PORTRAIT,
            resolution=Resolution.FULL_HD,
            sample_count=1,
            generate_audio=True,
            cinematic_style=CinematicStyle.LIFESTYLE,
            lighting_mood=LightingMood.MORNING_SOFT,
            use_enhanced_prompts=True
        ))
        
        return configs
    
    def get_all_scenarios(self) -> List[dict]:
        """Получить все доступные сценарии показа"""
        return self.showcase_scenarios
    
    def get_scenarios_by_focus(self, focus: str) -> List[dict]:
        """Получить сценарии по фокусу"""
        return [s for s in self.showcase_scenarios if s['focus'] == focus]
    
    def get_generation_analytics(self) -> Dict:
        """Получение аналитики генерации"""
        total = self.generation_stats["total_generated"]
        if total > 0:
            enhancement_rate = (self.generation_stats["enhanced_prompts_used"] / total) * 100
        else:
            enhancement_rate = 0
        
        return {
            **self.generation_stats,
            "enhancement_usage_percentage": enhancement_rate,
            "traditional_usage_percentage": 100 - enhancement_rate,
            "most_used_scenarios": dict(sorted(
                self.generation_stats["scenarios_used"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5])
        }
    
    def export_performance_report(self, filename: str = "turan_enhanced_performance_report.json"):
        """Экспорт отчета о производительности"""
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "product": "TURAN Lux Dressing Table Video Generator",
            "version": "Enhanced Cinematic v2.0",
            "analytics": self.get_generation_analytics(),
            "enhancement_features": {
                "cinematic_prompts": True,
                "professional_camera_specs": True,
                "lighting_moods": len(self.lighting_descriptions),
                "cinematic_styles": len(self.camera_setups),
                "enhanced_scenarios": len(self.showcase_scenarios)
            },
            "recommendations": [
                "Используйте enhanced_prompts=True для кинематографического качества",
                "Экспериментируйте с разными cinematic_style и lighting_mood",
                "Golden hour освещение дает наиболее привлекательные результаты",
                "Commercial стиль подходит для YouTube, Lifestyle для Instagram",
                "Применяйте A/B тестирование между enhanced и traditional промптами"
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Отчет о производительности сохранен: {filename}")

def main():
    """Основная функция для демонстрации улучшений"""
    
    # Инициализация улучшенного генератора
    generator = SimpleTuranGenerator()
    
    # Конфигурация с улучшениями (всегда 8 секунд, только VEO 3.0)
    config = VideoGenerationConfig(
        model=VeoModel.VEO_3_GENERATE,
        duration_seconds=8,
        aspect_ratio=AspectRatio.LANDSCAPE,
        resolution=Resolution.FULL_HD,
        generate_audio=True,
        sample_count=1,
        # Новые улучшенные параметры
        cinematic_style=CinematicStyle.COMMERCIAL,
        lighting_mood=LightingMood.GOLDEN_HOUR,
        use_enhanced_prompts=True
    )
    
    # Пути к файлам
    images_folder = "images/dressing_tables"
    output_folder = "output/dressing_table_enhanced"
    storage_bucket = "gs://turan-videos/enhanced-dressing-tables/"
    
    try:
        Path(images_folder).mkdir(parents=True, exist_ok=True)
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        logger.info("🎬 Запуск улучшенного генератора видео показа туалетных столиков TURAN Lux")
        logger.info(f"📁 Папка изображений: {images_folder}")
        logger.info(f"📁 Папка вывода: {output_folder}")
        logger.info(f"🎥 Улучшения: Кинематографические промпты включены")
        
        # Показать доступные улучшенные сценарии
        scenarios = generator.get_all_scenarios()
        print(f"🎥 Доступно {len(scenarios)} улучшенных кинематографических сценариев:")
        for scenario in scenarios[:3]:  # Показать первые 3
            print(f"  • {scenario['id']}: {scenario['russian_voiceover']}")
            print(f"    Стиль: {scenario['cinematic_style']}, Освещение: {scenario['lighting_mood']}")
        
        # Обработка всех изображений с улучшениями
        results = generator.process_image_folder(
            images_folder, 
            output_folder, 
            config,
            storage_uri=storage_bucket
        )
        
        # Сохранение отчета
        report_path = Path(output_folder) / "enhanced_showcase_generation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Экспорт аналитики производительности
        generator.export_performance_report()
        
        # Статистика
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = len(results) - successful
        
        print(f"\n🎉 УЛУЧШЕННАЯ ГЕНЕРАЦИЯ ВИДЕО ПОКАЗА ЗАВЕРШЕНА!")
        print(f"✅ Успешно: {successful}")
        print(f"❌ Ошибки: {failed}")
        print(f"📊 Всего: {len(results)}")
        print(f"📄 Отчет: {report_path}")
        print(f"🎥 Сценарии: generated_showcase_scenarios.json")
        print(f"📈 Аналитика: turan_enhanced_performance_report.json")
        
        # Показать статистику улучшений
        analytics = generator.get_generation_analytics()
        print(f"\n📊 СТАТИСТИКА УЛУЧШЕНИЙ:")
        print(f"   🎬 Кинематографических промптов: {analytics['enhancement_usage_percentage']:.1f}%")
        print(f"   📝 Традиционных промптов: {analytics['traditional_usage_percentage']:.1f}%")
        print(f"   🏆 Популярные сценарии: {list(analytics['most_used_scenarios'].keys())[:3]}")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()