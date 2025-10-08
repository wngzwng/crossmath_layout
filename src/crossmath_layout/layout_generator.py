from typing import Set, Generator
import time

from crossmath_layout.placement_generator import PlacementGenerator
from crossmath_layout.circle_block_count_extractor import CircleBlockCountExtractor, OuterCircleBlockCount
from crossmath_layout.models import Layout, Placement, Direction, Size
from crossmath_layout.utils.viewer import print_board
from crossmath_layout.layout_checker import LayoutChecker
from crossmath_layout.utils.time_formatter import TimeFormatter
from crossmath_layout.utils.dynamic_total_progress import DynamicTotalProgress



class LayoutGenerator:
    """
    盘面生成器
    """
    def __init__(self, equation_length: int = 5):
        self.equation_length = equation_length
        self.placement_generator = PlacementGenerator(equation_length=equation_length)
        self.circle_block_count_extractor = CircleBlockCountExtractor()
        self.layout_checker = LayoutChecker()

        self.count = 0
        self.pbar = None

    def generate_layout(self, size: Size, progress: bool = False) -> Generator[Layout, None, None]:
        self.count = 0
        placements = self.get_init_placements(size)
        seen_layouts = set()
        if progress:
            self.pbar = DynamicTotalProgress(desc=f"Generating layout for {size.height}*{size.width}", chunk_size=1000) 
            self.pbar.update(0)

        for placement in placements:
            layout = Layout(layout_info="0" * size.height * size.width, height=size.height, width=size.width)
            layout = self.apply_placement(layout, placement, check_valid=False)
            before_count = self.count
            yield from self.iter_dfs_generate_layout(layout, seen_layouts)
            after_count = self.count
            print(f"size: {size.height}*{size.width}, placement: {placement}, update count: {after_count - before_count}, current count: {self.count}")
          
        if progress and self.pbar is not None:
            self.pbar.close()
            self.pbar = None
    
    def iter_dfs_generate_layout(self, layout: Layout, seen_layouts: Set[str]) -> Generator[Layout, None, None]:
        # 检查是否已经处理过 
        if layout.layout_info in seen_layouts:
            return
        seen_layouts.add(layout.layout_info)

        # 检查是否成为合法盘面
        if self.is_valid_layout(layout):
            self.count += 1
            if self.pbar is not None:
                self.pbar.update(1)
            yield layout
        
        if not self.placement_generator.setup(layout):
            return

        # 生成放置点
        placements = self.placement_generator.generate_placement()
        for placement in placements:
            new_layout = self.apply_placement(layout, placement)
            yield from self.iter_dfs_generate_layout(new_layout, seen_layouts)
    
    def get_init_placements(self, size: Size):
        # 只生成首行的情况
        placements = []
        # # 横着 移动列
        # for col in range(0, size.width -  self.equation_length + 1, 2):
        #     placements.append(Placement(0, col, Direction.HORIZONTAL))
        # # 竖着 移动行
        # for row in range(0, size.height -  self.equation_length + 1, 2):
        #     placements.append(Placement(row, 0, Direction.VERTICAL))

            # 在首行的横的算式
        for col in range(0, size.width -  self.equation_length + 1, 2):
            placements.append(Placement(0, col, Direction.HORIZONTAL))

        # 在首行的竖的算式
        for col in range(0, size.width, 2):
            placements.append(Placement(0, col, Direction.VERTICAL))

        return placements

    def apply_placement(self, layout: Layout, placement: Placement, check_valid: bool = True):
        offset = (0, 1) if placement.direction == Direction.HORIZONTAL else (1, 0)
        set_one_points = [
            (placement.row + i * offset[0], placement.col + i * offset[1])
            for i in range(self.equation_length)
        ]
        layout_info = list(layout.layout_info)
        for point in set_one_points:
            layout_info[point[0] * layout.width + point[1]] = "1"

        if check_valid:
            if not self.layout_checker.setup(layout.layout_info, width=layout.width, height=layout.height):
                print(f"layout checker setup failed: {layout.layout_info}")
                print_board(layout.layout_info, width=layout.width, height=layout.height)
                input("按回车键继续...")
            else:
                if not self.layout_checker._check_cross_point(check_none_cross_point=False):
                    print("Invalid cross point")
                    print(f"orignal layout: {layout.layout_info}")
                    print(f"placement: {placement}")
                    print_board(layout.layout_info, width=layout.width, height=layout.height)
                    input("按回车键继续...")

        return Layout(layout_info="".join(layout_info), height=layout.height, width=layout.width)


    def is_valid_layout(self, layout: Layout):
        # 四周都有值
        outer_circle_block_count: OuterCircleBlockCount = self.circle_block_count_extractor.cal_outer_circle_block_count(layout.layout_info, layout.height, layout.width)
        return all(count > 0 for count in outer_circle_block_count.to_list())



