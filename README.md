### Первый запуск

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

# ------------------------------------------------

###     YouTube (горизонтальное, высокое качество)

python run_turan_generator.py \
  -i images/furniture \
  -o output/youtube \
  --model veo-3.0 \
  --duration 8 \
  --quality lossless

# ------------------------------------------------

###     Instagram Stories (вертикальное)

python run_turan_generator.py \
  -i images/furniture \
  -o output/instagram \
  --portrait \
  --duration 6


# ------------------------------------------------

###    TikTok (вертикальное, быстрое)

python run_turan_generator.py \
  -i images/furniture \
  -o output/tiktok \
  --model veo-3.0-fast \
  --portrait \
  --duration 6

# ------------------------------------------------

###    Быстрое превью

python run_turan_generator.py \
  -i images/furniture \
  -o output/preview \
  --preview


###   Кастомный промпт

python run_turan_generator.py \
  --single-image images/furniture/диван_люкс.jpg \
  --custom-prompt "Роскошный диван в стиле минимализм, TURAN качество, мягкое освещение" \
  -o output/custom

###   Несколько вариантов

python run_turan_generator.py \
  -i images/furniture \
  -o output/variants \
  --samples 3


###   С сохранением в Google Cloud Storage


python run_turan_generator.py \
  -i images/furniture \
  -o output/videos \
  --storage-uri gs://turan-videos/generated/


