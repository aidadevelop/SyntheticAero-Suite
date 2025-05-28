import tkinter as tk


class CanvasHandler:
    """Класс для работы с Canvas"""

    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.handlers = {}
        self.create_canvas()

    def create_canvas(self):
        """Создание Canvas с прокруткой"""
        canvas_frame = tk.Frame(self.parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(canvas_frame, bg="white", cursor="crosshair")

        self.v_scrollbar = tk.Scrollbar(
            canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview
        )
        self.h_scrollbar = tk.Scrollbar(
            canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview
        )

        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set
        )

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_handlers(self, handlers):
        """Привязка обработчиков событий"""
        self.handlers = handlers

        self.canvas.bind("<Button-1>", handlers.get("canvas_click"))
        self.canvas.bind("<Button-3>", handlers.get("canvas_right_click"))
        self.canvas.bind("<Motion>", handlers.get("canvas_motion"))

    def get_canvas_size(self):
        """Получение размеров Canvas"""
        return (self.canvas.winfo_width(), self.canvas.winfo_height())

    def display_image(self, photo):
        """Отображение изображения на Canvas"""
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, anchor=tk.NW, image=photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def canvas_to_image_coords(self, event, canvas_scale):
        """Преобразование координат Canvas в координаты изображения"""
        canvas_x = self.canvas.canvasx(event.x) - 10
        canvas_y = self.canvas.canvasy(event.y) - 10

        orig_x = int(canvas_x / canvas_scale)
        orig_y = int(canvas_y / canvas_scale)

        return (orig_x, orig_y)
