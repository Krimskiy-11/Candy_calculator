from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QStackedWidget, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QAbstractItemView, QFrame,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor


PREMIUM_THEME_QSS = """
/* Базовые параметры */
QMainWindow, QWidget {
    background-color: #0d0f14;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", Roboto, sans-serif;
    font-size: 13px;
}

/* Сайдбар */
#sidebar {
    background-color: #12151c;
    border-right: 1px solid #1e2330;
    min-width: 230px;
    max-width: 230px;
}

#brandBadge {
    background-color: #f59e0b;
    color: #0f1115;
    font-weight: 800;
    font-size: 10px;
    letter-spacing: 0.5px;
    padding: 3px 8px;
    border-radius: 4px;
}

#brandTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
    background: transparent;
}

#brandSubtitle {
    color: #64748b;
    font-size: 11px;
    background: transparent;
}

/* Кнопки навигации сайдбара */
QPushButton.nav-btn {
    background-color: transparent;
    color: #94a3b8;
    text-align: left;
    padding: 12px 16px;
    border: none;
    border-radius: 8px;
    margin: 3px 12px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton.nav-btn:hover {
    background-color: #1a1f2c;
    color: #ffffff;
}
QPushButton.nav-btn:checked {
    background-color: #1e2638;
    color: #60a5fa;
    border-left: 3px solid #3b82f6;
    font-weight: 600;
}

/* Карточка торта */
QFrame.cake-card {
    background-color: #151822;
    border: 1px solid #232838;
    border-radius: 10px;
    padding: 14px 18px;
}
QFrame.cake-card:hover {
    background-color: #1a1f2c;
    border-color: #3b82f6;
}

/* Детальная панель справа */
#detailPanel {
    background-color: #12151c;
    border: 1px solid #1e2330;
    border-radius: 12px;
    padding: 20px;
}

/* Таблицы */
QTableWidget {
    background-color: #12151c;
    border: 1px solid #1e2330;
    border-radius: 10px;
    color: #e2e8f0;
    gridline-color: #1c212e;
    outline: none;
}
QHeaderView::section {
    background-color: #0d0f14;
    color: #94a3b8;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #1e2330;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
}
QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #171b26;
}
QTableWidget::item:selected {
    background-color: #1e293b;
    color: #93c5fd;
}

/* Кнопки */
QPushButton.btn-primary {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 600;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}
QPushButton.btn-primary:hover {
    background-color: #3b82f6;
}

QPushButton.btn-success {
    background-color: #059669;
    color: #ffffff;
    font-weight: 600;
    border-radius: 6px;
    padding: 8px 16px;
    border: none;
}
QPushButton.btn-success:hover {
    background-color: #10b981;
}

QPushButton.btn-danger {
    background-color: transparent;
    color: #ef4444;
    font-weight: 600;
    border: 1px solid #3d1c21;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton.btn-danger:hover {
    background-color: #3d1c21;
}

QPushButton.btn-secondary {
    background-color: #1e2330;
    color: #cbd5e1;
    border-radius: 6px;
    padding: 8px 14px;
    border: 1px solid #2d3548;
}
QPushButton.btn-secondary:hover {
    background-color: #262d3e;
    color: #ffffff;
}

/* Скролл */
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #0d0f14;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #232838;
    border-radius: 3px;
}
"""


