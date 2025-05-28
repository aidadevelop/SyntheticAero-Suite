import os
import numpy as np
import threading
from config import SAM_MODELS, MODELS_DIR


class SAMIntegration:
    """Класс для работы с SAM моделью"""

    def __init__(self):
        self.sam_predictor = None
        self.sam_loaded = False
        self.current_model_type = None

    def is_loaded(self):
        """Проверка загрузки модели"""
        return self.sam_loaded and self.sam_predictor is not None

    def load_model(self, callback=None, progress_callback=None):
        """Загрузка модели SAM в отдельном потоке"""

        def load_in_thread():
            try:
                if progress_callback:
                    progress_callback(25)

                try:
                    from segment_anything import sam_model_registry, SamPredictor
                    import torch
                except ImportError:
                    raise ImportError(
                        "Не установлена библиотека segment-anything.\n"
                        "Установите: pip install git+https://github.com/facebookresearch/segment-anything.git"
                    )

                if progress_callback:
                    progress_callback(50)

                model_path = self._find_model_file()
                if not model_path:
                    raise FileNotFoundError(
                        "Файл модели SAM не найден.\n"
                        "Скачайте одну из моделей:\n"
                        + "\n".join(
                            [f"wget {info['url']}" for info in SAM_MODELS.values()]
                        )
                    )

                if progress_callback:
                    progress_callback(75)

                model_type = self._get_model_type(model_path)

                sam = sam_model_registry[model_type](checkpoint=model_path)

                device = "cuda" if torch.cuda.is_available() else "cpu"
                sam.to(device=device)

                self.sam_predictor = SamPredictor(sam)
                self.sam_loaded = True
                self.current_model_type = model_type

                if progress_callback:
                    progress_callback(100)

                device_info = f" (GPU)" if device == "cuda" else " (CPU)"
                success_message = (
                    f"Модель SAM ({model_type.upper()}) загружена успешно\n"
                    f"Устройство: {device.upper()}"
                )

                if callback:
                    callback(True, success_message)

            except Exception as e:
                error_message = f"Не удалось загрузить модель SAM: {str(e)}"
                if callback:
                    callback(False, error_message)

        threading.Thread(target=load_in_thread, daemon=True).start()

    def _find_model_file(self):
        """Поиск файла модели SAM"""

        search_paths = [
            MODELS_DIR,
            os.getcwd(),
            os.path.join(os.getcwd(), "models"),
        ]

        for model_info in SAM_MODELS.values():
            filename = model_info["filename"]
            for search_path in search_paths:
                full_path = os.path.join(search_path, filename)
                if os.path.exists(full_path):
                    return full_path

        return None

    def _get_model_type(self, model_path):
        """Определение типа модели по пути к файлу"""
        filename = os.path.basename(model_path)
        for model_type, info in SAM_MODELS.items():
            if info["filename"] == filename:
                return model_type
        return "vit_h"

    def set_image(self, image):
        """Установка изображения для SAM"""
        if self.is_loaded():
            self.sam_predictor.set_image(image)

    def segment_point(self, x, y):
        """Сегментация по одной точке"""
        if not self.is_loaded():
            raise RuntimeError("Модель SAM не загружена")

        point_coords = np.array([[x, y]])
        point_labels = np.array([1])

        masks, scores, logits = self.sam_predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            multimask_output=True,
        )

        best_mask_idx = np.argmax(scores)
        mask = masks[best_mask_idx]
        score = scores[best_mask_idx]

        mask = (mask * 255).astype(np.uint8)

        return mask, score

    def segment_with_points(self, manual_points):
        """Сегментация с несколькими точками"""
        if not self.is_loaded():
            raise RuntimeError("Модель SAM не загружена")

        if not manual_points:
            raise ValueError("Нет точек для сегментации")

        if len(manual_points[0]) == 3:
            point_coords = np.array([(p[0], p[1]) for p in manual_points])
            point_labels = np.array([p[2] for p in manual_points])
        else:
            point_coords = np.array(manual_points)
            point_labels = np.ones(len(manual_points))

        masks, scores, logits = self.sam_predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            multimask_output=True,
        )

        best_mask_idx = np.argmax(scores)
        mask = masks[best_mask_idx]
        score = scores[best_mask_idx]

        mask = (mask * 255).astype(np.uint8)

        return mask, score

    def segment_with_bbox(self, bbox):
        """Сегментация с bounding box"""
        if not self.is_loaded():
            raise RuntimeError("Модель SAM не загружена")

        input_box = np.array(bbox)

        masks, scores, logits = self.sam_predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_box[None, :],
            multimask_output=False,
        )

        mask = masks[0]
        score = scores[0]

        mask = (mask * 255).astype(np.uint8)

        return mask, score

    def auto_segment_everything(self, image):
        """Автоматическая сегментация всего изображения"""
        if not self.is_loaded():
            raise RuntimeError("Модель SAM не загружена")

        try:
            from segment_anything import SamAutomaticMaskGenerator

            mask_generator = SamAutomaticMaskGenerator(
                model=self.sam_predictor.model,
                points_per_side=32,
                pred_iou_thresh=0.86,
                stability_score_thresh=0.92,
                crop_n_layers=1,
                crop_n_points_downscale_factor=2,
                min_mask_region_area=100,
            )

            masks = mask_generator.generate(image)
            return masks

        except ImportError:
            raise ImportError("SamAutomaticMaskGenerator недоступен")

    def get_model_info(self):
        """Получение информации о загруженной модели"""
        if self.is_loaded():
            return {
                "type": self.current_model_type,
                "name": SAM_MODELS[self.current_model_type]["name"],
                "loaded": True,
            }
        else:
            return {"loaded": False}
