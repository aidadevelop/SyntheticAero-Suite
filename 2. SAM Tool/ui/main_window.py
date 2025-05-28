import tkinter as tk
from tkinter import ttk, simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np

from config import UI_CONFIG
from ui.panels import TopPanel, RightPanel, BottomPanel
from ui.canvas_handler import CanvasHandler


class MainWindow:
    """Класс главного окна приложения"""

    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.current_photo = None
        self.event_handlers = {}
        self.selected_class = tk.StringVar(value="car")
        self.mode_var = tk.StringVar(value="manual")
        self.progress_var = tk.DoubleVar()
        self.setup_ui()

    def setup_ui(self):
        """Создание интерфейса"""

        self.top_panel = TopPanel(self.root, self)

        main_frame = tk.Frame(self.root, bg=UI_CONFIG["panel_bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.setup_image_panel(main_frame)

        self.right_panel = RightPanel(main_frame, self)

        self.bottom_panel = BottomPanel(self.root, self)

        self.right_panel.update_class_list(self.app.available_classes)

    def setup_image_panel(self, parent):
        """Создание панели с изображением"""
        image_frame = tk.Frame(parent, bg="white", relief=tk.SUNKEN, bd=2)
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.canvas_handler = CanvasHandler(image_frame, self)

        info_frame = tk.Frame(image_frame, bg=UI_CONFIG["panel_bg"], height=30)
        info_frame.pack(fill=tk.X, side=tk.BOTTOM)
        info_frame.pack_propagate(False)

        self.image_info_label = tk.Label(
            info_frame,
            text="Изображение не загружено",
            bg=UI_CONFIG["panel_bg"],
            font=("Arial", 9),
        )
        self.image_info_label.pack(pady=5)

    def bind_events(self, handlers):
        """Привязка обработчиков событий"""
        self.event_handlers = handlers

        self.top_panel.bind_handlers(handlers)
        self.right_panel.bind_handlers(handlers)
        self.canvas_handler.bind_handlers(handlers)

    def get_canvas_size(self):
        """Получение размеров Canvas"""
        return self.canvas_handler.get_canvas_size()

    def display_image_on_canvas(self, image):
        """Отображение изображения на Canvas"""

        pil_image = Image.fromarray(image)
        self.current_photo = ImageTk.PhotoImage(pil_image)

        self.canvas_handler.display_image(self.current_photo)

    def canvas_to_image_coords(self, event, canvas_scale):
        """Преобразование координат Canvas в координаты изображения"""
        return self.canvas_handler.canvas_to_image_coords(event, canvas_scale)

    def update_status(self, message):
        """Обновление статусной строки"""
        self.bottom_panel.update_status(message)

    def set_progress(self, value):
        """Установка значения прогресс-бара"""
        self.progress_var.set(value)
        self.root.update_idletasks()

    def update_image_info(self, filename, shape, current_index, total_count):
        """Обновление информации об изображении"""
        height, width = shape[:2]
        info_text = f"{filename} | {width}x{height} | {current_index}/{total_count}"
        self.image_info_label.config(text=info_text)

    def get_current_mode(self):
        """Получение текущего режима работы"""
        return self.mode_var.get()

    def get_selected_class(self):
        """Получение выбранного класса"""
        return self.selected_class.get()

    def set_selected_class(self, class_name):
        """Установка выбранного класса"""
        self.selected_class.set(class_name)

    def update_class_list(self, classes):
        """Обновление списка классов"""
        self.right_panel.update_class_list(classes)

    def update_annotations_list(self, annotations):
        """Обновление списка аннотаций"""
        self.right_panel.update_annotations_list(annotations)

    def get_selected_annotation_index(self):
        """Получение индекса выбранной аннотации"""
        return self.right_panel.get_selected_annotation_index()

    def get_new_class_name(self):
        """Получение имени нового класса от пользователя"""
        return simpledialog.askstring("Новый класс", "Введите название нового класса:")
