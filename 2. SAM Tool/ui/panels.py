import tkinter as tk
from tkinter import ttk
from config import UI_CONFIG

class TopPanel:
    """Верхняя панель с кнопками управления"""
    
    def __init__(self, root, main_window):
        self.root = root
        self.main_window = main_window
        self.handlers = {}
        self.create_panel()
    
    def create_panel(self):
        """Создание верхней панели"""
        self.frame = tk.Frame(self.root, bg=UI_CONFIG['panel_bg'], height=60)
        self.frame.pack(fill=tk.X, padx=5, pady=5)
        self.frame.pack_propagate(False)
        
        # Кнопки файлов
        file_frame = tk.Frame(self.frame, bg=UI_CONFIG['panel_bg'])
        file_frame.pack(side=tk.LEFT, pady=10)
        
        self.folder_btn = tk.Button(file_frame, text="Выбрать папку",
                                   bg=UI_CONFIG['button_bg'], fg='white', 
                                   font=('Arial', 10, 'bold'))
        self.folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.sam_btn = tk.Button(file_frame, text="Загрузить SAM",
                                bg='#2196F3', fg='white', 
                                font=('Arial', 10, 'bold'))
        self.sam_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопки навигации
        nav_frame = tk.Frame(self.frame, bg=UI_CONFIG['panel_bg'])
        nav_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.prev_btn = tk.Button(nav_frame, text="◀ Предыдущее",
                                 font=('Arial', 10))
        self.prev_btn.pack(side=tk.LEFT, padx=2)
        
        self.next_btn = tk.Button(nav_frame, text="Следующее ▶",
                                 font=('Arial', 10))
        self.next_btn.pack(side=tk.LEFT, padx=2)
        
        # Кнопки сохранения
        save_frame = tk.Frame(self.frame, bg=UI_CONFIG['panel_bg'])
        save_frame.pack(side=tk.RIGHT, pady=10)
        
        self.csv_btn = tk.Button(save_frame, text="Экспорт в CSV",
                                bg='#FF9800', fg='white', 
                                font=('Arial', 10, 'bold'))
        self.csv_btn.pack(side=tk.RIGHT, padx=5)
        
        self.xml_btn = tk.Button(save_frame, text="Сохранить XML",
                                bg='#9C27B0', fg='white', 
                                font=('Arial', 10, 'bold'))
        self.xml_btn.pack(side=tk.RIGHT, padx=5)
    
    def bind_handlers(self, handlers):
        """Привязка обработчиков событий"""
        self.handlers = handlers
        
        self.folder_btn.config(command=handlers.get('select_folder'))
        self.sam_btn.config(command=handlers.get('load_sam'))
        self.prev_btn.config(command=handlers.get('prev_image'))
        self.next_btn.config(command=handlers.get('next_image'))
        self.xml_btn.config(command=handlers.get('save_xml'))
        self.csv_btn.config(command=handlers.get('export_csv'))


