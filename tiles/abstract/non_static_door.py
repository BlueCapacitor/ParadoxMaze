from abc import ABC, abstractmethod

from tiles.empty import EmptyTile


class NonStaticDoorTile(EmptyTile, ABC):
    is_static = False

    @abstractmethod
    def look(self, _state, _time):
        pass  # return(control_value, looks_open_on_value)

    @abstractmethod
    def crash_look(self, _state, _time):
        pass  # return(control_value, open_on_value)