class CakeCardWidget(QFrame):
    """Премиальная интерактивная карточка торта."""
    clicked = Signal(dict)
    calc_requested = Signal(dict)
    delete_requested = Signal(dict)

    def __init__(self, cake_data: dict, parent=None):
        super().__init__(parent)
        self.cake_data = cake_data
        self.setProperty("class", "cake-card")
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        # Иконка
        lbl_icon = QLabel("🎂")
        lbl_icon.setStyleSheet("font-size: 26px; background: transparent;")

        # Инфо о торте
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        lbl_name = QLabel(cake_data.get('name', 'Без названия'))
        lbl_name.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff; background: transparent;")

        dia = cake_data.get('base_diameter', 18)
        ingr_count = len(cake_data.get('cake_ingredients', []))
        lbl_meta = QLabel(f"Базовый диаметр: <b style='color:#60a5fa;'>{dia} см</b>  •  Ингредиентов: <b style='color:#94a3b8;'>{ingr_count}</b>")
        lbl_meta.setStyleSheet("color: #64748b; font-size: 12px; background: transparent;")

        info_layout.addWidget(lbl_name)
        info_layout.addWidget(lbl_meta)

        # Кнопки быстрых действий прямо в карточке
        btn_calc = QPushButton("Рассчитать себестоимость ➔")
        btn_calc.setProperty("class", "btn-primary")
        btn_calc.clicked.connect(lambda: self.calc_requested.emit(self.cake_data))

        btn_del = QPushButton("✕")
        btn_del.setToolTip("Удалить торт")
        btn_del.setProperty("class", "btn-danger")
        btn_del.setFixedSize(32, 32)
        btn_del.clicked.connect(lambda: self.delete_requested.emit(self.cake_data))

        layout.addWidget(lbl_icon)
        layout.addLayout(info_layout, stretch=1)
        layout.addWidget(btn_calc)
        layout.addWidget(btn_del)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self.cake_data)


