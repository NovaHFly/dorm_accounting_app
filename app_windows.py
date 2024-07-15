
#------------------------------------------------------------------
# Getting the current screen size
#------------------------------------------------------------------
from ctypes import windll

user32 = windll.user32
SCREEN_SIZE = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
#------------------------------------------------------------------
#------------------------------------------------------------------

import sys
import hashlib

from PySide6 import QtCore as qc
from abc import abstractclassmethod as abstract

from PySide6.QtWidgets import (
    QMainWindow as TopWindow,
    QDialog as Dialog,
    QMessageBox as MBox,
    QFrame as Frame,
    QGridLayout as LGrid,
    QHBoxLayout as LHBox,
    QVBoxLayout as LVBox,
    QSpinBox as Spin,
    QPushButton as Button,
    QRadioButton as RButton,
    QLabel as Label,
    QLineEdit as Line,
    QScrollArea as Scroll,
    QButtonGroup as BGroup,
    QMenuBar as MenuBar
)

from database import *
from custom_inputs import *
from custom_messages import *


class RelativePositionedWindow(TopWindow):

    def show(self, x_relative: float, y_relative: float):
        super().show()
        size = self.geometry().size().toTuple()
        pos_x = SCREEN_SIZE[0] * x_relative - size[0] // 2
        pos_y = SCREEN_SIZE[1] * y_relative - size[1] // 2
        self.move(pos_x, pos_y)


class CenteredWindow(RelativePositionedWindow):
    """
    Subclass for centered window
    """

    def show(self):
        super().show(0.5, 0.5)


class ViewItem(Frame):

    ITEM_SCHEME = "line"

    LABEL_SCHEME = {
        "number" : "Номер: {}"
    }

    LABEL_WIDTHS = [
        130
    ]

    LABEL_HEIGHT = 22

    LABEL_ALIGNMENT = qc.Qt.AlignHCenter | qc.Qt.AlignVCenter

    #------------------------------------------------------------------

    def select_self(self):
        """
        Change the item's style according to its status (Selected/Unselected)
        """

        if self.rbutton.isChecked():
            self.setProperty("selected", True)
            return

        self.setProperty("selected", False)
        

    #------------------------------------------------------------------

    @abstract
    def set_data(self, data):
        """
        Set item data. Should be redefined in derived classes
        """
        self.data = data.copy()

    #------------------------------------------------------------------

    def construct_rbutton(self):
        """
        Construct item's radio button (Used for selection)
        """

        content_view = self.parent()
        
        rbutton = self.rbutton = RButton()
        rbutton.key = self.element.key

        rbutton.toggled.connect(self.select_self)

        content_view.add_rbutton(rbutton)

        return rbutton

    def construct_contents(self):
        """
        Construct item contents
        """

        contents = []
        
        for key, scheme in self.LABEL_SCHEME.items():
            new_label = Label(scheme.format(self.data[key]))
            new_label.setProperty(key, True)
            new_label.setAlignment(qc.Qt.AlignCenter)
            contents.append(new_label)

        return contents

    def construct_item(self):
        """
        Construct item layout
        """

        rbutton = self.construct_rbutton()
        contents = self.construct_contents()

        if self.ITEM_SCHEME == "line":
        
            l_item = LHBox(self)

            for widget in [rbutton] + contents:
                l_item.addWidget(widget)

        if self.ITEM_SCHEME == "card":

            l_item = LGrid(self)

            for i, widget in enumerate(contents):
                l_item.addWidget(widget, i, 0, 1, 2)
                l_item.setAlignment(widget, qc.Qt.AlignCenter)

            l_item.addWidget(rbutton, 0, 0, 1, 1)
            l_item.setAlignment(rbutton, qc.Qt.AlignLeft)
            
    def __init__(self, parent=None, element=None):
        super().__init__(parent=parent)

        self.setProperty("selected", False)

        self.element = element
        self.set_data(element)

        self.construct_item()

    #------------------------------------------------------------------


class RoomItem(ViewItem):

    ITEM_SCHEME = "card"
    
    LABEL_SCHEME = {
        "number": "Номер: {}",
        "kind": "Тип комнаты: {}",
        "space": "Свободно мест: {}"
    }

    ROOM_TYPES = {
        "s": "Общая",
        "f": "Женская",
        "m": "Мужская"
    } 

    #------------------------------------------------------------------

    def open_occupants(self):
        window = Window_RoomOccupantsView(self.parent(), self.element)
        window.show()

    #------------------------------------------------------------------

    def set_data(self, element):
        """
        Set room item data to match the item scheme
        """

        raw_data = {}

        raw_data["number"] = element.number
        raw_data["kind"] = self.ROOM_TYPES.get(element.kind)
        raw_data["space"] = element.space

        self.data = raw_data

    def construct_contents(self):
        """
        Construct room item contents (Occupant button added)
        """
        contents = super().construct_contents()

        b_occupants = Button("Жильцы")
        b_occupants.clicked.connect(self.open_occupants)

        contents.append(b_occupants)

        return contents

    def __init__(self, parent, room:Room):
        super().__init__(parent, room)

        self.setProperty("space", room.space)
        self.setProperty("kind", room.kind)

    #------------------------------------------------------------------


