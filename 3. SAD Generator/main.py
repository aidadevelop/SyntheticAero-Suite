import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import cv2
import numpy as np
from PIL import Image, ImageTk
import json
import random
from pathlib import Path

class SyntheticDataGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор синтетических данных аэрофотосъемки")
        self.root.geometry("1200x800")
        
        
        self.background_folder = tk.StringVar()
        self.assets_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        
        
        self.background_images = []
        self.asset_objects = {}
        self.current_preview = None
        
        self.setup_ui()
        self.load_default_assets()
    
    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        
        paths_frame = ttk.LabelFrame(main_frame, text="Настройка путей", padding="10")
        paths_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        
        ttk.Label(paths_frame, text="Папка с фоновыми изображениями:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(paths_frame, textvariable=self.background_folder, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(paths_frame, text="Обзор", command=self.select_background_folder).grid(row=0, column=2)
        
        
        ttk.Label(paths_frame, text="Папка с объектами (assets):").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(paths_frame, textvariable=self.assets_folder, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(paths_frame, text="Обзор", command=self.select_assets_folder).grid(row=1, column=2)
        
        
        ttk.Label(paths_frame, text="Папка для сохранения:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(paths_frame, textvariable=self.output_folder, width=50).grid(row=2, column=1, padx=5)
        ttk.Button(paths_frame, text="Обзор", command=self.select_output_folder).grid(row=2, column=2)
        
        
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки генерации", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), pady=5)
        
        
        ttk.Label(settings_frame, text="Макс. объектов на изображение:").grid(row=0, column=0, sticky=tk.W)
        self.max_objects = tk.IntVar(value=5)
        ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.max_objects, width=10).grid(row=0, column=1)
        
        
        ttk.Label(settings_frame, text="Количество изображений:").grid(row=1, column=0, sticky=tk.W)
        self.num_images = tk.IntVar(value=10)
        ttk.Spinbox(settings_frame, from_=1, to=1000, textvariable=self.num_images, width=10).grid(row=1, column=1)
        
        
        controls_frame = ttk.Frame(settings_frame)
        controls_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(controls_frame, text="Загрузить изображения", command=self.load_background_images).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Предварительный просмотр", command=self.preview_generation).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Генерировать датасет", command=self.generate_dataset).pack(side=tk.LEFT, padx=5)
        
        
        preview_frame = ttk.LabelFrame(main_frame, text="Предварительный просмотр", padding="10")
        preview_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        self.preview_label = ttk.Label(preview_frame, text="Выберите изображения для предварительного просмотра")
        self.preview_label.pack(expand=True)
        
        
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        
        log_frame = ttk.LabelFrame(main_frame, text="Лог операций", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=8)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def select_background_folder(self):
        """Выбор папки с фоновыми изображениями"""
        folder = filedialog.askdirectory()
        if folder:
            self.background_folder.set(folder)
            self.log_message(f"Выбрана папка с фонами: {folder}")
    
    def select_assets_folder(self):
        """Выбор папки с объектами"""
        folder = filedialog.askdirectory()
        if folder:
            self.assets_folder.set(folder)
            self.log_message(f"Выбрана папка с объектами: {folder}")
            self.load_assets()
    
    def select_output_folder(self):
        """Выбор выходной папки"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)
            self.log_message(f"Выбрана выходная папка: {folder}")
    
    def load_default_assets(self):
        """Загрузка стандартных категорий объектов"""
        self.asset_objects = {
            'vehicles': [],    
            'people': [],      
            'animals': [],     
            'fire': [],        
            'smoke': [],       
            'trees': [],       
            'aircraft': [],    
            'boats': []        
        }
        
        self.log_message("Инициализированы категории объектов:")
        self.log_message("- vehicles: наземный транспорт")
        self.log_message("- people: люди")
        self.log_message("- animals: животные") 
        self.log_message("- fire: огонь")
        self.log_message("- smoke: дым")
        self.log_message("- trees: деревья")
        self.log_message("- aircraft: воздушный транспорт")
        self.log_message("- boats: водный транспорт")
    
    def load_background_images(self):
        """Загрузка фоновых изображений"""
        if not self.background_folder.get():
            messagebox.showerror("Ошибка", "Выберите папку с фоновыми изображениями")
            return
        
        folder = self.background_folder.get()
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        self.background_images = []
        
        for file_path in Path(folder).rglob('*'):
            if file_path.suffix.lower() in supported_formats:
                self.background_images.append(str(file_path))
        
        self.log_message(f"Загружено {len(self.background_images)} фоновых изображений")
        
        if len(self.background_images) == 0:
            messagebox.showwarning("Предупреждение", "В выбранной папке не найдено подходящих изображений")
    
    def load_assets(self):
        """Загрузка объектов из папки assets"""
        if not self.assets_folder.get():
            return
        
        assets_path = Path(self.assets_folder.get())
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp']
        
        
        for category in self.asset_objects:
            self.asset_objects[category] = []
        
        
        for category in self.asset_objects.keys():
            category_path = assets_path / category
            if category_path.exists():
                for file_path in category_path.rglob('*'):
                    if file_path.suffix.lower() in supported_formats:
                        self.asset_objects[category].append(str(file_path))
        
        total_assets = sum(len(assets) for assets in self.asset_objects.values())
        self.log_message(f"Загружено объектов:")
        for category, assets in self.asset_objects.items():
            if assets:
                self.log_message(f"  - {category}: {len(assets)}")
        
        if total_assets == 0:
            messagebox.showwarning("Предупреждение", 
                                 "Не найдено объектов. Создайте папки: vehicles, people, animals, fire, smoke, trees")
    
    def analyze_background(self, image):
        """Улучшенный анализ фона для определения зон размещения"""
        height, width = image.shape[:2]
        
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        zones = {
            'sky': [],       
            'road': [],      
            'forest': [],    
            'field': [],     
            'water': [],     
            'building': [],  
            'ground': [],    
            'snow': []       
        }
        
        
        grid_size = 12
        cell_w = width // grid_size
        cell_h = height // grid_size
        
        for i in range(grid_size):
            for j in range(grid_size):
                x1, y1 = j * cell_w, i * cell_h
                x2, y2 = min((j + 1) * cell_w, width), min((i + 1) * cell_h, height)
                
                
                cell = hsv[y1:y2, x1:x2]
                mean_color = np.mean(cell, axis=(0, 1))
                
                
                h, s, v = mean_color
                
                cell_info = {
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 
                    'center': ((x1+x2)//2, (y1+y2)//2),
                    'position_ratio': i / grid_size  
                }
                
                
                
                
                if i < grid_size // 3 and (90 <= h <= 130 or (s < 40 and v > 150)):
                    zones['sky'].append(cell_info)
                
                
                elif s < 30 and v > 200:
                    zones['snow'].append(cell_info)
                
                
                elif v < 80 and s < 60:
                    zones['road'].append(cell_info)
                
                
                elif 35 <= h <= 85 and s > 60 and v < 180:
                    zones['forest'].append(cell_info)
                
                
                elif (35 <= h <= 85 and 20 <= s <= 60) or (15 <= h <= 35 and s > 30):
                    zones['field'].append(cell_info)
                
                
                elif 100 <= h <= 130 and s > 40:
                    zones['water'].append(cell_info)
                
                
                elif s < 40 and 80 <= v <= 180:
                    zones['building'].append(cell_info)
                
                
                elif 5 <= h <= 25 and s > 30 and v < 120:
                    zones['ground'].append(cell_info)
                
                
                else:
                    zones['field'].append(cell_info)
        
        
        zone_counts = {zone: len(cells) for zone, cells in zones.items() if cells}
        self.log_message(f"Анализ сцены: {zone_counts}")
        
        return zones
        
    def detect_viewing_angle(self, image):
        """Определение ракурса съемки (вид сверху, сбоку, под углом)"""
        height, width = image.shape[:2]
        
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        horizontal_lines = 0
        vertical_lines = 0
        
        if lines is not None:
            for rho, theta in lines[:, 0]:
                angle = theta * 180 / np.pi
                if 80 <= angle <= 100 or 260 <= angle <= 280:  
                    horizontal_lines += 1
                elif 170 <= angle <= 190 or 350 <= angle <= 10:  
                    vertical_lines += 1
        
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        top_third = hsv[:height//3, :]
        bottom_third = hsv[2*height//3:, :]
        
        
        sky_mask_top = cv2.inRange(top_third, (90, 0, 150), (130, 255, 255))
        sky_ratio_top = np.sum(sky_mask_top > 0) / sky_mask_top.size
        
        
        ground_mask_bottom = cv2.inRange(bottom_third, (15, 30, 30), (85, 255, 200))
        ground_ratio_bottom = np.sum(ground_mask_bottom > 0) / ground_mask_bottom.size
        
        
        if sky_ratio_top < 0.1 and ground_ratio_bottom < 0.3:
            return "top_down"  
        elif sky_ratio_top > 0.4 and horizontal_lines > 2:
            return "side_view"  
        else:
            return "angled"     
    
    def get_suitable_objects_by_angle(self, category, viewing_angle):
        """Фильтрация объектов по ракурсу съемки"""
        objects = self.asset_objects.get(category, [])
        if not objects:
            return []
        
        
        
        
        
        
        
        
        
        return objects
    
    def get_suitable_zones(self, category, zones):
        """Определение подходящих зон для размещения объектов с учетом реалистичности"""
        suitable_zones = []
        
        if category == 'vehicles':
            
            suitable_zones.extend(zones['road'] * 3)  
            suitable_zones.extend(zones['building'])
            suitable_zones.extend(zones['field'][:len(zones['field'])//3])  
        
        elif category == 'people':
            
            suitable_zones.extend(zones['field'])
            suitable_zones.extend(zones['building'])
            suitable_zones.extend(zones['road'])
            suitable_zones.extend(zones['ground'])
        
        elif category == 'animals':
            
            suitable_zones.extend(zones['forest'] * 2)  
            suitable_zones.extend(zones['field'])
            suitable_zones.extend(zones['ground'])
        
        elif category == 'fire':
            
            suitable_zones.extend(zones['forest'] * 2)
            suitable_zones.extend(zones['field'])
            suitable_zones.extend(zones['ground'])
            if len(zones['building']) > 0:
                suitable_zones.extend(zones['building'][:2])  
        
        elif category == 'smoke':
            
            suitable_zones.extend(zones['forest'])
            suitable_zones.extend(zones['field'])
            suitable_zones.extend(zones['building'])
            suitable_zones.extend(zones['road'])
            suitable_zones.extend(zones['ground'])
        
        elif category == 'trees':
            
            suitable_zones.extend(zones['forest'])
            suitable_zones.extend(zones['field'])
            suitable_zones.extend(zones['ground'])
        
        elif category == 'aircraft':
            
            suitable_zones.extend(zones['sky'] * 3)  
            suitable_zones.extend(zones['field'])
        
        elif category == 'boats':
            
            suitable_zones.extend(zones['water'])
        
        
        
        
        if not suitable_zones and category != 'boats':
            suitable_zones = zones['field']
        
        return suitable_zones
    
    def should_avoid_zone(self, category, zone_type):
        """Проверка, нужно ли избегать определенную зону для объекта"""
        avoid_rules = {
            'vehicles': ['sky', 'water'],
            'people': ['sky', 'water'],
            'animals': ['sky', 'water', 'road'],
            'fire': ['sky', 'water'],
            'smoke': ['water'],  
            'trees': ['sky', 'water', 'road']
        }
        
        return zone_type in avoid_rules.get(category, [])
    
    def calculate_adaptive_scale(self, background_shape, zone_info, category, viewing_angle):
        """Расчет адаптивного масштаба объекта"""
        height, width = background_shape[:2]
        
        
        base_sizes = {
            'vehicles': {'min': 40, 'max': 120},
            'people': {'min': 20, 'max': 60},
            'animals': {'min': 30, 'max': 80},
            'trees': {'min': 60, 'max': 200},
            'fire': {'min': 30, 'max': 100},
            'smoke': {'min': 50, 'max': 150},
            'aircraft': {'min': 80, 'max': 300},
            'boats': {'min': 50, 'max': 150}
        }
        
        base_size = base_sizes.get(category, {'min': 30, 'max': 100})
        
        
        scale_factor = min(width, height) / 1000.0
        min_size = int(base_size['min'] * scale_factor)
        max_size = int(base_size['max'] * scale_factor)
        
        
        if viewing_angle == "top_down":
            
            min_size = int(min_size * 0.7)
            max_size = int(max_size * 0.8)
        elif viewing_angle == "side_view":
            
            min_size = int(min_size * 0.9)
            max_size = int(max_size * 1.1)
        
        
        position_y_ratio = zone_info.get('position_ratio', 0.5)
        
        if viewing_angle != "top_down":
            
            distance_scale = 1.0 - (position_y_ratio * 0.4)  
            min_size = int(min_size * distance_scale)
            max_size = int(max_size * distance_scale)
        
        
        target_size = random.randint(min_size, max_size)
        
        
        return target_size / 200.0
    
    def place_object_on_image(self, background, object_path, position, zone_info, category, viewing_angle):
        """Улучшенное размещение объекта на изображении с адаптивным масштабированием"""
        try:
            
            obj_img = cv2.imread(object_path, cv2.IMREAD_UNCHANGED)
            if obj_img is None:
                return background, None
            
            
            scale_factor = self.calculate_adaptive_scale(background.shape, zone_info, category, viewing_angle)
            
            
            h, w = obj_img.shape[:2]
            new_h, new_w = int(h * scale_factor), int(w * scale_factor)
            
            
            if new_h < 10 or new_w < 10:
                return background, None
            
            obj_img = cv2.resize(obj_img, (new_w, new_h))
            
            
            x, y = position
            
            
            zone_center_x = (zone_info['x1'] + zone_info['x2']) // 2
            zone_center_y = (zone_info['y1'] + zone_info['y2']) // 2
            
            
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            
            x = max(zone_info['x1'], min(zone_center_x + offset_x - new_w//2, zone_info['x2'] - new_w))
            y = max(zone_info['y1'], min(zone_center_y + offset_y - new_h//2, zone_info['y2'] - new_h))
            
            
            bg_h, bg_w = background.shape[:2]
            if x + new_w > bg_w or y + new_h > bg_h or x < 0 or y < 0:
                return background, None
            
            
            if obj_img.shape[2] == 4:  
                alpha = obj_img[:, :, 3] / 255.0
                for c in range(3):
                    background[y:y+new_h, x:x+new_w, c] = (
                        alpha * obj_img[:, :, c] + 
                        (1 - alpha) * background[y:y+new_h, x:x+new_w, c]
                    )
            else:  
                blend_factor = 0.9  
                background[y:y+new_h, x:x+new_w] = (
                    blend_factor * obj_img[:, :, :3] + 
                    (1 - blend_factor) * background[y:y+new_h, x:x+new_w]
                )
            
            
            bbox = {'x': x, 'y': y, 'width': new_w, 'height': new_h}
            return background, bbox
            
        except Exception as e:
            self.log_message(f"Ошибка размещения объекта: {e}")
            return background, None
    
    def generate_single_image(self, background_path):
        """Улучшенная генерация одного изображения с объектами"""
        try:
            
            background = cv2.imread(background_path)
            if background is None:
                return None, []
            
            
            viewing_angle = self.detect_viewing_angle(background)
            
            
            zones = self.analyze_background(background)
            
            
            annotations = []
            
            
            num_objects = random.randint(1, self.max_objects.get())
            
            
            placed_objects = []
            
            for _ in range(num_objects):
                
                available_categories = [cat for cat, objects in self.asset_objects.items() if objects]
                if not available_categories:
                    break
                
                category = random.choice(available_categories)
                
                
                suitable_objects = self.get_suitable_objects_by_angle(category, viewing_angle)
                if not suitable_objects:
                    continue
                
                object_path = random.choice(suitable_objects)
                
                
                suitable_zones = self.get_suitable_zones(category, zones)
                if not suitable_zones:
                    continue
                
                
                placement_attempts = 0
                max_placement_attempts = 5
                
                while placement_attempts < max_placement_attempts:
                    
                    zone = random.choice(suitable_zones)
                    
                    
                    background, bbox = self.place_object_on_image(
                        background, object_path, zone['center'], zone, category, viewing_angle
                    )
                    
                    if bbox:
                        
                        overlap = False
                        for placed_bbox in placed_objects:
                            if self.check_overlap(bbox, placed_bbox):
                                overlap = True
                                break
                        
                        if not overlap:
                            annotations.append({
                                'category': category,
                                'bbox': bbox,
                                'object_path': object_path,
                                'viewing_angle': viewing_angle
                            })
                            placed_objects.append(bbox)
                            break
                    
                    placement_attempts += 1
            
            return background, annotations
            
        except Exception as e:
            self.log_message(f"Ошибка генерации изображения: {e}")
            return None, []
    
    def check_overlap(self, bbox1, bbox2, threshold=0.3):
        """Проверка перекрытия двух bounding box"""
        x1_min, y1_min = bbox1['x'], bbox1['y']
        x1_max, y1_max = x1_min + bbox1['width'], y1_min + bbox1['height']
        
        x2_min, y2_min = bbox2['x'], bbox2['y']
        x2_max, y2_max = x2_min + bbox2['width'], y2_min + bbox2['height']
        
        
        intersection_x_min = max(x1_min, x2_min)
        intersection_y_min = max(y1_min, y2_min)
        intersection_x_max = min(x1_max, x2_max)
        intersection_y_max = min(y1_max, y2_max)
        
        if intersection_x_min >= intersection_x_max or intersection_y_min >= intersection_y_max:
            return False
        
        
        intersection_area = (intersection_x_max - intersection_x_min) * (intersection_y_max - intersection_y_min)
        
        
        area1 = bbox1['width'] * bbox1['height']
        area2 = bbox2['width'] * bbox2['height']
        
        
        overlap_ratio = intersection_area / min(area1, area2)
        
        return overlap_ratio > threshold
    
    def preview_generation(self):
        """Предварительный просмотр генерации"""
        if not self.background_images:
            messagebox.showerror("Ошибка", "Сначала загрузите фоновые изображения")
            return
        
        if not any(self.asset_objects.values()):
            messagebox.showerror("Ошибка", "Не загружены объекты для размещения")
            return
        
        
        background_path = random.choice(self.background_images)
        self.log_message(f"Генерация превью для: {os.path.basename(background_path)}")
        
        
        result_image, annotations = self.generate_single_image(background_path)
        
        if result_image is not None:
            
            self.show_preview(result_image, annotations)
            self.log_message(f"Размещено объектов: {len(annotations)}")
        else:
            messagebox.showerror("Ошибка", "Не удалось сгенерировать превью")
    
    def show_preview(self, image, annotations):
        """Отображение превью изображения"""
        
        preview_img = image.copy()
        for ann in annotations:
            bbox = ann['bbox']
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            cv2.rectangle(preview_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(preview_img, ann['category'], (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        
        preview_img = cv2.cvtColor(preview_img, cv2.COLOR_BGR2RGB)
        preview_img = Image.fromarray(preview_img)
        
        
        display_size = (400, 300)
        preview_img.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        
        photo = ImageTk.PhotoImage(preview_img)
        self.preview_label.configure(image=photo, text="")
        self.preview_label.image = photo  
    
    def generate_dataset(self):
        """Генерация полного датасета"""
        if not self.background_images:
            messagebox.showerror("Ошибка", "Сначала загрузите фоновые изображения")
            return
        
        if not self.output_folder.get():
            messagebox.showerror("Ошибка", "Выберите папку для сохранения")
            return
        
        if not any(self.asset_objects.values()):
            messagebox.showerror("Ошибка", "Не загружены объекты для размещения")
            return
        
        output_path = Path(self.output_folder.get())
        images_path = output_path / "images"
        labels_path = output_path / "labels"
        
        
        images_path.mkdir(parents=True, exist_ok=True)
        labels_path.mkdir(parents=True, exist_ok=True)
        
        num_to_generate = self.num_images.get()
        self.progress['maximum'] = num_to_generate
        
        self.log_message(f"Начинается генерация {num_to_generate} изображений...")
        
        
        categories = list(self.asset_objects.keys())
        
        successful_generations = 0
        attempts = 0
        max_attempts = num_to_generate * 3  
        
        while successful_generations < num_to_generate and attempts < max_attempts:
            
            background_path = random.choice(self.background_images)
            
            
            result_image, annotations = self.generate_single_image(background_path)
            
            
            if result_image is not None:
                
                image_filename = f"synthetic_{successful_generations:04d}.jpg"
                image_path = images_path / image_filename
                cv2.imwrite(str(image_path), result_image)
                
                
                label_filename = f"synthetic_{successful_generations:04d}.txt"
                label_path = labels_path / label_filename
                
                if annotations:
                    self.save_yolo_annotation(label_path, annotations, result_image.shape, categories)
                else:
                    
                    label_path.touch()
                
                successful_generations += 1
                if annotations:
                    self.log_message(f"Сгенерировано: {image_filename} с {len(annotations)} объектами")
                else:
                    self.log_message(f"Сгенерировано: {image_filename} (чистый фон)")
            
            attempts += 1
            
            
            self.progress['value'] = successful_generations
            self.root.update()
        
        
        classes_file = output_path / "classes.txt"
        with open(classes_file, 'w') as f:
            for category in categories:
                f.write(f"{category}\n")
        
        self.log_message(f"Генерация завершена! Успешно: {successful_generations}/{num_to_generate}")
        self.log_message(f"Файлы сохранены в: {output_path}")
        
        messagebox.showinfo("Готово", f"Датасет сгенерирован!\nУспешно: {successful_generations} изображений")
    
    def save_yolo_annotation(self, label_path, annotations, image_shape, categories):
        """Сохранение разметки в формате YOLO"""
        height, width = image_shape[:2]
        
        with open(label_path, 'w') as f:
            for ann in annotations:
                category = ann['category']
                bbox = ann['bbox']
                
                
                class_id = categories.index(category)
                
                
                x_center = (bbox['x'] + bbox['width'] / 2) / width
                y_center = (bbox['y'] + bbox['height'] / 2) / height
                norm_width = bbox['width'] / width
                norm_height = bbox['height'] / height
                
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {norm_width:.6f} {norm_height:.6f}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SyntheticDataGenerator(root)
    root.mainloop()