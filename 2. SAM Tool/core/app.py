import tkinter as tk
from tkinter import messagebox
import numpy as np
import cv2
from datetime import datetime
import os
from config import *
from ui.main_window import MainWindow
from core.sam_integration import SAMIntegration
from core.file_manager import FileManager
from core.export_manager import ExportManager
from utils.image_utils import ImageUtils
from utils.annotation_utils import AnnotationUtils


class SAMSegmentationApp:
    """Главный класс приложения"""

    def __init__(self, root):
        self.root = root
        self.setup_window()

        # Инициализация компонентов
        self.file_manager = FileManager()
        self.export_manager = ExportManager()
        self.sam_integration = SAMIntegration()
        self.image_utils = ImageUtils()
        self.annotation_utils = AnnotationUtils()

        # Данные приложения
        self.current_folder = ""
        self.image_files = []
        self.current_image_index = 0
        self.current_image = None
        self.annotations = {}
        self.available_classes = DEFAULT_CLASSES.copy()
        self.manual_points = []
        self.canvas_scale = 1.0

        # Создание интерфейса
        self.ui = MainWindow(root, self)

        # Настройка обработчиков событий
        self.setup_event_handlers()

    def setup_window(self):
        """Настройка главного окна"""
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry(UI_CONFIG["window_size"])
        self.root.configure(bg="#f0f0f0")
        self.root.minsize(1000, 700)

    def setup_event_handlers(self):
        """Настройка обработчиков событий"""
        # Привязка обработчиков к UI элементам
        self.ui.bind_events(
            {
                "select_folder": self.select_folder,
                "load_sam": self.load_sam_model,
                "prev_image": self.prev_image,
                "next_image": self.next_image,
                "save_xml": self.save_current_xml,
                "export_csv": self.export_to_csv,
                "canvas_click": self.on_canvas_click,
                "canvas_right_click": self.on_canvas_right_click,
                "canvas_motion": self.on_canvas_motion,
                "delete_annotation": self.delete_annotation,
                "clear_annotations": self.clear_all_annotations,
                "add_class": self.add_new_class,
                "remove_class": self.remove_class,
                "clear_points": self.clear_manual_points,
                "undo_action": self.undo_last_action,
            }
        )

    def select_folder(self):
        """Выбор папки с изображениями"""
        folder = self.file_manager.select_image_folder()
        if folder:
            self.current_folder = folder
            self.load_images_from_folder()

    def load_images_from_folder(self):
        """Загрузка списка изображений из папки"""
        self.image_files = self.file_manager.get_image_files(self.current_folder)

        if self.image_files:
            self.current_image_index = 0
            self.load_current_image()
            self.ui.update_status(f"Загружено {len(self.image_files)} изображений")
        else:
            messagebox.showwarning(
                "Предупреждение", "В выбранной папке нет поддерживаемых изображений"
            )

    def load_current_image(self):
        """Загрузка текущего изображения"""
        if not self.image_files:
            return

        filename = self.image_files[self.current_image_index]
        filepath = os.path.join(self.current_folder, filename)

        try:
            # Загрузка изображения
            self.current_image = self.image_utils.load_image(filepath)

            # Загрузка для SAM если модель загружена
            if self.sam_integration.is_loaded():
                self.sam_integration.set_image(self.current_image)

            # Отображение
            self.display_image()

            # Загрузка существующих аннотаций
            self.load_annotations_for_current_image()

            # Обновление информации
            self.ui.update_image_info(
                filename,
                self.current_image.shape,
                self.current_image_index + 1,
                len(self.image_files),
            )

        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Не удалось загрузить изображение: {str(e)}"
            )

    def display_image(self):
        """Отображение изображения на Canvas"""
        if self.current_image is None:
            return

        # Получение размеров Canvas
        canvas_size = self.ui.get_canvas_size()
        if canvas_size[0] <= 1 or canvas_size[1] <= 1:
            self.root.after(100, self.display_image)
            return

        # Масштабирование изображения
        display_image, self.canvas_scale = self.image_utils.scale_image_for_display(
            self.current_image, canvas_size
        )

        # Наложение аннотаций
        display_image = self.overlay_annotations(display_image)

        # Отображение на Canvas
        self.ui.display_image_on_canvas(display_image)

    def overlay_annotations(self, image):
        """Наложение аннотаций на изображение"""
        display_image = image.copy()
        current_filename = self.image_files[self.current_image_index]

        if current_filename in self.annotations:
            display_image = self.annotation_utils.draw_annotations(
                display_image,
                self.annotations[current_filename],
                self.canvas_scale,
                CLASS_COLORS,
            )

        # Отображение текущих точек
        display_image = self.annotation_utils.draw_manual_points(
            display_image, self.manual_points, self.canvas_scale
        )

        return display_image

    def on_canvas_click(self, event):
        """Обработка клика по Canvas"""
        if self.current_image is None:
            return

        # Получение координат на оригинальном изображении
        orig_coords = self.ui.canvas_to_image_coords(event, self.canvas_scale)
        if not orig_coords:
            return

        orig_x, orig_y = orig_coords
        mode = self.ui.get_current_mode()

        if mode == "manual":
            self.manual_points.append((orig_x, orig_y))
            self.display_image()
            self.ui.update_status(
                f"Добавлена точка: ({orig_x}, {orig_y}). "
                f"Всего: {len(self.manual_points)}"
            )

        elif mode == "sam_points" and self.sam_integration.is_loaded():
            # Shift + клик = отрицательная точка
            # Добавляем точку с меткой (positive/negative)
            point_label = 0 if event.state & 0x1 else 1
            self.manual_points.append((orig_x, orig_y, point_label))

            self.display_image()
            point_type = "отрицательная" if point_label == 0 else "положительная"
            self.ui.update_status(f"Добавлена {point_type} точка: ({orig_x}, {orig_y})")

        elif mode == "sam_auto" and self.sam_integration.is_loaded():
            self.run_sam_auto_segmentation(orig_x, orig_y)

    def on_canvas_right_click(self, event):
        """Обработка правого клика - завершение ручной аннотации"""
        if self.ui.get_current_mode() == "manual" and len(self.manual_points) >= 3:
            self.create_manual_annotation()

    def on_canvas_motion(self, event):
        """Обработка движения мыши"""
        if self.current_image is None:
            return

        orig_coords = self.ui.canvas_to_image_coords(event, self.canvas_scale)
        if orig_coords:
            self.ui.update_status(f"Координаты: ({orig_coords[0]}, {orig_coords[1]})")

    def create_manual_annotation(self):
        """Создание ручной аннотации из точек"""
        if len(self.manual_points) < 3:
            messagebox.showwarning(
                "Предупреждение", "Нужно минимум 3 точки для создания аннотации"
            )
            return

        current_filename = self.image_files[self.current_image_index]

        # Создание маски из точек
        mask = self.annotation_utils.points_to_mask(
            self.manual_points, self.current_image.shape[:2]
        )

        annotation = {
            "class": self.ui.get_selected_class(),
            "points": self.manual_points.copy(),
            "mask": mask,
            "type": "manual",
            "timestamp": datetime.now().isoformat(),
        }

        self.add_annotation(current_filename, annotation)

    def run_sam_segmentation_with_points(self):
        """Запуск SAM сегментации с точками"""
        if not self.sam_integration.is_loaded() or not self.manual_points:
            return

        try:
            mask, score = self.sam_integration.segment_with_points(self.manual_points)

            current_filename = self.image_files[self.current_image_index]
            points_coords = [
                (p[0], p[1]) if len(p) == 3 else p for p in self.manual_points
            ]

            annotation = {
                "class": self.ui.get_selected_class(),
                "points": points_coords,
                "mask": mask,
                "type": "sam_points",
                "timestamp": datetime.now().isoformat(),
                "sam_score": float(score),
            }

            self.add_annotation(current_filename, annotation)
            self.ui.update_status(f"SAM сегментация выполнена (score: {score:.3f})")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка SAM сегментации: {str(e)}")

    def run_sam_auto_segmentation(self, x, y):
        """Запуск автоматической SAM сегментации"""
        if not self.sam_integration.is_loaded():
            messagebox.showwarning("Предупреждение", "Модель SAM не загружена")
            return

        try:
            mask, score = self.sam_integration.segment_point(x, y)

            current_filename = self.image_files[self.current_image_index]

            annotation = {
                "class": self.ui.get_selected_class(),
                "points": [(x, y)],
                "mask": mask,
                "type": "sam_auto",
                "timestamp": datetime.now().isoformat(),
                "sam_score": float(score),
            }

            self.add_annotation(current_filename, annotation)
            self.ui.update_status(f"SAM автосегментация выполнена (score: {score:.3f})")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка SAM автосегментации: {str(e)}")

    def add_annotation(self, filename, annotation):
        """Добавление аннотации"""
        if filename not in self.annotations:
            self.annotations[filename] = []

        self.annotations[filename].append(annotation)

        # Очистка точек и обновление отображения
        self.manual_points.clear()
        self.display_image()
        self.ui.update_annotations_list(self.get_current_annotations())

    def get_current_annotations(self):
        """Получение аннотаций текущего изображения"""
        if not self.image_files:
            return []

        current_filename = self.image_files[self.current_image_index]
        return self.annotations.get(current_filename, [])

    def load_sam_model(self):
        """Загрузка модели SAM"""

        def load_callback(success, message):
            if success:
                self.ui.update_status("Модель SAM загружена успешно")
                messagebox.showinfo("Успех", message)
            else:
                self.ui.update_status("Ошибка загрузки SAM")
                messagebox.showerror("Ошибка", message)
            self.ui.set_progress(0)

        def progress_callback(progress):
            self.ui.set_progress(progress)

        self.sam_integration.load_model(load_callback, progress_callback)

    def prev_image(self):
        """Переход к предыдущему изображению"""
        if self.image_files and self.current_image_index > 0:
            self.save_current_annotations()
            self.current_image_index -= 1
            self.load_current_image()

    def next_image(self):
        """Переход к следующему изображению"""
        if self.image_files and self.current_image_index < len(self.image_files) - 1:
            self.save_current_annotations()
            self.current_image_index += 1
            self.load_current_image()

    def save_current_annotations(self):
        """Сохранение аннотаций текущего изображения"""
        if not self.image_files:
            return

        current_filename = self.image_files[self.current_image_index]
        if current_filename in self.annotations and self.annotations[current_filename]:
            self.file_manager.save_annotations_json(
                self.current_folder,
                current_filename,
                self.annotations[current_filename],
            )

    def load_annotations_for_current_image(self):
        """Загрузка аннотаций для текущего изображения"""
        if not self.image_files:
            return

        current_filename = self.image_files[self.current_image_index]
        annotations = self.file_manager.load_annotations_json(
            self.current_folder, current_filename
        )

        if annotations:
            self.annotations[current_filename] = annotations
        elif current_filename not in self.annotations:
            self.annotations[current_filename] = []

        self.ui.update_annotations_list(self.get_current_annotations())

    def save_current_xml(self):
        """Сохранение XML файла для текущего изображения"""
        if not self.image_files:
            messagebox.showwarning("Предупреждение", "Нет загруженных изображений")
            return

        current_filename = self.image_files[self.current_image_index]
        annotations = self.get_current_annotations()

        if not annotations:
            messagebox.showwarning("Предупреждение", "Нет аннотаций для сохранения")
            return

        try:
            xml_path = self.export_manager.save_xml_annotation(
                self.current_folder,
                current_filename,
                annotations,
                self.current_image.shape[:2],
            )

            messagebox.showinfo(
                "Успех", f"XML файл сохранен: {os.path.basename(xml_path)}"
            )
            self.ui.update_status(f"Сохранен XML: {os.path.basename(xml_path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить XML: {str(e)}")

    def export_to_csv(self):
        """Экспорт всех аннотаций в CSV файл"""
        if not self.annotations:
            messagebox.showwarning("Предупреждение", "Нет аннотаций для экспорта")
            return

        try:
            csv_path = self.export_manager.export_to_csv(
                self.annotations, self.current_folder, self.available_classes
            )

            messagebox.showinfo(
                "Успех", f"CSV файл сохранен: {os.path.basename(csv_path)}"
            )
            self.ui.update_status(f"Экспортирован CSV: {os.path.basename(csv_path)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать CSV: {str(e)}")

    # Остальные методы (delete_annotation, clear_all_annotations, и т.д.)
    def delete_annotation(self):
        """Удаление выбранной аннотации"""
        selection_index = self.ui.get_selected_annotation_index()
        if selection_index is None:
            messagebox.showwarning("Предупреждение", "Выберите аннотацию для удаления")
            return

        current_annotations = self.get_current_annotations()
        if selection_index < len(current_annotations):
            deleted_ann = current_annotations.pop(selection_index)
            self.ui.update_annotations_list(current_annotations)
            self.display_image()
            self.ui.update_status(f"Удалена аннотация класса '{deleted_ann['class']}'")

    def clear_all_annotations(self):
        """Очистка всех аннотаций текущего изображения"""
        if not self.image_files:
            return

        result = messagebox.askyesno(
            "Подтверждение", "Удалить все аннотации текущего изображения?"
        )
        if result:
            current_filename = self.image_files[self.current_image_index]
            if current_filename in self.annotations:
                count = len(self.annotations[current_filename])
                self.annotations[current_filename] = []
                self.ui.update_annotations_list([])
                self.display_image()
                self.ui.update_status(f"Удалено {count} аннотаций")

    def add_new_class(self):
        """Добавление нового класса"""
        new_class = self.ui.get_new_class_name()
        if new_class and new_class not in self.available_classes:
            self.available_classes.append(new_class)
            self.ui.update_class_list(self.available_classes)
            self.ui.set_selected_class(new_class)
            self.ui.update_status(f"Добавлен новый класс: '{new_class}'")
        elif new_class:
            messagebox.showwarning("Предупреждение", "Такой класс уже существует")

    def remove_class(self):
        """Удаление класса"""
        if len(self.available_classes) <= 1:
            messagebox.showwarning("Предупреждение", "Нельзя удалить последний класс")
            return

        current_class = self.ui.get_selected_class()
        result = messagebox.askyesno(
            "Подтверждение", f"Удалить класс '{current_class}'?"
        )
        if result:
            self.available_classes.remove(current_class)
            self.ui.update_class_list(self.available_classes)
            self.ui.set_selected_class(self.available_classes[0])
            self.ui.update_status(f"Удален класс: '{current_class}'")

    def clear_manual_points(self):
        """Очистка текущих точек"""
        self.manual_points.clear()
        self.display_image()
        self.ui.update_status("Точки очищены")

    def undo_last_action(self):
        """Отмена последнего действия"""
        if not self.image_files:
            return

        current_annotations = self.get_current_annotations()
        if current_annotations:
            removed_ann = current_annotations.pop()
            self.ui.update_annotations_list(current_annotations)
            self.display_image()
            self.ui.update_status(f"Отменена аннотация класса '{removed_ann['class']}'")
        elif self.manual_points:
            self.manual_points.pop()
            self.display_image()
            self.ui.update_status("Удалена последняя точка")
        else:
            self.ui.update_status("Нечего отменять")
