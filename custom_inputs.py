from PySide6.QtWidgets import (
    QComboBox as ComboBox,
    QSpinBox as Spin,
    QLineEdit as Line
)


class CustomCBox(ComboBox):

    COMBO_DATA = {}

    def setCurrentData(self, data):
        data_index = self.findData(data)
        self.setCurrentIndex(data_index)

    def __init__(self):
        super().__init__()

        for data, text in self.COMBO_DATA.items():
            self.addItem(text, data)


class KindBox(CustomCBox):
    
    COMBO_DATA = {
        "": "Не выбран",
        "m": "Мужская",
        "f": "Женская",
        "s": "Общая"
    }


class GenderBox(CustomCBox):

    COMBO_DATA = {
        "": "Не выбран",
        "m": "Мужской",
        "f": "Женский"
    }


class CustomSpin(Spin):

    MAXIMUM = 99
    MINIMUM = 0
    
    def __init__(self):
        super().__init__()

        self.setMaximum(self.MAXIMUM)
        self.setMinimum(self.MINIMUM)


class AgeSpin(CustomSpin):

    MAXIMUM = 120


class NumberSpin(CustomSpin):

    MAXIMUM = 2**16
    MINIMUM = 1


class PhoneLine(Line):

    MASK = "(999)-999-99-99"

    def __init__(self):
        super().__init__()

        self.setInputMask(self.MASK)


__all__ = [
    "CustomCBox",
    "KindBox",
    "GenderBox",
    "CustomSpin",
    "AgeSpin",
    "NumberSpin",
    "PhoneLine"
]