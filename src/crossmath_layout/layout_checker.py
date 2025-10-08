"""
检查面板是否合法, 比如是否连通, 是否只有一个连通区域, 是否只有0和1组成, 是否符合棋盘尺寸

检查步骤：
    1. 检查面板是否只有0和1组成
    2. 检查面板是否符合棋盘尺寸
    3. 检查面板是否连通
    4. 检查面板是否只有一个连通区域

"""

from dataclasses import dataclass
from typing import Dict, Set
from collections import defaultdict, deque

from crossmath_layout.equation_layout_builder import EquationLayoutBriefBuilder
from crossmath_layout.circle_block_count_extractor import CircleBlockCountExtractor
from crossmath_layout.models import RowCol
from crossmath_layout.cross_point_analyzer import CrossPointAnalyzer, CrossPointAnalysisResult, EquationCrossType
from crossmath_layout.utils.viewer import print_board

@dataclass
class LayoutResult:
    is_valid: bool
    error_message: str = ""
    formula_count: int = 0

class LayoutChecker:
    def __init__(self):
        self.equation_layout_brief_builder = EquationLayoutBriefBuilder(equation_length=5)
        self.equation_layout_brief = None

        self.cross_point_analyzer = CrossPointAnalyzer()
        self.circle_block_count_extractor = CircleBlockCountExtractor()

        self.coord_to_equation_ids: Dict[RowCol, Set[int]] = defaultdict(set)
        self.equation_id_to_coords: Dict[int, Set[RowCol]] = defaultdict(set)

        self.layout_info: str = None
        self.width: int = None
        self.height: int = None

    def clear(self):
        self.equation_layout_brief = None
        self.coord_to_equation_ids.clear()
        self.equation_id_to_coords.clear()

    
    def setup(self, layout_info: str, width: int, height: int) -> bool:
        self.clear()
        self.equation_layout_brief = self.equation_layout_brief_builder.build_by_layout(layout_info, width, height)
        if not self.equation_layout_brief:
            return False
        self.coord_to_equation_ids = self.equation_layout_brief.coord_to_equation_ids
        self.equation_id_to_coords = self.equation_layout_brief.equation_id_to_coords
        self.layout_info = layout_info
        self.width = width
        self.height = height

        self.cross_point_analyzer.setup(self.equation_id_to_coords)
        return True

    def check(self) -> LayoutResult:
        if not self._check_connected(self.layout_info, self.width, self.height):
            return LayoutResult(is_valid=False, error_message="面板不连通")
        
        if not self._check_cross_point():
            return LayoutResult(is_valid=False, error_message="面板有非法交叉点")

        if not self._check_puzzle_shape():
            return LayoutResult(is_valid=False, error_message="盘面形状不合法")

        if not self._check_size():
            return LayoutResult(is_valid=False, error_message="盘面尺寸不合法, 最外围有不存在格子")
    
        return LayoutResult(is_valid=True, formula_count=len(self.equation_id_to_coords.keys()))

    def _check_size(self):
        """
        检查盘面尺寸是否合法
        即查看盘面最外围是否有格子，没有格子说明边界不合法
        """
        circle_block_count = self.circle_block_count_extractor.cal_outer_circle_block_count(self.layout_info, self.height, self.width)
        if circle_block_count.top == 0 or circle_block_count.bottom == 0 or circle_block_count.left == 0 or circle_block_count.right == 0:
            return False
        return True


    def _check_puzzle_shape(self) -> bool:
        """检查盘面形状是否合法"""
        """ 去除这种面板 (0, 2) 与 (0, 3) 这块有问题
        0  1  2  3  4  5  6  7  8  9  10 11 12 13 14
        0      □  □                 □                  
        1         □                 □                  
        2   □  □  □  □  □           □  □  □  □  □     □
        3   □     □     □           □           □     □
        4   □     □     □  □  □  □  □     □  □  □  □  □
        5   □           □     □           □     □     □
        6   □           □     □     □  □  □  □  □     □
        7                     □           □            
        8   □  □  □  □  □     □     □  □  □  □  □     □
        9   □     □     □           □           □     □
        10  □     □  □  □  □  □     □  □  □  □  □     □
        11  □     □     □     □     □     □     □     □
        12  □     □     □  □  □  □  □     □  □  □  □  □
        13                    □           □            
        14        □  □  □  □  □     □  □  □  □  □      
        """
        all_valid_coords = set()
        for equation_id in self.equation_id_to_coords.keys():
            all_valid_coords.update(self.equation_id_to_coords[equation_id])
        
        if len(all_valid_coords) != self._find_all_one_count(self.layout_info):
            return False
        return True


    def _check_cross_point(self, check_none_cross_point: bool = True) -> bool:
        all_cross_points = self.cross_point_analyzer.get_all_cross_points()
        if len(all_cross_points) == 0 and check_none_cross_point:
            return False

        for cross_point in all_cross_points:
            cross_point_result = self.cross_point_analyzer.analyze_cross_point(cross_point)
            if cross_point_result is None:
                return False
            
            if cross_point_result.cross_type == EquationCrossType.NONE:
                return False
        return True

    def _check_connected(self, layout_info: str, width: int, height: int) -> bool:
        try:
            connected_ones_count = self._find_and_count_connected_ones(layout_info, width, height)
            all_one_count = self._find_all_one_count(layout_info)
            return connected_ones_count == all_one_count
        except Exception as e:
            return False
    
    def _check_only_0_and_1(self, layout_info: str) -> bool:
        return all(value == "0" or value == "1" for value in layout_info)
    
        
    def _find_all_one_count(self,layout_info: str) -> int:
        return layout_info.count('1')

    def _find_and_count_connected_ones(self, layout_info: str, width: int, height: int) -> int:
        """
        将01字符串转换为width×height的矩阵，找到第一个1，统计所有与之相连的1的数量（仅上下左右连通）
        
        :param layout_info: 盘面结构字符串，长度应为width*height
        :param width: 棋盘宽度
        :param height: 棋盘高度
        :param height: 矩阵高度（行数）
        :return: 连通区域中1的数量
        """ 
        # 验证输入
        if len(layout_info) != width * height:
            raise ValueError(f"字符串长度必须为{width*height}，当前长度为{len(layout_info)}")
        
        if not self._check_only_0_and_1(layout_info):
            raise ValueError("字符串只能包含0和1")
        
        # 将字符串转换为矩阵（行优先）
        matrix = [
            [int(layout_info[i * width + j]) for j in range(width)]
            for i in range(height)  
        ]
        
        # 定义4个移动方向（上、下、左、右）
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        # 找到第一个1的位置（行优先遍历）
        first_one = next(
            ((i, j) for i in range(height) for j in range(width) if matrix[i][j] == 1),
            None
        )
        
        if first_one is None:
            return 0  # 矩阵中没有1
        
        # 使用BFS遍历连通区域
        visited = [[False for _ in range(width)] for _ in range(height)]
        queue = deque([first_one])
        visited[first_one[0]][first_one[1]] = True
        count = 0
        
        while queue:
            x, y = queue.popleft()
            count += 1
            
            # 检查4个相邻位置
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < height and 0 <= ny < width:
                    # 检查是否越界
                    if not visited[nx][ny] and matrix[nx][ny] == 1:
                        visited[nx][ny] = True
                        queue.append((nx, ny))
        
        return count



def test(layout_info: str, width: int, height: int):
    layout_checker = LayoutChecker()
    if not layout_checker.setup(layout_info, width, height):
        raise ValueError("setup failed")
    layout_result = layout_checker.check()
    print(layout_result)

if __name__ == "__main__":
    layout_info = "111110000101010000101011111101010000111110000000000000000000000000000000000000000000000000000000000"
    print_board(layout_info, width=9, height=11)
    test("111110000101010000101011111101010000111110000000000000000000000000000000000000000000000000000000000", width=9, height=11)