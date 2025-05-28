import os

# Версия приложения
VERSION = "1.0.0"
APP_NAME = "SAM Tool"

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Поддерживаемые форматы изображений
SUPPORTED_IMAGE_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")

# Настройки SAM моделей
SAM_MODELS = {
    "vit_h": {
        "name": "ViT-H (Лучшая точность)",
        "filename": "sam_vit_h_4b8939.pth",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        "size": "2.6 GB",
    },
    "vit_l": {
        "name": "ViT-L (Средняя)",
        "filename": "sam_vit_l_0b3195.pth",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
        "size": "1.3 GB",
    },
    "vit_b": {
        "name": "ViT-B (Быстрая)",
        "filename": "sam_vit_b_01ec64.pth",
        "url": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth",
        "size": "0.4 GB",
    },
}

# Предустановленные классы объектов
DEFAULT_CLASSES = [
    "car",
    "person",
    "animal",
    "fire",
    "smoke",
    "forest_cut",
    "building",
    "road",
    "water",
    "vegetation",
]

# Цвета для классов (RGB)
CLASS_COLORS = {
    "car": (255, 0, 0),
    "person": (0, 255, 0),
    "animal": (0, 0, 255),
    "fire": (255, 165, 0),
    "smoke": (128, 128, 128),
    "forest_cut": (139, 69, 19),
    "building": (255, 20, 147),
    "road": (128, 128, 0),
    "water": (0, 191, 255),
    "vegetation": (34, 139, 34),
}

# Настройки интерфейса
UI_CONFIG = {
    "window_size": "1400x900",
    "canvas_bg": "white",
    "panel_bg": "#fafafa",
    "button_bg": "#4CAF50",
    "error_color": "#f44336",
    "success_color": "#4CAF50",
    "warning_color": "#FF9800",
}

# Настройки экспорта
EXPORT_CONFIG = {
    "xml_format": "pascal_voc",
    "csv_encoding": "utf-8",
    "image_quality": 95,
    "backup_annotations": True,
}


# Создание необходимых директорий
def create_directories():
    """Создание необходимых директорий"""
    dirs = [MODELS_DIR, TEMP_DIR]
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


# Инициализация при импорте
create_directories()
