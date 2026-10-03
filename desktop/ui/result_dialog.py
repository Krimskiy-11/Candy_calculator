from decimal import Decimal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QTabWidget, QPushButton, QHeaderView, QFrame,
    QGridLayout, QWidget, QMessageBox
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt


class ResultDialog(QDialog):
    def __init__(self, cake_name: str, calc_data: dict, parent=None):
        super().__init__(parent)
        self.cake_name = cake_name
        self.calc_data = calc_data

        # Базовые финансовые показатели торта (из ответа DRF)
        self.cake_sale_price = Decimal(str(calc_data.get('cake_sale_price', '0.00')))
        self.ingredients_total = Decimal(str(calc_data.get('ingredients_total', '0.00')))

        self.setWindowTitle(f'Калькуляция: {cake_name}')
        self.resize(780, 640)

        # Флаг для предотвращения рекурсии при авто-пересчете ячеек таблицы
        self._is_updating_table = False

        # 1. Шапка: параметры торта
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #26292e;
                border: 1px solid #383c44;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #e0e4eb;
                font-size: 13px;
            }
        """)
        h_layout = QGridLayout(header)
        h_layout.addWidget(QLabel(f"<b>Торт:</b> <span style='color: #64b5f6;'>{cake_name}</span>"), 0, 0)
        h_layout.addWidget(QLabel(f"<b>Диаметр:</b> {calc_data.get('target_diameter')} см (коэфф. <b>×{calc_data.get('scale_factor')}</b>)"), 0, 1)
        h_layout.addWidget(QLabel(f"<b>Вес изделия (с упёком):</b> <span style='color: #81c784;'>{calc_data.get('net_weight_kg')} кг</span>"), 1, 0)
        h_layout.addWidget(QLabel(f"<b>Себестоимость сырья / кг:</b> {calc_data.get('cost_per_kg')} ₽"), 1, 1)

        # 2. Вкладки
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #383c44;
                background-color: #1e2024;
            }
            QTabBar::tab {
                background-color: #2b2e35;
                color: #b0b6c2;
                padding: 8px 16px;
                border: 1px solid #383c44;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1e2024;
                color: #ffffff;
                font-weight: bold;
            }
        """)

        # Таблица ингредиентов
        table_ingr = self._create_ingredients_table()
        self.tabs.addTab(table_ingr, 'Ингредиенты по слоям')

        # Вкладка декора и упаковки
        decor_tab = self._create_decor_tab()
        self.tabs.addTab(decor_tab, 'Декор и упаковка')

        # 3. Финансовая сводка
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame {
                background-color: #172a1e;
                border: 1px solid #2e7d32;
                border-radius: 8px;
                padding: 12px;
            }
            QLabel {
                color: #c8e6c9;
                font-size: 13px;
            }
        """)
        s_layout = QGridLayout(self.summary_frame)

        self.lbl_ingr_total = QLabel(f"Себестоимость сырья: <b>{self.ingredients_total} ₽</b>")
        self.lbl_pack_total = QLabel("Упаковка и декор: <b>0.00 ₽</b>")
        self.lbl_price_kg = QLabel(f"Цена за 1 кг с работой: <b>{calc_data.get('price_per_kg')} ₽/кг</b>")
        self.lbl_profit = QLabel("Чистая прибыль: <b>+0.00 ₽</b>")
        self.lbl_profit.setStyleSheet("color: #81c784; font-size: 14px; font-weight: bold;")

        self.lbl_grand_total = QLabel("ИТОГО КЛИЕНТУ: 0.00 ₽")
        self.lbl_grand_total.setStyleSheet("color: #a5d6a7; font-size: 18px; font-weight: bold; margin-top: 6px;")

        s_layout.addWidget(self.lbl_ingr_total, 0, 0)
        s_layout.addWidget(self.lbl_pack_total, 0, 1)
        s_layout.addWidget(self.lbl_price_kg, 1, 0)
        s_layout.addWidget(self.lbl_profit, 1, 1)
        s_layout.addWidget(self.lbl_grand_total, 2, 0, 1, 2, alignment=Qt.AlignCenter)

        # Кнопка закрыть
        btn_close = QPushButton('Закрыть')
        btn_close.setFixedWidth(110)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #374151;
                color: #ffffff;
                font-weight: bold;
                border-radius: 4px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        btn_close.clicked.connect(self.accept)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_close)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(header)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.summary_frame)
        main_layout.addLayout(bottom)

        # Выполняем первичный расчет сумм
        self.recalculate_totals()

    def _create_ingredients_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setStyleSheet("""
            QTableWidget {
                background-color: #1e2024;
                color: #e0e4eb;
                gridline-color: #2c3038;
                border: none;
            }
            QHeaderView::section {
                background-color: #26292e;
                color: #9aa0ac;
                padding: 6px;
                border: 1px solid #333842;
                font-weight: bold;
            }
        """)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Слой / Продукт', 'Кол-во', 'Ед.', 'Сумма'])

        layers = self.calc_data.get('ingredients_by_layer', {})
        total_rows = sum(len(items) for items in layers.values()) + len(layers)
        table.setRowCount(total_rows)

        row_idx = 0
        for layer_name, items in layers.items():
            layer_header = QTableWidgetItem(f"▸ {layer_name.upper()}")
            layer_header.setBackground(QColor('#2d3748'))
            layer_header.setForeground(QColor('#90caf9'))
            font = QFont()
            font.setBold(True)
            layer_header.setFont(font)
            table.setItem(row_idx, 0, layer_header)

            for col in range(1, 4):
                empty = QTableWidgetItem("")
                empty.setBackground(QColor('#2d3748'))
                table.setItem(row_idx, col, empty)
            row_idx += 1

            for it in items:
                name_item = QTableWidgetItem(f"    {it['name']}")
                name_item.setForeground(QColor('#e0e4eb'))
                table.setItem(row_idx, 0, name_item)

                qty_item = QTableWidgetItem(str(it['quantity']))
                qty_item.setForeground(QColor('#b0b6c2'))
                table.setItem(row_idx, 1, qty_item)

                unit_item = QTableWidgetItem(str(it['unit']))
                unit_item.setForeground(QColor('#b0b6c2'))
                table.setItem(row_idx, 2, unit_item)

                cost_item = QTableWidgetItem(f"{it['cost']} ₽")
                cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                cost_item.setForeground(QColor('#ffffff'))
                table.setItem(row_idx, 3, cost_item)
                row_idx += 1

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        return table

    def _create_decor_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        # Панель кнопок добавления/удаления
        btn_bar = QHBoxLayout()
        btn_add = QPushButton('+ Добавить декор / расходник')
        btn_add.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 6px 12px;")
        btn_add.clicked.connect(self.add_decor_row)

        btn_remove = QPushButton('✕ Удалить позицию')
        btn_remove.setStyleSheet("color: #ef5350; font-weight: bold; padding: 6px 12px;")
        btn_remove.clicked.connect(self.remove_decor_row)

        lbl_hint = QLabel('<i>(кликните дважды по ячейке для изменения названия или цены)</i>')
        lbl_hint.setStyleSheet("color: #9aa0ac; font-size: 11px;")

        btn_bar.addWidget(btn_add)
        btn_bar.addWidget(btn_remove)
        btn_bar.addSpacing(10)
        btn_bar.addWidget(lbl_hint)
        btn_bar.addStretch()

        # Таблица декора
        self.table_decor = QTableWidget(0, 4)
        self.table_decor.setStyleSheet("""
            QTableWidget {
                background-color: #1e2024;
                color: #e0e4eb;
                gridline-color: #2c3038;
                border: none;
            }
            QHeaderView::section {
                background-color: #26292e;
                color: #9aa0ac;
                padding: 6px;
                border: 1px solid #333842;
                font-weight: bold;
            }
        """)
        self.table_decor.setHorizontalHeaderLabels(['Наименование декора / упаковки', 'Кол-во', 'Цена за шт. (₽)', 'Итого (₽)'])
        self.table_decor.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_decor.cellChanged.connect(self.on_decor_cell_changed)

        layout.addLayout(btn_bar)
        layout.addWidget(self.table_decor)

        # Подгружаем декор, если он уже был в рецепте
        preset_decor = self.calc_data.get('packaging', [])
        for p in preset_decor:
            self._insert_decor_row(p.get('name', ''), p.get('quantity', 1.0), p.get('price', 0.0))

        return container

    def _insert_decor_row(self, name: str, qty: float, price: float):
        self._is_updating_table = True
        row = self.table_decor.rowCount()
        self.table_decor.insertRow(row)

        item_name = QTableWidgetItem(str(name))
        item_qty = QTableWidgetItem(str(qty))
        item_price = QTableWidgetItem(str(price))

        total = round(float(qty) * float(price), 2)
        item_total = QTableWidgetItem(f"{total:.2f}")
        # Итоговая ячейка только для чтения
        item_total.setFlags(item_total.flags() & ~Qt.ItemIsEditable)
        item_total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item_total.setForeground(QColor('#ffffff'))

        self.table_decor.setItem(row, 0, item_name)
        self.table_decor.setItem(row, 1, item_qty)
        self.table_decor.setItem(row, 2, item_price)
        self.table_decor.setItem(row, 3, item_total)
        self._is_updating_table = False

    def add_decor_row(self):
        # Добавляем стандартную заготовку (например, коробка или ягоды)
        self._insert_decor_row('Коробка / Подложка / Топпер', 1.0, 150.0)
        self.recalculate_totals()
        # Автоматически переходим в режим редактирования названия добавленной строки
        last_row = self.table_decor.rowCount() - 1
        self.table_decor.setCurrentCell(last_row, 0)
        self.table_decor.editItem(self.table_decor.item(last_row, 0))

    def remove_decor_row(self):
        current_row = self.table_decor.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите строку декора для удаления.')
            return
        self.table_decor.removeRow(current_row)
        self.recalculate_totals()

    def on_decor_cell_changed(self, row: int, col: int):
        if self._is_updating_table or col == 3:
            return

        # Если изменилось кол-во (col 1) или цена (col 2), пересчитываем столбец «Итого»
        qty_item = self.table_decor.item(row, 1)
        price_item = self.table_decor.item(row, 2)

        try:
            qty = float(qty_item.text().replace(',', '.')) if qty_item else 1.0
        except ValueError:
            qty = 1.0

        try:
            price = float(price_item.text().replace(',', '.')) if price_item else 0.0
        except ValueError:
            price = 0.0

        row_total = round(qty * price, 2)

        self._is_updating_table = True
        total_item = self.table_decor.item(row, 3)
        if not total_item:
            total_item = QTableWidgetItem()
            total_item.setFlags(total_item.flags() & ~Qt.ItemIsEditable)
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table_decor.setItem(row, 3, total_item)
        total_item.setText(f"{row_total:.2f}")
        self._is_updating_table = False

        self.recalculate_totals()

    def recalculate_totals(self):
        """Пересчитывает финансовый итог на основе введенного декора."""
        total_decor = Decimal('0.00')

        for r in range(self.table_decor.rowCount()):
            tot_item = self.table_decor.item(r, 3)
            if tot_item:
                try:
                    val = Decimal(str(tot_item.text()).replace(' ₽', '').strip())
                    total_decor += val
                except Exception:
                    pass

        # Итоговая цена для клиента = цена торта (с работой) + декор и упаковка
        final_client_price = self.cake_sale_price + total_decor
        # Прибыль = Выручка - сырьё - декор/упаковка
        net_profit = final_client_price - self.ingredients_total - total_decor

        # Обновляем надписи
        self.lbl_pack_total.setText(f"Упаковка и декор: <b>{total_decor:.2f} ₽</b>")
        self.lbl_grand_total.setText(f"ИТОГО КЛИЕНТУ: {final_client_price:.2f} ₽")
        self.lbl_profit.setText(f"Чистая прибыль: <b>+{net_profit:.2f} ₽</b>")

        # Обновляем счетчик на вкладке
        count = self.table_decor.rowCount()
        self.tabs.setTabText(1, f"Декор и упаковка ({count})")
