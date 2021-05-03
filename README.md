# ProxyPool

#### 使用协程实现ip代理池维护
- 异步维护ip池
  - aiofiles, aiomysql, aioredis等异步库
- 定时任务
  - 使用AsyncIOScheduler：当你的程序使用了asyncio（一个异步框架）的时候使用

#### 代理 ip 
- 准备一堆ip地址，组成ip池，随机选择一个ip来使用
  
- 如何随机选择代理ip
  - {"ip":ip,"score",10}  (score：分数)
  - [{},{},{},{},{}]，对这个ip列表进行排序，按照分数进行排序
  - 选择质量好的ip(随机选择一个)
    
- 检查ip的可用性
  - 可以使用aiohttp添加超时参数，判断ip的质量