class RightPanel:
    """Правая панель с настройками"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.handlers = {}
        self.create_panel()
    
    def create_panel(self):
        """Создание правой панели"""
        self.frame = tk.Frame(self.parent, bg=UI_CONFIG['panel_bg'], 
                             width=350, relief=tk.SUNKEN, bd=2)
        self.frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame.pack_propagate(False)
        
        # Заголовок
        tk.Label(self.frame, text="Панель управления", 
                font=('Arial', 12, 'bold'), bg=UI_CONFIG['panel_bg']).pack(pady=10)
        
        # Настройки классов
        self.create_class_settings()
        
        # Режимы работы
        self.create_mode_settings()
        
        # Список аннотаций
        self.create_annotations_list()
        
        # Инструменты
        self.create_tools_panel()
    
    def create_class_settings(self):
        """Создание настроек классов"""
        class_frame = tk.LabelFrame(self.frame, text="Классы объектов", 
                                   bg=UI_CONFIG['panel_bg'], font=('Arial', 10, 'bold'))
        class_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(class_frame, text="Текущий класс:", 
                bg=UI_CONFIG['panel_bg']).pack(anchor=tk.W, padx=5)
        
        from config import DEFAULT_CLASSES
        self.class_combo = ttk.Combobox(class_frame, textvariable=self.main_window.selected_class,
                                       state='readonly')
        self.class_combo['values'] = DEFAULT_CLASSES
        self.class_combo.pack(fill=tk.X, padx=5, pady=2)

        # Управление классами
        btn_frame = tk.Frame(class_frame, bg=UI_CONFIG['panel_bg'])
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_class_btn = tk.Button(btn_frame, text="Добавить", font=('Arial', 8))
        self.add_class_btn.pack(side=tk.LEFT, padx=2)
        
        self.remove_class_btn = tk.Button(btn_frame, text="Удалить", font=('Arial', 8))
        self.remove_class_btn.pack(side=tk.LEFT, padx=2)
    
    def create_mode_settings(self):
        """Создание настроек режимов"""
        mode_frame = tk.LabelFrame(self.frame, text="Режим работы", 
                                  bg=UI_CONFIG['panel_bg'], font=('Arial', 10, 'bold'))
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Радиокнопки режимов
        tk.Radiobutton(mode_frame, text="Ручная разметка", 
                      variable=self.main_window.mode_var, value="manual",
                      bg=UI_CONFIG['panel_bg']).pack(anchor=tk.W, padx=5)
        
        tk.Radiobutton(mode_frame, text="SAM автосегментация", 
                      variable=self.main_window.mode_var, value="sam_auto",
                      bg=UI_CONFIG['panel_bg']).pack(anchor=tk.W, padx=5)
        
        # tk.Radiobutton(mode_frame, text="SAM с точками", 
        #               variable=self.main_window.mode_var, value="sam_points",
        #               bg=UI_CONFIG['panel_bg']).pack(anchor=tk.W, padx=5)
        
        # Инструкции
        info_frame = tk.Frame(mode_frame, bg=UI_CONFIG['panel_bg'])
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=4, width=35, font=('Arial', 8),
                                bg=UI_CONFIG['panel_bg'], wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X)
        
        instructions = (
            "• Ручная: клики + правый клик для завершения\n"
            "• SAM авто: один клик = автосегментация\n"
            "  Shift+клик = отрицательная точка"
        )
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, instructions)
        self.info_text.config(state=tk.DISABLED)
    
    def create_annotations_list(self):
        """Создание списка аннотаций"""
        ann_frame = tk.LabelFrame(self.frame, text="Аннотации текущего изображения", 
                                 bg=UI_CONFIG['panel_bg'], font=('Arial', 10, 'bold'))
        ann_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Список с прокруткой
        list_frame = tk.Frame(ann_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.annotations_listbox = tk.Listbox(list_frame, font=('Arial', 9))
        scrollbar_list = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        
        self.annotations_listbox.configure(yscrollcommand=scrollbar_list.set)
        scrollbar_list.configure(command=self.annotations_listbox.yview)
        
        self.annotations_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления аннотациями
        btn_frame = tk.Frame(ann_frame, bg=UI_CONFIG['panel_bg'])
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.delete_ann_btn = tk.Button(btn_frame, text="Удалить", font=('Arial', 8),
                                       bg=UI_CONFIG['error_color'], fg='white')
        self.delete_ann_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_ann_btn = tk.Button(btn_frame, text="Очистить все", font=('Arial', 8),
                                      bg='#ff7043', fg='white')
        self.clear_ann_btn.pack(side=tk.LEFT, padx=2)
    
    def create_tools_panel(self):
        """Создание панели инструментов"""
        tools_frame = tk.LabelFrame(self.frame, text="Инструменты", 
                                   bg=UI_CONFIG['panel_bg'], font=('Arial', 10, 'bold'))
        tools_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.clear_points_btn = tk.Button(tools_frame, text="Очистить точки", font=('Arial', 9))
        self.clear_points_btn.pack(fill=tk.X, padx=5, pady=2)
        
        self.undo_btn = tk.Button(tools_frame, text="Отменить последнее", font=('Arial', 9))
        self.undo_btn.pack(fill=tk.X, padx=5, pady=2)
    
    def bind_handlers(self, handlers):
        """Привязка обработчиков событий"""
        self.handlers = handlers
        
        self.add_class_btn.config(command=handlers.get('add_class'))
        self.remove_class_btn.config(command=handlers.get('remove_class'))
        self.delete_ann_btn.config(command=handlers.get('delete_annotation'))
        self.clear_ann_btn.config(command=handlers.get('clear_annotations'))
        self.clear_points_btn.config(command=handlers.get('clear_points'))
        self.undo_btn.config(command=handlers.get('undo_action'))
    
    def update_class_list(self, classes):
        """Обновление списка классов"""
        self.class_combo['values'] = classes
    
    def update_annotations_list(self, annotations):
        """Обновление списка аннотаций"""
        self.annotations_listbox.delete(0, tk.END)
        
        for i, ann in enumerate(annotations):
            display_text = f"{i+1}. {ann['class']} ({ann['type']})"
            if 'timestamp' in ann:
                timestamp = ann['timestamp'][:19]
                display_text += f" - {timestamp}"
            if 'sam_score' in ann:
                display_text += f" [{ann['sam_score']:.3f}]"
            self.annotations_listbox.insert(tk.END, display_text)
    
    def get_selected_annotation_index(self):
        """Получение индекса выбранной аннотации"""
        selection = self.annotations_listbox.curselection()
        return selection[0] if selection else None


class BottomPanel:
    """Нижняя панель статуса"""
    
    def __init__(self, root, main_window):
        self.root = root
        self.main_window = main_window
        self.create_panel()
    
    def create_panel(self):
        """Создание нижней панели"""
        self.frame = tk.Frame(self.root, bg=UI_CONFIG['panel_bg'], height=30)
        self.frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        self.frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.frame, text="Готов к работе", 
                                    bg=UI_CONFIG['panel_bg'], font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, pady=5)
        
        self.progress_bar = ttk.Progressbar(self.frame, variable=self.main_window.progress_var,
                                           maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, pady=5, padx=10)
    
    def update_status(self, message):
        """Обновление статуса"""
        self.status_label.config(text=message)
        self.root.update_idletasks()