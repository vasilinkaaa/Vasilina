import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("1000x650")
        self.root.resizable(True, True)
        
        # Установка стиля
        self.root.configure(bg='#f0f0f0')
        
        # Файл для хранения данных
        self.data_file = "weather_data.json"
        self.entries = []
        self.current_filter = None
        
        # Загрузка существующих данных
        self.load_data()
        
        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_treeview()
        self.create_button_frame()
        
        # Отображение всех записей
        self.refresh_treeview()
        
        # Привязка клавиш
        self.root.bind('<Return>', lambda e: self.add_entry())
    
    def create_input_frame(self):
        """Создание фрейма для ввода данных"""
        input_frame = tk.LabelFrame(self.root, text="➕ Добавление новой записи", 
                                   padx=15, pady=10, font=("Arial", 12, "bold"),
                                   bg='#f0f0f0', fg='#333')
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Дата
        tk.Label(input_frame, text="📅 Дата (ГГГГ-ММ-ДД):", font=("Arial", 10), 
                bg='#f0f0f0').grid(row=0, column=0, sticky="w", padx=5, pady=8)
        self.date_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.date_entry.grid(row=0, column=1, padx=5, pady=8)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Температура
        tk.Label(input_frame, text="🌡️ Температура (°C):", font=("Arial", 10), 
                bg='#f0f0f0').grid(row=0, column=2, sticky="w", padx=5, pady=8)
        self.temp_entry = tk.Entry(input_frame, width=10, font=("Arial", 10))
        self.temp_entry.grid(row=0, column=3, padx=5, pady=8)
        
        # Описание погоды
        tk.Label(input_frame, text="☁️ Описание погоды:", font=("Arial", 10), 
                bg='#f0f0f0').grid(row=1, column=0, sticky="w", padx=5, pady=8)
        self.desc_entry = tk.Entry(input_frame, width=50, font=("Arial", 10))
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=8, sticky="ew")
        
        # Осадки
        tk.Label(input_frame, text="💧 Осадки:", font=("Arial", 10), 
                bg='#f0f0f0').grid(row=2, column=0, sticky="w", padx=5, pady=8)
        self.precipitation_var = tk.BooleanVar()
        self.precipitation_check = tk.Checkbutton(input_frame, text="Да", 
                                                  variable=self.precipitation_var, 
                                                  font=("Arial", 10), bg='#f0f0f0')
        self.precipitation_check.grid(row=2, column=1, sticky="w", padx=5, pady=8)
        
        # Кнопка добавления
        self.add_btn = tk.Button(input_frame, text="Добавить запись", command=self.add_entry,
                                 bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), 
                                 padx=20, pady=5, cursor="hand2")
        self.add_btn.grid(row=2, column=3, padx=5, pady=8)
        
        # Настройка растягивания колонок
        input_frame.columnconfigure(1, weight=1)
    
    def create_filter_frame(self):
        """Создание фрейма для фильтрации"""
        filter_frame = tk.LabelFrame(self.root, text="🔍 Фильтрация записей", 
                                    padx=15, pady=10, font=("Arial", 12, "bold"),
                                    bg='#f0f0f0', fg='#333')
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по дате
        tk.Label(filter_frame, text="По дате:", font=("Arial", 10, "bold"), 
                bg='#f0f0f0').grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=12, font=("Arial", 10))
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.filter_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.filter_date_btn = tk.Button(filter_frame, text="Показать за день", 
                                         command=self.filter_by_date,
                                         bg="#2196F3", fg="white", font=("Arial", 9),
                                         cursor="hand2")
        self.filter_date_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Фильтр по температуре
        tk.Label(filter_frame, text="Температура выше:", font=("Arial", 10, "bold"), 
                bg='#f0f0f0').grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.temp_filter_entry = tk.Entry(filter_frame, width=6, font=("Arial", 10))
        self.temp_filter_entry.grid(row=0, column=4, padx=5, pady=5)
        tk.Label(filter_frame, text="°C", font=("Arial", 10), 
                bg='#f0f0f0').grid(row=0, column=5, sticky="w", padx=0, pady=5)
        
        self.filter_temp_btn = tk.Button(filter_frame, text="Применить", 
                                         command=self.filter_by_temperature,
                                         bg="#FF9800", fg="white", font=("Arial", 9),
                                         cursor="hand2")
        self.filter_temp_btn.grid(row=0, column=6, padx=5, pady=5)
        
        # Кнопка сброса фильтров
        self.reset_btn = tk.Button(filter_frame, text="🔄 Сбросить фильтры", 
                                   command=self.reset_filters,
                                   bg="#9E9E9E", fg="white", font=("Arial", 9),
                                   cursor="hand2")
        self.reset_btn.grid(row=0, column=7, padx=5, pady=5)
    
    def create_treeview(self):
        """Создание таблицы для отображения записей"""
        # Фрейм для таблицы и скроллбара
        tree_frame = tk.Frame(self.root, bg='#f0f0f0')
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание скроллбаров
        scrollbar_y = tk.Scrollbar(tree_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Создание таблицы
        columns = ("ID", "Дата", "Температура (°C)", "Описание", "Осадки")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 yscrollcommand=scrollbar_y.set, 
                                 xscrollcommand=scrollbar_x.set,
                                 height=15)
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Температура (°C)", text="Температура (°C)")
        self.tree.heading("Описание", text="Описание")
        self.tree.heading("Осадки", text="Осадки")
        
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Дата", width=120, anchor="center")
        self.tree.column("Температура (°C)", width=130, anchor="center")
        self.tree.column("Описание", width=550)
        self.tree.column("Осадки", width=100, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        
        # Настройка скроллбаров
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Цветовая схема для таблицы
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        
        # Привязка двойного клика для удаления
        self.tree.bind("<Double-1>", self.delete_entry)
    
    def create_button_frame(self):
        """Создание фрейма с дополнительными кнопками"""
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.save_btn = tk.Button(button_frame, text="💾 Сохранить в JSON", 
                                  command=self.save_to_json,
                                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
                                  padx=15, cursor="hand2")
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_btn = tk.Button(button_frame, text="📂 Загрузить из JSON", 
                                  command=self.load_from_json,
                                  bg="#2196F3", fg="white", font=("Arial", 10, "bold"), 
                                  padx=15, cursor="hand2")
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = tk.Button(button_frame, text="📄 Экспорт в TXT", 
                                    command=self.export_to_txt,
                                    bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), 
                                    padx=15, cursor="hand2")
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_all_btn = tk.Button(button_frame, text="🗑️ Очистить все записи", 
                                       command=self.clear_all_entries,
                                       bg="#F44336", fg="white", font=("Arial", 10, "bold"), 
                                       padx=15, cursor="hand2")
        self.clear_all_btn.pack(side=tk.RIGHT, padx=5)
        
        # Статистика
        self.stats_label = tk.Label(button_frame, text="", font=("Arial", 9), 
                                    bg='#f0f0f0', fg='#666')
        self.stats_label.pack(side=tk.RIGHT, padx=15)
        
        # Статусная строка
        self.status_label = tk.Label(self.root, text="✅ Готов к работе", 
                                     relief=tk.SUNKEN, anchor=tk.W,
                                     font=("Arial", 9), fg="green", bg='#e0e0e0')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_input(self, date_str, temp_str, description):
        """Валидация входных данных"""
        # Проверка даты
        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка", 
                               "❌ Неверный формат даты!\nИспользуйте формат: ГГГГ-ММ-ДД\nПример: 2024-12-25")
            return False
        
        # Проверка температуры
        try:
            temp = float(temp_str)
            if temp < -100 or temp > 60:
                messagebox.showerror("Ошибка", 
                                   "❌ Температура должна быть в диапазоне от -100 до +60°C")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "❌ Температура должна быть числом!\nПример: 15.5 или -5")
            return False
        
        # Проверка описания
        if not description.strip():
            messagebox.showerror("Ошибка", "❌ Описание погоды не может быть пустым!")
            return False
        
        return True
    
    def add_entry(self):
        """Добавление новой записи"""
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = "Да" if self.precipitation_var.get() else "Нет"
        
        if not self.validate_input(date, temp, description):
            return
        
        # Создание новой записи
        new_id = max([entry["id"] for entry in self.entries], default=0) + 1
        entry = {
            "id": new_id,
            "date": date,
            "temperature": round(float(temp), 1),
            "description": description,
            "precipitation": precipitation
        }
        
        self.entries.append(entry)
        self.refresh_treeview()
        
        # Очистка полей ввода
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precipitation_var.set(False)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.update_status(f"✅ Запись добавлена: {date} - {temp}°C", "green")
        
        # Автосохранение
        self.save_to_json(quiet=True)
    
    def refresh_treeview(self, entries_to_show=None):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Отображение записей
        show_entries = entries_to_show if entries_to_show is not None else self.entries
        
        # Сортировка по дате (новые сверху)
        show_entries_sorted = sorted(show_entries, key=lambda x: x["date"], reverse=True)
        
        for entry in show_entries_sorted:
            # Цветовая индикация температуры
            temp_display = f"{entry['temperature']:.1f}"
            self.tree.insert("", tk.END, values=(
                entry["id"],
                entry["date"],
                temp_display,
                entry["description"],
                entry["precipitation"]
            ))
        
        # Обновление статистики
        self.update_stats()
    
    def update_stats(self):
        """Обновление статистики"""
        total = len(self.entries)
        if total > 0:
            avg_temp = sum(e["temperature"] for e in self.entries) / total
            rainy_days = sum(1 for e in self.entries if e["precipitation"] == "Да")
            self.stats_label.config(text=f"📊 Всего: {total} | Средняя t°: {avg_temp:.1f}°C | Дождливых: {rainy_days}")
        else:
            self.stats_label.config(text="📊 Нет записей")
    
    def filter_by_date(self):
        """Фильтрация по дате"""
        filter_date = self.filter_date_entry.get().strip()
        
        if not self.validate_date(filter_date):
            messagebox.showerror("Ошибка", "❌ Неверный формат даты для фильтрации!")
            return
        
        filtered = [entry for entry in self.entries if entry["date"] == filter_date]
        
        if filtered:
            self.refresh_treeview(filtered)
            self.current_filter = f"date_{filter_date}"
            self.update_status(f"📅 Найдено {len(filtered)} записей за {filter_date}", "blue")
        else:
            messagebox.showinfo("Информация", f"ℹ️ Нет записей за {filter_date}")
            self.reset_filters()
    
    def filter_by_temperature(self):
        """Фильтрация по температуре"""
        try:
            min_temp = float(self.temp_filter_entry.get().strip())
            filtered = [entry for entry in self.entries if entry["temperature"] > min_temp]
            
            if filtered:
                self.refresh_treeview(filtered)
                self.current_filter = f"temp_{min_temp}"
                self.update_status(f"🌡️ Найдено {len(filtered)} записей с температурой выше {min_temp}°C", "blue")
            else:
                messagebox.showinfo("Информация", f"ℹ️ Нет записей с температурой выше {min_temp}°C")
                self.reset_filters()
        except ValueError:
            messagebox.showerror("Ошибка", "❌ Введите корректное значение температуры для фильтрации!")
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.refresh_treeview()
        self.filter_date_entry.delete(0, tk.END)
        self.filter_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.temp_filter_entry.delete(0, tk.END)
        self.current_filter = None
        self.update_status("🔄 Фильтры сброшены", "green")
    
    def delete_entry(self, event):
        """Удаление записи по двойному клику"""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        # Получение ID записи
        values = self.tree.item(selected_item[0])["values"]
        entry_id = values[0]
        
        # Находим запись для отображения информации
        entry_to_delete = next((e for e in self.entries if e["id"] == entry_id), None)
        
        if entry_to_delete:
            msg = f"Удалить запись #{entry_id}?\n\nДата: {entry_to_delete['date']}\nТемпература: {entry_to_delete['temperature']}°C\nОписание: {entry_to_delete['description']}"
            
            if messagebox.askyesno("Подтверждение удаления", msg, icon='warning'):
                self.entries = [entry for entry in self.entries if entry["id"] != entry_id]
                
                # Перенумерация ID
                for idx, entry in enumerate(sorted(self.entries, key=lambda x: x["date"]), 1):
                    entry["id"] = idx
                
                self.refresh_treeview()
                self.save_to_json(quiet=True)
                self.update_status(f"🗑️ Запись #{entry_id} удалена", "red")
    
    def save_to_json(self, quiet=False):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=2, sort_keys=False)
            if not quiet:
                self.update_status(f"💾 Данные сохранены в {self.data_file}", "green")
            return True
        except Exception as e:
            if not quiet:
                messagebox.showerror("Ошибка", f"❌ Не удалось сохранить данные: {e}")
            return False
    
    def load_from_json(self):
        """Загрузка данных из JSON файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_entries = json.load(f)
                
                # Проверка корректности загруженных данных
                if isinstance(loaded_entries, list):
                    self.entries = loaded_entries
                    self.refresh_treeview()
                    self.reset_filters()
                    self.update_status(f"📂 Загружено {len(self.entries)} записей из {self.data_file}", "green")
                else:
                    raise ValueError("Неверный формат данных")
            else:
                messagebox.showwarning("Предупреждение", f"⚠️ Файл {self.data_file} не найден!\nБудет создан новый при сохранении.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Не удалось загрузить данные: {e}")
    
    def export_to_txt(self):
        """Экспорт данных в текстовый файл"""
        if not self.entries:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
            return
        
        try:
            export_file = f"weather_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("ДНЕВНИК ПОГОДЫ - ЭКСПОРТ ДАННЫХ\n")
                f.write(f"Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                for entry in sorted(self.entries, key=lambda x: x["date"]):
                    f.write(f"ID: {entry['id']}\n")
                    f.write(f"Дата: {entry['date']}\n")
                    f.write(f"Температура: {entry['temperature']}°C\n")
                    f.write(f"Описание: {entry['description']}\n")
                    f.write(f"Осадки: {entry['precipitation']}\n")
                    f.write("-"*40 + "\n")
                
                f.write(f"\nВсего записей: {len(self.entries)}\n")
                
                if self.entries:
                    avg_temp = sum(e["temperature"] for e in self.entries) / len(self.entries)
                    rainy = sum(1 for e in self.entries if e["precipitation"] == "Да")
                    f.write(f"Средняя температура: {avg_temp:.1f}°C\n")
                    f.write(f"Дней с осадками: {rainy}\n")
            
            self.update_status(f"📄 Данные экспортированы в файл: {export_file}", "purple")
            messagebox.showinfo("Успех", f"✅ Данные успешно экспортированы в файл:\n{export_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Ошибка при экспорте: {e}")
    
    def load_data(self):
        """Загрузка данных при запуске"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.entries = json.load(f)
                self.update_status(f"📂 Загружено {len(self.entries)} записей", "green", True)
            except:
                self.entries = []
                self.update_status("⚠️ Не удалось загрузить данные, создан новый файл", "orange", True)
        else:
            # Добавляем пример записи
            self.entries = [{
                "id": 1,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "temperature": 22.5,
                "description": "Солнечно, ясное небо",
                "precipitation": "Нет"
            }]
            self.save_to_json(quiet=True)
    
    def clear_all_entries(self):
        """Очистка всех записей"""
        if not self.entries:
            messagebox.showinfo("Информация", "Нет записей для удаления")
            return
            
        if messagebox.askyesno("Подтверждение", 
                              "⚠️ ВНИМАНИЕ! ⚠️\n\nВы уверены, что хотите удалить ВСЕ записи?\n"
                              "Это действие необратимо!", icon='warning'):
            self.entries = []
            self.refresh_treeview()
            self.save_to_json(quiet=True)
            self.reset_filters()
            self.update_status("🗑️ Все записи удалены", "red")
    
    def update_status(self, message, color, permanent=False):
        """Обновление статусной строки"""
        self.status_label.config(text=message, fg=color)
        if not permanent:
            self.root.after(3000, lambda: self.status_label.config(
                text="✅ Готов к работе", fg="green" 
                if self.status_label.cget("text") == message else self.status_label.cget("text")))

if __name__ == "__main__":
    root = tk.Tk()
    
    # Установка иконки (опционально, если есть файл)
    try:
        root.iconbitmap('weather.ico')
    except:
        pass
    
    app = WeatherDiary(root)
    root.mainloop()