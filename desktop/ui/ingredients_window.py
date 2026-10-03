from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt


class IngredientsWindow(QWidget):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle('Справочник ингредиентов')
        self.resize(750, 480)

        # Хранилище объектов для быстрого доступа при редактировании
        self.ingredients_cache = {}

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Название', 'Цена закупки', 'Фасовка', 'Себестоимость за ед.'
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # Открытие редактирования по двойному клику на строку
        self.table.cellDoubleClicked.connect(lambda row, col: self.edit_ingredient())

        # Кнопки панели управления
        btn_add = QPushButton('+ Добавить')
        btn_add.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 5px 12px;")
        btn_add.clicked.connect(self.add_ingredient)

        btn_edit = QPushButton('Редактировать')
        btn_edit.clicked.connect(self.edit_ingredient)

        btn_delete = QPushButton('Удалить')
        btn_delete.setStyleSheet("color: #ff5252; font-weight: bold;")
        btn_delete.clicked.connect(self.delete_ingredient)

        btn_refresh = QPushButton('Обновить')
        btn_refresh.clicked.connect(self.load_data)

        actions = QHBoxLayout()
        actions.addWidget(btn_add)
        actions.addWidget(btn_edit)
        actions.addWidget(btn_delete)
        actions.addSpacing(15)
        actions.addWidget(btn_refresh)
        actions.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(actions)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        try:
            ingredients = self.api.list_ingredients()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось загрузить данные: {e}')
            return

        self.ingredients_cache = {item['id']: item for item in ingredients}
        self.table.setRowCount(len(ingredients))
        unit_labels = {'g': 'г', 'ml': 'мл', 'pcs': 'шт'}

        for i, item in enumerate(ingredients):
            unit = unit_labels.get(item.get('unit'), item.get('unit', ''))
            cost = item.get('cost_per_unit', '—')

            id_item = QTableWidgetItem(str(item['id']))
            id_item.setData(Qt.UserRole, item['id'])

            self.table.setItem(i, 0, id_item)
            self.table.setItem(i, 1, QTableWidgetItem(item['name']))
            self.table.setItem(i, 2, QTableWidgetItem(f"{item['package_price']} ₽"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{item['package_quantity']} {unit}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{cost} ₽ / {unit}"))

    def _get_selected_ingredient(self) -> dict | None:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, 'Внимание', 'Сначала выберите ингредиент в таблице.')
            return None
        row = selected_rows[0].row()
        item_id = self.table.item(row, 0).data(Qt.UserRole)
        return self.ingredients_cache.get(item_id)

    def add_ingredient(self):
        from .ingredient_dialog import IngredientDialog
        dialog = IngredientDialog(self.api, parent=self)
        if dialog.exec():
            self.load_data()

    def edit_ingredient(self):
        ingredient = self._get_selected_ingredient()
        if not ingredient:
            return

        from .ingredient_dialog import IngredientDialog
        dialog = IngredientDialog(self.api, ingredient_data=ingredient, parent=self)
        if dialog.exec():
            self.load_data()

    def delete_ingredient(self):
        ingredient = self._get_selected_ingredient()
        if not ingredient:
            return

        confirm = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f"Вы уверены, что хотите удалить ингредиент «{ingredient['name']}»?\n"
            f"Если он используется в рецептах тортов, его удаление может повлиять на расчёты.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                self.api.delete_ingredient(ingredient['id'])
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка удаления', f'Не удалось удалить ингредиент: {e}')
