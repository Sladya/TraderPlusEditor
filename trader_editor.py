import sys
import json
import os
from typing import Dict, List, Any
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton,
                             QTreeWidget, QTreeWidgetItem, QMenuBar, QStatusBar,
                             QFileDialog, QMessageBox, QInputDialog, QDialog,
                             QFormLayout, QHeaderView, QMenu,
                             QAction, QProgressBar, QSplitter, QTextEdit, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QKeySequence, QPixmap

class TraderPlusEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Данные
        self.config_data = {}
        self.current_file = ""
        self.file_type = "price"  # "price" или "general"
        
        # Настройка окна
        self.setWindowTitle("TraderPlusEditor")
        self.setGeometry(100, 100, 1000, 800)
        
        # Установка иконки окна
        try:
            # Пробуем загрузить иконку из файла
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                print(f"Иконка загружена: {icon_path}")
            else:
                # Если файл не найден, создаем простую иконку
                print(f"Файл иконки не найден: {icon_path}")
                # Создаем простую иконку
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor(52, 152, 219))  # Синий цвет
                self.setWindowIcon(QIcon(pixmap))
        except Exception as e:
            print(f"Ошибка загрузки иконки: {e}")
            # Создаем простую иконку в случае ошибки
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(52, 152, 219))
            self.setWindowIcon(QIcon(pixmap))
        
        # Установка минимального размера
        self.setMinimumSize(1100, 800)
        
        # Настройка стилей приложения
        self.setup_application_style()
        
        # Создание интерфейса
        self.create_interface()
        self.setup_drag_drop()
        
    def setup_application_style(self):
        """Настройка стилей всего приложения"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QLabel {
                font-size: 13px;
                color: #333;
            }
            
            QLineEdit {
                font-size: 13px;
                padding: 8px 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #4CAF50;
                outline: none;
            }
            
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                background-color: #4CAF50;
                color: white;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QTreeWidget {
                font-size: 13px;
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #e3f2fd;
            }
            
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eeeeee;
            }
            
            QTreeWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            
            QTreeWidget::item:hover {
                background-color: #e8f4f8;
            }
            
            QHeaderView::section {
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 2px solid #4CAF50;
                background-color: #fafafa;
            }
            
            QStatusBar {
                font-size: 12px;
                background-color: #eeeeee;
                border-top: 1px solid #ddd;
                padding: 5px;
            }
            

        """)
        
    def create_interface(self):
        """Создание основного интерфейса"""
        
        # Информация о файле (создаем заранее)
        self.file_info_label = QLabel("📄 Файл не загружен")
        self.file_info_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #7f8c8d;
                background-color: #ecf0f1;
                padding: 8px 15px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            }
        """)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout с отступами
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 15, 20, 15)  # Отступы от краев
        main_layout.setSpacing(15)  # Расстояние между элементами
        
        # Заголовок и поиск
        header_layout = self.create_header_section()
        main_layout.addLayout(header_layout)
        
        # Создаем контейнер для таблицы и подсказки
        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        # Таблица категорий
        self.create_category_table()
        content_layout.addWidget(self.category_table)
        
        # Подсказка о перетаскивании (изначально скрыта)
        self.drag_hint_label = QLabel()
        self.drag_hint_label.setAlignment(Qt.AlignCenter)
        self.drag_hint_label.setWordWrap(True)
        self.drag_hint_label.setMinimumHeight(150)
        self.drag_hint_label.setMaximumHeight(200)
        self.drag_hint_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.drag_hint_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #3498db;
                background-color: #f8f9fa;
                padding: 40px 30px;
                border: 3px dashed #3498db;
                border-radius: 15px;
                margin: 10px;
                font-weight: bold;
            }
        """)
        self.drag_hint_label.setText("📁 Перетащите файл конфигурации TraderPlus сюда\n\n"
                                   "Поддерживаемые файлы:\n\n"
                                   "TraderPlusPriceConfig.json\n"
                                   "TraderPlusGeneralConfig.json\n"
                                   "TraderPlusIDsConfig.json")
        content_layout.addWidget(self.drag_hint_label)
        
        main_layout.addWidget(self.content_container)
        
        # Кнопки управления
        buttons_layout = self.create_buttons_section()
        main_layout.addLayout(buttons_layout)
        
        # Статусная строка
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                font-size: 13px;
                background-color: #34495e;
                color: white;
                border-top: 2px solid #3498db;
                padding: 8px;
                font-weight: bold;
            }
        """)
        self.status_bar.showMessage("🚀 Готов к работе")
        
        # Показываем подсказку при запуске
        self.show_drag_drop_hint()
        

    def create_header_section(self):
        """Создание секции заголовка и поиска"""
        header_layout = QHBoxLayout()
        
        # Поиск
        search_label = QLabel("🔍 Поиск:")
        search_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                margin-right: 5px;
            }
        """)
        header_layout.addWidget(search_label)
        
        self.search_entry = QLineEdit()
        self.search_entry.setMinimumWidth(300)
        self.search_entry.setMaximumWidth(400)
        self.search_entry.setPlaceholderText("Введите текст для поиска категорий и товаров...")
        self.search_entry.textChanged.connect(self.on_search_change)
        self.search_entry.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 12px 16px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #3498db;
                box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
            }
        """)
        header_layout.addWidget(self.search_entry)
        
        # Кнопка очистки
        clear_button = QPushButton("🗑️ Очистить")
        clear_button.clicked.connect(self.clear_search)
        clear_button.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: bold;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                background-color: #e74c3c;
                color: white;
                margin-left: 10px;
            }
            
            QPushButton:hover {
                background-color: #c0392b;
            }
            
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        header_layout.addWidget(clear_button)
        
        header_layout.addStretch()
        
        # Информация о файле
        header_layout.addWidget(self.file_info_label)
        
        return header_layout
        
    def create_category_table(self):
        """Создание таблицы категорий"""
        self.category_table = QTreeWidget()
        self.category_table.setHeaderLabels(["📂 Название категории", "📊 Информация о товарах"])
        
        # Настройка колонок
        header = self.category_table.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Установка минимальных размеров колонок
        self.category_table.setColumnWidth(0, 500)
        
        # Настройка внешнего вида
        self.category_table.setAlternatingRowColors(True)
        self.category_table.setRootIsDecorated(False)
        self.category_table.setSelectionBehavior(QTreeWidget.SelectRows)
        
        # Увеличиваем высоту строк
        self.category_table.setStyleSheet("""
            QTreeWidget {
                font-size: 14px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #3498db;
                gridline-color: #ecf0f1;
            }
            
            QTreeWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 14px;
            }
            
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            
            QTreeWidget::item:hover {
                background-color: #e8f4f8;
                color: #2c3e50;
            }
            
            QHeaderView::section {
                font-size: 15px;
                font-weight: bold;
                padding: 15px 10px;
                border: none;
                border-right: 1px solid #bdc3c7;
                border-bottom: 3px solid #3498db;
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            
            QHeaderView::section:hover {
                background-color: #d5dbdb;
            }
        """)
        
        # Подключение событий
        self.category_table.itemDoubleClicked.connect(self.on_category_double_click)
        
    def show_drag_drop_hint(self):
        """Показать подсказку о перетаскивании файлов"""
        # Скрываем таблицу и показываем подсказку на всё пространство
        self.category_table.hide()
        self.drag_hint_label.show()
        
        # Убираем ограничения по высоте для подсказки
        self.drag_hint_label.setMinimumHeight(600)
        self.drag_hint_label.setMaximumHeight(16777215)  # Максимальное значение
        
    def create_buttons_section(self):
        """Создание секции кнопок"""
        buttons_layout = QHBoxLayout()
        
        # Стиль для кнопок
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 15px 25px;
                border: none;
                border-radius: 8px;
                color: white;
                margin: 5px;
                min-width: 150px;
            }
        """
        
        self.add_button = QPushButton("➕ Добавить категорию")
        self.add_button.clicked.connect(self.add_category)
        self.add_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #27ae60;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        buttons_layout.addWidget(self.add_button)
        
        self.delete_button = QPushButton("🗑️ Удалить категорию")
        self.delete_button.clicked.connect(self.delete_category)
        self.delete_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        buttons_layout.addWidget(self.delete_button)
        
        # Кнопка сохранить
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_file)
        save_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #f39c12;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        buttons_layout.addWidget(save_button)
        
        # Кнопка выгрузить файл
        unload_button = QPushButton("Закрыть файл")
        unload_button.clicked.connect(self.unload_file)
        unload_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #9b59b6;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        buttons_layout.addWidget(unload_button)
        
        buttons_layout.addStretch()
        
        # Кнопка "О программе"
        about_button = QPushButton("О программе")
        about_button.clicked.connect(self.show_about_dialog)
        about_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #3498db;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        buttons_layout.addWidget(about_button)
        
        return buttons_layout
        
    def unload_file(self):
        """Выгрузка текущего файла"""
        if not self.config_data:
            QMessageBox.information(self, "Информация", "Файл не загружен")
            return
            
        # Очищаем данные
        self.config_data = {}
        self.current_file = ""
        self.file_type = "price"
        
        # Очищаем поиск
        self.search_entry.clear()
        
        # Показываем подсказку и скрываем таблицу
        self.show_drag_drop_hint()
        
        # Обновляем информацию о файле
        self.file_info_label.setText("📄 Файл не загружен")
        self.file_info_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #7f8c8d;
                background-color: #ecf0f1;
                padding: 8px 15px;
                border-radius: 6px;
                border: 1px solid #bdc3c7;
            }
        """)
        
        # Обновляем заголовки кнопок
        self.update_button_labels()
        
        # Обновляем статус
        self.status_bar.showMessage("🚀 Готов к работе")
        
    def setup_drag_drop(self):
        """Настройка drag and drop"""
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        """Обработка входа перетаскиваемого файла"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        """Обработка сброса файла"""
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].lower().endswith('.json'):
            self.load_file(files[0])
        else:
            QMessageBox.warning(self, "Предупреждение", "Поддерживаются только JSON файлы")
            
    def load_file(self, filename):
        """Загрузка файла конфигурации"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            self.current_file = filename
            
            # Определяем тип файла
            self.detect_file_type()
            
            # Скрываем подсказку и показываем таблицу
            self.drag_hint_label.hide()
            self.category_table.show()
            
            # Восстанавливаем нормальный размер подсказки
            self.drag_hint_label.setMinimumHeight(150)
            self.drag_hint_label.setMaximumHeight(200)
            
            # Очищаем таблицу перед загрузкой новых данных
            self.category_table.clear()
            
            # Загружаем данные в зависимости от типа
            if self.file_type == "price":
                self.filter_categories()
            elif self.file_type == "general":
                self.filter_traders()
            else:
                self.filter_ids()
                
            # Обновляем заголовки кнопок
            self.update_button_labels()
                
            self.file_info_label.setText(f"📄 {os.path.basename(filename)}")
            self.file_info_label.setStyleSheet("""
                QLabel {
                    font-size: 13px;
                    color: #27ae60;
                    background-color: #d5f4e6;
                    padding: 8px 15px;
                    border-radius: 6px;
                    border: 1px solid #27ae60;
                    font-weight: bold;
                }
            """)
            self.status_bar.showMessage(f"✅ Файл успешно загружен: {os.path.basename(filename)}")
            self.auto_save()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")
            
    def detect_file_type(self):
        """Определение типа файла конфигурации"""
        if 'TraderCategories' in self.config_data:
            self.file_type = "price"
        elif 'Traders' in self.config_data:
            self.file_type = "general"
        elif 'IDs' in self.config_data:
            self.file_type = "ids"
        else:
            self.file_type = "unknown"
            

            
    def update_button_labels(self):
        """Обновление заголовков кнопок в зависимости от типа файла"""
        if self.file_type == "price":
            self.add_button.setText("➕ Добавить категорию")
            self.delete_button.setText("🗑️ Удалить категорию")
        elif self.file_type == "general":
            self.add_button.setText("➕ Добавить торговца")
            self.delete_button.setText("🗑️ Удалить торговца")
        else:
            self.add_button.setText("➕ Добавить ID торговца")
            self.delete_button.setText("🗑️ Удалить ID торговца")
            

                
    def filter_categories(self):
        """Фильтрация категорий по поисковому запросу"""
        search_text = self.search_entry.text().lower().strip()
        
        self.category_table.clear()
        
        if 'TraderCategories' in self.config_data:
            display_index = 0
            for category in self.config_data['TraderCategories']:
                category_name = category['CategoryName']
                product_count = len(category['Products'])
                show_category = False
                found_in_products = False
                
                # Если поиск пустой, показываем все
                if not search_text:
                    show_category = True
                else:
                    # Поиск в названии категории
                    if search_text in category_name.lower():
                        show_category = True
                    
                    # Поиск по товарам
                    if not show_category:
                        for product in category['Products']:
                            # Разбираем строку товара
                            parts = product.split(',')
                            if len(parts) >= 6:
                                product_text = ','.join(parts).lower()
                                if search_text in product_text:
                                    show_category = True
                                    found_in_products = True
                                    break
                
                if show_category:
                    # Информация для отображения
                    display_name = category_name
                    product_info = f"Товаров: {product_count}"
                    
                    if search_text and found_in_products:
                        # Ищем первый найденный товар для отображения его информации
                        for product in category['Products']:
                            parts = product.split(',')
                            if len(parts) >= 6:
                                product_text = ','.join(parts).lower()
                                if search_text in product_text:
                                    # Найден товар - формируем информацию о нем
                                    classname = parts[0]
                                    buy_price = parts[4]
                                    sell_price = parts[5]
                                    product_info = f"{classname} | Покупка:{buy_price} | Продажа:{sell_price}"
                                    display_name = f"{category_name} ★"
                                    break
                    
                    item = QTreeWidgetItem([display_name, product_info])
                    
                    # Применяем стили
                    if search_text and "★" in display_name:
                        # Подсветка найденных товаров - яркий золотистый цвет
                        item.setBackground(0, QColor(255, 193, 7))  # Золотистый
                        item.setBackground(1, QColor(255, 193, 7))
                        item.setForeground(0, QColor(33, 37, 41))   # Темный текст
                        item.setForeground(1, QColor(33, 37, 41))
                        font = QFont()
                        font.setBold(True)
                        font.setPointSize(14)
                        item.setFont(0, font)
                        item.setFont(1, font)
                        
                        # Добавляем иконку к товару
                        if "★" not in display_name:
                            item.setText(0, f"⭐ {display_name}")
                    else:
                        # Чередующиеся цвета - более мягкие
                        if display_index % 2 == 0:
                            item.setBackground(0, QColor(248, 249, 250))  # Светло-серый
                            item.setBackground(1, QColor(248, 249, 250))
                        else:
                            item.setBackground(0, QColor(255, 255, 255))  # Белый
                            item.setBackground(1, QColor(255, 255, 255))
                    
                    self.category_table.addTopLevelItem(item)
                    display_index += 1
                        
    def filter_traders(self):
        """Фильтрация торговцев по поисковому запросу"""
        search_text = self.search_entry.text().lower().strip()
        
        self.category_table.clear()
        
        if 'Traders' in self.config_data:
            display_index = 0
            for trader in self.config_data['Traders']:
                trader_name = trader.get('GivenName', 'Неизвестный')
                trader_role = trader.get('Role', 'Торговец')
                trader_id = trader.get('Id', -1)
                show_trader = False
                
                # Если поиск пустой, показываем все
                if not search_text:
                    show_trader = True
                else:
                    # Поиск в названии торговца
                    if search_text in trader_name.lower():
                        show_trader = True
                    # Поиск в роли
                    elif search_text in trader_role.lower():
                        show_trader = True
                    # Поиск в ID
                    elif search_text in str(trader_id):
                        show_trader = True
                
                if show_trader:
                    # Информация для отображения
                    display_name = trader_name
                    trader_info = f"ID: {trader_id} | Роль: {trader_role}"
                    
                    if search_text and (search_text in trader_name.lower() or 
                                      search_text in trader_role.lower() or 
                                      search_text in str(trader_id)):
                        display_name = f"{trader_name} ★"
                    
                    item = QTreeWidgetItem([display_name, trader_info])
                    
                    # Применяем стили
                    if search_text and "★" in display_name:
                        # Подсветка найденных торговцев - яркий золотистый цвет
                        item.setBackground(0, QColor(255, 193, 7))  # Золотистый
                        item.setBackground(1, QColor(255, 193, 7))
                        item.setForeground(0, QColor(33, 37, 41))   # Темный текст
                        item.setForeground(1, QColor(33, 37, 41))
                        font = QFont()
                        font.setBold(True)
                        font.setPointSize(14)
                        item.setFont(0, font)
                        item.setFont(1, font)
                    else:
                        # Чередующиеся цвета - более мягкие
                        if display_index % 2 == 0:
                            item.setBackground(0, QColor(248, 249, 250))  # Светло-серый
                            item.setBackground(1, QColor(248, 249, 250))
                        else:
                            item.setBackground(0, QColor(255, 255, 255))  # Белый
                            item.setBackground(1, QColor(255, 255, 255))
                    
                    self.category_table.addTopLevelItem(item)
                    display_index += 1
                    
    def filter_ids(self):
        """Фильтрация ID торговцев по поисковому запросу"""
        search_text = self.search_entry.text().lower().strip()
        
        self.category_table.clear()
        
        if 'IDs' in self.config_data:
            display_index = 0
            for trader_id in self.config_data['IDs']:
                trader_id_value = trader_id.get('Id', -1)
                categories = trader_id.get('Categories', [])
                categories_count = len(categories)
                show_trader = False
                
                # Если поиск пустой, показываем все
                if not search_text:
                    show_trader = True
                else:
                    # Поиск в ID торговца
                    if search_text in str(trader_id_value):
                        show_trader = True
                    # Поиск в категориях
                    else:
                        for category in categories:
                            if search_text in category.lower():
                                show_trader = True
                                break
                
                if show_trader:
                    # Информация для отображения
                    display_name = f"ID: {trader_id_value}"
                    trader_info = f"Категорий: {categories_count}"
                    
                    if search_text and (search_text in str(trader_id_value) or 
                                      any(search_text in cat.lower() for cat in categories)):
                        display_name = f"ID: {trader_id_value} ★"
                    
                    item = QTreeWidgetItem([display_name, trader_info])
                    
                    # Применяем стили
                    if search_text and "★" in display_name:
                        # Подсветка найденных торговцев - яркий золотистый цвет
                        item.setBackground(0, QColor(255, 193, 7))  # Золотистый
                        item.setBackground(1, QColor(255, 193, 7))
                        item.setForeground(0, QColor(33, 37, 41))   # Темный текст
                        item.setForeground(1, QColor(33, 37, 41))
                        font = QFont()
                        font.setBold(True)
                        font.setPointSize(14)
                        item.setFont(0, font)
                        item.setFont(1, font)
                    else:
                        # Чередующиеся цвета - более мягкие
                        if display_index % 2 == 0:
                            item.setBackground(0, QColor(248, 249, 250))  # Светло-серый
                            item.setBackground(1, QColor(248, 249, 250))
                        else:
                            item.setBackground(0, QColor(255, 255, 255))  # Белый
                            item.setBackground(1, QColor(255, 255, 255))
                    
                    self.category_table.addTopLevelItem(item)
                    display_index += 1
                    
    def on_search_change(self):
        """Обработчик изменения поискового запроса"""
        if self.file_type == "price":
            self.filter_categories()
        elif self.file_type == "general":
            self.filter_traders()
        else:
            self.filter_ids()
        
    def clear_search(self):
        """Очистка поискового запроса"""
        self.search_entry.clear()
        self.search_entry.setFocus()
        
        # Если файл не загружен, показываем подсказку о перетаскивании
        if not self.config_data:
            self.show_drag_drop_hint()
        

    def on_category_double_click(self, item):
        """Обработчик двойного клика по категории/торговцу"""
        if not item or not self.config_data:
            return
            
        item_name = item.text(0)
        
        # Убираем звездочку из названия, если она есть
        if item_name.endswith(" ★"):
            item_name = item_name[:-2]
        
        if self.file_type == "price":
            # Обработка для файла цен
            # Находим индекс категории
            category_index = None
            for i, category in enumerate(self.config_data['TraderCategories']):
                if category['CategoryName'] == item_name:
                    category_index = i
                    break
            
            if category_index is not None:
                # Получаем текущий поисковый запрос
                search_text = self.search_entry.text().strip()
            
            # Если поиск активен и товар найден в данной категории, сразу открываем редактор первого найденного товара
            if search_text and "★" in item.text(0):
                category = self.config_data['TraderCategories'][category_index]
                for product_index, product in enumerate(category['Products']):
                    parts = product.split(',')
                    if len(parts) >= 6:
                        # Ищем во всех полях товара
                        product_text = f"{parts[0]},{parts[1]},{parts[2]},{parts[3]},{parts[4]},{parts[5]}".lower()
                        if search_text.lower() in product_text:
                            # Найден товар! Сразу открываем редактор
                            self.edit_product_dialog(category_index, product_index, product)
                            return
            
            # Обычное открытие окна с товарами
            self.open_product_window(category_index, item_name, search_text)
        elif self.file_type == "general":
            # Обработка для файла general
            # Находим индекс торговца
            trader_index = None
            for i, trader in enumerate(self.config_data['Traders']):
                if trader.get('GivenName', '') == item_name:
                    trader_index = i
                    break
            
            if trader_index is not None:
                # Открываем диалог редактирования торговца
                self.edit_trader_dialog(trader_index)
        else:
            # Обработка для файла IDs
            # Извлекаем ID из названия (формат: "ID: X")
            if item_name.startswith("ID: "):
                try:
                    trader_id_value = int(item_name[4:])  # Убираем "ID: "
                    # Находим индекс торговца по ID
                    trader_index = None
                    for i, trader_id in enumerate(self.config_data['IDs']):
                        if trader_id.get('Id') == trader_id_value:
                            trader_index = i
                            break
                    
                    if trader_index is not None:
                        # Открываем диалог редактирования ID торговца
                        self.edit_trader_id_dialog(trader_index)
                except ValueError:
                    pass
                
    def edit_trader_dialog(self, trader_index):
        """Диалог редактирования торговца"""
        trader = self.config_data['Traders'][trader_index]
        dialog = TraderEditDialog(self, trader)
        if dialog.exec_() == QDialog.Accepted:
            # Обновляем данные
            updated_trader = dialog.get_trader_data()
            self.config_data['Traders'][trader_index] = updated_trader
            
            self.filter_traders()
            self.auto_save()
            self.status_bar.showMessage("Торговец отредактирован")
            
    def edit_trader_id_dialog(self, trader_index):
        """Диалог редактирования ID торговца"""
        trader_id_data = self.config_data['IDs'][trader_index]
        dialog = TraderIDEditDialog(self, trader_id_data)
        if dialog.exec_() == QDialog.Accepted:
            # Обновляем данные
            updated_trader_id = dialog.get_trader_id_data()
            self.config_data['IDs'][trader_index] = updated_trader_id
            
            self.filter_ids()
            self.auto_save()
            self.status_bar.showMessage("ID торговца отредактирован")
            
    def edit_product_dialog(self, category_index, product_index, product_str):
        """Диалог редактирования товара"""
        dialog = ProductEditDialog(self, product_str)
        if dialog.exec_() == QDialog.Accepted:
            # Обновляем данные
            new_product_str = dialog.get_product_string()
            category = self.config_data['TraderCategories'][category_index]
            category['Products'][product_index] = new_product_str
            
            self.filter_categories()
            self.auto_save()
            self.status_bar.showMessage("Товар отредактирован из поиска")
            
    def open_product_window(self, category_index, category_name, search_text=""):
        """Открытие окна с товарами"""
        window = ProductWindow(self, self.config_data, category_index, category_name, search_text)
        window.exec_()
        # Обновляем список категорий после закрытия окна
        self.filter_categories()
        self.auto_save()
        
    def add_category(self):
        """Добавление новой категории/торговца"""
        if self.file_type == "price":
            name, ok = QInputDialog.getText(self, 'Новая категория', 'Введите название категории:')
            if ok and name:
                new_category = {
                    "CategoryName": name,
                    "Products": []
                }
                if 'TraderCategories' not in self.config_data:
                    self.config_data['TraderCategories'] = []
                self.config_data['TraderCategories'].append(new_category)
                self.filter_categories()
                self.auto_save()
                self.status_bar.showMessage(f"Добавлена категория: {name}")
        elif self.file_type == "general":
            # Добавление нового торговца
            self.add_trader()
        else:
            # Добавление нового ID торговца
            self.add_trader_id()
            
    def add_trader(self):
        """Добавление нового торговца"""
        # Создаем базовый торговец
        new_trader = {
            "Id": len(self.config_data.get('Traders', [])),
            "Name": "pr_npc_neutrals",
            "GivenName": "Новый торговец",
            "Role": "Торговец",
            "Position": [0, 0, 0],
            "Orientation": [0, 0, 0],
            "Clothes": []
        }
        
        # Открываем диалог редактирования
        dialog = TraderEditDialog(self, new_trader)
        if dialog.exec_() == QDialog.Accepted:
            updated_trader = dialog.get_trader_data()
            
            if 'Traders' not in self.config_data:
                self.config_data['Traders'] = []
            self.config_data['Traders'].append(updated_trader)
            
            self.filter_traders()
            self.auto_save()
            self.status_bar.showMessage(f"Добавлен торговец: {updated_trader['GivenName']}")
            
    def add_trader_id(self):
        """Добавление нового ID торговца"""
        # Создаем базовый ID торговца
        new_trader_id = {
            "Id": len(self.config_data.get('IDs', [])),
            "Categories": [],
            "LicencesRequired": [],
            "CurrenciesAccepted": []
        }
        
        # Открываем диалог редактирования
        dialog = TraderIDEditDialog(self, new_trader_id)
        if dialog.exec_() == QDialog.Accepted:
            updated_trader_id = dialog.get_trader_id_data()
            
            if 'IDs' not in self.config_data:
                self.config_data['IDs'] = []
            self.config_data['IDs'].append(updated_trader_id)
            
            self.filter_ids()
            self.auto_save()
            self.status_bar.showMessage(f"Добавлен ID торговца: {updated_trader_id['Id']}")
            
    def delete_category(self):
        """Удаление выбранной категории/торговца"""
        current_item = self.category_table.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Выберите элемент для удаления")
            return
        
        item_name = current_item.text(0)
        if item_name.endswith(" ★"):
            item_name = item_name[:-2]
        
        if self.file_type == "price":
            reply = QMessageBox.question(self, 'Подтверждение', 
                                       f"Удалить категорию '{item_name}' и все товары в ней?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Находим и удаляем категорию
                for i, category in enumerate(self.config_data['TraderCategories']):
                    if category['CategoryName'] == item_name:
                        del self.config_data['TraderCategories'][i]
                        break
                
                self.filter_categories()
                self.auto_save()
                self.status_bar.showMessage(f"Удалена категория: {item_name}")
        elif self.file_type == "general":
            reply = QMessageBox.question(self, 'Подтверждение', 
                                       f"Удалить торговца '{item_name}'?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Находим и удаляем торговца
                for i, trader in enumerate(self.config_data['Traders']):
                    if trader.get('GivenName', '') == item_name:
                        del self.config_data['Traders'][i]
                        break
                
                self.filter_traders()
                self.auto_save()
                self.status_bar.showMessage(f"Удален торговец: {item_name}")
        else:
            # Удаление ID торговца
            if item_name.startswith("ID: "):
                try:
                    trader_id_value = int(item_name[4:])  # Убираем "ID: "
                    reply = QMessageBox.question(self, 'Подтверждение', 
                                               f"Удалить ID торговца '{trader_id_value}'?",
                                               QMessageBox.Yes | QMessageBox.No)
                    
                    if reply == QMessageBox.Yes:
                        # Находим и удаляем ID торговца
                        for i, trader_id in enumerate(self.config_data['IDs']):
                            if trader_id.get('Id') == trader_id_value:
                                del self.config_data['IDs'][i]
                                break
                        
                        self.filter_ids()
                        self.auto_save()
                        self.status_bar.showMessage(f"Удален ID торговца: {trader_id_value}")
                except ValueError:
                    pass
            
    def open_file(self):
        """Открытие файла через диалог"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл конфигурации", "",
            "JSON files (*.json);;All files (*.*)"
        )
        if filename:
            self.load_file(filename)
            
    def save_file(self):
        """Сохранение файла"""
        if not self.current_file:
            return self.save_file_as()
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            self.status_bar.showMessage(f"Файл сохранен: {os.path.basename(self.current_file)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
            
    def save_file_as(self):
        """Сохранение файла как"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл как", "",
            "JSON files (*.json);;All files (*.*)"
        )
        if filename:
            self.current_file = filename
            self.save_file()
            
    def auto_save(self):
        """Автоматическое сохранение файла"""
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config_data, f, indent=4, ensure_ascii=False)
                self.status_bar.showMessage(f"Автосохранение: {os.path.basename(self.current_file)}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
                
    def show_about_dialog(self):
        """Показать диалог 'О программе'"""
        about_text = """
        <div style="text-align: center; padding: 20px;">
            <h2 style="color: #2c3e50; margin-bottom: 15px;">TraderPlusEditor</h2>
            <p style="font-size: 14px; color: #34495e; margin-bottom: 10px;">
                <strong>Версия:</strong> 1.0.0
            </p>
            <p style="font-size: 14px; color: #34495e; margin-bottom: 10px;">
                <strong>Описание:</strong> Редактор конфигураций для мода TraderPlus в DayZ
            </p>
            <p style="font-size: 14px; color: #27ae60; margin-bottom: 10px; font-weight: bold;">
                <strong>Программа распространяется бесплатно</strong>
            </p>
            <hr style="border: 1px solid #bdc3c7; margin: 15px 0;">
            <p style="font-size: 14px; color: #34495e; margin-bottom: 10px;">
                <strong>Автор:</strong> Sladya
            </p>
            <p style="font-size: 14px; color: #34495e; margin-bottom: 10px;">
                <strong>Связь в :</strong> 
                <a href="https://discord.gg/jdaxza27Db" style="color: #3498db; text-decoration: none;">
                    Discord
                </a>
            </p>
            <p style="font-size: 14px; color: #34495e; margin-bottom: 15px;">
                <strong>GitHub:</strong> 
                <a href="https://github.com/Sladya/TraderPlusEditor" style="color: #3498db; text-decoration: none;">
                    Репозиторий проекта
                </a>
            </p>
            <p style="font-size: 12px; color: #7f8c8d; margin-top: 20px;">
                © 2025 TraderPlusEditor. Все права защищены.
            </p>
        </div>
        """
        
        QMessageBox.about(self, "О программе", about_text)


class ProductWindow(QDialog):
    def __init__(self, parent, config_data, category_index, category_name, search_text=""):
        super().__init__(parent)
        self.parent = parent
        self.config_data = config_data
        self.category_index = category_index
        self.category_name = category_name
        self.search_text = search_text.lower()
        
        # Формируем заголовок с информацией о поиске
        title = f"Товары: {category_name}"
        if self.search_text:
            title += f" | Поиск: '{search_text}'"
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(1400, 800)
        
        # Установка иконки окна
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor(52, 152, 219))
                self.setWindowIcon(QIcon(pixmap))
        except Exception as e:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(52, 152, 219))
            self.setWindowIcon(QIcon(pixmap))
        self.setMinimumSize(900, 700)
        
        self.setup_ui()
        self.load_products()
        
    def setup_ui(self):
        """Настройка интерфейса окна товаров"""
        layout = QVBoxLayout(self)
        
        # Заголовок и кнопки
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"📦 Категория: {self.category_name}")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)  # Увеличил размер
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                margin: 5px;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Стиль для кнопок в окне товаров
        button_style = """
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                color: white;
                margin: 5px;
                min-width: 130px;
            }
        """
        
        add_button = QPushButton("➕ Добавить товар")
        add_button.clicked.connect(self.add_product)
        add_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #27ae60;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        header_layout.addWidget(add_button)
        
        delete_button = QPushButton("🗑️ Удалить товар")
        delete_button.clicked.connect(self.delete_product)
        delete_button.setStyleSheet(button_style + """
            QPushButton {
                background-color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        header_layout.addWidget(delete_button)
        
        layout.addLayout(header_layout)
        
        # Таблица товаров
        self.product_table = QTreeWidget()
        self.product_table.setHeaderLabels([
            "🔹 Класснейм", "⚙️ Коэффициент", "📦 Макс. запас", 
            "🔢 Кол-во", "💰 Цена покупки", "💵 Цена продажи"
        ])
        
        # Настройка колонок
        header = self.product_table.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Классnейм с возможностью изменения
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # Коэффициент
        header.setSectionResizeMode(2, QHeaderView.Interactive)  # Макс. запас
        header.setSectionResizeMode(3, QHeaderView.Interactive)  # Кол-во
        header.setSectionResizeMode(4, QHeaderView.Interactive)  # Цена покупки
        header.setSectionResizeMode(5, QHeaderView.Interactive)  # Цена продажи
        
        # Установка оптимальных размеров колонок
        self.product_table.setColumnWidth(0, 350)  # Класснейм - увеличил для длинных названий
        self.product_table.setColumnWidth(1, 150)  # Коэффициент
        self.product_table.setColumnWidth(2, 150)  # Макс. запас
        self.product_table.setColumnWidth(3, 120)  # Кол-во
        self.product_table.setColumnWidth(4, 150)  # Цена покупки
        self.product_table.setColumnWidth(5, 150)  # Цена продажи
        
        # Настройка внешнего вида с увеличенным шрифтом
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setRootIsDecorated(False)
        self.product_table.setSelectionBehavior(QTreeWidget.SelectRows)
        
        # Улучшенные стили для таблицы товаров
        self.product_table.setStyleSheet("""
            QTreeWidget {
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #3498db;
                gridline-color: #ecf0f1;
                outline: none;
            }
            
            QTreeWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 14px;
                font-weight: normal;
                height: 32px;
            }
            
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            
            QTreeWidget::item:hover {
                background-color: #e8f4f8;
                color: #2c3e50;
            }
            
            QHeaderView::section {
                font-size: 13px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 12px 8px;
                border: none;
                border-right: 1px solid #bdc3c7;
                border-bottom: 3px solid #3498db;
                background-color: #ecf0f1;
                color: #2c3e50;
                text-align: center;
            }
            
            QHeaderView::section:hover {
                background-color: #d5dbdb;
            }
            
            QHeaderView::section:first {
                text-align: left;
            }
        """)
        
        # Подключение событий
        self.product_table.itemDoubleClicked.connect(self.edit_product)
        
        layout.addWidget(self.product_table)
        
        # Статусная строка
        self.status_label = QLabel("🖱️ Двойной клик для редактирования товара")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                background-color: #34495e;
                color: white;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label)
        
    def load_products(self):
        """Загрузка товаров в таблицу"""
        self.product_table.clear()
        
        category = self.config_data['TraderCategories'][self.category_index]
        display_index = 0
        first_found_item = None
        
        for i, product in enumerate(category['Products']):
            parts = product.split(',')
            if len(parts) >= 6:
                classname = parts[0]
                coefficient = parts[1]
                maxstock = parts[2]
                trade_quantity = parts[3]
                buy_price = parts[4]
                sell_price = parts[5]
                
                # Проверяем, соответствует ли товар поиску
                show_product = True
                is_found_item = False
                
                if self.search_text:
                    # Ищем во всех полях товара
                    product_text = f"{classname},{coefficient},{maxstock},{trade_quantity},{buy_price},{sell_price}".lower()
                    if self.search_text in product_text:
                        is_found_item = True
                    else:
                        # Если поиск активен, но товар не найден, пропускаем его
                        show_product = False
                
                if show_product:
                    item = QTreeWidgetItem([classname, coefficient, maxstock, trade_quantity, buy_price, sell_price])
                    
                    # Определяем стиль
                    if is_found_item:
                        # Стиль для найденных товаров - золотистый
                        highlight_color = QColor(255, 193, 7)
                        text_color = QColor(33, 37, 41)
                        for col in range(6):
                            item.setBackground(col, highlight_color)
                            item.setForeground(col, text_color)
                        font = QFont()
                        font.setBold(True)
                        font.setPointSize(14)
                        for col in range(6):
                            item.setFont(col, font)
                    else:
                        # Стандартные цвета для обычных строк
                        pass  # Используем стандартное чередование из CSS
                    
                    self.product_table.addTopLevelItem(item)
                    
                    # Запоминаем первый найденный товар для автовыбора
                    if is_found_item and first_found_item is None:
                        first_found_item = item
                    
                    display_index += 1
        
        # Автоматически выбираем первый найденный товар
        if first_found_item and self.search_text:
            self.product_table.setCurrentItem(first_found_item)
            self.product_table.scrollToItem(first_found_item)
            
    def edit_product(self, item):
        """Редактирование выбранного товара"""
        if not item:
            return
            
        # Получаем данные товара
        classname = item.text(0)
        
        # Находим индекс товара в данных
        category = self.config_data['TraderCategories'][self.category_index]
        product_index = None
        product_str = None
        
        for i, product in enumerate(category['Products']):
            if product.split(',')[0] == classname:
                product_index = i
                product_str = product
                break
        
        if product_index is not None and product_str is not None:
            dialog = ProductEditDialog(self, product_str)
            if dialog.exec_() == QDialog.Accepted:
                # Обновляем данные
                new_product_str = dialog.get_product_string()
                category['Products'][product_index] = new_product_str
                
                self.load_products()
                self.parent.auto_save()
                self.status_label.setText("✅ Товар успешно отредактирован")
                
    def add_product(self):
        """Добавление нового товара"""
        dialog = ProductAddDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_product_str = dialog.get_product_string()
            
            category = self.config_data['TraderCategories'][self.category_index]
            category['Products'].append(new_product_str)
            
            self.load_products()
            self.parent.auto_save()
            classname = new_product_str.split(',')[0]
            self.status_label.setText(f"✅ Товар добавлен: {classname}")
            
    def delete_product(self):
        """Удаление выбранного товара"""
        current_item = self.product_table.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Выберите товар для удаления")
            return
        
        classname = current_item.text(0)
        
        reply = QMessageBox.question(self, 'Подтверждение', 
                                   f"Удалить товар '{classname}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Находим и удаляем товар
            category = self.config_data['TraderCategories'][self.category_index]
            for i, product in enumerate(category['Products']):
                if product.split(',')[0] == classname:
                    del category['Products'][i]
                    break
            
            self.load_products()
            self.parent.auto_save()
            self.status_label.setText(f"🗑️ Товар удален: {classname}")


class ProductAddDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("➕ Добавить товар")
        self.setModal(True)
        self.resize(550, 480)
        self.setMinimumSize(500, 450)
        
        # Установка иконки окна
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor(52, 152, 219))
                self.setWindowIcon(QIcon(pixmap))
        except Exception as e:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(52, 152, 219))
            self.setWindowIcon(QIcon(pixmap))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса диалога добавления"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel("🛒 Добавление нового товара")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Форма
        form_layout = QFormLayout()
        form_layout.setSpacing(18)
        form_layout.setVerticalSpacing(15)
        
        # Стиль для полей ввода
        input_style = """
            QLineEdit {
                font-size: 14px;
                padding: 12px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-height: 20px;
                max-height: 40px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        
        # Стиль для меток
        label_style = """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                padding: 5px;
            }
        """
        
        self.classname_edit = QLineEdit()
        self.classname_edit.setStyleSheet(input_style)
        label1 = QLabel("🔹 Класснейм:")
        label1.setStyleSheet(label_style)
        form_layout.addRow(label1, self.classname_edit)
        
        self.coefficient_edit = QLineEdit("1")
        self.coefficient_edit.setStyleSheet(input_style)
        label2 = QLabel("⚙️ Коэффициент:")
        label2.setStyleSheet(label_style)
        form_layout.addRow(label2, self.coefficient_edit)
        
        self.maxstock_edit = QLineEdit("100")
        self.maxstock_edit.setStyleSheet(input_style)
        label3 = QLabel("📦 Макс. запас:")
        label3.setStyleSheet(label_style)
        form_layout.addRow(label3, self.maxstock_edit)
        
        self.trade_quantity_edit = QLineEdit("1")
        self.trade_quantity_edit.setStyleSheet(input_style)
        label4 = QLabel("🔢 Кол-во для торговли:")
        label4.setStyleSheet(label_style)
        form_layout.addRow(label4, self.trade_quantity_edit)
        
        self.buy_price_edit = QLineEdit("100")
        self.buy_price_edit.setStyleSheet(input_style)
        label5 = QLabel("💰 Цена покупки:")
        label5.setStyleSheet(label_style)
        form_layout.addRow(label5, self.buy_price_edit)
        
        self.sell_price_edit = QLineEdit("50")
        self.sell_price_edit.setStyleSheet(input_style)
        label6 = QLabel("💵 Цена продажи:")
        label6.setStyleSheet(label_style)
        form_layout.addRow(label6, self.sell_price_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                background-color: #27ae60;
                color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_button.clicked.connect(self.validate_and_accept)
        
        cancel_button = QPushButton("Закрыть")
        cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                background-color: #e74c3c;
                color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def validate_and_accept(self):
        """Проверка данных и принятие диалога"""
        if not all([self.classname_edit.text().strip(), self.coefficient_edit.text().strip(),
                   self.maxstock_edit.text().strip(), self.trade_quantity_edit.text().strip(),
                   self.buy_price_edit.text().strip(), self.sell_price_edit.text().strip()]):
            QMessageBox.warning(self, "Предупреждение", "Все поля должны быть заполнены")
            return
        
        self.accept()
        
    def get_product_string(self):
        """Получение строки товара из полей"""
        return f"{self.classname_edit.text().strip()},{self.coefficient_edit.text().strip()}," \
               f"{self.maxstock_edit.text().strip()},{self.trade_quantity_edit.text().strip()}," \
               f"{self.buy_price_edit.text().strip()},{self.sell_price_edit.text().strip()}"


class ProductEditDialog(QDialog):
    def __init__(self, parent, product_str):
        super().__init__(parent)
        self.product_str = product_str
        self.setWindowTitle("✏️ Редактирование товара")
        self.setModal(True)
        self.resize(550, 480)
        self.setMinimumSize(500, 450)
        
        # Установка иконки окна
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                pixmap = QPixmap(32, 32)
                pixmap.fill(QColor(52, 152, 219))
                self.setWindowIcon(QIcon(pixmap))
        except Exception as e:
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(52, 152, 219))
            self.setWindowIcon(QIcon(pixmap))
        
        self.setup_ui()
        self.load_product_data()
        
    def setup_ui(self):
        """Настройка интерфейса диалога редактирования"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Заголовок
        title_label = QLabel("✏️ Редактирование товара")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Форма
        form_layout = QFormLayout()
        form_layout.setSpacing(18)
        form_layout.setVerticalSpacing(15)
        
        # Стиль для полей ввода
        input_style = """
            QLineEdit {
                font-size: 14px;
                padding: 12px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                min-height: 20px;
                max-height: 40px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        
        # Стиль для меток
        label_style = """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                padding: 5px;
            }
        """
        
        self.classname_edit = QLineEdit()
        self.classname_edit.setStyleSheet(input_style)
        label1 = QLabel("🔹 Класснейм:")
        label1.setStyleSheet(label_style)
        form_layout.addRow(label1, self.classname_edit)
        
        self.coefficient_edit = QLineEdit()
        self.coefficient_edit.setStyleSheet(input_style)
        label2 = QLabel("⚙️ Коэффициент:")
        label2.setStyleSheet(label_style)
        form_layout.addRow(label2, self.coefficient_edit)
        
        self.maxstock_edit = QLineEdit()
        self.maxstock_edit.setStyleSheet(input_style)
        label3 = QLabel("📦 Макс. запас:")
        label3.setStyleSheet(label_style)
        form_layout.addRow(label3, self.maxstock_edit)
        
        self.trade_quantity_edit = QLineEdit()
        self.trade_quantity_edit.setStyleSheet(input_style)
        label4 = QLabel("🔢 Кол-во для торговли:")
        label4.setStyleSheet(label_style)
        form_layout.addRow(label4, self.trade_quantity_edit)
        
        self.buy_price_edit = QLineEdit()
        self.buy_price_edit.setStyleSheet(input_style)
        label5 = QLabel("💰 Цена покупки:")
        label5.setStyleSheet(label_style)
        form_layout.addRow(label5, self.buy_price_edit)
        
        self.sell_price_edit = QLineEdit()
        self.sell_price_edit.setStyleSheet(input_style)
        label6 = QLabel("💵 Цена продажи:")
        label6.setStyleSheet(label_style)
        form_layout.addRow(label6, self.sell_price_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                background-color: #27ae60;
                color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Закрыть")
        cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                background-color: #e74c3c;
                color: white;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def load_product_data(self):
        """Загрузка данных товара в поля"""
        parts = self.product_str.split(',')
        if len(parts) >= 6:
            self.classname_edit.setText(parts[0])
            self.coefficient_edit.setText(parts[1])
            self.maxstock_edit.setText(parts[2])
            self.trade_quantity_edit.setText(parts[3])
            self.buy_price_edit.setText(parts[4])
            self.sell_price_edit.setText(parts[5])
            
    def get_product_string(self):
        """Получение строки товара из полей"""
        return f"{self.classname_edit.text()},{self.coefficient_edit.text()}," \
               f"{self.maxstock_edit.text()},{self.trade_quantity_edit.text()}," \
               f"{self.buy_price_edit.text()},{self.sell_price_edit.text()}"


class TraderEditDialog(QDialog):
    def __init__(self, parent, trader_data):
        super().__init__(parent)
        self.trader_data = trader_data.copy()
        self.setWindowTitle("Редактирование торговца")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.load_trader_data()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        # Поля торговца
        self.id_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.given_name_edit = QLineEdit()
        self.role_edit = QLineEdit()
        self.position_edit = QLineEdit()
        self.orientation_edit = QLineEdit()
        
        form_layout.addRow("ID:", self.id_edit)
        form_layout.addRow("Класснейм объекта:", self.name_edit)
        form_layout.addRow("Отображаемое имя:", self.given_name_edit)
        form_layout.addRow("Роль:", self.role_edit)
        form_layout.addRow("Позиция (X Y Z):", self.position_edit)
        form_layout.addRow("Ориентация (X Y Z):", self.orientation_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def load_trader_data(self):
        """Загрузка данных торговца в форму"""
        self.id_edit.setText(str(self.trader_data.get('Id', '')))
        self.name_edit.setText(self.trader_data.get('Name', ''))
        self.given_name_edit.setText(self.trader_data.get('GivenName', ''))
        self.role_edit.setText(self.trader_data.get('Role', ''))
        
        # Позиция
        position = self.trader_data.get('Position', [0, 0, 0])
        if len(position) >= 3:
            position_str = f"{position[0]} {position[1]} {position[2]}"
            self.position_edit.setText(position_str)
        
        # Ориентация
        orientation = self.trader_data.get('Orientation', [0, 0, 0])
        if len(orientation) >= 3:
            orientation_str = f"{orientation[0]} {orientation[1]} {orientation[2]}"
            self.orientation_edit.setText(orientation_str)
            
    def get_trader_data(self):
        """Получение данных торговца из формы"""
        updated_trader = self.trader_data.copy()
        
        try:
            updated_trader['Id'] = int(self.id_edit.text())
        except ValueError:
            updated_trader['Id'] = 0
            
        updated_trader['Name'] = self.name_edit.text()
        updated_trader['GivenName'] = self.given_name_edit.text()
        updated_trader['Role'] = self.role_edit.text()
        
        # Позиция
        try:
            position_parts = self.position_edit.text().split()
            if len(position_parts) >= 3:
                x = float(position_parts[0])
                y = float(position_parts[1])
                z = float(position_parts[2])
                updated_trader['Position'] = [x, y, z]
            else:
                updated_trader['Position'] = [0, 0, 0]
        except ValueError:
            updated_trader['Position'] = [0, 0, 0]
        
        # Ориентация
        try:
            orientation_parts = self.orientation_edit.text().split()
            if len(orientation_parts) >= 3:
                x = float(orientation_parts[0])
                y = float(orientation_parts[1])
                z = float(orientation_parts[2])
                updated_trader['Orientation'] = [x, y, z]
            else:
                updated_trader['Orientation'] = [0, 0, 0]
        except ValueError:
            updated_trader['Orientation'] = [0, 0, 0]
            
        return updated_trader


class TraderIDEditDialog(QDialog):
    def __init__(self, parent, trader_id_data):
        super().__init__(parent)
        self.trader_id_data = trader_id_data.copy()
        self.setWindowTitle("Редактирование ID торговца")
        self.setModal(True)
        self.resize(600, 500)
        self.setup_ui()
        self.load_trader_id_data()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        # Поля ID торговца
        self.id_edit = QLineEdit()
        self.categories_edit = QTextEdit()
        self.categories_edit.setMaximumHeight(200)
        
        form_layout.addRow("ID:", self.id_edit)
        form_layout.addRow("Категории (по одной на строку):", self.categories_edit)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def load_trader_id_data(self):
        """Загрузка данных ID торговца в форму"""
        self.id_edit.setText(str(self.trader_id_data.get('Id', '')))
        
        # Категории
        categories = self.trader_id_data.get('Categories', [])
        categories_text = '\n'.join(categories)
        self.categories_edit.setPlainText(categories_text)
        
    def get_trader_id_data(self):
        """Получение данных ID торговца из формы"""
        updated_trader_id = self.trader_id_data.copy()
        
        try:
            updated_trader_id['Id'] = int(self.id_edit.text())
        except ValueError:
            updated_trader_id['Id'] = 0
            
        # Категории
        categories_text = self.categories_edit.toPlainText()
        categories = [cat.strip() for cat in categories_text.split('\n') if cat.strip()]
        updated_trader_id['Categories'] = categories
        
        return updated_trader_id


def main():
    app = QApplication(sys.argv)
    
    # Настройка стиля приложения
    app.setStyle('Fusion')
    
    # Увеличиваем базовый шрифт приложения
    font = QFont()
    font.setPointSize(11)  # Базовый размер шрифта
    app.setFont(font)
    
    # Создание и отображение главного окна
    window = TraderPlusEditor()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()