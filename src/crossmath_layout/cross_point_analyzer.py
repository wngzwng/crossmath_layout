"""
交点格子分析器
用于分析算式中交点格子的类型
"""

from dataclasses import dataclass
from typing import Dict, Set, Tuple, Optional
from collections import defaultdict
from enum import Enum

from crossmath_layout.models import RowCol


class CrossPointType(Enum):
    """交点类型枚举"""
    NONE = 0
    HEAD = 1    # 起点
    MIDDLE = 2  # 中间点
    TAIL = 3    # 终点


class EquationCrossType(Enum):
    """算式交叉类型枚举"""
    NONE = 0
    HEAD_TO_HEAD = 1
    HEAD_TO_MIDDLE = 2
    HEAD_TO_TAIL = 3
    TAIL_TO_HEAD = 4
    TAIL_TO_MIDDLE = 5
    TAIL_TO_TAIL = 6
    MIDDLE_TO_HEAD = 7
    MIDDLE_TO_MIDDLE = 8
    MIDDLE_TO_TAIL = 9

    @staticmethod
    def is_point_to_point(cross_type: "EquationCrossType") -> bool:
        """判断是否是端点对端点的交叉类型"""
        return cross_type in [
            EquationCrossType.HEAD_TO_HEAD,
            EquationCrossType.TAIL_TO_HEAD,
            EquationCrossType.HEAD_TO_TAIL,
            EquationCrossType.TAIL_TO_TAIL
        ]

    @staticmethod
    def is_point_to_middle(cross_type: "EquationCrossType") -> bool:
        """判断是否是端点对中间点的交叉类型"""
        return cross_type in [
            EquationCrossType.HEAD_TO_MIDDLE,
            EquationCrossType.TAIL_TO_MIDDLE,
            EquationCrossType.MIDDLE_TO_HEAD,
            EquationCrossType.MIDDLE_TO_TAIL
        ]

    @staticmethod
    def is_middle_to_middle(cross_type: "EquationCrossType") -> bool:
        """判断是否是中间点对中间点的交叉类型"""
        return cross_type == EquationCrossType.MIDDLE_TO_MIDDLE


@dataclass
class CrossPointAnalysisResult:
    """交点分析结果"""
    coord: RowCol
    equation_ids: Tuple[int, int]
    point_types: Tuple[CrossPointType, CrossPointType]
    cross_type: EquationCrossType


class CrossPointAnalyzer:
    """交点格子分析器"""
    def __init__(self):
        """
        初始化分析器
        :param equation_id_to_coords: 算式ID到坐标集合的映射
        """
        self.equation_id_to_coords = None
        self.coord_to_equation_ids = None 

    def setup(self, equation_id_to_coords: Dict[int, Set[RowCol]]):
        self.equation_id_to_coords = equation_id_to_coords
        self._build_coord_to_equation_ids()

    def _build_coord_to_equation_ids(self):
        """构建坐标到算式ID的映射"""
        self.coord_to_equation_ids = defaultdict(set)
        for equation_id, coords in self.equation_id_to_coords.items():
            for coord in coords:
                self.coord_to_equation_ids[coord].add(equation_id)

    def get_all_cross_points(self) -> Dict[RowCol, Set[int]]:
        """获取所有交点格子及其对应的算式ID集合"""
        return {coord: eq_ids for coord, eq_ids in self.coord_to_equation_ids.items() 
                if len(eq_ids) > 1}

    def analyze_cross_point(self, coord: RowCol) -> Optional[CrossPointAnalysisResult]:
        """
        分析单个交点格子
        :param coord: 要分析的坐标
        :return: 交点分析结果，如果不是交点则返回None
        """
        equation_ids = self.coord_to_equation_ids.get(coord, set())
        if len(equation_ids) != 2:  # 最多只有两个算式相交
            return None

        # 取前两个算式进行分析
        equation_id1, equation_id2 = sorted(equation_ids)[:2]
        point_type1 = self._get_point_type(equation_id1, coord)
        point_type2 = self._get_point_type(equation_id2, coord)
        cross_type = self._determine_cross_type(point_type1, point_type2)

        return CrossPointAnalysisResult(
            coord=coord,
            equation_ids=(equation_id1, equation_id2),
            point_types=(point_type1, point_type2),
            cross_type=cross_type
        )

    def _get_point_type(self, equation_id: int, coord: RowCol) -> CrossPointType:
        """获取坐标在算式中的位置类型"""
        sorted_coords = sorted(self.equation_id_to_coords[equation_id])
        index = sorted_coords.index(coord)

        if index == 0:
            return CrossPointType.HEAD
        elif index == len(sorted_coords) - 1:
            return CrossPointType.TAIL
        elif index == 2:  # 假设中间点是第三个点
            return CrossPointType.MIDDLE
        return CrossPointType.NONE

    def _determine_cross_type(self, type1: CrossPointType, type2: CrossPointType) -> EquationCrossType:
        """根据两个点的类型确定交叉类型"""
        cross_type_map = {
            (CrossPointType.HEAD, CrossPointType.HEAD): EquationCrossType.HEAD_TO_HEAD,
            (CrossPointType.HEAD, CrossPointType.MIDDLE): EquationCrossType.HEAD_TO_MIDDLE,
            (CrossPointType.HEAD, CrossPointType.TAIL): EquationCrossType.HEAD_TO_TAIL,
            (CrossPointType.TAIL, CrossPointType.HEAD): EquationCrossType.TAIL_TO_HEAD,
            (CrossPointType.TAIL, CrossPointType.MIDDLE): EquationCrossType.TAIL_TO_MIDDLE,
            (CrossPointType.TAIL, CrossPointType.TAIL): EquationCrossType.TAIL_TO_TAIL,
            (CrossPointType.MIDDLE, CrossPointType.HEAD): EquationCrossType.MIDDLE_TO_HEAD,
            (CrossPointType.MIDDLE, CrossPointType.MIDDLE): EquationCrossType.MIDDLE_TO_MIDDLE,
            (CrossPointType.MIDDLE, CrossPointType.TAIL): EquationCrossType.MIDDLE_TO_TAIL,
        }
        return cross_type_map.get((type1, type2), EquationCrossType.NONE)