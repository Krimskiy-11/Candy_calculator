from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox,
    QComboBox, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel
)


INGR_THEME = """
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

QLineEdit, QDoubleSpinBox, QComboBox {
    background-color: #171a22;
    border: 1px solid #272d3b;
    border-radius: 8px;
    padding: 9px 12px;
    color: #ffffff;
    font-size: 13px;
    selection-background-color: #3b82f6;
}

QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {
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
"""


class IngredientDialog(QDialog):
    def __init__(self, api, ingredient_data: dict | None = None, parent=None):
        super().__init__(parent)
        self.api = api
        self.ingredient_data = ingredient_data
        self.is_edit = ingredient_data is not None

        self.setWindowTitle('Редактировать продукт' if self.is_edit else 'Новый ингредиент')
        self.resize(440, 290)
        self.setStyleSheet(INGR_THEME)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Мука пшеничная в/с, Сыр Маскарпоне 78%...')

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 100000.0)
        self.price_input.setValue(150.0)
        self.price_input.setDecimals(2)
        self.price_input.setSuffix(' ₽')

        self.qty_input = QDoubleSpinBox()
        self.qty_input.setRange(0.01, 100000.0)
        self.qty_input.setValue(1000.0)
        self.qty_input.setDecimals(2)

        self.unit_combo = QComboBox()
        self.unit_combo.addItem('Граммы (г)', userData='g')
        self.unit_combo.addItem('Миллилитры (мл)', userData='ml')
        self.unit_combo.addItem('Штуки (шт)', userData='pcs')

        # Заполнение при редактировании
        if self.is_edit:
            self.name_input.setText(str(ingredient_data.get('name', '')))
            self.price_input.setValue(float(ingredient_data.get('package_price', 0.0)))
            self.qty_input.setValue(float(ingredient_data.get('package_quantity', 1.0)))
            unit_val = ingredient_data.get('unit', 'g')
            idx = self.unit_combo.findData(unit_val)
            if idx >= 0:
                self.unit_combo.setCurrentIndex(idx)

        btn_save = QPushButton('Сохранить изменения' if self.is_edit else 'Добавить на склад')
        btn_save.setProperty('class', 'btn-save')
        btn_save.clicked.connect(self.save)

        btn_cancel = QPushButton('Отмена')
        btn_cancel.setProperty('class', 'btn-cancel')
        btn_cancel.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_save)

        form = QFormLayout()
        form.setSpacing(14)
        form.addRow('Название продукта:*', self.name_input)
        form.addRow('Цена закупки:*', self.price_input)
        form.addRow('Фасовка упаковки:*', self.qty_input)
        form.addRow('Единица измерения:*', self.unit_combo)

        title_lbl = QLabel('Редактирование сырья' if self.is_edit else 'Добавление сырья на склад')
        title_lbl.setStyleSheet('color: #ffffff; font-size: 16px; font-weight: 700; margin-bottom: 6px;')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.addWidget(title_lbl)
        layout.addLayout(form)
        layout.addSpacing(10)
        layout.addLayout(buttons)

    def save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Ошибка', 'Введите наименование продукта.')
            return

        payload = {
            'name': name,
            'package_price': self.price_input.value(),
            'package_quantity': self.qty_input.value(),
            'unit': self.unit_combo.currentData(),
        }

        try:
            if self.is_edit:
                self.api.update_ingredient(self.ingredient_data['id'], payload)
            else:
                self.api.create_ingredient(payload)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка сохранения', f'Не удалось сохранить: {e}')
