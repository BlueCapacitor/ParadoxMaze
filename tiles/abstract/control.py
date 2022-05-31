from abc import ABC, abstractmethod

from tiles.empty import EmptyTile


class ControlTile(EmptyTile, ABC):

    @abstractmethod
    def trigger(self, _state, _time):
        pass
