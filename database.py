import os
import pickle
import hashlib

class SingletonMeta(type):
    """
    Metaclass for singleton pattern implementation
    """
    
    def __call__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__call__()
        return cls.instance


class DataBaseObject:
    """
    Base class for database objects
    """

    properties_to_jsonify = ["key"] 
    
    def jsonify(self) -> dict:
        """
        Jsonifies the database object
        """

        properties_json = {key: getattr(self, key) for key in self.properties_to_jsonify}
        return properties_json

    def __eq__(self, o) -> bool:

        if type(self) != type(o):
            return False
        
        if self.jsonify() == o.jsonify():
            return True

        return False

    def __init__(self, key:str) -> None:
        """
        Create database object (e.g. Room, Person)

        @key - database key
        """

        self.key = key


class Room(DataBaseObject):

    #------------------------------------------------------------------

    def add_occupant(self, key:str) -> None:
        """
        Adds occupant to the room

        @key - occupant's key in db
        """
        
        self.occupants.append(key)
        person = DataBase().get_person(key)

        person.change_room(self.key)

        self.space -= 1
    
    def remove_occupant(self, key:str) -> None:
        """
        Removes occupant from the room

        @key - occupant's key in db
        """

        self.occupants.remove(key)
        
        person = DataBase().get_person(key)
        person.reset_room()

        self.space += 1

    #------------------------------------------------------------------

    def edit(self, params:dict) -> None:
        """
        Edit room's parameters

        @params - new parameters
        """

        self.number = params["number"]
        self.change_kind(params["kind"])
        self.change_capacity(params["capacity"])

    def change_kind(self, kind:str) -> None:
        """
        Safe change room kind

        @kind - room kind
        """

        if kind == self.kind:
            return

        if kind != "s":
            for occupant in self.occupants:
                person = DataBase().get_person(occupant)
                if person.gender != kind:
                    self.remove_occupant(occupant)

        self.kind = kind

    def change_capacity(self, capacity:int) -> None:
        """
        Safe change room capacity

        @capacity - room capacity
        """

        self.space = capacity - len(self.occupants)

        while self.space < 0:
            occupant = self.occupants[-1]
            self.remove_occupant(occupant)

        self.capacity = capacity

    #------------------------------------------------------------------

    def clear_connections(self) -> None:
        """
        Clears room connections for safe deletion
        """

        for occupant in self.occupants:
            self.remove_occupant(occupant)

    #------------------------------------------------------------------
    
    def __init__(self, key:str, number:int, kind:str, capacity:int, occupants:list=[]) -> None:
        """
        Creates new room object

        @key - database key
        @number - room number
        @kind - room kind
        @capacity - room capacity
        @occupants - room occupants (Default empty list)
        """

        super().__init__(key)

        self.properties_to_jsonify = ["key", "number", "kind", "capacity", "occupants"]

        self.number = number
        self.kind = kind
        self.capacity = capacity
        self.occupants = occupants.copy()
        self.space = self.capacity - len(self.occupants)

    #------------------------------------------------------------------


class Person(DataBaseObject):

    #------------------------------------------------------------------

    def edit(self, params):
        """
        Edit occupant's parameters

        @params - new parameters
        """

        self.change_gender(params["gender"])
        self.age = params["age"]
        self.name = params["name"]
        self.phone = params["phone"]
        self.passport = params["passport"]
        
    def change_gender(self, gender):
        """
        Safe change occupant's gender

        @gender - occupant gender
        """

        if self.gender == gender:
            return

        if self.room:            
            room = DataBase().get_room(self.room)
            if room.kind != "s":
                room.remove_occupant(self.key)
            
        self.gender = gender

    #------------------------------------------------------------------

    def change_room(self, key):
        """
        Change the occupant's room

        @key - room database key
        """
        
        old_room = DataBase().get_room(self.room)
        if old_room:
            old_room.remove_occupant(self.key)
        self.room = key
    
    def reset_room(self):
        """
        Reset occupant's room to 0 (int)
        """

        self.room = 0

    #------------------------------------------------------------------

    def clear_connections(self):
        """
        Clears occupant connections for safe deletion
        """

        room = DataBase().get_room(self.room)
        if room:
            room.remove_occupant(self.key)
        self.reset_room()

    #------------------------------------------------------------------

    def __init__(self, key:str, name:str, gender:str, age:int, phone:str, passport:str, room=0):
        super().__init__(key)
        """
        Create new person object

        @key - database key
        @name - occupant name
        @gender - occupant gender
        @age - occupant age
        @phone - occupant phone number
        @passport - occupant identification data (passport)
        @room - occupant's room (Default 0)
        """

        self.properties_to_jsonify = ["key", "room", "name", "gender", "age", "phone", "passport"]

        self.room = room
        self.name = name
        self.gender = gender
        self.age = age
        self.phone = phone
        self.passport = passport

    #------------------------------------------------------------------


