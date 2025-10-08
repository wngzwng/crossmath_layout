
from enum import Enum
from typing import NamedTuple, Tuple

from dataclasses import dataclass, field
from typing import Dict, Set, List
from collections import defaultdict


class Size(NamedTuple):
    """
    盘面大小
    """
    height: int
    width: int

    def to_tuple(self):
        return (self.height, self.width)

    def from_tuple(self, tuple: Tuple[int, int]):
        return Size(tuple[0], tuple[1])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Size):
            return False
        return self.height == other.height and self.width == other.width

    def __repr__(self):
        return f"Size(height={self.height}, width={self.width})"

class RowCol(NamedTuple):
    """
    行列坐标
    """
    row: int
    col: int

    def to_tuple(self):
        return (self.row, self.col)

    def from_tuple(self, tuple: Tuple[int, int]):
        return RowCol(tuple[0], tuple[1])
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RowCol):
            return False
        return self.row == other.row and self.col == other.col

    def __repr__(self):
        return f"RowCol(row={self.row}, col={self.col})"

class Direction(Enum):
    """
    方向
    """
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

    def __repr__(self):
        return self.value 
    
    def reverse(self):
        """返回相反方向"""
        return Direction.VERTICAL if self == Direction.HORIZONTAL else Direction.HORIZONTAL

class Placement(NamedTuple):
    """
    放置点 (row, col, direction)
    """
    row: int
    col: int
    direction: Direction

    def to_tuple(self):
        return (self.row, self.col, self.direction)

    def from_tuple(self, tuple: Tuple[int, int, Direction]):
        return Placement(tuple[0], tuple[1], tuple[2])

    def from_RowCol(self, rowCol: RowCol, direction: Direction):
        return Placement(rowCol.row, rowCol.col, direction)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Placement):
            return False
        return self.row == other.row and self.col == other.col and self.direction == other.direction

    def __repr__(self):
        return f"Placement(row={self.row}, col={self.col}, direction={self.direction})"



@dataclass
class EquationLayoutBrief:
    """算式布局简要信息"""
    layout_info: str
    """布局信息"""
    
    size: Size
    """大小规格"""
    
    coord_to_equation_ids: Dict[RowCol, Set[int]] = field(
        default_factory=lambda: defaultdict(set)
    )
    """坐标到算式ID集合的映射"""
    
    equation_id_to_coords: Dict[int, Set[RowCol]] = field(
        default_factory=lambda: defaultdict(set)
    )
    """算式ID到坐标集合的映射"""

    all_valid_coords: List[RowCol] = field(
        default_factory=lambda: []
    )
    """所有有效坐标"""

@dataclass
class Layout:
    """
    盘面信息
    """
    layout_info: str
    height: int
    width: int

@dataclass
class LayoutBrief:
    """
    盘面简要信息
    """
    layout_info: str 
    size: Size
    cell_count: int
    cross_point_count: int
    equation_count: int
    ring_count: int
    sigma_value: float
    center_of_mass: RowCol

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LayoutBrief):
            return False
        return self.layout_info == other.layout_info


    def __repr__(self):
        return f"LayoutBrief(layout_info={self.layout_info}, size={self.size}, cell_count={self.cell_count}, cross_point_count={self.cross_point_count}, equation_count={self.equation_count}, ring_count={self.ring_count}, sigma_value={self.sigma_value}, center_of_mass={self.center_of_mass})"