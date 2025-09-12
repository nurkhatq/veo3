### 🎬 4. Первый запуск

```bash
# Быстрый тест (1 изображение, быстрая модель)
python run_turan_generator.py \
  --single-image images/furniture/диван.jpg \
  --output output/test \
  --preview

# Обработка всей папки
python run_turan_generator.py \
  --input images/furniture \
  --output output/videos

# Создание видео для всех соцсетей
python run_turan_generator.py \
  --input images/furniture \
  --output output/social \
  --batch-social-media
```

## 📱 Готовые команды для разных целей

### YouTube (горизонтальное, высокое качество)

```bash
python run_turan_generator.py \
  -i images/furniture \
  -o output/youtube \
  --model veo-3.0 \
  --duration 8 \
  --quality lossless
```

### Instagram Stories (вертикальное)

```bash
python run_turan_generator.py \
  -i images/furniture \
  -o output/instagram \
  --model veo-3.0
  --portrait \
  --duration 6
```

### TikTok (вертикальное, быстрое)

```bash
python run_turan_generator.py \
  -i images/furniture \
  -o output/tiktok \
  --model veo-3.0-fast \
  --portrait \
  --duration 6
```

### Быстрое превью

```bash
python run_turan_generator.py \
  -i images/furniture \
  -o output/preview \
  --preview
```

## 🎯 Примеры кастомизации

### Кастомный промпт

```bash
python run_turan_generator.py \
  --single-image images/furniture/диван_люкс.jpg \
  --custom-prompt "Роскошный диван в стиле минимализм, TURAN качество, мягкое освещение" \
  -o output/custom
```

### Несколько вариантов

```bash
python run_turan_generator.py \
  -i images/furniture \
  -o output/variants \
  --samples 3
```

### С сохранением в Google Cloud Storage

```bash
python run_turan_generator.py \
  -i images/furniture \
  -o output/videos \
  --storage-uri gs://turan-videos/generated/
```

## 🔧 Основные параметры

| Параметр       | Описание              | Примеры                   |
| -------------- | --------------------- | ------------------------- |
| `-i, --input`  | Папка с изображениями | `images/furniture`        |
| `-o, --output` | Папка для видео       | `output/videos`           |
| `--model`      | Модель Veo            | `veo-3.0`, `veo-3.0-fast` |
| `--duration`   | Длительность (сек)    | `4`, `6`, `8`             |
| `--portrait`   | Вертикальное видео    | Stories/TikTok            |
| `--hd`         | 720p вместо 1080p     | Быстрее                   |
| `--samples`    | Количество вариантов  | `1-4`                     |
| `--preview`    | Быстрый режим         | 4 сек, 720p               |
| `--no-audio`   | Без звука             | Быстрее                   |