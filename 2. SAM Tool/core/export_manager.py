import os
import pandas as pd
import cv2
import numpy as np
from tkinter import filedialog
from utils.xml_utils import XMLUtils


class ExportManager:
    """Класс для экспорта данных"""

    def save_xml_annotation(self, folder_path, filename, annotations, image_shape):
        """Сохранение аннотации в XML формате"""
        xml_filename = os.path.splitext(filename)[0] + ".xml"
        xml_path = os.path.join(folder_path, xml_filename)

        XMLUtils.create_xml_annotation(
            xml_path, filename, folder_path, annotations, image_shape
        )

        return xml_path

    def export_to_csv(self, all_annotations, base_folder, available_classes):
        """Экспорт всех аннотаций в CSV"""
        csv_path = filedialog.asksaveasfilename(
            title="Сохранить CSV файл",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )

        if not csv_path:
            return None

        data = []

        for filename, annotations in all_annotations.items():
            if not annotations:
                continue

            image_path = os.path.join(base_folder, filename)

            img = cv2.imread(image_path)
            if img is None:
                continue

            img_height, img_width = img.shape[:2]

            for ann in annotations:
                bbox = self._get_bbox_from_annotation(ann, img_width, img_height)

                norm_bbox = [
                    bbox[0] / img_width,
                    bbox[1] / img_height,
                    bbox[2] / img_width,
                    bbox[3] / img_height,
                ]

                center_x = (norm_bbox[0] + norm_bbox[2]) / 2
                center_y = (norm_bbox[1] + norm_bbox[3]) / 2
                width = norm_bbox[2] - norm_bbox[0]
                height = norm_bbox[3] - norm_bbox[1]

                data.append(
                    {
                        "filename": filename,
                        "image_path": image_path,
                        "image_width": img_width,
                        "image_height": img_height,
                        "class": ann["class"],
                        "annotation_type": ann["type"],
                        "bbox_x_min": bbox[0],
                        "bbox_y_min": bbox[1],
                        "bbox_x_max": bbox[2],
                        "bbox_y_max": bbox[3],
                        "normalized_x_min": norm_bbox[0],
                        "normalized_y_min": norm_bbox[1],
                        "normalized_x_max": norm_bbox[2],
                        "normalized_y_max": norm_bbox[3],
                        "yolo_center_x": center_x,
                        "yolo_center_y": center_y,
                        "yolo_width": width,
                        "yolo_height": height,
                        "timestamp": ann.get("timestamp", ""),
                        "sam_score": ann.get("sam_score", 0.0),
                    }
                )

        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False, encoding="utf-8")

        self._create_yolo_format(csv_path, df, available_classes)

        return csv_path

    def _get_bbox_from_annotation(self, annotation, img_width, img_height):
        """Получение bbox из аннотации"""
        if "mask" in annotation and annotation["mask"] is not None:
            return self._mask_to_bbox(annotation["mask"])
        elif "points" in annotation and annotation["points"]:
            return self._points_to_bbox(annotation["points"])
        else:
            return [0, 0, 1, 1]

    def _mask_to_bbox(self, mask):
        """Получение bbox из маски"""
        coords = np.where(mask > 0)
        if len(coords[0]) == 0:
            return [0, 0, 1, 1]

        y_min, y_max = coords[0].min(), coords[0].max()
        x_min, x_max = coords[1].min(), coords[1].max()

        return [x_min, y_min, x_max, y_max]

    def _points_to_bbox(self, points):
        """Получение bbox из точек"""
        if not points:
            return [0, 0, 1, 1]

        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

        return [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

    def _create_yolo_format(self, csv_path, df, available_classes):
        """Создание YOLO формата"""
        yolo_path = csv_path.replace(".csv", "_yolo.txt")
        with open(yolo_path, "w") as f:
            for _, row in df.iterrows():
                class_id = available_classes.index(row["class"])
                f.write(
                    f"{class_id} {row['yolo_center_x']:.6f} {row['yolo_center_y']:.6f} "
                    f"{row['yolo_width']:.6f} {row['yolo_height']:.6f}\n"
                )
