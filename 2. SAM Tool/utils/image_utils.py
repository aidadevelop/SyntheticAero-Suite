import cv2
import numpy as np
from PIL import Image
import os

from config import SUPPORTED_IMAGE_FORMATS


class ImageUtils:
    """Утилиты для работы с изображениями"""

    @staticmethod
    def load_image(filepath):
        """Загрузка изображения из файла"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл не найден: {filepath}")

        image = cv2.imread(filepath)
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение: {filepath}")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image

    @staticmethod
    def save_image(image, filepath, quality=95):
        """Сохранение изображения в файл"""

        if len(image.shape) == 3:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image

        save_params = []
        ext = os.path.splitext(filepath)[1].lower()

        if ext in [".jpg", ".jpeg"]:
            save_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        elif ext == ".png":
            save_params = [cv2.IMWRITE_PNG_COMPRESSION, 9]

        success = cv2.imwrite(filepath, image_bgr, save_params)
        if not success:
            raise RuntimeError(f"Не удалось сохранить изображение: {filepath}")

    @staticmethod
    def scale_image_for_display(image, canvas_size, max_scale=1.0):
        """Масштабирование изображения для отображения на Canvas"""
        canvas_width, canvas_height = canvas_size
        img_height, img_width = image.shape[:2]

        scale_x = (canvas_width - 20) / img_width
        scale_y = (canvas_height - 20) / img_height
        scale = min(scale_x, scale_y, max_scale)

        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        scaled_image = cv2.resize(
            image, (new_width, new_height), interpolation=cv2.INTER_AREA
        )

        return scaled_image, scale

    @staticmethod
    def resize_image(image, target_size, keep_aspect_ratio=True):
        """Изменение размера изображения"""
        if keep_aspect_ratio:
            h, w = image.shape[:2]
            target_w, target_h = target_size

            scale = min(target_w / w, target_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)

            resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

            if new_w != target_w or new_h != target_h:

                result = np.zeros((target_h, target_w, 3), dtype=np.uint8)

                y_offset = (target_h - new_h) // 2
                x_offset = (target_w - new_w) // 2
                result[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = (
                    resized
                )

                return result
            else:
                return resized
        else:
            return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

    @staticmethod
    def crop_image(image, bbox):
        """Обрезка изображения по bounding box"""
        x_min, y_min, x_max, y_max = bbox
        h, w = image.shape[:2]

        x_min = max(0, min(x_min, w - 1))
        y_min = max(0, min(y_min, h - 1))
        x_max = max(x_min + 1, min(x_max, w))
        y_max = max(y_min + 1, min(y_max, h))

        return image[y_min:y_max, x_min:x_max]

    @staticmethod
    def apply_mask(image, mask, color=(255, 0, 0), alpha=0.3):
        """Применение маски к изображению с прозрачностью"""
        result = image.copy()

        if len(mask.shape) == 2:
            mask_3d = np.stack([mask] * 3, axis=-1)
        else:
            mask_3d = mask

        if mask_3d.max() > 1:
            mask_3d = mask_3d / 255.0

        colored_mask = np.zeros_like(result, dtype=np.float32)
        colored_mask[:, :] = color

        mask_area = mask_3d > 0.5
        result = result.astype(np.float32)
        result[mask_area] = (1 - alpha) * result[mask_area] + alpha * colored_mask[
            mask_area
        ]

        return result.astype(np.uint8)

    @staticmethod
    def enhance_image(image, brightness=0, contrast=1.0, saturation=1.0):
        """Улучшение изображения (яркость, контраст, насыщенность)"""
        result = image.copy().astype(np.float32)

        if brightness != 0:
            result = result + brightness

        if contrast != 1.0:
            result = result * contrast

        if saturation != 1.0:
            hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(
                np.float32
            )
            hsv[:, :, 1] = hsv[:, :, 1] * saturation
            hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
            result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(
                np.float32
            )

        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)

    @staticmethod
    def get_image_info(filepath):
        """Получение информации об изображении"""
        try:
            image = cv2.imread(filepath)
            if image is None:
                return None

            h, w, c = image.shape
            file_size = os.path.getsize(filepath)

            return {
                "width": w,
                "height": h,
                "channels": c,
                "file_size": file_size,
                "format": os.path.splitext(filepath)[1].lower(),
                "aspect_ratio": w / h,
            }
        except Exception:
            return None

    @staticmethod
    def is_supported_format(filepath):
        """Проверка поддержки формата изображения"""
        ext = os.path.splitext(filepath)[1].lower()
        return ext in SUPPORTED_IMAGE_FORMATS

    @staticmethod
    def convert_color_space(image, conversion):
        """Конвертация цветового пространства"""
        if conversion == "RGB2BGR":
            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        elif conversion == "BGR2RGB":
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif conversion == "RGB2HSV":
            return cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        elif conversion == "HSV2RGB":
            return cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
        elif conversion == "RGB2GRAY":
            return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            raise ValueError(f"Неподдерживаемая конвертация: {conversion}")

    @staticmethod
    def create_thumbnail(image, size=(150, 150)):
        """Создание миниатюры изображения"""
        return ImageUtils.resize_image(image, size, keep_aspect_ratio=True)
