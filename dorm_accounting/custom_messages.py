from PySide6.QtWidgets import (
    QMessageBox as MBox
)

class WarningMessageDialog(MBox):
    

    def __init__(self, message):
        super().__init__()

        self.setText(message)
        self.setIcon(self.Warning)

        b_ok = self.addButton("Ок", self.AcceptRole)
        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Внимание!")


class DeletionConfirmDialog(MBox):
    """
    Возвращает 0 - Да, 1 - Нет
    """

    MESSAGE = "Данное действие удалит всю информацию о {}. Продолжить?"

    ELEM_TYPES = {
        "rooms": "комнате",
        "persons": "жильце"
    }

    WINDOW_TITLE = "Подтвердите действие!"

    def __init__(self, parent, db_element:str):
        super().__init__(parent=parent)
        
        self.setIcon(self.Question)

        elem_type = self.ELEM_TYPES.get(db_element)
        self.setText(self.MESSAGE.format(elem_type))

        b_yes = self.addButton("Да", self.YesRole)
        b_no = self.addButton("Нет", self.NoRole)

        self.setDefaultButton(b_no)
        self.setEscapeButton(b_no)

        self.setWindowTitle(self.WINDOW_TITLE)


class RoomChangeConfirmDialog(MBox):

    MESSAGE = "Внесённые изменения могут повлечь выселение одного или нескольких жильцов из комнаты. Продолжить?"

    WINDOW_TITLE = "Подтвердите действие!"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Question)

        self.setText(self.MESSAGE)

        b_yes = self.addButton("Да", self.YesRole)
        b_no = self.addButton("Нет", self.NoRole)

        self.setDefaultButton(b_no)
        self.setEscapeButton(b_no)

        self.setWindowTitle(self.WINDOW_TITLE)


class PersonChangeConfirmDialog(MBox):

    MESSAGE = "Внесённые изменения могут повлечь выселение жильца из комнаты. Продолжить?"

    WINDOW_TITLE = "Подтвердите действие!"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Question)

        self.setText(self.MESSAGE)

        b_yes = self.addButton("Да", self.YesRole)
        b_no = self.addButton("Нет", self.NoRole)

        self.setDefaultButton(b_no)
        self.setEscapeButton(b_no)

        self.setWindowTitle(self.WINDOW_TITLE)


class PersonRemoveConfirmDialog(MBox):
    
    MESSAGE = "Данное действие выселит {} из комнаты {}. Продолжить?"

    WINDOW_TITLE = "Подтвердите действие!"

    def __init__(self, parent, person_name:str, number:str):
        super().__init__(parent=parent)
        
        self.setIcon(self.Question)

        self.setText(self.MESSAGE.format(person_name, number))

        b_yes = self.addButton("Да", self.YesRole)
        b_no = self.addButton("Нет", self.NoRole)

        self.setDefaultButton(b_no)
        self.setEscapeButton(b_no)

        self.setWindowTitle(self.WINDOW_TITLE)


class InvalidOccupantDialog(MBox):

    MESSAGE = "Данный человек не может быть заселён в эту комнату: \"{}\"!"

    ROOM_KINDS = {
        "f": "Женская",
        "m": "Мужская"
    }

    def __init__(self, parent, kind):
        super().__init__(parent=parent)

        self.setIcon(self.Warning)

        self.setText(self.MESSAGE.format(self.ROOM_KINDS.get(kind)))

        b_ok = self.addButton("Ок", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Внимание!")


class NoRoomDialog(MBox):

    MESSAGE = "В комнате недостаточно мест!"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Warning)

        self.setText(self.MESSAGE)

        b_ok = self.addButton("Ок", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Внимание!")


class OccupantInRoomDialog(MBox):

    MESSAGE = "Данный человек уже живёт в комнате!"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Warning)

        self.setText(self.MESSAGE)

        b_ok = self.addButton("Ок", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Внимание!")

class WrongPasswordDialog(MBox):

    MESSAGE = "Неверный пароль!"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Critical)

        self.setText(self.MESSAGE)

        b_ok = self.addButton("Ок", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Внимание!")

class SamePasswordDialog(MBox):

    MESSAGE = "Новый пароль не может совпадать с текущим!"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Critical)

        self.setText(self.MESSAGE)

        b_ok = self.addButton("Ок", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Внимание!")

class PasswordsDontMatchDialog(MBox):

    MESSAGE = "Пароли не совпадают!"
    INFO_MESSAGE = "(Поля новый пароль и подтверждение пароля)"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Critical)

        self.setText(self.MESSAGE)
        self.setInformativeText(self.INFO_MESSAGE)

        b_ok = self.addButton("Ок", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Внимание!")


class PasswordChangedDialog(MBox):

    MESSAGE = "Пароль успешно изменён!"
    INFO_MESSAGE = "Не потеряйте его!"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Information)

        self.setText(self.MESSAGE)
        self.setInformativeText(self.INFO_MESSAGE)

        b_ok = self.addButton("Ок", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Пароль")


class EmptyPasswordDialog(MBox):

    MESSAGE = "Заполните поля ввода паролей!"
    INFO_MESSAGE = "(Одно или несколько полей ввода пустые)"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Critical)

        self.setText(self.MESSAGE)
        self.setInformativeText(self.INFO_MESSAGE)

        b_ok = self.addButton("Ок", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Внимание!")


class ShortPasswordDialog(MBox):

    MESSAGE = "Слишком короткий пароль!"
    INFO_MESSAGE = "Пожалуйста, введите пароль как минимум из 7 символов!"

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setIcon(self.Critical)

        self.setText(self.MESSAGE)
        self.setInformativeText(self.INFO_MESSAGE)

        b_ok = self.addButton("Ок", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)

        self.setWindowTitle("Внимание!")


__all__ = [
    "WarningMessageDialog",
    "DeletionConfirmDialog",
    "RoomChangeConfirmDialog",
    "PersonChangeConfirmDialog",
    "PersonRemoveConfirmDialog",
    "InvalidOccupantDialog",
    "NoRoomDialog",
    "OccupantInRoomDialog",
    "WrongPasswordDialog",
    "SamePasswordDialog",
    "PasswordsDontMatchDialog",
    "PasswordChangedDialog",
    "EmptyPasswordDialog",
    "ShortPasswordDialog"
]