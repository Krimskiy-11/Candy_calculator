from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QSpinBox,
    QPushButton, QLabel, QMessageBox
)
from .result_dialog import ResultDialog


class CalcWindow(QWidget):
    def __init__(self, api, cake_id: int, cake_name: str, base_diameter: int = 18, parent=None):
        super().__init__(parent)
        self.api = api
        self.cake_id = cake_id
        self.cake_name = cake_name

        self.setWindowTitle(f'Калькулятор — {cake_name}')
        self.resize(350, 180)

        # Выбор диаметра для пересчёта
        self.diameter_input = QSpinBox()
        self.diameter_input.setRange(8, 60)
        self.diameter_input.setValue(base_diameter)
        self.diameter_input.setSuffix(' см')

        btn_calculate = QPushButton('Рассчитать себестоимость')
        btn_calculate.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        btn_calculate.clicked.connect(self.do_calculate)

        form = QFormLayout()
        form.addRow('Целевой диаметр:', self.diameter_input)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>Торт:</b> {cake_name}"))
        layout.addWidget(QLabel(f"Базовый диаметр рецепта: {base_diameter} см"))
        layout.addSpacing(10)
        layout.addLayout(form)
        layout.addSpacing(10)
        layout.addWidget(btn_calculate)
        self.setLayout(layout)

    def do_calculate(self):
        target_dia = self.diameter_input.value()
        try:
            # Запрос к DRF: GET /api/cakes/{id}/calculate/?diameter=XX
            calc_data = self.api.calculate(self.cake_id, target_dia)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка расчёта', f'Не удалось получить данные: {e}')
            return

        # Открываем результат в отдельном окне (модальный диалог)
        dlg = ResultDialog(self.cake_name, calc_data, self)
        dlg.exec()
