# 🪞 TURAN Dressing Table Video Generator

Автоматическая генерация мемных вирусных видео для туалетных столиков TURAN Lux с помощью Google Veo 3.0 API.

## 🎯 Особенности

- **Только VEO 3.0** - Лучшее качество видео
- **8 секунд** - Оптимальная длительность для соцсетей
- **Мемный контент** - Вирусные ситуации и приколы
- **Английские промпты** - Высокое качество генерации
- **Русские описания** - Готовый контент для публикации
- **Автоматические хештеги** - SEO оптимизация

## 🛍️ Продукт: TURAN Lux Dressing Table

**Туалетный столик Lux** — стильное и функциональное решение:
- Белая закаленная стеклянная столешница
- 4 ящика (2 встроенных + 2 съемных)
- Зеркало с 3 режимами LED подсветки
- Металлические ножки + стул в комплекте
- Регулируемое расположение внешних ящиков

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка Google Cloud

```bash
# Установка gcloud CLI
gcloud auth application-default login
gcloud config set project turantt
```

### 3. Первый запуск

```bash
# Быстрый тест с одним изображением
python run_turan_dressing_table_generator.py \
  --single-image images/dressing_tables/туалетный_столик_lux.jpg \
  --output output/test

# Обработка всей папки
python run_turan_dressing_table_generator.py \
  --input images/dressing_tables \
  --output output/videos

# Создание для всех соцсетей
python run_turan_dressing_table_generator.py \
  --input images/dressing_tables \
  --output output/social \
  --batch-social-media
```

## 📱 Команды для разных платформ

### YouTube/Facebook (горизонтальное)

```bash
python run_turan_dressing_table_generator.py \
  -i images/dressing_tables \
  -o output/youtube \
  --samples 2
```

### Instagram Stories/TikTok (вертикальное)

```bash
python run_turan_dressing_table_generator.py \
  -i images/dressing_tables \
  -o output/instagram \
  --portrait
```

### Быстрое превью (720p)

```bash
python run_turan_dressing_table_generator.py \
  -i images/dressing_tables \
  -o output/preview \
  --hd
```

## 🎭 Мемные сценарии

Генератор автоматически создает вирусный контент на основе:

### 🌅 Утренний хаос
- Поиск косметики в 6 утра
- Попытки повторить макияж с TikTok
- Опоздание на работу

### 👨‍👩‍👧‍👦 Семейные приколы
- Мама vs дочка за зеркалом
- Прятание покупок в ящиках
- Подготовка к первому свиданию

### 🎉 Праздники и события
- Новогодняя подготовка в 23:58
- Свадебные сборы с подружками
- Первый день на новой работе

### 📱 Современные проблемы
- Стрим макияжа с провалами
- Instagram vs реальность
- Видеозвонки во время сборов

### 🐱 Домашние животные
- Кот идет по косметике
- Собака ворует кисти
- Питомцы мешают макияжу

## 🛠️ Параметры команд

| Параметр | Описание | Примеры |
|----------|----------|---------|
| `-i, --input` | Папка с изображениями | `images/dressing_tables` |
| `-o, --output` | Папка для видео | `output/videos` |
| `--portrait` | Вертикальное видео | Stories/TikTok |
| `--hd` | 720p вместо 1080p | Быстрее |
| `--samples` | Количество вариантов | `1-3` |
| `--no-audio` | Без звука | Тишина |
| `--custom-prompt` | Свой промпт (англ.) | Творчество |

## 🎨 Кастомизация

### Свой мемный промпт

```bash
python run_turan_dressing_table_generator.py \
  --single-image images/dressing_tables/столик.jpg \
  --custom-prompt "Woman hiding expensive makeup purchases in TURAN Lux dressing table drawers from husband, guilty expression, comedy gold" \
  -o output/custom
```

### Несколько вариантов

```bash
python run_turan_dressing_table_generator.py \
  -i images/dressing_tables \
  -o output/variants \
  --samples 3
```

### С сохранением в Cloud Storage

