from typing import Dict, Set, List
from crossmath_layout.models import RowCol, Size, EquationLayoutBrief

class EquationLayoutBriefBuilder:
    """算式布局简要信息构建器"""
    def __init__(self, width: int = None, height: int = None, equation_length: int = 5):
        self.width = None 
        self.height = None 
        self.equation_length = equation_length

    def build_by_layout(self, layout_info: str, width: int, height: int) -> EquationLayoutBrief | None:
        """根据布局信息构建EquationLayoutBrief"""
        width = width or self.width
        height = height or self.height
        equation_length = self.equation_length

        if (width is None) or (height is None) or (layout_info is None) or (len(layout_info) != (width * height)):
            return None 

        def update(coords: List[RowCol], equation_id: int, equation_id_to_coords: Dict[int, Set[RowCol]], coord_to_equation_ids: Dict[RowCol, Set[int]]):
            if not coords:
                return False

            if all(value == "1" for value in map(lambda coord: layout_info[coord.row * width + coord.col], coords)):
                equation_id_to_coords[equation_id] = set(coords)
                for coord in coords:
                    coord_to_equation_ids[coord].add(equation_id)
                return True

            return False
    
        size_limit = Size(width=width, height=height)
        equation_layout_brief = EquationLayoutBrief(layout_info=layout_info, size=size_limit, all_valid_coords=self.get_all_valid_coords(layout_info, size_limit))

        equation_id_to_coords = equation_layout_brief.equation_id_to_coords
        coord_to_equation_ids = equation_layout_brief.coord_to_equation_ids

        current_equation_id = 1
        for row in range(height):
            for col in range(width):
                start_coord = RowCol(row, col)
                # 横向算式收集
                if (horizontal_equation_coords := self.get_horizontal_range_coords(start_coord, equation_length, size_limit)):
                    if update(horizontal_equation_coords, current_equation_id, equation_id_to_coords, coord_to_equation_ids):
                        current_equation_id += 1
                # 纵向算式收集
                if (vertical_equation_coords := self.get_vertical_range_coords(start_coord, equation_length, size_limit)):
                    if update(vertical_equation_coords, current_equation_id, equation_id_to_coords, coord_to_equation_ids):
                        current_equation_id += 1

        return equation_layout_brief
    
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

    def get_all_valid_coords(self, layout_info: str, size_limit: Size) -> List[RowCol]:
        """获取所有有效坐标"""
        if not layout_info or len(layout_info) != size_limit.width * size_limit.height:
            return []
    
        return [
            RowCol(row, col)
            for row in range(size_limit.height)
            for col in range(size_limit.width)
            if layout_info[row * size_limit.width + col] == "1"
        ]
