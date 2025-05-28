import os
import json
import numpy as np
from tkinter import filedialog
from config import SUPPORTED_IMAGE_FORMATS


class FileManager:
    """Класс для работы с файлами"""

    def select_image_folder(self):
        """Выбор папки с изображениями"""
        return filedialog.askdirectory(title="Выберите папку с изображениями")

    def get_image_files(self, folder_path):
        """Получение списка файлов изображений"""
        if not os.path.exists(folder_path):
            return []

        image_files = []
        for file in os.listdir(folder_path):
            if file.lower().endswith(SUPPORTED_IMAGE_FORMATS):
                image_files.append(file)

        return sorted(image_files)

    def save_annotations_json(self, folder_path, filename, annotations):
        """Сохранение аннотаций в JSON"""
        json_path = os.path.join(folder_path, f"{filename}_annotations.json")

        json_data = []
        for ann in annotations:
            ann_copy = ann.copy()
            if "mask" in ann_copy and ann_copy["mask"] is not None:
                ann_copy["mask"] = ann_copy["mask"].tolist()
            json_data.append(ann_copy)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

    def load_annotations_json(self, folder_path, filename):
        """Загрузка аннотаций из JSON"""
        json_path = os.path.join(folder_path, f"{filename}_annotations.json")

        if not os.path.exists(json_path):
            return []

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            annotations = []
            for ann in json_data:
                if "mask" in ann and ann["mask"] is not None:
                    ann["mask"] = np.array(ann["mask"], dtype=np.uint8)
                annotations.append(ann)

            return annotations
        except Exception as e:
            print(f"Ошибка загрузки JSON: {e}")
            return []
