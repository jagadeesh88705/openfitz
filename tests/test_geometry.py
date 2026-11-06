import pytest
from fitz import Matrix, Point, Rect


def test_point_creation_and_indexing():
    p = Point(10.5, 20.5)
    assert p.x == 10.5
    assert p.y == 20.5
    assert p[0] == 10.5
    assert p[1] == 20.5
    assert len(p) == 2
    x, y = p
    assert (x, y) == (10.5, 20.5)


def test_rect_creation_and_attributes():
    r = Rect(10, 20, 110, 220)
    assert r.x0 == 10.0
    assert r.y0 == 20.0
    assert r.x1 == 110.0
    assert r.y1 == 220.0
    assert r.width == 100.0
    assert r.height == 200.0
    assert r.is_valid is True
    assert r.is_empty is False

    # Tuple unpacking
    x0, y0, x1, y1 = r
    assert (x0, y0, x1, y1) == (10.0, 20.0, 110.0, 220.0)
    assert r[0] == 10.0
    assert r[3] == 220.0


def test_rect_from_tuple_and_points():
    r1 = Rect((15, 25, 115, 225))
    assert r1.x0 == 15.0 and r1.width == 100.0

    p1 = Point(5, 10)
    p2 = Point(55, 110)
    r2 = Rect(p1, p2)
    assert r2.width == 50.0 and r2.height == 100.0


def test_rect_intersections():
    r1 = Rect(0, 0, 100, 100)
    r2 = Rect(50, 50, 150, 150)
    r3 = Rect(200, 200, 300, 300)

    assert r1.intersects(r2) is True
    assert r1.intersects(r3) is False

    inter = r1.intersect(r2)
    assert inter == Rect(50, 50, 100, 100)


def test_matrix():
    m = Matrix(2, 2)
    assert m.a == 2.0
    assert m.d == 2.0
    assert m.b == 0.0
    assert m.c == 0.0
    assert len(m) == 6

