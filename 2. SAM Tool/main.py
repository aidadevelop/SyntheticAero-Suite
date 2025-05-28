import sys
import os
import tkinter as tk
from tkinter import messagebox


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Главная функция запуска приложения"""
    try:

        if sys.version_info < (3, 7):
            messagebox.showerror("Ошибка", "Требуется Python 3.7 или выше")
            return

        from core.app import SAMSegmentationApp

        root = tk.Tk()
        app = SAMSegmentationApp(root)

        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")

        def on_closing():
            if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
                app.save_current_annotations()
                root.quit()
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        root.mainloop()

    except ImportError as e:
        messagebox.showerror(
            "Ошибка импорта",
            f"Не удалось импортировать необходимые модули:\n{str(e)}\n\n"
            "Установите зависимости: pip install -r requirements.txt",
        )
    except Exception as e:
        messagebox.showerror(
            "Критическая ошибка", f"Произошла критическая ошибка:\n{str(e)}"
        )


if __name__ == "__main__":
    main()
