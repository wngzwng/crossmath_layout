class TimeFormatter:
    """时间格式化类"""
    
    @staticmethod
    def format(elapsed_time: float, digits: int = 2) -> str:
        if elapsed_time < 60:
            return f"{elapsed_time:.{digits}f}s"
        elif elapsed_time < 3600:
            return f"{elapsed_time / 60:.{digits}f}m"
        else:
            return f"{elapsed_time / 3600:.{digits}f}h"
