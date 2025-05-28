# 🚁 SAM Tool

**Профессиональный инструмент для сегментации изображений с интеграцией SAM (Segment Anything Model)**

**Версия**: 1.0.0  
**Автор**: Команда хакатона A.I.C.O  
**Дата**: 28.05.2025

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)](https://opencv.org)
[![SAM](https://img.shields.io/badge/SAM-Meta-red.svg)](https://github.com/facebookresearch/segment-anything)

## 🎯 Возможности

- **Ручная разметка** - создание аннотаций кликами мыши
- **SAM автосегментация** - один клик для автоматической сегментации объекта
- **Множественные классы** - управление классами объектов
- **Экспорт данных** - XML (Pascal VOC), CSV для машинного обучения
- **Навигация по изображениям** - удобная работа с папками изображений

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Основные пакеты
pip install -r requirements.txt

# SAM модель
pip install git+https://github.com/facebookresearch/segment-anything.git

# PyTorch (выберите версию для вашей системы)
pip install torch torchvision torchaudio
```

### 2. Загрузка модели SAM

Скачайте одну из моделей SAM и поместите в папку `models/`:

```bash
# Лучшая точность (2.6 GB)
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

# Средняя модель (1.3 GB)
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth

# Быстрая модель (0.4 GB)
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
```

### 3. Запуск

```bash
python main.py
```

### 4. Создание исполняемого файла

```bash
python build_exe.py
```

## 📁 Структура проекта

```
sam_segmentation_tool/
├── main.py                   # Точка входа
├── config.py                 # Конфигурация
├── requirements.txt          # Зависимости
├── build_exe.py              # Создание exe
├── core/                     # Основная логика
│   ├── app.py                # Главное приложение
│   ├── sam_integration.py    # Интеграция SAM
│   ├── file_manager.py       # Работа с файлами
│   └── export_manager.py     # Экспорт данных
├── ui/                       # Интерфейс
│   ├── main_window.py        # Главное окно
│   ├── panels.py             # Панели UI
│   └── canvas_handler.py     # Canvas обработка
├── utils/                    # Утилиты
│   ├── image_utils.py        # Работа с изображениями
│   ├── annotation_utils.py   # Аннотации
│   └── xml_utils.py          # XML операции
└── models/                   # SAM модели
```

## 🎮 Использование

### Основные режимы работы:

1. **Ручная разметка**
   - Кликайте левой кнопкой для добавления точек
   - Правый клик для завершения области

2. **SAM автосегментация** 
   - Один клик - автоматическая сегментация объекта

### Горячие клавиши:

- `←/→` - Навигация по изображениям
- `Ctrl+S` - Сохранить XML
- `Ctrl+E` - Экспорт в CSV
- `Del` - Удалить выбранную аннотацию
- `Ctrl+Z` - Отменить последнее действие

## 📊 Форматы экспорта

### XML (Pascal VOC совместимый)
```xml
<annotation>
  <filename>image.jpg</filename>
  <object>
    <name>car</name>
    <bndbox>
      <xmin>100</xmin>
      <ymin>200</ymin>
      <xmax>300</xmax>
      <ymax>400</ymax>
    </bndbox>
    <segmentation>...</segmentation>
  </object>
</annotation>
```

### CSV для машинного обучения
```csv
filename,class,bbox_x_min,bbox_y_min,bbox_x_max,bbox_y_max,yolo_center_x,yolo_center_y,yolo_width,yolo_height
image.jpg,car,100,200,300,400,0.5,0.6,0.2,0.3
```

## ⚙️ Конфигурация

Настройки в `config.py`:

```python
# Классы объектов по умолчанию
DEFAULT_CLASSES = [
    'car', 'person', 'animal', 'fire', 'smoke', 
    'forest_cut', 'building', 'road', 'water', 'vegetation'
]

# Цвета для классов
CLASS_COLORS = {
    'car': (255, 0, 0),
    'person': (0, 255, 0),
    # ...
}
```

## 🔧 Разработка

### Создание исполняемого файла:

```bash
# PyInstaller (рекомендуется)
python build_exe.py

# Или вручную:
pyinstaller --onedir --windowed main.py
```

### Тестирование:

```bash
pip install pytest
pytest tests/
```

## 📋 Системные требования

- **Python**: 3.7+
- **ОС**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **RAM**: 8GB+ (16GB+ для больших изображений)
- **GPU**: CUDA совместимая (опционально, для ускорения SAM)