def build_empty_layout(height: int, width: int) -> Layout:
    return Layout(layout_info="0" * height * width, height=height, width=width)


if __name__ == "__main__":
    layout_generator = LayoutGenerator()

    result_map = {}
    size_list = [
        (5, 5),
        (7, 5),
        (7, 7),
        (9, 7),
        (9, 9),
        # (11, 9),
        # (11, 11),
        # (13, 11),
        # (13, 13),
        # (15, 13),
        # (15, 15),
    ]
    for height, width in size_list:
        start_time = time.time()
        # print(f"start time: {time.ctime(start_time)}")  # 自动转换为可读格式
        count = sum(1 for _ in layout_generator.generate_layout(Size(height=height, width=width)))
        end_time = time.time()
        # print(f"end time: {time.ctime(end_time)}")
        # print(f"{height}*{width}: {count} Time: {end_time - start_time} seconds")
        result_map[f"{height}*{width}"] = (count, TimeFormatter.format(end_time - start_time, digits=3))

    for size, (count, time) in result_map.items():
        print(f"{size}: {count} Time: {time}")

    # layout_generator.count = 0
    # init_layout = layout_generator.apply_placement(build_empty_layout(11, 9), Placement(row=0, col=0, direction=Direction.HORIZONTAL))
    # for layout in layout_generator.iter_dfs_generate_layout(init_layout, set()):
    #     print(f"\n{layout.height}*{layout.width}: {layout.layout_info}")
    #     print_board(layout.layout_info, layout.width, layout.height)
    #     input("按回车键生成下一个布局（或 Ctrl+C 退出）...")



    # for layout in layout_generator.generate_layout(Size(height=5, width=5)):
    #     print_board(layout.layout_info, layout.width, layout.height)
    #     input("按回车键生成下一个布局（或 Ctrl+C 退出）...")




""" 
修改前：checker中的size 宽高设置反了
5*5: 40 Time: 0.0053958892822265625 seconds
7*5: 369 Time: 0.0958259105682373 seconds
7*7: 1155 Time: 0.47053980827331543 seconds
9*7: 25632 Time: 17.08006978034973 seconds
9*9: 33971 Time: 27.201441764831543 seconds


# size恢复正常后
{'5*5': 40, '7*5': 132, '7*7': 1155, '9*7': 5304, '9*9': 33971}
5*5: 40 Time: 0.017s
7*5: 132 Time: 0.136s
7*7: 1155 Time: 1.758s
9*7: 5304 Time: 11.414s
9*9: 33971 Time: 1.652m
11*9: 744408 Time: 45.765m
"""

"""
placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 9401, current count: 9401
placement: Placement(row=0, col=1, direction=Direction.HORIZONTAL), update count: 0, current count: 9401
placement: Placement(row=0, col=2, direction=Direction.HORIZONTAL), update count: 7838, current count: 17239
placement: Placement(row=0, col=3, direction=Direction.HORIZONTAL), update count: 0, current count: 17239
placement: Placement(row=0, col=4, direction=Direction.HORIZONTAL), update count: 9401, current count: 26640
placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 2561, current count: 29201
placement: Placement(row=1, col=0, direction=Direction.VERTICAL), update count: 0, current count: 29201
placement: Placement(row=2, col=0, direction=Direction.VERTICAL), update count: 2176, current count: 31377
placement: Placement(row=3, col=0, direction=Direction.VERTICAL), update count: 0, current count: 31377
placement: Placement(row=4, col=0, direction=Direction.VERTICAL), update count: 2594, current count: 33971
9*9: 33971 Time: 27.212185859680176 seconds
"""

