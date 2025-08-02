import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
from typing import Dict, List, Any
import tkinterdnd2 as tkdnd

class TraderPlusEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("TraderPlusEditor [PERIMETER]")
        self.root.geometry("800x600")
        
        # Настройка drag and drop
        self.root.drop_target_register(tkdnd.DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # Данные
        self.config_data = {}
        self.current_file = ""
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть", command=self.open_file)
        file_menu.add_command(label="Сохранить", command=self.save_file)
        file_menu.add_command(label="Сохранить как", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Категории товаров", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        # Поиск по категориям
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(search_frame, text="Очистить", command=self.clear_search).pack(side=tk.LEFT)
        
        # Информация о файле
        self.file_info_var = tk.StringVar()
        self.file_info_var.set("Файл не загружен")
        ttk.Label(header_frame, textvariable=self.file_info_var, foreground="gray").pack(side=tk.RIGHT)
        
        # Список категорий
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Treeview для отображения категорий
        columns = ("Название", "Количество товаров")
        self.category_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Настройка колонок
        self.category_tree.heading("Название", text="Название категории")
        self.category_tree.heading("Количество товаров", text="Количество товаров")
        self.category_tree.column("Название", width=400, anchor=tk.W)
        self.category_tree.column("Количество товаров", width=150, anchor=tk.CENTER)
        
        # Привязываем двойной клик
        self.category_tree.bind("<Double-1>", self.on_category_double_click)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.category_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.category_tree.xview)
        self.category_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение элементов
        self.category_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Добавить категорию", command=self.add_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Удалить категорию", command=self.delete_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Обновить список", command=self.refresh_categories).pack(side=tk.LEFT, padx=(0, 5))
        
        # Статус
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_label = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
    def on_drop(self, event):
        """Обработчик перетаскивания файлов"""
        file_path = event.data
        
        # Убираем фигурные скобки, если они есть (Windows)
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        # Проверяем, что это JSON файл
        if file_path.lower().endswith('.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                self.current_file = file_path
                self.load_categories()
                self.file_info_var.set(f"Файл: {os.path.basename(file_path)}")
                self.status_var.set(f"Файл загружен: {os.path.basename(file_path)}")
                self.auto_save()  # Сохраняем сразу после загрузки для создания резервной копии
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
        else:
            messagebox.showwarning("Предупреждение", "Поддерживаются только JSON файлы")
    
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Открыть файл конфигурации",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                self.current_file = filename
                self.load_categories()
                self.file_info_var.set(f"Файл: {os.path.basename(filename)}")
                self.status_var.set(f"Файл загружен: {os.path.basename(filename)}")
                self.auto_save()  # Сохраняем сразу после загрузки для создания резервной копии
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
    
    def auto_save(self):
        """Автоматическое сохранение файла"""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config_data, f, indent=4, ensure_ascii=False)
                self.status_var.set(f"Автосохранение: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            self.status_var.set(f"Файл сохранен: {os.path.basename(self.current_file)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def save_file_as(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить файл как",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.current_file = filename
            self.save_file()
    
    def load_categories(self):
        # Очищаем дерево
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        if 'TraderCategories' in self.config_data:
            for category in self.config_data['TraderCategories']:
                category_name = category['CategoryName']
                product_count = len(category['Products'])
                self.category_tree.insert("", tk.END, values=(category_name, product_count))
    
    def on_search_change(self, *args):
        """Обработчик изменения поискового запроса"""
        self.filter_categories()
    
    def filter_categories(self):
        """Фильтрация категорий по поисковому запросу"""
        search_text = self.search_var.get().lower().strip()
        
        # Очищаем дерево
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        if 'TraderCategories' in self.config_data:
            for category in self.config_data['TraderCategories']:
                category_name = category['CategoryName']
                product_count = len(category['Products'])
                
                # Если поиск пустой или категория содержит поисковый текст
                if not search_text or search_text in category_name.lower():
                    self.category_tree.insert("", tk.END, values=(category_name, product_count))
    
    def clear_search(self):
        """Очистка поискового запроса"""
        self.search_var.set("")
        self.search_entry.focus()
    
    def refresh_categories(self):
        self.filter_categories()
        self.status_var.set("Список категорий обновлен")
    
    def on_category_double_click(self, event):
        selection = self.category_tree.selection()
        if selection:
            item = self.category_tree.item(selection[0])
            category_name = item['values'][0]
            
            # Находим индекс категории
            category_index = None
            for i, category in enumerate(self.config_data['TraderCategories']):
                if category['CategoryName'] == category_name:
                    category_index = i
                    break
            
            if category_index is not None:
                # Открываем окно с товарами
                ProductWindow(self.root, self.config_data, category_index, category_name, self.on_product_window_closed)
    
    def on_product_window_closed(self):
        # Обновляем список категорий после закрытия окна с товарами
        self.refresh_categories()
        self.auto_save()
    
    def add_category(self):
        name = simpledialog.askstring("Новая категория", "Введите название категории:")
        if name:
            new_category = {
                "CategoryName": name,
                "Products": []
            }
            self.config_data['TraderCategories'].append(new_category)
            self.filter_categories()
            self.auto_save()
            self.status_var.set(f"Добавлена категория: {name}")
    
    def delete_category(self):
        selection = self.category_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите категорию для удаления")
            return
        
        item = self.category_tree.item(selection[0])
        category_name = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить категорию '{category_name}' и все товары в ней?"):
            # Находим и удаляем категорию
            for i, category in enumerate(self.config_data['TraderCategories']):
                if category['CategoryName'] == category_name:
                    del self.config_data['TraderCategories'][i]
                    break
            
            self.filter_categories()
            self.auto_save()
            self.status_var.set(f"Удалена категория: {category_name}")

class ProductWindow:
    def __init__(self, parent, config_data, category_index, category_name, callback):
        self.parent = parent
        self.config_data = config_data
        self.category_index = category_index
        self.category_name = category_name
        self.callback = callback
        self.selected_product = None
        
        # Создаем окно
        self.window = tk.Toplevel(parent)
        self.window.title(f"Товары: {category_name}")
        self.window.geometry("1000x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем окно
        self.window.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        self.load_products()
        
        # Обработчик закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        # Заголовок
        header_frame = ttk.Frame(self.window)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text=f"Категория: {self.category_name}", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # Кнопки управления
        ttk.Button(header_frame, text="Добавить товар", command=self.add_product).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(header_frame, text="Удалить товар", command=self.delete_product).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Основной контент
        content_frame = ttk.Frame(self.window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Список товаров
        list_frame = ttk.LabelFrame(content_frame, text="Товары")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем Treeview для товаров
        columns = ("Classname", "Coefficient", "Max Stock", "Trade Quantity", "Buy Price", "Sell Price")
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.product_tree.heading("Classname", text="Класснейм")
        self.product_tree.heading("Coefficient", text="Коэффициент")
        self.product_tree.heading("Max Stock", text="Макс. запас")
        self.product_tree.heading("Trade Quantity", text="Кол-во")
        self.product_tree.heading("Buy Price", text="Цена покупки")
        self.product_tree.heading("Sell Price", text="Цена продажи")
        
        self.product_tree.column("Classname", width=180, anchor=tk.W)
        self.product_tree.column("Coefficient", width=80, anchor=tk.CENTER)
        self.product_tree.column("Max Stock", width=80, anchor=tk.CENTER)
        self.product_tree.column("Trade Quantity", width=90, anchor=tk.CENTER)
        self.product_tree.column("Buy Price", width=80, anchor=tk.CENTER)
        self.product_tree.column("Sell Price", width=80, anchor=tk.CENTER)
        
        # Привязываем выбор
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        self.product_tree.bind("<Double-1>", self.on_product_double_click)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.product_tree.xview)
        self.product_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение элементов
        self.product_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Статус
        self.status_var = tk.StringVar()
        self.status_var.set("Двойной клик для редактирования товара")
        status_label = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_products(self):
        # Очищаем дерево
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        
        category = self.config_data['TraderCategories'][self.category_index]
        for product in category['Products']:
            parts = product.split(',')
            if len(parts) >= 6:
                classname = parts[0]
                coefficient = parts[1]
                maxstock = parts[2]
                trade_quantity = parts[3]
                buy_price = parts[4]
                sell_price = parts[5]
                
                self.product_tree.insert("", tk.END, values=(classname, coefficient, maxstock, trade_quantity, buy_price, sell_price))
    
    def on_product_select(self, event):
        """Обработчик выбора товара (оставлен для совместимости)"""
        pass
    
    def on_product_double_click(self, event):
        """Обработчик двойного клика по товару"""
        selection = self.product_tree.selection()
        if selection:
            item = self.product_tree.item(selection[0])
            values = item['values']
            
            # Находим индекс товара
            item_name = values[0]
            category = self.config_data['TraderCategories'][self.category_index]
            
            for i, product in enumerate(category['Products']):
                if product.split(',')[0] == item_name:
                    # Открываем окно редактирования товара
                    ProductEditWindow(self.window, self.config_data, self.category_index, i, product, self.on_product_edited)
                    break
    
    def on_product_edited(self):
        """Callback после редактирования товара"""
        self.load_products()
        self.auto_save()
        self.status_var.set("Товар отредактирован")
    
    def auto_save(self):
        """Автоматическое сохранение файла"""
        if hasattr(self.parent, 'auto_save'):
            self.parent.auto_save()
    
    def add_product(self):
        dialog = ProductDialog(self.window)
        if dialog.result:
            classname, coefficient, maxstock, trade_quantity, buy_price, sell_price = dialog.result
            new_product_str = f"{classname},{coefficient},{maxstock},{trade_quantity},{buy_price},{sell_price}"
            
            category = self.config_data['TraderCategories'][self.category_index]
            category['Products'].append(new_product_str)
            
            self.load_products()
            self.auto_save()
            self.status_var.set(f"Добавлен товар: {classname}")
    
    def delete_product(self):
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return
        
        item = self.product_tree.item(selection[0])
        item_name = item['values'][0]
        
        # Находим индекс товара
        category = self.config_data['TraderCategories'][self.category_index]
        product_index = None
        for i, product in enumerate(category['Products']):
            if product.split(',')[0] == item_name:
                product_index = i
                break
        
        if product_index is not None:
            if messagebox.askyesno("Подтверждение", f"Удалить товар '{item_name}'?"):
                del category['Products'][product_index]
                self.load_products()
                self.auto_save()
                self.status_var.set(f"Удален товар: {item_name}")
    
    def clear_product_fields(self):
        """Очистка полей (оставлен для совместимости)"""
        pass
    
    def on_closing(self):
        if self.callback:
            self.callback()
        self.window.destroy()

class ProductDialog:
    def __init__(self, parent):
        self.result = None
        
        # Создаем диалоговое окно
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить товар")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрируем окно
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Создаем поля
        ttk.Label(self.dialog, text="Название предмета:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.classname_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.classname_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.dialog, text="Коэффициент:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.coefficient_var = tk.StringVar(value="1")
        ttk.Entry(self.dialog, textvariable=self.coefficient_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.dialog, text="Макс. запас:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.maxstock_var = tk.StringVar(value="100")
        ttk.Entry(self.dialog, textvariable=self.maxstock_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.dialog, text="Кол-во для торговли:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.trade_quantity_var = tk.StringVar(value="1")
        ttk.Entry(self.dialog, textvariable=self.trade_quantity_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.dialog, text="Цена покупки:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.buy_price_var = tk.StringVar(value="100")
        ttk.Entry(self.dialog, textvariable=self.buy_price_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.dialog, text="Цена продажи:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.sell_price_var = tk.StringVar(value="50")
        ttk.Entry(self.dialog, textvariable=self.sell_price_var, width=10).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)
        
        # Ждем закрытия окна
        self.dialog.wait_window()
    
    def ok_clicked(self):
        # Проверяем, что все поля заполнены
        if not all([self.classname_var.get().strip(), self.coefficient_var.get().strip(), 
                   self.maxstock_var.get().strip(), self.trade_quantity_var.get().strip(), 
                   self.buy_price_var.get().strip(), self.sell_price_var.get().strip()]):
            messagebox.showwarning("Предупреждение", "Все поля должны быть заполнены")
            return
        
        self.result = (
            self.classname_var.get().strip(),
            self.coefficient_var.get().strip(),
            self.maxstock_var.get().strip(),
            self.trade_quantity_var.get().strip(),
            self.buy_price_var.get().strip(),
            self.sell_price_var.get().strip()
        )
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()

class ProductEditWindow:
    def __init__(self, parent, config_data, category_index, product_index, product_str, callback):
        self.parent = parent
        self.config_data = config_data
        self.category_index = category_index
        self.product_index = product_index
        self.product_str = product_str
        self.callback = callback
        
        # Создаем окно
        self.window = tk.Toplevel(parent)
        self.window.title("Редактирование товара")
        self.window.geometry("400x350")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Центрируем окно
        self.window.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        self.create_widgets()
        self.load_product_data()
        
        # Обработчик закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        # Заголовок
        header_frame = ttk.Frame(self.window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="Редактирование товара", font=("Arial", 12, "bold")).pack()
        
        # Основной контент
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Поля для редактирования
        fields_frame = ttk.LabelFrame(main_frame, text="Параметры товара")
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Classname
        ttk.Label(fields_frame, text="Название предмета:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.classname_var = tk.StringVar()
        self.classname_entry = ttk.Entry(fields_frame, textvariable=self.classname_var, width=30)
        self.classname_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Coefficient
        ttk.Label(fields_frame, text="Коэффициент:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.coefficient_var = tk.StringVar()
        self.coefficient_entry = ttk.Entry(fields_frame, textvariable=self.coefficient_var, width=10)
        self.coefficient_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Max Stock
        ttk.Label(fields_frame, text="Макс. запас:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.maxstock_var = tk.StringVar()
        self.maxstock_entry = ttk.Entry(fields_frame, textvariable=self.maxstock_var, width=10)
        self.maxstock_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Trade Quantity
        ttk.Label(fields_frame, text="Кол-во для торговли:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.trade_quantity_var = tk.StringVar()
        self.trade_quantity_entry = ttk.Entry(fields_frame, textvariable=self.trade_quantity_var, width=10)
        self.trade_quantity_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buy Price
        ttk.Label(fields_frame, text="Цена покупки:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.buy_price_var = tk.StringVar()
        self.buy_price_entry = ttk.Entry(fields_frame, textvariable=self.buy_price_var, width=10)
        self.buy_price_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Sell Price
        ttk.Label(fields_frame, text="Цена продажи:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.sell_price_var = tk.StringVar()
        self.sell_price_entry = ttk.Entry(fields_frame, textvariable=self.sell_price_var, width=10)
        self.sell_price_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Применить", command=self.apply_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Отмена", command=self.cancel_changes).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Статус
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к редактированию")
        status_label = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN)
        status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
    def load_product_data(self):
        """Загружаем данные товара в поля"""
        parts = self.product_str.split(',')
        if len(parts) >= 6:
            self.classname_var.set(parts[0])
            self.coefficient_var.set(parts[1])
            self.maxstock_var.set(parts[2])
            self.trade_quantity_var.set(parts[3])
            self.buy_price_var.set(parts[4])
            self.sell_price_var.set(parts[5])
            
            self.status_var.set(f"Редактирование: {parts[0]}")
    
    def apply_changes(self):
        """Применяем изменения"""
        try:
            # Собираем новые данные
            classname = self.classname_var.get().strip()
            coefficient = self.coefficient_var.get().strip()
            maxstock = self.maxstock_var.get().strip()
            trade_quantity = self.trade_quantity_var.get().strip()
            buy_price = self.buy_price_var.get().strip()
            sell_price = self.sell_price_var.get().strip()
            
            # Проверяем, что все поля заполнены
            if not all([classname, coefficient, maxstock, trade_quantity, buy_price, sell_price]):
                messagebox.showwarning("Предупреждение", "Все поля должны быть заполнены")
                return
            
            # Формируем новую строку товара
            new_product_str = f"{classname},{coefficient},{maxstock},{trade_quantity},{buy_price},{sell_price}"
            
            # Обновляем данные
            category = self.config_data['TraderCategories'][self.category_index]
            category['Products'][self.product_index] = new_product_str
            
            self.status_var.set("Изменения применены")
            
            # Вызываем callback для обновления основного окна
            if self.callback:
                self.callback()
            
            # Автосохранение
            self.auto_save()
            
            # Закрываем окно
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить изменения: {str(e)}")
    
    def auto_save(self):
        """Автоматическое сохранение файла"""
        # Находим главное окно и вызываем автосохранение
        main_window = self.parent
        while hasattr(main_window, 'parent') and main_window.parent:
            main_window = main_window.parent
        if hasattr(main_window, 'auto_save'):
            main_window.auto_save()
    
    def cancel_changes(self):
        """Отменяем изменения и закрываем окно"""
        self.window.destroy()
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.window.destroy()

def main():
    root = tkdnd.TkinterDnD.Tk()
    app = TraderPlusEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main() 