class PersonItem(ViewItem):

    ITEM_SCHEME = "line"
    
    LABEL_SCHEME = {
        "key": "№ {}",
        "name": "{}",
        "room": "Комната: {}",
        "phone": "Телефон: {}"
    }

    GENDERS = {
        "f": "Не заселена",
        "m": "Не заселён"
    }

    def construct_contents(self):

        contents = []
        
        for key, scheme in self.LABEL_SCHEME.items():
            new_label = Label(scheme.format(self.data[key]))
            new_label.setProperty("field", key)
            new_label.setAlignment(qc.Qt.AlignLeft|qc.Qt.AlignVCenter)
            contents.append(new_label)

        return contents

    def __init__(self, parent, person):
        super().__init__(parent, person)

        self.setProperty("gender", person.gender)

    #------------------------------------------------------------------

    def set_data(self, element):
        """
        Set person item data
        """

        raw_data = {}

        raw_data["key"] = int(element.key)+1
        raw_data["name"] = element.name
        raw_data["phone"] = element.phone
        raw_data["gender"] = self.GENDERS.get(element.gender)
        room = DataBase().get_room(element.room)
        raw_data["room"] = room.number if room else raw_data["gender"]
        
        self.data = raw_data
    
    #------------------------------------------------------------------

#------------------------------------------------------------------

class ObjectView(Frame):

    SPACING = 7
    MARGINS = 7,7,7,7

    VIEW_ITEM = ViewItem

    VIEW_COLS = 1

    #------------------------------------------------------------------

    def clear_view(self):
        for item in self.items:
            item.deleteLater()
        
        self.items = list()

    def fill_view(self):

        data = self.data

        for key, element in self.sort_data(data.items()):
            new_item = self.VIEW_ITEM(self, element)
            self.add_item(new_item)

            if key == self.selected_key:
                new_item.rbutton.toggle()
                new_item.selected = True

    def update_view(self):
        self.clear_view()
        self.fill_view()

    def add_item(self, item):

        count_items = len(self.items)

        current_row = count_items // self.VIEW_COLS
        current_col = count_items % self.VIEW_COLS

        self.l_view.addWidget(item, current_row, current_col)
        self.items.append(item)

    #------------------------------------------------------------------
    
    def set_data(self, data:dict):
        self.data = data
        self.update_view()
    
    def set_sorting_rule(self, rule):
        
        self.sort_data = rule

    #------------------------------------------------------------------

    def select_item(self, key):
        self.selected_key = key
        
    def deselect_item(self):
        self.selected_key = None
    
    def get_selected_item(self):

        for key, value in self.data.items():
            if self.selected_key == key:
                return value

    #------------------------------------------------------------------

    def add_rbutton(self, button:RButton):
        self.rbutton_group.addButton(button)
    
    #------------------------------------------------------------------

    def construct_layout(self):
        l_view = self.l_view = LGrid(self)

        l_view.setSpacing(self.SPACING)
        l_view.setContentsMargins(*self.MARGINS)

        l_view.setSizeConstraint(l_view.SetFixedSize)
    
    def construct_scroll(self):
        self.scroll_area = Scroll()
        self.scroll_area.setWidget(self)

    def construct_view(self):
        self.construct_layout()
        self.construct_scroll()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        #------------------------------------------------------------------

        self.selected_key = None

        self.items = []
        self.data = {}

        self.sort_data = lambda it: sorted(it, key=lambda x: x[1].key)

        #------------------------------------------------------------------

        self.rbutton_group = BGroup()

        self.construct_view()

        self.fill_view()

        #------------------------------------------------------------------

    #------------------------------------------------------------------


class RoomView(ObjectView):
    
    VIEW_ITEM = RoomItem

    VIEW_COLS = 6


class PersonView(ObjectView):
    
    VIEW_ITEM = PersonItem

    VIEW_COLS = 1

#------------------------------------------------------------------

class CustomMenu(MenuBar):

    def add_menu(self, title):
        return super().addMenu(title)

    def add_action(self, menu, title, action, togglable=False, shortcut=None):
        m_action = menu.addAction(title)
        m_action.triggered.connect(action)

        if togglable:
            m_action.setEnabled(False)
            self.toggle_actions.append(m_action)

        if shortcut:
            m_action.setShortcut(shortcut)

    def __init__(self):
        super().__init__()

        self.toggle_actions = []


class ControlsFrame(Frame):


    def add_button(self, text, action, togglable=False):
        
        new_button = Button(text)
        new_button.clicked.connect(action)

        self.layout().addWidget(new_button)

        if togglable:
            new_button.setEnabled(False)
            self.toggle_buttons.append(new_button)

    
    def set_buttons_active(self, active:bool):

        for button in self.toggle_buttons:
            button.setEnabled(active)

    def __init__(self):
        super().__init__()

        self.toggle_buttons = []

        layout = LHBox(self)