"""
size: 5*5, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 28, current count: 28
size: 5*5, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 12, current count: 40
size: 7*5, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 72, current count: 72
size: 7*5, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 30, current count: 102
size: 7*5, placement: Placement(row=2, col=0, direction=Direction.VERTICAL), update count: 30, current count: 132
size: 7*7, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 444, current count: 444
size: 7*7, placement: Placement(row=0, col=2, direction=Direction.HORIZONTAL), update count: 444, current count: 888
size: 7*7, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 132, current count: 1020
size: 7*7, placement: Placement(row=2, col=0, direction=Direction.VERTICAL), update count: 135, current count: 1155
size: 9*7, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 1909, current count: 1909
size: 9*7, placement: Placement(row=0, col=2, direction=Direction.HORIZONTAL), update count: 1909, current count: 3818
size: 9*7, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 567, current count: 4385
size: 9*7, placement: Placement(row=2, col=0, direction=Direction.VERTICAL), update count: 375, current count: 4760
size: 9*7, placement: Placement(row=4, col=0, direction=Direction.VERTICAL), update count: 544, current count: 5304
size: 9*9, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 9401, current count: 9401
size: 9*9, placement: Placement(row=0, col=2, direction=Direction.HORIZONTAL), update count: 7838, current count: 17239
size: 9*9, placement: Placement(row=0, col=4, direction=Direction.HORIZONTAL), update count: 9401, current count: 26640
size: 9*9, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 2561, current count: 29201
size: 9*9, placement: Placement(row=2, col=0, direction=Direction.VERTICAL), update count: 2176, current count: 31377
size: 9*9, placement: Placement(row=4, col=0, direction=Direction.VERTICAL), update count: 2594, current count: 33971
5*5: 40 Time: 0.018s
7*5: 132 Time: 0.134s
7*7: 1155 Time: 1.747s
9*7: 5304 Time: 11.408s
9*9: 33971 Time: 1.647m


size: 5*5, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 28, current count: 28
size: 5*5, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 12, current count: 40
size: 5*5, placement: Placement(row=0, col=2, direction=Direction.VERTICAL), update count: 6, current count: 46
size: 5*5, placement: Placement(row=0, col=4, direction=Direction.VERTICAL), update count: 3, current count: 49
size: 7*5, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 72, current count: 72
size: 7*5, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 30, current count: 102
size: 7*5, placement: Placement(row=0, col=2, direction=Direction.VERTICAL), update count: 24, current count: 126
size: 7*5, placement: Placement(row=0, col=4, direction=Direction.VERTICAL), update count: 18, current count: 144
size: 7*7, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 444, current count: 444
size: 7*7, placement: Placement(row=0, col=2, direction=Direction.HORIZONTAL), update count: 444, current count: 888
size: 7*7, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 132, current count: 1020
size: 7*7, placement: Placement(row=0, col=2, direction=Direction.VERTICAL), update count: 102, current count: 1122
size: 7*7, placement: Placement(row=0, col=4, direction=Direction.VERTICAL), update count: 84, current count: 1206
size: 7*7, placement: Placement(row=0, col=6, direction=Direction.VERTICAL), update count: 54, current count: 1260
size: 9*7, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 1909, current count: 1909
size: 9*7, placement: Placement(row=0, col=2, direction=Direction.HORIZONTAL), update count: 1909, current count: 3818
size: 9*7, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 567, current count: 4385
size: 9*7, placement: Placement(row=0, col=2, direction=Direction.VERTICAL), update count: 526, current count: 4911
size: 9*7, placement: Placement(row=0, col=4, direction=Direction.VERTICAL), update count: 502, current count: 5413
size: 9*7, placement: Placement(row=0, col=6, direction=Direction.VERTICAL), update count: 303, current count: 5716
size: 9*9, placement: Placement(row=0, col=0, direction=Direction.HORIZONTAL), update count: 9401, current count: 9401
size: 9*9, placement: Placement(row=0, col=2, direction=Direction.HORIZONTAL), update count: 7838, current count: 17239
size: 9*9, placement: Placement(row=0, col=4, direction=Direction.HORIZONTAL), update count: 9401, current count: 26640
size: 9*9, placement: Placement(row=0, col=0, direction=Direction.VERTICAL), update count: 2561, current count: 29201
size: 9*9, placement: Placement(row=0, col=2, direction=Direction.VERTICAL), update count: 2266, current count: 31467
size: 9*9, placement: Placement(row=0, col=4, direction=Direction.VERTICAL), update count: 1718, current count: 33185
size: 9*9, placement: Placement(row=0, col=6, direction=Direction.VERTICAL), update count: 1905, current count: 35090
size: 9*9, placement: Placement(row=0, col=8, direction=Direction.VERTICAL), update count: 1258, current count: 36348
5*5: 49 Time: 0.022s
7*5: 144 Time: 0.129s
7*7: 1260 Time: 1.912s
9*7: 5716 Time: 11.093s
9*9: 36348 Time: 1.746m
"""