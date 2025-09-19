import requests
import random
import time
import hashlib
import os
import json
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
import logging

class EnhancedImageDownloader:
    """
    增强型图片下载器
    支持会话保持、代理池、多重回退机制
    """
    
    def __init__(self, cache_dir="image_cache", enable_proxy=False):
        """
        初始化下载器
        
        Args:
            cache_dir: 缓存目录
            enable_proxy: 是否启用代理池
        """
        self.cache_dir = cache_dir
        self.enable_proxy = enable_proxy
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)
        
        # User-Agent池
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]
        
        # 代理池（示例，实际使用时需要配置真实代理）
        self.proxy_pool = []
        if enable_proxy:
            self.load_proxy_pool()
    
    def load_proxy_pool(self):
        """
        加载代理池
        实际使用时需要从代理服务商API获取
        """
        # 示例代理配置
        self.proxy_pool = [
            # {"http": "http://proxy1:port", "https": "https://proxy1:port"},
            # {"http": "http://proxy2:port", "https": "https://proxy2:port"},
        ]
    
    def get_cache_path(self, url):
        """
        根据URL生成缓存文件路径
        
        Args:
            url: 图片URL
            
        Returns:
            str: 缓存文件路径
        """
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.cache")
    
    def get_random_headers(self, url):
        """
        生成随机请求头
        
        Args:
            url: 目标URL
            
        Returns:
            dict: 请求头字典
        """
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'image',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }
        
        # 针对不同域名设置特殊Referer
        domain = urlparse(url).netloc.lower()
        if 'sinaimg.cn' in domain:
            headers['Referer'] = random.choice([
                'https://finance.sina.com.cn/',
                'https://news.sina.com.cn/',
                'https://www.sina.com.cn/'
            ])
        elif 'sina.com' in domain:
            headers['Referer'] = 'https://www.sina.com.cn/'
        elif 'weibo.com' in domain:
            headers['Referer'] = 'https://weibo.com/'
        else:
            # 通用策略：使用同域名作为Referer
            parsed = urlparse(url)
            headers['Referer'] = f"{parsed.scheme}://{parsed.netloc}/"
        
        return headers
    
    def exponential_backoff(self, attempt):
        """
        指数退避算法
        
        Args:
            attempt: 重试次数
            
        Returns:
            float: 等待时间（秒）
        """
        base_delay = 1
        max_delay = 60
        delay = min(base_delay * (2 ** attempt), max_delay)
        jitter = random.uniform(0.1, 0.3) * delay
        return delay + jitter
    
    def download_with_session(self, url, max_retries=5):
        """
        使用会话下载图片
        
        Args:
            url: 图片URL
            max_retries: 最大重试次数
            
        Returns:
            bytes: 图片数据，失败返回None
        """
        for attempt in range(max_retries):
            try:
                # 随机等待，避免请求过于频繁
                if attempt > 0:
                    wait_time = self.exponential_backoff(attempt - 1)
                    time.sleep(wait_time)
                
                # 设置随机请求头
                headers = self.get_random_headers(url)
                
                # 选择代理（如果启用）
                proxies = None
                if self.enable_proxy and self.proxy_pool:
                    proxies = random.choice(self.proxy_pool)
                
                # 动态调整超时时间
                timeout = 15 + (attempt * 5)
                
                # 发送请求
                response = self.session.get(
                    url, 
                    headers=headers, 
                    proxies=proxies,
                    timeout=timeout,
                    stream=True
                )
                response.raise_for_status()
                
                # 验证内容类型
                content_type = response.headers.get('Content-Type', '').lower()
                if 'image' not in content_type:
                    self.logger.warning(f"非图片内容: {content_type} for {url}")
                    continue
                
                # 获取图片数据
                data = response.content
                if len(data) < 100:
                    raise ValueError(f"图片文件过小: {len(data)} bytes")
                
                # 验证图片格式
                try:
                    img = Image.open(BytesIO(data))
                    if img.size[0] < 10 or img.size[1] < 10:
                        raise ValueError(f"图片尺寸过小: {img.size}")
                    img.verify()  # 验证图片完整性
                except Exception as e:
                    self.logger.warning(f"图片验证失败: {e}")
                    continue
                
                self.logger.info(f"成功下载图片: {url} (尝试 {attempt + 1}/{max_retries})")
                return data
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"下载失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"所有重试均失败: {url}")
            except Exception as e:
                self.logger.error(f"未知错误: {e}")
                break
        
        return None
    
    def try_cdn_mirrors(self, url):
        """
        尝试CDN镜像下载
        
        Args:
            url: 原始图片URL
            
        Returns:
            bytes: 图片数据，失败返回None
        """
        # CDN镜像服务列表
        cdn_services = [
            f"https://images.weserv.nl/?url={url}",
            f"https://imageproxy.pimg.tw/resize?url={url}",
            # 可以添加更多CDN服务
        ]
        
        for cdn_url in cdn_services:
            try:
                self.logger.info(f"尝试CDN镜像: {cdn_url}")
                data = self.download_with_session(cdn_url, max_retries=2)
                if data:
                    return data
            except Exception as e:
                self.logger.warning(f"CDN镜像失败: {e}")
                continue
        
        return None
    
    def get_placeholder_image(self, width=300, height=200):
        """
        生成占位符图片
        
        Args:
            width: 图片宽度
            height: 图片高度
            
        Returns:
            bytes: 占位符图片数据
        """
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建占位符图片
        img = Image.new('RGB', (width, height), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # 添加文字
        text = "图片加载失败"
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # 计算文字位置
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='#666666', font=font)
        
        # 转换为字节数据
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def download_image(self, url, use_cache=True, save_to_cache=True):
        """
        主下载方法，整合所有策略
        
        Args:
            url: 图片URL
            use_cache: 是否使用缓存
            save_to_cache: 是否保存到缓存
            
        Returns:
            tuple: (图片数据, 是否成功)
        """
        # 1. 检查本地缓存
        if use_cache:
            cache_path = self.get_cache_path(url)
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'rb') as f:
                        data = f.read()
                    self.logger.info(f"使用缓存: {url}")
                    return data, True
                except Exception as e:
                    self.logger.warning(f"缓存读取失败: {e}")
        
        # 2. 尝试直接下载
        data = self.download_with_session(url)
        if data:
            # 保存到缓存
            if save_to_cache:
                try:
                    cache_path = self.get_cache_path(url)
                    with open(cache_path, 'wb') as f:
                        f.write(data)
                except Exception as e:
                    self.logger.warning(f"缓存保存失败: {e}")
            return data, True
        
        # 3. 尝试CDN镜像
        data = self.try_cdn_mirrors(url)
        if data:
            if save_to_cache:
                try:
                    cache_path = self.get_cache_path(url)
                    with open(cache_path, 'wb') as f:
                        f.write(data)
                except Exception as e:
                    self.logger.warning(f"缓存保存失败: {e}")
            return data, True
        
        # 4. 返回占位符
        self.logger.warning(f"所有下载策略失败，使用占位符: {url}")
        placeholder_data = self.get_placeholder_image()
        return placeholder_data, False

# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建下载器实例
    downloader = EnhancedImageDownloader(enable_proxy=False)
    
    # 测试下载
    test_url = "https://n.sinaimg.cn/finance/crawl/20241201/example.jpg"
    data, success = downloader.download_image(test_url)
    
    if success:
        print("下载成功！")
    else:
        print("下载失败，使用占位符")