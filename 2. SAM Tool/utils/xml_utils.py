import xml.etree.ElementTree as ET
import cv2
import numpy as np
import os


class XMLUtils:
    """Утилиты для XML"""

    @staticmethod
    def create_xml_annotation(
        xml_path, filename, folder_path, annotations, image_shape
    ):
        """Создание XML файла аннотации"""
        img_height, img_width = image_shape

        root = ET.Element("annotation")

        folder_elem = ET.SubElement(root, "folder")
        folder_elem.text = os.path.basename(folder_path)

        filename_elem = ET.SubElement(root, "filename")
        filename_elem.text = filename

        path_elem = ET.SubElement(root, "path")
        path_elem.text = os.path.join(folder_path, filename)

        size_elem = ET.SubElement(root, "size")
        ET.SubElement(size_elem, "width").text = str(img_width)
        ET.SubElement(size_elem, "height").text = str(img_height)
        ET.SubElement(size_elem, "depth").text = "3"

        ET.SubElement(root, "segmented").text = "1"

        for ann in annotations:
            obj_elem = ET.SubElement(root, "object")

            ET.SubElement(obj_elem, "name").text = ann["class"]
            ET.SubElement(obj_elem, "pose").text = "Unspecified"
            ET.SubElement(obj_elem, "truncated").text = "0"
            ET.SubElement(obj_elem, "difficult").text = "0"

            ET.SubElement(obj_elem, "annotation_type").text = ann["type"]

            if "timestamp" in ann:
                ET.SubElement(obj_elem, "timestamp").text = ann["timestamp"]

            if "sam_score" in ann:
                ET.SubElement(obj_elem, "confidence").text = str(ann["sam_score"])

            bbox = XMLUtils._get_bbox_from_annotation(ann)
            bbox_elem = ET.SubElement(obj_elem, "bndbox")
            ET.SubElement(bbox_elem, "xmin").text = str(bbox[0])
            ET.SubElement(bbox_elem, "ymin").text = str(bbox[1])
            ET.SubElement(bbox_elem, "xmax").text = str(bbox[2])
            ET.SubElement(bbox_elem, "ymax").text = str(bbox[3])

            if ann["points"]:
                points_elem = ET.SubElement(obj_elem, "points")
                for i, point in enumerate(ann["points"]):
                    point_elem = ET.SubElement(points_elem, f"point_{i}")
                    ET.SubElement(point_elem, "x").text = str(point[0])
                    ET.SubElement(point_elem, "y").text = str(point[1])

            if "mask" in ann and ann["mask"] is not None:
                mask_elem = ET.SubElement(obj_elem, "segmentation")
                polygons = XMLUtils._mask_to_polygons(ann["mask"])
                for i, polygon in enumerate(polygons):
                    poly_elem = ET.SubElement(mask_elem, f"polygon_{i}")
                    poly_elem.text = ",".join(map(str, polygon.flatten()))

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def _get_bbox_from_annotation(annotation):
        """Получение bbox из аннотации"""
        if "mask" in annotation and annotation["mask"] is not None:
            return XMLUtils._mask_to_bbox(annotation["mask"])
        elif "points" in annotation and annotation["points"]:
            return XMLUtils._points_to_bbox(annotation["points"])
        else:
            return [0, 0, 1, 1]

    @staticmethod
    def _mask_to_bbox(mask):
        """Получение bbox из маски"""
        coords = np.where(mask > 0)
        if len(coords[0]) == 0:
            return [0, 0, 1, 1]

        y_min, y_max = coords[0].min(), coords[0].max()
        x_min, x_max = coords[1].min(), coords[1].max()

        return [x_min, y_min, x_max, y_max]

    @staticmethod
    def _points_to_bbox(points):
        """Получение bbox из точек"""
        if not points:
            return [0, 0, 1, 1]

        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]

        return [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

    @staticmethod
    def _mask_to_polygons(mask):
        """Преобразование маски в полигоны"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        polygons = []

        for contour in contours:
            if len(contour) >= 3:
                epsilon = 0.005 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                polygons.append(approx.reshape(-1, 2))

        return polygons
