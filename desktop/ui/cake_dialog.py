from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QTextEdit, QPushButton, QComboBox, QDoubleSpinBox,
    QLabel, QScrollArea, QWidget, QMessageBox, QFrame
)
from PySide6.QtCore import Qt


DIALOG_THEME = """
QDialog {
    background-color: #0f1115;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

QLabel {
    color: #94a3b8;
    font-size: 13px;
    font-weight: 500;
}

QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #171a22;
    border: 1px solid #272d3b;
    border-radius: 8px;
    padding: 8px 12px;
    color: #ffffff;
    font-size: 13px;
    selection-background-color: #3b82f6;
}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #3b82f6;
    background-color: #1a1e28;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: #171a22;
    color: #ffffff;
    border: 1px solid #272d3b;
    selection-background-color: #2563eb;
    outline: none;
}

QScrollArea {
    border: 1px solid #222733;
    border-radius: 8px;
    background-color: #12141a;
}

QPushButton.btn-save {
    background-color: #059669;
    color: #ffffff;
    font-weight: 600;
    border-radius: 8px;
    padding: 10px 20px;
    border: none;
}
QPushButton.btn-save:hover {
    background-color: #10b981;
}

QPushButton.btn-cancel {
    background-color: #1c202a;
    color: #94a3b8;
    border-radius: 8px;
    padding: 10px 18px;
    border: 1px solid #272d3b;
}
QPushButton.btn-cancel:hover {
    background-color: #252b38;
    color: #ffffff;
}

QPushButton.btn-add {
    background-color: #1e2638;
    color: #60a5fa;
    border: 1px dashed #3b82f6;
    border-radius: 8px;
    padding: 10px;
    font-weight: 600;
}
QPushButton.btn-add:hover {
    background-color: #243048;
}
"""


class IngredientRow(QFrame):
    """Строка ингредиента: Слой -> Продукт -> Граммовка -> Удалить."""
    COMPONENT_CHOICES = [
        ('biscuit', 'Бисквит'),
        ('cream', 'Крем / Прослойка'),
        ('filling', 'Начинка / Конфи'),
        ('soak', 'Пропитка'),
        ('coating', 'Выравнивание'),
        ('decor', 'Декор'),
    ]

    def __init__(self, available_ingredients: list, on_delete_callback, parent=None):
        super().__init__(parent)
        self.on_delete_callback = on_delete_callback
        self.setStyleSheet("""
            IngredientRow {
                background-color: #161922;
                border: 1px solid #232838;
                border-radius: 8px;
                padding: 4px;
            }
        """)

        # 1. Выбор слоя торта
        self.component_combo = QComboBox()
        self.component_combo.setFixedWidth(140)
        for code, label in self.COMPONENT_CHOICES:
            self.component_combo.addItem(label, userData=code)

        # 2. Выбор продукта
        self.ingredient_combo = QComboBox()
        for item in available_ingredients:
            unit = item.get('unit', '')
            self.ingredient_combo.addItem(f"{item['name']} ({unit})", userData=item['id'])

        # 3. Ввод количества
        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0.01, 99999.0)
        self.qty_input.setValue(100.0)
        self.qty_input.setDecimals(1)
        self.qty_input.setFixedWidth(110)

        # 4. Удаление
        self.btn_del = QPushButton('✕')
        self.btn_del.setFixedSize(30, 30)
        self.btn_del.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ef4444;
                border: 1px solid #3d1c21;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d1c21;
            }
        """)
        self.btn_del.clicked.connect(lambda: self.on_delete_callback(self))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        layout.addWidget(self.component_combo)
        layout.addWidget(self.ingredient_combo, stretch=1)
        layout.addWidget(self.qty_input)
        layout.addWidget(self.btn_del)

    def get_data(self) -> dict:
        return {
            'component': self.component_combo.currentData(),
            'ingredient_id': self.ingredient_combo.currentData(),
            'quantity': self.qty_input.value()
        }


class CakeDialog(QDialog):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle('Создание нового рецепта')
        self.resize(680, 680)
        self.setStyleSheet(DIALOG_THEME)

        try:
            self.available_ingredients = self.api.list_ingredients()
        except Exception:
            self.available_ingredients = []

        # Поля
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Например: Красный бархат с вишней')

        self.diameter_input = QSpinBox()
        self.diameter_input.setRange(8, 60)
        self.diameter_input.setValue(18)
        self.diameter_input.setSuffix(' см')
        self.diameter_input.setFixedWidth(120)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText('Опишите этапы приготовления (выпечка коржей, пропитка, сборка, охлаждение)...')
        self.desc_input.setMaximumHeight(90)

        # Контейнер ингредиентов со скроллом
        self.ingredients_rows = []
        self.ingredients_container = QWidget()
        self.ingredients_layout = QVBoxLayout(self.ingredients_container)
        self.ingredients_layout.setContentsMargins(8, 8, 8, 8)
        self.ingredients_layout.setSpacing(6)
        self.ingredients_layout.setAlignment(Qt.AlignTop)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.ingredients_container)

        self.btn_add = QPushButton('+ Добавить компонент в рецепт')
        self.btn_add.setProperty('class', 'btn-add')
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.clicked.connect(self.add_ingredient_row)

        # Нижняя панель
        btn_cancel = QPushButton('Отмена')
        btn_cancel.setProperty('class', 'btn-cancel')
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton('Сохранить торт')
        btn_save.setProperty('class', 'btn-save')
        btn_save.clicked.connect(self.save_cake)

        bottom = QHBoxLayout()
        bottom.addStretch()
        bottom.addWidget(btn_cancel)
        bottom.addWidget(btn_save)

        # Сборка формы
        form = QFormLayout()
        form.setSpacing(12)
        form.addRow('Название рецепта:*', self.name_input)
        form.addRow('Базовый диаметр:', self.diameter_input)
        form.addRow('Этапы приготовления:', self.desc_input)

        lbl_section = QLabel('Ингредиенты базового рецепта (по слоям):')
        lbl_section.setStyleSheet('color: #ffffff; font-weight: 700; font-size: 14px; margin-top: 10px;')

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(12)
        main_layout.addLayout(form)
        main_layout.addWidget(lbl_section)
        main_layout.addWidget(scroll, stretch=1)
        main_layout.addWidget(self.btn_add)
        main_layout.addSpacing(6)
        main_layout.addLayout(bottom)

        if self.available_ingredients:
            self.add_ingredient_row()

    def add_ingredient_row(self):
        if not self.available_ingredients:
            QMessageBox.warning(self, 'Внимание', 'Сначала заполните сырьё во вкладке «Склад ингредиентов».')
            return
        row = IngredientRow(self.available_ingredients, self.remove_ingredient_row, self.ingredients_container)
        self.ingredients_rows.append(row)
        self.ingredients_layout.addWidget(row)

    def remove_ingredient_row(self, row: IngredientRow):
        if row in self.ingredients_rows:
            self.ingredients_rows.remove(row)
            self.ingredients_layout.removeWidget(row)
            row.deleteLater()

    def save_cake(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Ошибка', 'Укажите название торта.')
            return

        items = [r.get_data() for r in self.ingredients_rows if r.get_data()['ingredient_id']]
        if not items:
            QMessageBox.warning(self, 'Ошибка', 'Добавьте хотя бы один ингредиент.')
            return

        payload = {
            'name': name,
            'base_diameter': self.diameter_input.value(),
            'description': self.desc_input.toPlainText().strip(),
            'cake_ingredients': items
        }

        try:
            self.api.create_cake(payload)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка сохранения', f'Не удалось сохранить рецепт: {e}')