class SortingFrame(Frame):
    """
    SortFormat = {
        "param" : "text"
    }
    """

    def get_sorting_rule(self):

        def custom_sorted(rules):

            key = lambda x: getattr(x[1], rules[0])

            if rules[1]:
                return lambda it: reversed(sorted(it, key=key))
            
            return lambda it: sorted(it, key=key)
                
        param = self.param_box.currentData()
        order = self.order_box.currentData()

        rules = (param, order)

        return custom_sorted(rules)

    def construct_widgets(self, sort_params, sort_action):
        
        param_box = self.param_box = CustomCBox()

        for param, text in sort_params.items():
            param_box.addItem(text, param)
        
        order_box = self.order_box = CustomCBox()
        order_box.addItem("По возрастанию", 0)
        order_box.addItem("По убыванию", 1)

        b_sort = Button("Сортировать")
        b_sort.clicked.connect(sort_action)

        layout = LHBox(self)
        layout.addWidget(param_box)
        layout.addWidget(order_box)
        layout.addWidget(b_sort)
    
    def __init__(self, sort_params:dict, sort_action):
        super().__init__()

        self.construct_widgets(sort_params, sort_action)


class SearchFrame(Frame):

    def get_query(self):
        
        query = (
            self.f_line.text(),
            self.f_cbox.currentData()
        )

        return query

    def construct_widgets(self, placeholder_text:str, search_action):
        
        search_line = self.f_line = Line()
        search_line.setPlaceholderText(placeholder_text)

        search_cbox = self.f_cbox = GenderBox()

        b_search = Button("Найти")
        b_search.clicked.connect(search_action)

        layout = LHBox(self)
        layout.addWidget(search_line)
        layout.addWidget(search_cbox)
        layout.addWidget(b_search)
    
    def __init__(self, placeholder_text:str, search_action):
        super().__init__()

        self.construct_widgets(placeholder_text, search_action)

#------------------------------------------------------------------

class Dialog_Help(MBox):

    HELP_PARTS = {
        "room": "help\\help_rooms.html",
        "person": "help\\help_occupants.html",
        "room-occupants": "help\\help_room_occupants.html"
    }

    def __init__(self, parent, help_part:str):
        super().__init__(parent=parent)

        with open(self.HELP_PARTS.get(help_part), "r", encoding="UTF-8") as f:
            message = f.read()

        self.setText(message)

        b_ok = self.addButton("ОК", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)
        
        self.setWindowTitle("Справка")


class Window_Password(CenteredWindow):

    MESSAGE = """Добро пожаловать, Пользователь
    Пожалуйста, введите пароль:"""

    TITLE = "Введите пароль"

    def check_password(self):

        password = self.password.text()
        pass_hash = hashlib.sha256(password.encode("UTF-8")).hexdigest()

        if pass_hash == DataBase().get_pass_hash():
            return True

        return False

    def authorize(self):

        password = self.password.text()
        
        if not DataBase().check_password(password):
            dialog = WrongPasswordDialog(self)
            dialog.exec_()
            self.password.setText("")
            return

        self.parent().show()

        self.hide()

    def construct_window(self):

        welcome_message = Label(self.MESSAGE)
        welcome_message.setProperty("password", True)

        fl_password = self.password = Line()
        fl_password.setEchoMode(fl_password.Password)
        fl_password.setProperty("password", True)

        b_password = Button("Войти")
        b_password.clicked.connect(self.authorize)
        b_password.setShortcut("Return")
        b_password.setProperty("password", True)

        f_password = Frame()
        l_password = LVBox(f_password)

        l_password.addWidget(welcome_message)
        l_password.addWidget(fl_password)
        l_password.addWidget(b_password)

        l_password.setAlignment(welcome_message, qc.Qt.AlignHCenter | qc.Qt.AlignVCenter)
        l_password.setAlignment(fl_password, qc.Qt.AlignHCenter)
        l_password.setAlignment(b_password, qc.Qt.AlignHCenter)

        self.setCentralWidget(f_password)
    
    def closeEvent(self, event):
        if not DataBase().authorized:
            sys.exit(1)

        super().closeEvent(event)
    
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.construct_window()

        self.setWindowTitle(self.TITLE)
        self.setWindowModality(qc.Qt.ApplicationModal)


class Dialog_About(MBox):

    MESSAGE = "{name} v{version}"
    INFORMATIVE_MESSAGE = "by {dev}"

    def __init__(self, parent, program_info: dict):
        super().__init__(parent=parent)

        self.setText(f'<h4>{self.MESSAGE.format(name=program_info["name"], version=program_info["version"])}</h3>')
        self.setInformativeText(self.INFORMATIVE_MESSAGE.format( dev=program_info["dev"]))

        self.setIcon(self.Information)

        b_ok = self.addButton("ОК", self.AcceptRole)

        self.setDefaultButton(b_ok)
        self.setEscapeButton(b_ok)
        
        self.setWindowTitle("О программе")


