from abc import ABC, abstractmethod

from tiles.empty import EmptyTile


class TransportTile(EmptyTile, ABC):
    @abstractmethod
    def get_destinations(self, _state, _robot):
        pass  # return [(new_x, new_y, new_time), ...]
