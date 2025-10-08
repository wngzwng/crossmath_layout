"""
盘面放置点生成器
"""

from typing import List, Tuple
from crossmath_layout.models import Placement, Layout, RowCol, Direction
from crossmath_layout.layout_checker import LayoutChecker
from crossmath_layout.equation_layout_builder import EquationLayoutBriefBuilder
from crossmath_layout.utils.viewer import print_board

class PlacementGenerator:
    """
    盘面放置点生成器
    """

    def __init__(self, equation_length: int = 5):
        self.equation_length = equation_length

        self.equation_layout_builder = EquationLayoutBriefBuilder(equation_length=equation_length)
        self.equation_layout_brief = None

        self.layout_checker = LayoutChecker()
        self.board = None 
        self.layout = None
        self.width = None
        self.height = None

        self.is_setup = False

    
    def clear(self):
        self.equation_layout_brief = None
        self.board = None
        self.layout = None
        self.width = None
        self.height = None
        self.is_setup = False

    def setup(self, layout: Layout):
        self.clear()

        if len(layout.layout_info) != (layout.height * layout.width):
            # print("Invalid layout")
            return False
        self.layout = layout
        self.build_board(layout)

        self.equation_layout_brief = self.equation_layout_builder.build_by_layout(layout.layout_info, width=layout.width, height=layout.height)
        if self.equation_layout_brief is None:
            # print("Invalid layout")
            return False
        
        self.is_setup = True
        return True

    def generate_placement(self) -> List[Placement]:
        if not self.is_setup:
            # print("Not setup")
            return []
    
        # 获取所有的放置点，然后判断是否合法
        placements = []
        for equation_start_rowcol, direction in self.get_all_equation_start_rowcol_and_direction():
            # print(equation_start_rowcol, direction)
            for placement in self.get_equation_possible_placements(equation_start_rowcol, direction):
                # print(placement)
                if self.is_valid_placement(placement):
                    placements.append(placement)
        return placements
    
    def generate_placement_iter(self, layout: Layout):
        if self.board is None:
            raise ValueError("Board not built")

    def build_board(self, layout: Layout):
        self.board = [
            [int(layout.layout_info[row * layout.width + col]) for col in range(layout.width)] 
            for row in range(layout.height)
        ]
        self.width = layout.width
        self.height = layout.height

    
    def is_valid_row_col(self, rowCol: RowCol):
        return 0 <= rowCol.row < self.height and 0 <= rowCol.col < self.width 

    def is_valid_placement(self, placement: Placement):
        # 1. 位置不越界  
        start_rowcol = RowCol(placement.row, placement.col)
        end_rowcol = self.get_end_rowcol(placement)
        if not self.is_valid_row_col(start_rowcol) or not self.is_valid_row_col(end_rowcol):
            # print("Invalid rowcol")
            return False
        
        # 2. 首位不与其他算式挨着
        if not self.check_first_and_last_edge(start_rowcol, end_rowcol, placement.direction):
            # print("Invalid first and last edge")
            return False
        
        # 3. 检查焦点位置是否合法
        if not self.check_cross_point(placement):
            # print("Invalid cross point")
            return False
        return True

    def get_end_rowcol(self, placement: Placement):
        offset = (0, 0)
        if placement.direction == Direction.HORIZONTAL:
            offset = (0, self.equation_length - 1)
        elif placement.direction == Direction.VERTICAL:
            offset = (self.equation_length - 1, 0)
        else:
            raise ValueError("Invalid direction")
        return RowCol(placement.row + offset[0], placement.col + offset[1])

    def check_first_and_last_edge(self, start_rowcol: RowCol, end_rowcol: RowCol, direction: Direction):
        # 检查首位边界是否与其他算式挨着
        if direction == Direction.HORIZONTAL:
            if start_rowcol.col != 0 and self.board[start_rowcol.row][start_rowcol.col - 1] != 0:
                return False
            if end_rowcol.col != self.width - 1 and self.board[end_rowcol.row][end_rowcol.col + 1] != 0:
                return False
        elif direction == Direction.VERTICAL:
            if start_rowcol.row != 0 and self.board[start_rowcol.row - 1][start_rowcol.col] != 0:
                return False
            if end_rowcol.row != self.height - 1 and self.board[end_rowcol.row + 1][end_rowcol.col] != 0:
                return False
        return True
        
    def check_cross_point(self, placement: Placement):
        start_rowcol = RowCol(placement.row, placement.col)
        direction = placement.direction
        # 收集焦点位置，判断是否合法
        cross_points = []
        offset = (0, 1) if direction == Direction.HORIZONTAL else (1, 0)
        for i in range(self.equation_length):
            cur_rowcol = RowCol(start_rowcol.row + i * offset[0], start_rowcol.col + i * offset[1])
            if not self.is_valid_row_col(cur_rowcol): # 位置越界，直接返回False
                # print(f"rowcol overflow: {cur_rowcol}")
                return False

            if self.board[cur_rowcol.row][cur_rowcol.col] != 0:
                cross_points.append(cur_rowcol)
       
        # 盘面焦点的数量, 至少一个，至多三个
        cross_count = len(cross_points)
        if cross_count < 1 or cross_count > 3:
            # print(f"cross count error: {cross_count}")
            return False

        # 焦点的位置 
        real_cross_point_ofsets = [
            (cross_point.row - start_rowcol.row, cross_point.col - start_rowcol.col)
            for cross_point in cross_points
        ]
        valid_cross_point_offsets = [(0, 0), (0, 2), (0, 4)] if direction == Direction.HORIZONTAL else [(0, 0), (2, 0), (4, 0)]
        
        if len(set(real_cross_point_ofsets) - set(valid_cross_point_offsets)) != 0: # 存在不合法的焦点位置
            # print(f"Invalid cross point offsets: {real_cross_point_ofsets} - {valid_cross_point_offsets}")
            return False  
        return True
       
    def get_equation_possible_placements(self, equation_start_rowcol: RowCol, direction: Direction):
        if direction == Direction.HORIZONTAL:
            possible_rowcol_offset = [
                (0, 0),  (0, 2), (0, 4),
                (-2, 0), (-2, 2), (-2, 4),
                (-4, 0), (-4, 2), (-4, 4),
            ]
        elif direction == Direction.VERTICAL:
            possible_rowcol_offset = [
                (0, 0), (0, -2), (0, -4),
                (2, 0), (2, -2), (2, -4),
                (4, 0), (4, -2), (4, -4),
            ]
        else:
            raise ValueError("Invalid direction")

        real_valid_rowcol = []
        for rowcol_offset in possible_rowcol_offset:
            new_rowcol = RowCol(equation_start_rowcol.row + rowcol_offset[0], equation_start_rowcol.col + rowcol_offset[1])
            if self.is_valid_row_col(new_rowcol):
                real_valid_rowcol.append(new_rowcol)
        
        # # print(real_valid_rowcol, direction.reverse())
        return [Placement(rowcol.row, rowcol.col, direction.reverse()) for rowcol in real_valid_rowcol]

    def get_all_equation_start_rowcol_and_direction(self) -> List[Tuple[RowCol, Direction]]:
        if not self.is_setup:
            # print("Not setup")
            raise ValueError("Not setup")
            # return []
        
        def get_equation_direction(coords: List[RowCol]) -> Direction:
            if coords[0].row == coords[1].row:
                return Direction.HORIZONTAL
            elif coords[0].col == coords[1].col:
                return Direction.VERTICAL
            else:
                raise ValueError("Invalid coords")
        
        equation_start_rowcol_and_direction = []
        for coords in self.equation_layout_brief.equation_id_to_coords.values():
            sorted_coords = sorted(coords, key=lambda x: (x.row, x.col))
            equation_start_rowcol_and_direction.append((sorted_coords[0], get_equation_direction(sorted_coords)))
        return equation_start_rowcol_and_direction
        

if __name__ == "__main__":
    layout = Layout(layout_info="111110000101010000101011111101010000111110000000000000000000000000000000000000000000000000000000000", height=11, width=9)
    print_board(layout.layout_info, layout.width, layout.height)
    placement_generator = PlacementGenerator()
    print(placement_generator.setup(layout))

    print(f"\n{placement_generator.generate_placement()}\n")
    print_board(layout.layout_info, layout.width, layout.height)