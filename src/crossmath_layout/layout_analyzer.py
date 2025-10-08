"""
盘面分析器
"""

from crossmath_layout.models import LayoutBrief
class LayoutAnalyzer:
    """
    盘面分析器
    """
    def __init__(self, layout_info: str, height: int, width: int):
        self.layout_info = layout_info
        self.height = height
        self.width = width

    def analyze_layout(self) -> LayoutBrief:
        """
        分析盘面
        """
        return LayoutBrief(self.layout_info, self.height, self.width)