class EditDialog(Dialog):

    DB_ELEMENT = ""

    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 160
    WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

    INPUT_SCHEME = {
        "number" : ("Номер:", Line)
    }

    BUTTON_ACCEPT_TEXT = "Сохранить"
    BUTTON_REJECT_TEXT = "Отменить"

    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 25
    BUTTON_SIZE = BUTTON_WIDTH, BUTTON_HEIGHT

    BUTTON_SPACING = 0
    BUTTON_MARGINS = 10,0,10,0

    WINDOW_TITLE = "{}:"

    ELEMENT_TITLES = {
        "rooms": "Комната",
        "persons": "Жилец"
    }

    #------------------------------------------------------------------

    @abstract
    def check_conditions(self):
        ...

    @abstract
    def check_changes(self):
        ...

    def get_data(self):

        def extract_data(field):

            if type(field) in (Line, PhoneLine):
                return field.text()
            
            if type(field) in (Spin, AgeSpin, NumberSpin):
                return field.value()

            if type(field) in (GenderBox, KindBox):
                return field.currentData()
        
        data = {key: extract_data(value) for key, value in self.fields.items()}

        return data

    def accept(self):

        if not self.check_conditions():
            return

        if not self.check_changes():
            return

        super().accept()

    #------------------------------------------------------------------

    def construct_inputs(self):

        def set_data(field, value):

            if type(field) in (Line, PhoneLine):
                field.setText(value)
            
            if type(field) in (Spin, AgeSpin, NumberSpin):
                field.setValue(value)

            if type(field) in (GenderBox, KindBox):
                field.setCurrentData(value)

        params = {}

        if self.element:
            params = self.element.jsonify()

        f_inputs = Frame()
        f_inputs.setProperty("frame", "inputs")
        l_inputs = LGrid(f_inputs)

        fields = self.fields = {}

        for i, (key, (label, Field)) in enumerate(self.INPUT_SCHEME.items()):
            new_label = Label(label)
            new_field = Field()

            value = params.get(key)

            if value:
                set_data(new_field, value)

            fields[key] = new_field

            l_inputs.addWidget(new_label, i, 0)
            l_inputs.addWidget(new_field, i, 1)

        return f_inputs

    def construct_buttons(self):
        b_accept = Button(self.BUTTON_ACCEPT_TEXT)
        b_reject = Button(self.BUTTON_REJECT_TEXT)

        b_accept.clicked.connect(self.accept)
        b_reject.clicked.connect(self.reject)



        buttons = Frame()

        l_buttons = LHBox(buttons)

        for button in (b_accept, b_reject):
            button.setFixedSize(*self.BUTTON_SIZE)
            l_buttons.addWidget(button)

        l_buttons.setSpacing(self.BUTTON_SPACING)
        l_buttons.setContentsMargins(*self.BUTTON_MARGINS)

        return buttons

    def construct_window(self):
        inputs = self.construct_inputs()
        buttons = self.construct_buttons()

        l_dialog = LVBox(self)

        l_dialog.addWidget(inputs)
        l_dialog.addWidget(buttons)

    def __init__(self, parent_window=None, element=None):
        super().__init__(parent=parent_window)

        #------------------------------------------------------------------
        
        self.element = element
        self.view_window = parent_window

        #------------------------------------------------------------------

        self.construct_window()

        #------------------------------------------------------------------
        
        self.setFixedSize(*self.WINDOW_SIZE)

        title = self.WINDOW_TITLE.format(self.ELEMENT_TITLES.get(self.DB_ELEMENT))
        self.setWindowTitle(f"{title} {'Создать' if not element else 'Редактировать'}")

        self.setWindowModality(qc.Qt.WindowModal)


        #------------------------------------------------------------------

    #------------------------------------------------------------------


class RoomEditDialog(EditDialog):

    DB_ELEMENT = "rooms"

    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 200
    WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

    INPUT_SCHEME = {
        "number": ("Номер комнаты:", NumberSpin),
        "kind": ("Тип комнаты:", KindBox),
        "capacity": ("Кол-во мест:", Spin)
    }

    def check_conditions(self):

        kind_empty = not self.fields["kind"].currentData()

        if kind_empty:
            WarningMessageDialog("Не выбран тип комнаты!").exec_()
            return False

        return True
        
    def check_changes(self):

        if self.element:

            kind_changed = self.element.kind != self.fields["kind"].currentData()
            capacity_changed = self.element.capacity != self.fields["capacity"].value()

            if any((kind_changed, capacity_changed)):
                dialog = RoomChangeConfirmDialog(self)
                dialog.exec_()

                if dialog.result():
                    return False
            
        return True