class DataBase(metaclass=SingletonMeta):

    FILENAME = "program_data.dat"

    RESERVE = "program_data_copy.dat"

    ELEMENTS = {
        "rooms": Room,
        "persons": Person
    }

    #------------------------------------------------------------------

    def create_data(self, part:str, params:dict) -> None:
        """
        Create database object

        @part - database part, used to specify which object to create
        @params - object parameters
        """

        Element = self.ELEMENTS.get(part)
        new_key = self.get_next_available_key(part)
        new_element = Element(new_key, **params)

        self.push_data(part, new_key, new_element)

    def update_data(self, part:str, key:str, params:dict) -> None:
        """
        Edits the database object

        @part - database part
        @key - database key
        @params - new object parameters
        """

        element = self.db.get(part)[key]
        element.edit(params)

    def delete_data(self, part:str, key:str) -> None:
        """
        Deletes database object

        @part - database part
        @key - database key
        """

        db_part = self.db.get(part)

        element = db_part.get(key)
        element.clear_connections()

        db_part.pop(key)

        keys = self.keys[part]

        keys.append(int(key))
        keys.sort()

    #------------------------------------------------------------------

    def push_data(self, part:str, key:str, value) -> None:
        """
        Save object to the database

        @part - database part
        @key - database key
        @value - database object

        ! Not used outside of database object
        """

        self.db.get(part)[key] = value

    def save_data(self) -> None:
        """
        Saves the database into a file
        """

        with open(self.FILENAME, "wb") as f:
            pickle.dump(self.db, f)

        with open(self.RESERVE, "wb") as f:
            pickle.dump(self.db, f)

    def load_data(self) -> None:
        """
        Loads data from file
        """

        if not os.path.exists(self.FILENAME):
            with open (self.FILENAME, "wb") as nul_file:
                pickle.dump({"rooms": {}, "persons": {}}, nul_file)

        with open(self.FILENAME, "rb") as f:
            database = pickle.load(f)
            self.db = database

            if not self.db.get("password"):
                self.db["password"] = "123b1bf932b8d863f41e07dba383d23d5ff9b54fdfd3d33695f3fe76d861f319"

        self.authorized = False

    def load_keys(self) -> None:
        """
        Loads the unique database keys
        """

        try:
            keys_rooms = tuple(map(int, self.db["rooms"].keys()))
            
            max_key = max(keys_rooms)
        except ValueError:
            self.room_keys = [0]
        else:
            self.room_keys = [key for key in range(max_key+2) if key not in keys_rooms]

        try:
            keys_persons = tuple(map(int, self.db["persons"].keys()))
            max_key = max(keys_persons)
        except ValueError:
            self.person_keys = [0]
        else:
            self.person_keys = [key for key in range(max_key+2) if key not in keys_persons]

        self.keys = {
            "rooms": self.room_keys,
            "persons": self.person_keys
        }

    def check_password(self, password:str) -> bool:
        """
        Checks if the password is correct

        @password - password
        """

        pass_hash = hashlib.sha256(password.encode("UTF-8")).hexdigest()

        if pass_hash == self.get_pass_hash():
            return True

        return False

    def get_pass_hash(self) -> str:
        """
        Returns the password hash from database
        """

        return self.db["password"]

    def set_password(self, password:str):
        """
        Sets new password for the database

        @password - new password
        """

        new_hash = hashlib.sha256(password.encode("UTF-8")).hexdigest()

        self.db["password"] = new_hash

    #------------------------------------------------------------------

    def get_elements(self, name) -> dict:
        """
        Returns specified part of the database

        @name - part name
        """
        
        data = self.db.get(name)

        return data

    def get_room(self, key) -> Room:
        """
        Returns room with a given key

        @key - database key
        """
        
        return self.db["rooms"].get(key)
    
    def get_person(self, key) -> Person:
        """
        Returns person with a given key

        @key - database key
        """
        
        return self.db["persons"].get(key)

    #------------------------------------------------------------------

    def get_next_available_key(self, part:str) -> str:
        """
        Returns next available key for the needed object

        @part - part name

        ! not used outside of database
        """
        keys = self.keys.get(part)

        new_key = keys.pop(0)
        if not keys:
            keys.append(new_key+1)

        return str(new_key)

    #------------------------------------------------------------------

    def __init__(self):
        """
        Initializes the database
        """

        self.load_data()
        self.load_keys()

    #------------------------------------------------------------------

__all__ = [
    "DataBase",
    "Room",
    "Person"
]