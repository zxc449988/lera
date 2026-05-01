import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List, Dict, Any

class WeatherDiary:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Weather Diary / Дневник погоды")
        self.root.geometry("800x500")

        # Хранилище всех записей
        self.all_entries: List[Dict[str, Any]] = []

        # Переменные для полей ввода
        self.date_var = tk.StringVar()
        self.temp_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.precip_var = tk.BooleanVar(value=False)

        # Переменные фильтров
        self.filter_date_var = tk.StringVar()
        self.filter_temp_active = tk.BooleanVar(value=False)

        self._create_widgets()
        self._update_table()  # начальное отображение (пусто)

    # ------------------------------------------------------------
    # Построение интерфейса
    # ------------------------------------------------------------
    def _create_widgets(self):
        # Рамка ввода новой записи
        input_frame = ttk.LabelFrame(self.root, text="Новая запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поле даты
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5, pady=2)

        # Поле температуры
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="e", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.temp_var, width=10).grid(row=0, column=3, padx=5, pady=2)

        # Поле описания
        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Entry(input_frame, textvariable=self.desc_var, width=40).grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky="ew")

        # Чекбокс осадков
        ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=0, column=4, padx=10, pady=2)

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить запись", command=self._add_entry).grid(row=1, column=4, padx=10, pady=2)

        input_frame.columnconfigure(1, weight=1)

        # Таблица для отображения записей
        table_frame = ttk.LabelFrame(self.root, text="Записи", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура, °C")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.column("date", width=100)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Рамка фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по дате (ДД.ММ.ГГГГ):").grid(row=0, column=0, padx=5, pady=2)
        ttk.Entry(filter_frame, textvariable=self.filter_date_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(filter_frame, text="Применить фильтр даты", command=self._apply_filters).grid(row=0, column=2, padx=5, pady=2)

        ttk.Checkbutton(filter_frame, text="Температура > 10°C", variable=self.filter_temp_active,
                        command=self._apply_filters).grid(row=0, column=3, padx=15, pady=2)

        ttk.Button(filter_frame, text="Сбросить фильтры", command=self._reset_filters).grid(row=0, column=4, padx=5, pady=2)

        # Рамка действий с файлом
        file_frame = ttk.Frame(self.root, padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(file_frame, text="Сохранить в JSON", command=self._save_to_json).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Загрузить из JSON", command=self._load_from_json).pack(side="left", padx=5)

    # ------------------------------------------------------------
    # Работа с записями и таблицей
    # ------------------------------------------------------------
    def _add_entry(self):
        """Добавить новую запись после проверки ввода."""
        date_str = self.date_var.get().strip()
        temp_str = self.temp_var.get().strip()
        desc = self.desc_var.get().strip()
        precip = self.precip_var.get()

        # Валидация
        if not date_str:
            messagebox.showerror("Ошибка", "Дата не может быть пустой.")
            return
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ (например, 25.04.2025).")
            return

        if not temp_str:
            messagebox.showerror("Ошибка", "Температура не может быть пустой.")
            return
        try:
            temp_val = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом (целым или дробным).")
            return

        if not desc:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым.")
            return

        # Создание записи
        entry = {
            "date": date_str,
            "temperature": temp_val,
            "description": desc,
            "precipitation": "Да" if precip else "Нет"
        }
        self.all_entries.append(entry)
        # Очистка полей для удобства
        self.date_var.set("")
        self.temp_var.set("")
        self.desc_var.set("")
        self.precip_var.set(False)

        self._apply_filters()  # обновить отображение с учётом текущих фильтров

    def _update_table(self, entries_to_show: List[Dict[str, Any]]):
        """Обновить таблицу на основе переданного списка записей."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for e in entries_to_show:
            self.tree.insert("", "end", values=(
                e["date"],
                f"{e['temperature']:.1f}" if isinstance(e["temperature"], float) else str(e["temperature"]),
                e["description"],
                e["precipitation"]
            ))

    # ------------------------------------------------------------
    # Фильтрация
    # ------------------------------------------------------------
    def _apply_filters(self):
        """Применить текущие фильтры к self.all_entries и обновить таблицу."""
        date_filter = self.filter_date_var.get().strip()
        temp_filter_active = self.filter_temp_active.get()

        filtered = self.all_entries[:]

        if date_filter:
            # Проверка корректности даты фильтра
            try:
                datetime.strptime(date_filter, "%d.%m.%Y")
            except ValueError:
                messagebox.showwarning("Предупреждение", "Неверный формат даты фильтра. Фильтр по дате не применяется.")
                date_filter = ""
            else:
                filtered = [e for e in filtered if e["date"] == date_filter]

        if temp_filter_active:
            filtered = [e for e in filtered if e["temperature"] > 10.0]

        self._update_table(filtered)

    def _reset_filters(self):
        """Сбросить все фильтры и показать все записи."""
        self.filter_date_var.set("")
        self.filter_temp_active.set(False)
        self._update_table(self.all_entries)

    # ------------------------------------------------------------
    # Работа с JSON
    # ------------------------------------------------------------
    def _save_to_json(self):
        """Сохранить все записи в файл JSON."""
        if not self.all_entries:
            if not messagebox.askyesno("Подтверждение", "Нет записей для сохранения. Сохранить пустой файл?"):
                return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить дневник"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.all_entries, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", f"Данные сохранены в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def _load_from_json(self):
        """Загрузить записи из файла JSON."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить дневник"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("Файл должен содержать список записей.")
                # Базовая проверка структуры каждой записи
                for entry in data:
                    if not all(k in entry for k in ("date", "temperature", "description", "precipitation")):
                        raise ValueError("Неверный формат записи в файле.")
                self.all_entries = data
                self._reset_filters()  # сбросить фильтры и показать загруженные записи
                messagebox.showinfo("Успех", f"Загружено {len(self.all_entries)} записей.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")


# ------------------------------------------------------------
# Запуск приложения
# ------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
