"""Geometry classes: Point, Rect, and Matrix."""

from __future__ import annotations
from typing import Any, Iterator, Sequence, Tuple, Union


class Point:
    """Represents a 2D point (x, y)."""

    def __init__(self, *args: Any):
        if len(args) == 2:
            self.x = float(args[0])
            self.y = float(args[1])
        elif len(args) == 1:
            val = args[0]
            if isinstance(val, (Point, tuple, list)):
                self.x = float(val[0])
                self.y = float(val[1])
            else:
                raise TypeError(f"Cannot initialize Point from {type(val)}")
        elif len(args) == 0:
            self.x = 0.0
            self.y = 0.0
        else:
            raise TypeError(f"Point takes at most 2 arguments, got {len(args)}")

    def __getitem__(self, idx: int) -> float:
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        raise IndexError("Point index out of range (must be 0 or 1)")

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, (Point, tuple, list)) and len(other) == 2:
            return abs(self.x - other[0]) < 1e-6 and abs(self.y - other[1]) < 1e-6
        return False


class Rect:
    """Represents a rectangle (x0, y0, x1, y1) in top-left coordinate system."""

    def __init__(self, *args: Any):
        if len(args) == 4:
            self.x0 = float(args[0])
            self.y0 = float(args[1])
            self.x1 = float(args[2])
            self.y1 = float(args[3])
        elif len(args) == 2:
            p0, p1 = Point(args[0]), Point(args[1])
            self.x0 = min(p0.x, p1.x)
            self.y0 = min(p0.y, p1.y)
            self.x1 = max(p0.x, p1.x)
            self.y1 = max(p0.y, p1.y)
        elif len(args) == 1:
            val = args[0]
            if isinstance(val, (Rect, tuple, list)) and len(val) == 4:
                self.x0 = float(val[0])
                self.y0 = float(val[1])
                self.x1 = float(val[2])
                self.y1 = float(val[3])
            else:
                raise TypeError(f"Cannot initialize Rect from {val}")
        elif len(args) == 0:
            self.x0 = self.y0 = self.x1 = self.y1 = 0.0
        else:
            raise TypeError(f"Rect takes 0, 1, 2, or 4 arguments, got {len(args)}")

    @property
    def width(self) -> float:
        return max(0.0, self.x1 - self.x0)

    @property
    def height(self) -> float:
        return max(0.0, self.y1 - self.y0)

    @property
    def top_left(self) -> Point:
        return Point(self.x0, self.y0)

    @property
    def bottom_right(self) -> Point:
        return Point(self.x1, self.y1)

    @property
    def top_right(self) -> Point:
        return Point(self.x1, self.y0)

    @property
    def bottom_left(self) -> Point:
        return Point(self.x0, self.y1)

    @property
    def is_empty(self) -> bool:
        return self.x0 >= self.x1 or self.y0 >= self.y1

    @property
    def is_valid(self) -> bool:
        return self.x0 <= self.x1 and self.y0 <= self.y1

    def normalize(self) -> Rect:
        """Ensures x0 <= x1 and y0 <= y1."""
        if self.x0 > self.x1:
            self.x0, self.x1 = self.x1, self.x0
        if self.y0 > self.y1:
            self.y0, self.y1 = self.y1, self.y0
        return self

    def intersects(self, other: Union[Rect, Sequence[float]]) -> bool:
        """Returns True if this rect intersects with another."""
        o = Rect(other)
        return not (self.x1 <= o.x0 or self.x0 >= o.x1 or self.y1 <= o.y0 or self.y0 >= o.y1)

    def intersect(self, other: Union[Rect, Sequence[float]]) -> Rect:
        """Returns the intersection of two rectangles."""
        o = Rect(other)
        if not self.intersects(o):
            return Rect(0, 0, 0, 0)
        return Rect(
            max(self.x0, o.x0),
            max(self.y0, o.y0),
            min(self.x1, o.x1),
            min(self.y1, o.y1)
        )

    def include_rect(self, other: Union[Rect, Sequence[float]]) -> Rect:
        """Expands this rectangle to include another rectangle."""
        o = Rect(other)
        if self.is_empty:
            self.x0, self.y0, self.x1, self.y1 = o.x0, o.y0, o.x1, o.y1
        elif not o.is_empty:
            self.x0 = min(self.x0, o.x0)
            self.y0 = min(self.y0, o.y0)
            self.x1 = max(self.x1, o.x1)
            self.y1 = max(self.y1, o.y1)
        return self

    def include_point(self, point: Union[Point, Sequence[float]]) -> Rect:
        """Expands this rectangle to include a point."""
        p = Point(point)
        if self.is_empty:
            self.x0 = self.x1 = p.x
            self.y0 = self.y1 = p.y
        else:
            self.x0 = min(self.x0, p.x)
            self.y0 = min(self.y0, p.y)
            self.x1 = max(self.x1, p.x)
            self.y1 = max(self.y1, p.y)
        return self

    def __getitem__(self, idx: int) -> float:
        coords = (self.x0, self.y0, self.x1, self.y1)
        return coords[idx]

    def __len__(self) -> int:
        return 4

    def __iter__(self) -> Iterator[float]:
        yield self.x0
        yield self.y0
        yield self.x1
        yield self.y1

    def __repr__(self) -> str:
        return f"Rect({self.x0}, {self.y0}, {self.x1}, {self.y1})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, (Rect, tuple, list)) and len(other) == 4:
            return all(abs(self[i] - other[i]) < 1e-4 for i in range(4))
        return False


class Matrix:
    """Represents a 2D affine transformation matrix [a, b, c, d, e, f]."""

    def __init__(self, *args: Any):
        if len(args) == 6:
            self.a = float(args[0])
            self.b = float(args[1])
            self.c = float(args[2])
            self.d = float(args[3])
            self.e = float(args[4])
            self.f = float(args[5])
        elif len(args) == 2:
            # zoom_x, zoom_y
            self.a = float(args[0])
            self.b = 0.0
            self.c = 0.0
            self.d = float(args[1])
            self.e = 0.0
            self.f = 0.0
        elif len(args) == 1:
            val = args[0]
            if isinstance(val, (Matrix, tuple, list)) and len(val) == 6:
                self.a, self.b, self.c, self.d, self.e, self.f = (float(x) for x in val)
            elif isinstance(val, (int, float)):
                # uniform scale
                self.a = self.d = float(val)
                self.b = self.c = self.e = self.f = 0.0
            else:
                raise TypeError(f"Cannot initialize Matrix from {val}")
        elif len(args) == 0:
            # Identity matrix
            self.a = self.d = 1.0
            self.b = self.c = self.e = self.f = 0.0
        else:
            raise TypeError(f"Matrix takes 0, 1, 2, or 6 arguments, got {len(args)}")

    def __getitem__(self, idx: int) -> float:
        values = (self.a, self.b, self.c, self.d, self.e, self.f)
        return values[idx]

    def __len__(self) -> int:
        return 6

    def __iter__(self) -> Iterator[float]:
        yield self.a
        yield self.b
        yield self.c
        yield self.d
        yield self.e
        yield self.f

    def __repr__(self) -> str:
        return f"Matrix({self.a}, {self.b}, {self.c}, {self.d}, {self.e}, {self.f})"

