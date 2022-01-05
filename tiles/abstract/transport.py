from abc import ABC, abstractmethod

from tiles.empty import EmptyTile


class TransportTile(EmptyTile, ABC):

    @abstractmethod
    def get_destination(self, _state, _time, _robot):
        pass  # return((new_x, new_y, new_time))