class PersonEditDialog(EditDialog):

    DB_ELEMENT = "persons"

    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 270
    WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

    INPUT_SCHEME = {
        "name": ("ФИО жильца:", Line),
        "gender": ("Пол:", GenderBox),
        "age": ("Возраст:", AgeSpin),
        "phone": ("Ном. телефона:", PhoneLine),
        "passport": ("Паспорт", Line)
    }

    def check_conditions(self):

        kind_empty = not self.fields["gender"].currentData()

        if kind_empty:
            WarningMessageDialog("Не выбран пол жильца!").exec_()
            return False

        return True

    def check_changes(self):

        if self.element:

            gender_changed = self.element.gender != self.fields["gender"].currentData()

            if gender_changed:
                dialog = PersonChangeConfirmDialog(self)
                dialog.exec_()

                if dialog.result():
                    return False
        
        return True


class Dialog_OccupantSelect(Dialog):

    WINDOW_WIDTH = 687
    WINDOW_HEIGHT = 500

    WINDOW_TITLE = "Выберите человека!"
    
    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 25
    BUTTON_SIZE = BUTTON_WIDTH, BUTTON_HEIGHT

    SORT_SCHEME = {
        "key": "Номер в базе данных",
        "name": "ФИО жильца",
        "gender": "Пол жильца"
    }

    PLACEHOLDER_TEXT = "Введите ФИО человека (Полное или часть). . ."

    #------------------------------------------------------------------

    def accept(self):

        person = self.view.get_selected_item()

        if self.room.kind != "s" and self.room.kind != person.gender:
            InvalidOccupantDialog(self, self.room.kind).exec_()
            return
                
        if person.key in self.room.occupants:
            OccupantInRoomDialog(self).exec_()
            return              
        
        super().accept()

    def get_selected_person(self):
        return self.view.get_selected_item()

    #------------------------------------------------------------------

    def set_buttons_active(self, active:bool):
        self.b_accept.setEnabled(active)

    def rbutton_clicked(self, button:RButton):

        key = button.key

        if key == self.view.selected_key:
            self.view.deselect_item()
            self.set_buttons_active(False)
            self.view.update_view()
            return

        self.view.select_item(key)
        self.set_buttons_active(True)

    #------------------------------------------------------------------

    def sort_items(self):
        self.view.set_sorting_rule(self.sort.get_sorting_rule())
        self.view.update_view()

    def search_items(self):
        
        query = self.search.get_query()

        data = {key: value for key, value in self.data.items() if query[0] in value.name and query[1] in value.gender}

        self.view.set_data(data)
        self.view.deselect_item()
        self.set_buttons_active(False)
        self.view.update_view()

    #------------------------------------------------------------------

    def construct_sort(self):
        self.sort = SortingFrame(self.SORT_SCHEME, self.sort_items)

        return self.sort

    def construct_search(self):
        self.search = SearchFrame(self.PLACEHOLDER_TEXT, self.search_items)

        return self.search

    def construct_view(self):
        
        self.view = PersonView(self)
        self.view.set_data(self.data)

        self.view.rbutton_group.buttonClicked.connect(self.rbutton_clicked)

        return self.view.scroll_area

    def construct_buttons(self):
        
        b_accept = Button("Добавить")
        b_reject = Button("Отмена")

        b_accept.clicked.connect(self.accept)
        b_reject.clicked.connect(self.reject)

        b_accept.setFixedSize(*self.BUTTON_SIZE)
        b_reject.setFixedSize(*self.BUTTON_SIZE)

        b_accept.setEnabled(False)

        self.b_accept = b_accept

        f_buttons = Frame()
        l_buttons = LHBox(f_buttons)

        l_buttons.addWidget(b_accept)
        l_buttons.addWidget(b_reject)

        l_buttons.setAlignment(b_accept, qc.Qt.AlignRight)
        l_buttons.setAlignment(b_reject, qc.Qt.AlignLeft)

        return f_buttons

    def construct_window(self):

        sort = self.construct_sort()
        search = self.construct_search()
        
        view = self.construct_view()
        buttons = self.construct_buttons()

        l_central = LVBox(self)

        l_central.addWidget(sort)
        l_central.addWidget(search)
        l_central.addWidget(view)
        l_central.addWidget(buttons)

    def __init__(self, parent, room):
        super().__init__(parent=parent)

        self.room = room
        self.data = DataBase().get_elements("persons")

        self.construct_window()

        self.setFixedWidth(self.WINDOW_WIDTH)
        self.setMinimumHeight(self.WINDOW_HEIGHT)

        self.setWindowTitle(self.WINDOW_TITLE)

    #------------------------------------------------------------------


