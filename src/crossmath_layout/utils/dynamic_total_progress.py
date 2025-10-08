from tqdm import tqdm

class DynamicTotalProgress:
    def __init__(self, chunk_size=1000, desc="Processing", **kwargs):
        self.chunk_size = chunk_size
        self.current = 0  # 当前已处理量
        self.total = chunk_size  # 初始预估值
        self.pbar = tqdm(
            desc=desc,
            total=self.total,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{percentage:.0f}%] speed: {rate:.2f}/s",
            dynamic_ncols=True,
            mininterval=1.0,  # 每秒最多刷新1次
            maxinterval=5.0,  # 强制刷新间隔上限
            smoothing=0.3,     # 更强的平滑效果
            ascii=" #",
            **kwargs,
        )
    
    def update(self, n=1):
        self.current += n
        
        # 达到当前chunk边界时扩展total
        if self.current >= self.total:
            self.total += self.chunk_size
            self.pbar.total = self.total
        
        self.pbar.update(n)
    
    def close(self):
        # 修正最终总数
        self.pbar.total = self.current
        self.pbar.refresh()
        self.pbar.close()
        return self.current