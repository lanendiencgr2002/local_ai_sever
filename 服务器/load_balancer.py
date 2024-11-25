from itertools import cycle
from typing import List, Dict, Tuple

class LoadBalancer:
    def __init__(self, apis: List[Dict]):
        """初始化负载均衡器
        
        Args:
            apis: API配置列表
        """
        self.apis = list(enumerate(apis))
        self.current = cycle(self.apis)
    
    def get_next_api(self) -> Tuple[int, Dict]:
        """获取下一个可用的API配置
        
        Returns:
            Tuple[int, Dict]: (API索引, API配置)
        """
        return next(self.current) 