class Dialog_PassChange(Dialog):

    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 160
    WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

    BUTTON_SPACING = 0
    BUTTON_MARGINS = 10,0,10,0

    def construct_inputs(self):

        lb_old = Label("Старый пароль:")
        lb_new = Label("Новый пароль:")
        lb_repeat = Label("Подтвердите пароль:")

        fl_old = self.fl_old = Line()
        fl_new = self.fl_new = Line()
        fl_repeat = self.fl_repeat = Line()

        fl_old.setEchoMode(fl_old.Password)
        fl_new.setEchoMode(fl_new.Password)
        fl_repeat.setEchoMode(fl_repeat.Password)

        f_inputs = Frame()
        f_inputs.setProperty("inputs", True)
        l_inputs = LGrid(f_inputs)

        inputs = {
            lb_old: fl_old,
            lb_new: fl_new,
            lb_repeat: fl_repeat
        }

        for i, (label, field) in enumerate( inputs.items() ):
            l_inputs.addWidget(label, i, 0)
            l_inputs.addWidget(field, i, 1)

        return f_inputs

    def clear_fields(self):
        self.fl_old.setText("")
        self.fl_new.setText("")
        self.fl_repeat.setText("")

    def check_password(self):

        pass_old = self.fl_old.text()
        pass_new = self.fl_new.text()
        pass_repeat = self.fl_repeat.text()

        if any( map( lambda x: not x, (pass_old, pass_new, pass_repeat)) ):
            EmptyPasswordDialog(self).exec_()
            return False

        if not DataBase().check_password(pass_old):
            WrongPasswordDialog(self).exec_()
            return False

        if len(pass_new) < 7:
            ShortPasswordDialog(self).exec_()
            return False
        
        if DataBase().check_password(pass_new):
            SamePasswordDialog(self).exec_()
            return False

        if not pass_new == pass_repeat:
            PasswordsDontMatchDialog(self).exec_()
            return False

        self.set_pass(pass_new)
        return True

    def set_pass(self, password):
        self.password = password

    def get_pass(self):
        return self.password

    def accept(self):

        if self.check_password():
            super().accept()
            return
        
        self.clear_fields()
      
    def construct_buttons(self):
        b_accept = Button("Сохранить")
        b_reject = Button("Отмена")

        b_accept.clicked.connect(self.accept)
        b_reject.clicked.connect(self.reject)

        buttons = Frame()

        l_buttons = LHBox(buttons)

        for button in (b_accept, b_reject):
            l_buttons.addWidget(button)

        l_buttons.setSpacing(self.BUTTON_SPACING)
        l_buttons.setContentsMargins(*self.BUTTON_MARGINS)

        return buttons

    def construct_window(self):
        inputs = self.construct_inputs()
        buttons = self.construct_buttons()

        l_dialog = LVBox(self)
        l_dialog.addWidget(inputs)
        l_dialog.addWidget(buttons)
    
    def __init__(self, parent):
        super().__init__(parent=parent)

        
        self.construct_window()

#------------------------------------------------------------------

class Window_View(CenteredWindow):

    DB_ELEMENT = ""

    DIALOG = EditDialog
    VIEW_WIDGET = ObjectView
    ELEMENT = ""
    
    WINDOW_WIDTH = 910
    WINDOW_HEIGHT = 500

    WINDOW_TITLE = "Учёт жильцов: {}"

    ELEMENT_TITLES = {
        "rooms": "Комнаты",
        "persons": "Жильцы"
    }

    SORT_SCHEME = {
        "number": "Номер"
    }

    #------------------------------------------------------------------

    def create_item(self):
        
        dialog_edit = self.DIALOG(self)
        dialog_edit.exec_()

        if not dialog_edit.result():
            return

        params = dialog_edit.get_data()
        DataBase().create_data(self.DB_ELEMENT, params)
        self.view.update_view()

    def edit_item(self):
        
        key = self.view.selected_key
        element = self.data[key]

        dialog_edit = self.DIALOG(self, element)
        dialog_edit.exec_()

        if not dialog_edit.result():
            return

        params = dialog_edit.get_data()

        DataBase().update_data(self.DB_ELEMENT, key, params)

        self.view.update_view()

    def delete_item(self):

        key = self.view.selected_key

        dialog = DeletionConfirmDialog(self, self.DB_ELEMENT)
        dialog.exec_()

        if not dialog.result() == 0:
            return
        
        DataBase().delete_data(self.DB_ELEMENT, key)    

        self.view.deselect_item()
        self.set_buttons_active(False)

        self.view.update_view()

    #------------------------------------------------------------------

    def sort_items(self):
        self.view.set_sorting_rule(self.sort.get_sorting_rule())
        self.view.update_view()

    #------------------------------------------------------------------

    def close_window(self):
        
        self.close()

    def set_buttons_active(self, active:bool):
        
        self.controls.set_buttons_active(active)

        for action in self.menu.toggle_actions:
            action.setEnabled(active)

    def rbutton_clicked(self, button:RButton):

        key = button.key

        if key == self.view.selected_key:
            self.view.deselect_item()
            self.set_buttons_active(False)
            self.view.update_view()
            return

        self.view.select_item(key)
        self.set_buttons_active(True)
        self.view.update_view()

    #------------------------------------------------------------------

    def construct_menu(self):

        menu = self.menu = CustomMenu()

        #------------------------------------------------------------------

        m_win = menu.add_menu("Окно")
        menu.add_action(m_win, "Закрыть", self.close_window)

        m_object = menu.add_menu("Элемент")
        menu.add_action(m_object, "Создать", self.create_item)
        menu.add_action(m_object, "Редактировать", self.edit_item, True)
        menu.add_action(m_object, "Удалить", self.delete_item, True)

        return menu

    def construct_sort(self):
        self.sort = SortingFrame(self.SORT_SCHEME, self.sort_items)

        return self.sort

    def construct_controls(self):

        controls = self.controls = ControlsFrame()

        controls.add_button("Создать", self.create_item)
        controls.add_button("Редактировать", self.edit_item, True)
        controls.add_button("Удалить", self.delete_item, True)

        return self.controls

    def construct_view(self):
        
        self.view = self.VIEW_WIDGET(self)
        self.view.set_data(self.data)

        self.view.rbutton_group.buttonClicked.connect(self.rbutton_clicked)

        return self.view.scroll_area

    def construct_window(self):
        """
        Construct window layout
        """
        
        menu = self.construct_menu()
        self.setMenuBar(menu)

        sort = self.construct_sort()
        controls = self.construct_controls()
        view = self.construct_view()

        f_central = Frame()
        l_central = self.l_central = LVBox(f_central)

        l_central.addWidget(controls)
        l_central.addWidget(sort)
        l_central.addWidget(view)

        self.setCentralWidget(f_central)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.data = DataBase().get_elements(self.DB_ELEMENT)

        self.construct_window()

        self.setWindowModality(qc.Qt.WindowModal)

        title = self.WINDOW_TITLE.format(self.ELEMENT_TITLES.get(self.DB_ELEMENT))
        self.setWindowTitle(title)

        self.setFixedWidth(self.WINDOW_WIDTH)
        self.setMinimumHeight(self.WINDOW_HEIGHT)

    #------------------------------------------------------------------