```bash
python run_turan_dressing_table_generator.py \
  -i images/dressing_tables \
  -o output/videos \
  --storage-uri gs://turan-videos/dressing-tables/
```

## 📊 Результаты с JSON структурой

После генерации вы получите:

### 🎬 Видео файлы
- `turan_lux_[scenario_id]_[название]_v0.mp4`
- Формат: MP4, 8 секунд
- Качество: 1080p или 720p  
- Русская озвучка с эмоциями

### 📝 JSON отчеты
- `generated_scenarios.json` - Информация о сценариях
- `meme_generation_report.json` - Статистика генерации

### 🎭 Пример JSON сценария:
```json
{
  "столик_lux.jpg": {
    "scenario_id": "cat_chaos_1",
    "category": "pets",
    "emotion": "surprised_laughter", 
    "english_prompt": "Preserve dressing table from image. Add: Cat jumps onto glass surface...",
    "russian_voiceover": "Когда кот решил помочь с макияжем! Столик TURAN выдержит всё!",
    "timestamp": "2024-01-15 14:30:22"
  }
}
```

### 📱 Готовый контент для постов
- Русский текст готов для копирования
- Хештеги автоматически подобраны
- Эмоции для engagement

## 🛠️ Параметры команд

## 🎯 Примеры контента

### Русские описания (автогенерируемые):
- "Когда проснулась за 5 минут до работы, а туалетный столик TURAN стал твоим спасением 💅"
- "POV: Прячешь покупки с Wildberries в ящики туалетного столика от мужа 🤫"
- "Мама vs дочка за зеркалом туалетного столика TURAN - битва поколений 😂"

### Английские промпты (для качества):
- "Luxurious white glass dressing table with LED mirror lighting, woman frantically searching for makeup at 6 AM, dramatic morning chaos"
- "Beautiful white dressing table setup, woman hiding online shopping packages in the 4 drawers from husband, sneaky behavior"

## 🔧 Структура проекта

```
turan-dressing-table-generator/
├── main.py                                    # Основной модуль
├── run_turan_dressing_table_generator.py     # CLI runner
├── dressing_table_config.yaml               # Конфигурация
├── requirements.txt                          # Зависимости
├── images/dressing_tables/                   # Входные изображения
├── output/dressing_table_videos/            # Готовые видео
├── content_descriptions.json                # Русские описания
└── logs/                                    # Логи работы
```

## 📱 Социальные сети

### TikTok оптимизация
- Вертикальное видео 9:16
- 8 секунд - идеально для зацикливания
- Мемный контент с хуками

### Instagram Stories/Reels
- Портретный формат
- Яркие эмоции и релевантность
- Готовые хештеги

### YouTube Shorts
- Горизонтальное видео
- Качество 1080p
- Кинематографическая подача

## 🎪 Показать примеры описаний

```bash
python run_turan_dressing_table_generator.py --show-descriptions
```

## ⚡ Производительность

- **Модель**: Только VEO 3.0 (лучшее качество)
- **Время**: ~2-5 минут на видео
- **Параллельность**: 2-3 операции одновременно
- **Размер**: ~10-50 МБ на видео

## 🔍 Отладка

### Посмотреть план без выполнения

```bash
python run_turan_dressing_table_generator.py \
  -i images/dressing_tables \
  -o output/test \
  --dry-run --verbose
```

### Подробные логи

```bash
python run_turan_dressing_table_generator.py \
  -i images/dressing_tables \
  -o output/debug \
  --verbose
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте аутентификацию: `gcloud auth list`
2. Убедитесь в наличии изображений в папке
3. Проверьте логи: `turan_dressing_table_generator.log`
4. Формат изображений: JPG, PNG, WEBP

## 🚀 Дальнейшее развитие

- [ ] Автоматическая публикация в соцсети
- [ ] A/B тестирование промптов
- [ ] Интеграция с аналитикой
- [ ] Голосовая озвучка на русском
- [ ] Персонализация под аудиторию

---

**TURAN Lux** - Красота начинается с правильного туалетного столика! 🪞✨