class MainWindow(QMainWindow):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.setWindowTitle("CakeStudio OS — Калькулятор кондитерской себестоимости")
        self.resize(1150, 720)
        self.setStyleSheet(PREMIUM_THEME_QSS)

        self.stack = QStackedWidget()
        self.screen_cakes = self._build_cakes_screen()
        self.screen_ingredients = self._build_ingredients_screen()

        self.stack.addWidget(self.screen_cakes)
        self.stack.addWidget(self.screen_ingredients)

        sidebar = self._build_sidebar()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, stretch=1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.refresh_cakes()

    def _build_sidebar(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("sidebar")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 24, 0, 20)
        layout.setSpacing(4)

        # Логотип и брендинг
        brand_box = QVBoxLayout()
        brand_box.setContentsMargins(20, 0, 20, 24)
        brand_box.setSpacing(6)

        badge_container = QHBoxLayout()
        lbl_badge = QLabel("PRO CALCULATOR")
        lbl_badge.setObjectName("brandBadge")
        badge_container.addWidget(lbl_badge)
        badge_container.addStretch()

        lbl_title = QLabel("CakeStudio")
        lbl_title.setObjectName("brandTitle")

        lbl_sub = QLabel("Управление себестоимостью")
        lbl_sub.setObjectName("brandSubtitle")

        brand_box.addLayout(badge_container)
        brand_box.addWidget(lbl_title)
        brand_box.addWidget(lbl_sub)
        layout.addLayout(brand_box)

        # Навигация
        self.btn_nav_cakes = QPushButton("  🍰  Рецепты и торты")
        self.btn_nav_cakes.setProperty("class", "nav-btn")
        self.btn_nav_cakes.setCheckable(True)
        self.btn_nav_cakes.setChecked(True)

        self.btn_nav_create = QPushButton("  ➕  Новый рецепт")
        self.btn_nav_create.setProperty("class", "nav-btn")

        self.btn_nav_ingredients = QPushButton("  📦  Склад ингредиентов")
        self.btn_nav_ingredients.setProperty("class", "nav-btn")
        self.btn_nav_ingredients.setCheckable(True)

        self.btn_nav_cakes.clicked.connect(self._go_to_cakes)
        self.btn_nav_create.clicked.connect(self.create_cake)
        self.btn_nav_ingredients.clicked.connect(self._go_to_ingredients)

        layout.addWidget(self.btn_nav_cakes)
        layout.addWidget(self.btn_nav_create)
        layout.addWidget(self.btn_nav_ingredients)
        layout.addStretch()

        lbl_version = QLabel("v2.5 • Локальный сервер")
        lbl_version.setStyleSheet("color: #475569; font-size: 11px; padding: 0 20px; background: transparent;")
        layout.addWidget(lbl_version)

        return panel

    def _go_to_cakes(self):
        self.btn_nav_cakes.setChecked(True)
        self.btn_nav_ingredients.setChecked(False)
        self.stack.setCurrentIndex(0)
        self.refresh_cakes()

    def _go_to_ingredients(self):
        self.btn_nav_cakes.setChecked(False)
        self.btn_nav_ingredients.setChecked(True)
        self.stack.setCurrentIndex(1)
        self.refresh_ingredients()

    # ================== ЭКРАН 1: ТОРТЫ ==================
    def _build_cakes_screen(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        # Шапка секции
        header_box = QHBoxLayout()
        v_title = QVBoxLayout()
        title = QLabel("Каталог рецептов")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #ffffff;")
        subtitle = QLabel("Выберите торт для пересчёта по диаметру и детального расчёта")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 13px;")
        v_title.addWidget(title)
        v_title.addWidget(subtitle)

        btn_refresh = QPushButton("Обновить")
        btn_refresh.setProperty("class", "btn-secondary")
        btn_refresh.clicked.connect(self.refresh_cakes)

        btn_create = QPushButton("+ Новый рецепт")
        btn_create.setProperty("class", "btn-success")
        btn_create.clicked.connect(self.create_cake)

        header_box.addLayout(v_title)
        header_box.addStretch()
        header_box.addWidget(btn_refresh)
        header_box.addWidget(btn_create)

        # Скролл-контейнер для карточек
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignTop)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.cards_container)

        layout.addLayout(header_box)
        layout.addWidget(scroll, stretch=1)
        return widget

    def refresh_cakes(self):
        # Очищаем старые карточки
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        try:
            cakes = self.api.list_cakes()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка связи", f"Сервер недоступен: {e}")
            return

        if not cakes:
            empty_lbl = QLabel("В базе пока нет рецептов. Нажмите «+ Новый рецепт», чтобы добавить первый торт!")
            empty_lbl.setStyleSheet("color: #64748b; font-size: 14px; padding: 40px 0;")
            empty_lbl.setAlignment(Qt.AlignCenter)
            self.cards_layout.addWidget(empty_lbl)
            return

        for cake in cakes:
            card = CakeCardWidget(cake, self.cards_container)
            card.calc_requested.connect(self.open_cake_calc)
            card.delete_requested.connect(self.delete_cake)
            self.cards_layout.addWidget(card)

    def create_cake(self):
        from .cake_dialog import CakeDialog
        dialog = CakeDialog(self.api, self)
        if dialog.exec():
            self._go_to_cakes()

    def open_cake_calc(self, cake_data: dict):
        cake_id = cake_data['id']
        cake_name = cake_data['name']
        base_dia = cake_data.get('base_diameter', 18)

        from .calc_window import CalcWindow
        self.calc_win = CalcWindow(self.api, cake_id, cake_name, base_diameter=base_dia)
        self.calc_win.show()

    def delete_cake(self, cake_data: dict):
        cake_name = cake_data['name']
        cake_id = cake_data['id']

        answer = QMessageBox.question(
            self, "Удаление рецепта",
            f"Удалить торт «{cake_name}» безвозвратно?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if answer == QMessageBox.Yes:
            self.api.delete_cake(cake_id)
            self.refresh_cakes()

    # ================== ЭКРАН 2: ИНГРЕДИЕНТЫ ==================
    def _build_ingredients_screen(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        header_box = QHBoxLayout()
        v_title = QVBoxLayout()
        title = QLabel("Склад сырья и ингредиентов")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #ffffff;")
        subtitle = QLabel("Цены закупки упаковок и актуальная себестоимость за 1 г / 1 мл / 1 шт")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 13px;")
        v_title.addWidget(title)
        v_title.addWidget(subtitle)

        btn_add = QPushButton("+ Добавить продукт")
        btn_add.setProperty("class", "btn-success")
        btn_add.clicked.connect(self.add_ingredient)

        header_box.addLayout(v_title)
        header_box.addStretch()
        header_box.addWidget(btn_add)

        self.ingr_table = QTableWidget(0, 5)
        self.ingr_table.setHorizontalHeaderLabels([
            "ID", "Наименование продукта", "Цена закупки", "Фасовка упаковки", "Себестоимость за ед."
        ])
        self.ingr_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ingr_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ingr_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ingr_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ingr_table.cellDoubleClicked.connect(lambda row, col: self.edit_ingredient())

        # Нижняя панель склада
        actions = QHBoxLayout()
        btn_edit = QPushButton("Редактировать цену/фасовку")
        btn_edit.setProperty("class", "btn-primary")
        btn_edit.clicked.connect(self.edit_ingredient)

        btn_del = QPushButton("Удалить")
        btn_del.setProperty("class", "btn-danger")
        btn_del.clicked.connect(self.delete_ingredient)

        btn_refresh = QPushButton("Обновить")
        btn_refresh.setProperty("class", "btn-secondary")
        btn_refresh.clicked.connect(self.refresh_ingredients)

        actions.addWidget(btn_edit)
        actions.addWidget(btn_del)
        actions.addStretch()
        actions.addWidget(btn_refresh)

        layout.addLayout(header_box)
        layout.addWidget(self.ingr_table)
        layout.addLayout(actions)
        return widget

    def refresh_ingredients(self):
        try:
            items = self.api.list_ingredients()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")
            return

        self.ingr_cache = {i['id']: i for i in items}
        self.ingr_table.setRowCount(len(items))
        unit_map = {'g': 'г', 'ml': 'мл', 'pcs': 'шт'}

        for row, it in enumerate(items):
            unit = unit_map.get(it.get('unit'), it.get('unit', ''))
            cost = it.get('cost_per_unit', '—')

            id_item = QTableWidgetItem(f"#{it['id']}")
            id_item.setData(Qt.UserRole, it['id'])
            id_item.setForeground(QColor('#64748b'))

            name_item = QTableWidgetItem(it['name'])
            name_item.setFont(QFont("", 10, QFont.Bold))

            price_item = QTableWidgetItem(f"{it['package_price']} ₽")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            qty_item = QTableWidgetItem(f"{it['package_quantity']} {unit}")
            qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            cost_item = QTableWidgetItem(f"{cost} ₽ / {unit}")
            cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            cost_item.setForeground(QColor('#34d399'))

            self.ingr_table.setItem(row, 0, id_item)
            self.ingr_table.setItem(row, 1, name_item)
            self.ingr_table.setItem(row, 2, price_item)
            self.ingr_table.setItem(row, 3, qty_item)
            self.ingr_table.setItem(row, 4, cost_item)

    def add_ingredient(self):
        from .ingredient_dialog import IngredientDialog
        dialog = IngredientDialog(self.api, parent=self)
        if dialog.exec():
            self.refresh_ingredients()

    def edit_ingredient(self):
        selected = self.ingr_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите ингредиент для редактирования.")
            return

        row = selected[0].row()
        item_id = self.ingr_table.item(row, 0).data(Qt.UserRole)
        ingr_data = self.ingr_cache.get(item_id)

        from .ingredient_dialog import IngredientDialog
        dialog = IngredientDialog(self.api, ingredient_data=ingr_data, parent=self)
        if dialog.exec():
            self.refresh_ingredients()

    def delete_ingredient(self):
        selected = self.ingr_table.selectionModel().selectedRows()
        if not selected:
            return

        row = selected[0].row()
        item_id = self.ingr_table.item(row, 0).data(Qt.UserRole)
        ingr_data = self.ingr_cache.get(item_id)

        confirm = QMessageBox.question(
            self, "Удаление",
            f"Удалить ингредиент «{ingr_data['name']}»?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.api.delete_ingredient(item_id)
            self.refresh_ingredients()