#------------------------------------------------------------------

class Window_Rooms(Window_View):

    DB_ELEMENT = "rooms"

    DIALOG = RoomEditDialog
    VIEW_WIDGET = RoomView
    ELEMENT = Room
    
    WINDOW_WIDTH = 1036
    WINDOW_HEIGHT = 550

    SORT_SCHEME = {
        "key": "Номер в базе данных",
        "number": "Номер комнаты",
        "kind": "Тип комнаты",
        "space": "Свободно мест"
    }

    DEVELOPER = "@NovaHFly"
    VERSION = "0.4"
    NAME = "Учёт жильцов"

    APPLICATION_INFO = {
        "dev": DEVELOPER,
        "version": VERSION,
        "name": NAME
    }

    def open_window_occupants(self):
        
        window = Window_Persons(self)
        window.show()

    def show_about(self):
        
        dialog = Dialog_About(self, self.APPLICATION_INFO)
        dialog.exec_()

    def show_help(self):
        
        dialog = Dialog_Help(self, "room")
        dialog.exec_()

    def change_password(self):

        dialog = Dialog_PassChange(self)
        dialog.exec_()

        if dialog.result():
            DataBase().set_password(dialog.get_pass())
            PasswordChangedDialog(self).exec_()

    def construct_menu(self):

        menu = self.menu = CustomMenu()

        m_win = menu.add_menu("Программа")
        menu.add_action(m_win, "Жильцы", self.open_window_occupants, shortcut="Ctrl+O")
        menu.add_action(m_win, "Изменить пароль", self.change_password)
        menu.add_action(m_win, "Закрыть", self.close_window, shortcut="Alt+F4")

        m_room = menu.add_menu("Комната")
        menu.add_action(m_room, "Создать", self.create_item, shortcut="Ctrl+N")
        menu.add_action(m_room, "Редактировать", self.edit_item, True, shortcut="Ctrl+E")
        menu.add_action(m_room, "Удалить", self.delete_item, True, shortcut="Del")

        m_help = menu.add_menu("Справка")
        menu.add_action(m_help, "Посмотреть справку", self.show_help, shortcut="F1")
        menu.add_action(m_help, "О программе", self.show_about, shortcut="F2")

        return menu

    def close_window(self):
        
        self.close()

    def closeEvent(self, event):
        DataBase().save_data()
        super().closeEvent(event)


class Window_Persons(Window_View):
    
    DB_ELEMENT = "persons"

    DIALOG = PersonEditDialog
    VIEW_WIDGET = PersonView
    ELEMENT = Person
    
    WINDOW_WIDTH = 695
    WINDOW_HEIGHT = 500

    SORT_SCHEME = {
        "key": "Номер в базе данных",
        "name": "ФИО жильца",
        "gender": "Пол жильца"
    }

    PLACEHOLDER_TEXT = "Введите ФИО человека (Полное или часть). . ."

    def search_items(self):
        
        query = self.search.get_query()

        data = {key: value for key, value in self.data.items() if query[0] in value.name and query[1] in value.gender}

        self.view.set_data(data)
        self.view.deselect_item()
        self.set_buttons_active(False)
        self.view.update_view()

    def construct_search(self):
        self.search = SearchFrame(self.PLACEHOLDER_TEXT, self.search_items)

        return self.search

    def construct_window(self):
        super().construct_window()

        search = self.construct_search()
        self.l_central.insertWidget(2, search)

    def show_help(self):
        
        dialog = Dialog_Help(self, "person")
        dialog.exec_()

    def construct_menu(self):

        menu = self.menu = CustomMenu()

        m_win = menu.add_menu("Окно")
        menu.add_action(m_win, "Закрыть", self.close_window, shortcut="Alt+F4")

        m_person = menu.add_menu("Жилец")
        menu.add_action(m_person, "Создать", self.create_item, shortcut="Ctrl+N")
        menu.add_action(m_person, "Редактировать", self.edit_item, True, shortcut="Ctrl+E")
        menu.add_action(m_person, "Удалить", self.delete_item, True, shortcut="Del")

        m_help = menu.add_menu("Справка")
        menu.add_action(m_help, "Показать справку", self.show_help, shortcut="F1")

        return menu


