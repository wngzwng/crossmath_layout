from dataclasses import dataclass
from typing import List
from enum import Enum

from crossmath_layout.models import RowCol, Size, Direction


@dataclass
class OuterCircleBlockCount:
    top: int
    bottom: int
    left: int
    right: int

    def to_list(self) -> List[int]:
        return [self.top, self.bottom, self.left, self.right]


@dataclass
class ExtractArg:
    row_col_coord: RowCol
    count: int
    direction: Direction


class CircleBlockCountExtractor:
    def __init__(self):
        pass

    def cal_outer_circle_block_count(self,layout_info: str, height: int, width: int) -> OuterCircleBlockCount:
        """
        计算最外圈用到的格子数
        """
        extract_args = [
            ExtractArg(RowCol(0, 0), width, Direction.HORIZONTAL),
            ExtractArg(RowCol(height - 1, 0), width, Direction.HORIZONTAL),
            ExtractArg(RowCol(0, 0), height, Direction.VERTICAL),
            ExtractArg(RowCol(0, width - 1), height, Direction.VERTICAL),
        ]
        block_count_list = self.extract(layout_info, height, width, extract_args)
        return OuterCircleBlockCount(block_count_list[0], block_count_list[1], block_count_list[2], block_count_list[3])

    def cal_second_outer_circle_block_count(self,layout_info: str, height: int, width: int) -> OuterCircleBlockCount:
        """
        计算次外圈用到的格子数
        """
        extract_args = [
            ExtractArg(RowCol(1, 1), width - 2, Direction.HORIZONTAL),
            ExtractArg(RowCol(height - 2, 1), width - 2, Direction.HORIZONTAL),
            ExtractArg(RowCol(1, 1), height - 2, Direction.VERTICAL),
            ExtractArg(RowCol(1, width - 2), height - 2, Direction.VERTICAL),
        ]
        block_count_list = self.extract(layout_info, height, width, extract_args)
        return OuterCircleBlockCount(block_count_list[0], block_count_list[1], block_count_list[2], block_count_list[3])

    def extract(self, layout_info: str, height: int, width: int, extract_args: List[ExtractArg]) -> List[int]:
        block_count_list = []
        for extract_arg in extract_args:
            block_count_list.append(self._extract_1_count(layout_info, height, width, extract_arg))
        
        return block_count_list

    
    def _extract_1_count(self, layout_info: str, height: int, width: int, extract_arg: ExtractArg) -> int:
        row_col_coord = extract_arg.row_col_coord
        count = extract_arg.count
        direction = extract_arg.direction

        coords = []
        if direction == Direction.HORIZONTAL:
            coords = self.get_horizontal_range_coords(row_col_coord, count, Size(height=height, width=width))
        else:
            coords = self.get_vertical_range_coords(row_col_coord, count, Size(height=height, width=width))
        
        if not coords:
            raise ValueError(f"coords is None, row_col_coord: {row_col_coord}, count: {count}, direction: {direction}, height: {height}, width: {width} \n layout_info: {layout_info}")
        return sum(layout_info[coord.row * width + coord.col] == "1" for coord in coords)


    def is_valid_coord(self, coord: RowCol, size_limit: Size):
        """检查坐标是否有效"""
        return (0 <= coord.row < size_limit.height) and (0 <= coord.col < size_limit.width)

    def get_horizontal_range_coords(self, start_coord: RowCol, count: int, size_limit: Size) -> List[RowCol] | None:
        """获取水平方向坐标范围"""
        # 判断是否越界
        # 行，列坐标
        end_coord = RowCol(start_coord.row, start_coord.col + count - 1)
        if not self.is_valid_coord(start_coord, size_limit) or not self.is_valid_coord(end_coord, size_limit):
            return None
        
        return [
            RowCol(start_coord.row, start_coord.col + i)
            for i in range(count)
        ]

    def get_vertical_range_coords(self, start_coord: RowCol, count: int, size_limit: Size)-> List[RowCol] | None:
        """获取垂直方向坐标范围"""
        # 判断是否越界
        end_coord = RowCol(start_coord.row + count - 1, start_coord.col)
        if not self.is_valid_coord(start_coord, size_limit) or not self.is_valid_coord(end_coord, size_limit):
                return None
        
        return [
            RowCol(start_coord.row + i, start_coord.col)
            for i in range(count)
        ]
