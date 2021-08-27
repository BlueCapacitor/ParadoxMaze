from typing import NewType

Time = NewType("Time", int)
PCoord = NewType("PCoord", int)
PCoords = NewType("PCoords", tuple[PCoord, PCoord])
Coords = NewType("Coords", tuple[PCoord, PCoord, Time])

Color = NewType("Color", list[float])

ControlID = NewType("ControlID", int)