class Window_RoomOccupantsView(CenteredWindow):
    
    WINDOW_WIDTH = 687
    WINDOW_HEIGHT = 500

    WINDOW_TITLE = "Комната {}: Жильцы"

    #------------------------------------------------------------------

    def add_person(self):

        if not self.room.space:
            NoRoomDialog(self).exec_()
            return
        
        dialog = Dialog_OccupantSelect(self, self.room)
        dialog.exec_()

        if not dialog.result():
            return

        occupant = dialog.get_selected_person()
        key = occupant.key

        self.room.add_occupant(key)
        self.occupant_data[key] = occupant
        
        self.view.update_view()

    def remove_person(self):

        selected_occupant = self.view.get_selected_item()

        dialog = PersonRemoveConfirmDialog(self, selected_occupant.name, self.room.number)
        dialog.exec_()

        if not dialog.result() == 0:
            return

        key = self.view.selected_key
        
        self.room.remove_occupant(key)
        self.occupant_data.pop(key)

        self.view.deselect_item()
        self.set_buttons_active(False)

        self.view.update_view()

    def show_help(self):
        
        dialog = Dialog_Help(self, "room-occupants")
        dialog.exec_()

    #------------------------------------------------------------------

    def close_window(self):
        self.close()

    #------------------------------------------------------------------

    def closeEvent(self, event):
        self.parent().update_view()
        super().closeEvent(event)

    def set_buttons_active(self, active:bool):
        for button in self.controls.toggle_buttons + self.menu.toggle_actions:
            button.setEnabled(active)

    def rbutton_clicked(self, button:RButton):

        key = button.key

        if key == self.view.selected_key:
            self.view.deselect_item()
            self.set_buttons_active(False)
            self.view.update_view()
            return

        self.view.select_item(key)
        self.set_buttons_active(True)

    #------------------------------------------------------------------

    

    def construct_menu(self):

        menu = self.menu = CustomMenu()

        m_win = menu.add_menu("Окно")
        menu.add_action(m_win, "Закрыть", self.close_window, shortcut="Alt+F4")

        m_occupants = menu.add_menu("Жильцы")
        menu.add_action(m_occupants, "Заселить", self.add_person, shortcut="Ctrl+A")
        menu.add_action(m_occupants, "Выселить", self.remove_person, True, shortcut="Del")

        m_help = menu.add_menu("Справка")
        menu.add_action(m_help, "Посмотреть справку", self.show_help, shortcut="F1")

        return menu

    def construct_controls(self):

        controls = self.controls = ControlsFrame()

        controls.add_button("Заселить", self.add_person)
        controls.add_button("Выселить", self.remove_person, True)

        return self.controls

    def construct_view(self):
        
        self.view = PersonView(self)
        self.view.set_data(self.occupant_data)

        self.view.rbutton_group.buttonClicked.connect(self.rbutton_clicked)

        return self.view.scroll_area

    def construct_window(self):

        menu = self.construct_menu()
        self.setMenuBar(menu)

        controls = self.construct_controls()
        view = self.construct_view()

        f_central = Frame()
        l_central = LVBox(f_central)
        l_central.addWidget(controls)
        l_central.addWidget(view)

        self.setCentralWidget(f_central)

    def __init__(self, parent=None, room:Room=None):
        super().__init__(parent=parent)

        self.room = room
        self.occupant_data = {number: DataBase().get_person(number) for number in room.occupants}

        self.construct_window()

        self.setWindowModality(qc.Qt.WindowModal)

        title = self.WINDOW_TITLE.format(self.room.number)
        self.setWindowTitle(title)

        self.setFixedWidth(self.WINDOW_WIDTH)
        self.setMinimumHeight(self.WINDOW_HEIGHT)

    #------------------------------------------------------------------

#------------------------------------------------------------------

__all__ = [
    "RelativePositionedWindow",
    "CenteredWindow",
    "Dialog_Help",
    "Window_Password",
    "Dialog_About",
    "EditDialog",
    "RoomEditDialog",
    "PersonEditDialog",
    "Dialog_OccupantSelect",
    "Dialog_PassChange",
    "Window_View",
    "Window_Rooms",
    "Window_Persons",
    "Window_RoomOccupantsView",
]