import sys
import os
import argparse
from typing import List, Dict
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from crossmath_layout.layout_generator import LayoutGenerator
from crossmath_layout.models import Size


class Args:
    def __init__(self, height: int, width: int, output_file: str, chunk_size: int = 1000):
        self.height = height
        self.width = width
        self.output_file = output_file
        self.chunk_size = chunk_size
        self.check_dir()

    def check_dir(self):
        """确保输出目录存在"""
        dir_path = os.path.dirname(self.output_file)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def __repr__(self):
        return f"Args(height={self.height}, width={self.width}, output_file={self.output_file}, chunk_size={self.chunk_size})"


def save_result_list(result_list: List[Dict], output_file: str):
    """保存结果到文件（支持CSV/Excel）"""
    file_ext = Path(output_file).suffix.lower()
    
    try:
        df = pd.DataFrame(result_list)
        if file_ext == ".csv":
            df.to_csv(output_file, index=False)
        elif file_ext in (".xlsx", ".xls"):
            df.to_excel(output_file, index=False)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        print(f"Successfully saved {len(result_list)} records to {output_file}")
    except Exception as e:
        print(f"Error saving file {output_file}: {str(e)}")
        raise


def build_file_name(output_file: str, chunk_index: int) -> str:
    """生成分块文件名"""
    path = Path(output_file)
    new_dir = path.parent / f"{path.stem}"
    if not new_dir.exists():
        new_dir.mkdir(parents=True)
    return str(new_dir / f"{path.stem}_{chunk_index}{path.suffix}")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Generate crossmath layouts")
    parser.add_argument("-H", "--height", type=int, required=True, help="Grid height")
    parser.add_argument("-W", "--width", type=int, required=True, help="Grid width")
    parser.add_argument("-o", "--output", required=True, help="Output file path (.csv or .xlsx)")
    parser.add_argument("-s", "--chunk-size", type=int, default=50000, 
                       help="Number of records per file chunk (default: 1000)")
    return parser.parse_args()


def main():
    # 解析命令行参数
    args = parse_args()
    
    # 初始化参数对象
    params = Args(
        height=args.height,
        width=args.width,
        output_file=args.output,
        chunk_size=args.chunk_size
    )
    print(params)
    # 初始化生成器
    generator = LayoutGenerator()
    size = Size(height=params.height, width=params.width)
    
    # 结果收集
    result_list = []
    chunk_index = 0
    
    # 进度条配置
    pbar = tqdm(
        desc=f"Generating {size.height}x{size.width} layouts",
        unit="layout",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{percentage:.0f}%] {rate_fmt}",
        dynamic_ncols=True
    )

    try:
        for index, layout in enumerate(generator.generate_layout(size), start=1):
            result_list.append({
                "index": index,
                "layout_info": layout.layout_info,
                "height": layout.height,
                "width": layout.width
            })

            # 分块保存
            if index % params.chunk_size == 0:
                output_path = build_file_name(params.output_file, chunk_index)
                save_result_list(result_list, output_path)
                result_list = []
                chunk_index += 1
            
            pbar.update(1)
            pbar.set_postfix(file_chunk=chunk_index)

    finally:
        # 保存剩余数据
        if result_list:
            output_path = params.output_file if chunk_index == 0 else build_file_name(params.output_file, chunk_index)
            save_result_list(result_list, output_path)
        
        pbar.close()


if __name__ == "__main__":
    # try:
    #     main()
    # except KeyboardInterrupt:
    #     print("\nProcess interrupted by user")
    #     sys.exit(1)
    # except Exception as e:
    #     print(f"Error: {str(e)}", file=sys.stderr)
    #     sys.exit(1)
    print(build_file_name("/Users/admin/crossmath_layout/data/export_1008/11x9.csv", 0))


"""
uv run crossmath-layout-generator -H 11 -W 9 -o "/Users/admin/crossmath_layout/data/export_1008/11x9.csv"
uv run crossmath-layout-generator -H 11 -W 11 -o "/Users/admin/crossmath_layout/data/export_1008/11x11.csv"
uv run crossmath-layout-generator -H 13 -W 11 -o "/Users/admin/crossmath_layout/data/export_1008/13x11.csv"
uv run crossmath-layout-generator -H 13 -W 13 -o "/Users/admin/crossmath_layout/data/export_1008/13x13.csv"
"""