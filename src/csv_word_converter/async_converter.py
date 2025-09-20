#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步CSV-Word转换器模块

提供异步处理能力，支持并发转换多个CSV文件，提升处理效率。
使用asyncio和ThreadPoolExecutor实现异步I/O和CPU密集型任务的并发处理。

主要功能:
- 异步CSV文件读取和处理
- 并发Word文档生成
- 进度跟踪和状态监控
- 错误处理和重试机制
"""

import asyncio
import aiofiles
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd

from .core import UniversalDocumentGenerator
from . import convert_csv_to_word


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待处理
    RUNNING = "running"      # 正在处理
    COMPLETED = "completed"  # 处理完成
    FAILED = "failed"        # 处理失败
    CANCELLED = "cancelled"  # 已取消


@dataclass
class ConversionTask:
    """转换任务数据类"""
    task_id: str                           # 任务唯一标识
    csv_file: Path                         # CSV文件路径
    output_path: Path                      # 输出文件路径
    template_type: str = "default"         # 模板类型
    status: TaskStatus = TaskStatus.PENDING # 任务状态
    progress: float = 0.0                  # 进度百分比 (0-100)
    start_time: Optional[float] = None     # 开始时间戳
    end_time: Optional[float] = None       # 结束时间戳
    error_message: Optional[str] = None    # 错误信息
    retry_count: int = 0                   # 重试次数
    max_retries: int = 3                   # 最大重试次数
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据

    @property
    def duration(self) -> Optional[float]:
        """计算任务执行时长（秒）"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def is_finished(self) -> bool:
        """判断任务是否已完成（成功或失败）"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]


class AsyncConverter:
    """异步CSV-Word转换器
    
    提供异步处理能力，支持并发转换多个CSV文件。
    使用线程池处理CPU密集型的文档生成任务，使用asyncio处理I/O操作。
    """

    def __init__(self, 
                 max_workers: int = 4,
                 max_concurrent_tasks: int = 10,
                 default_timeout: float = 300.0):
        """
        初始化异步转换器

        Args:
            max_workers: 线程池最大工作线程数，用于CPU密集型任务
            max_concurrent_tasks: 最大并发任务数，控制内存使用
            default_timeout: 单个任务默认超时时间（秒）
        """
        self.max_workers = max_workers
        self.max_concurrent_tasks = max_concurrent_tasks
        self.default_timeout = default_timeout
        
        # 任务管理
        self.tasks: Dict[str, ConversionTask] = {}
        self.task_queue = asyncio.Queue(maxsize=max_concurrent_tasks)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # 进度回调函数
        self.progress_callbacks: List[Callable[[ConversionTask], None]] = []
        
        # 日志配置
        self.logger = logging.getLogger(__name__)
        
        # 信号量控制并发数
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    def add_progress_callback(self, callback: Callable[[ConversionTask], None]) -> None:
        """
        添加进度回调函数

        Args:
            callback: 回调函数，接收ConversionTask参数
        """
        self.progress_callbacks.append(callback)

    def _notify_progress(self, task: ConversionTask) -> None:
        """
        通知所有进度回调函数

        Args:
            task: 更新的任务对象
        """
        for callback in self.progress_callbacks:
            try:
                callback(task)
            except Exception as e:
                self.logger.warning(f"进度回调函数执行失败: {e}")

    async def _read_csv_async(self, csv_file: Path) -> pd.DataFrame:
        """
        异步读取CSV文件

        Args:
            csv_file: CSV文件路径

        Returns:
            pandas.DataFrame: CSV数据

        Raises:
            FileNotFoundError: 文件不存在
            pd.errors.EmptyDataError: 文件为空
            pd.errors.ParserError: 解析错误
        """
        try:
            async with aiofiles.open(csv_file, mode='r', encoding='utf-8') as f:
                content = await f.read()
            
            # 使用StringIO在内存中处理CSV内容
            from io import StringIO
            return pd.read_csv(StringIO(content))
            
        except Exception as e:
            self.logger.error(f"读取CSV文件失败 {csv_file}: {e}")
            raise

    def _convert_sync(self, 
                     csv_file: Path, 
                     output_path: Path, 
                     template_type: str) -> str:
        """
        同步执行CSV到Word转换（在线程池中运行）

        Args:
            csv_file: CSV文件路径
            output_path: 输出文件路径
            template_type: 模板类型

        Returns:
            str: 生成的文档路径

        Raises:
            Exception: 转换过程中的各种异常
        """
        try:
            # 调用现有的转换函数
            result_path = convert_csv_to_word(
                csv_file=str(csv_file),
                template_type=template_type,
                output_path=str(output_path)
            )
            return result_path
            
        except Exception as e:
            self.logger.error(f"转换失败 {csv_file} -> {output_path}: {e}")
            raise

    async def _process_single_task(self, task: ConversionTask) -> ConversionTask:
        """
        处理单个转换任务

        Args:
            task: 转换任务对象

        Returns:
            ConversionTask: 更新后的任务对象
        """
        async with self.semaphore:  # 控制并发数
            try:
                # 更新任务状态
                task.status = TaskStatus.RUNNING
                task.start_time = time.time()
                task.progress = 10.0
                self._notify_progress(task)

                self.logger.info(f"开始处理任务 {task.task_id}: {task.csv_file}")

                # 验证输入文件
                if not task.csv_file.exists():
                    raise FileNotFoundError(f"CSV文件不存在: {task.csv_file}")

                # 创建输出目录
                task.output_path.parent.mkdir(parents=True, exist_ok=True)
                task.progress = 20.0
                self._notify_progress(task)

                # 异步读取CSV文件
                try:
                    df = await self._read_csv_async(task.csv_file)
                    task.metadata['row_count'] = len(df)
                    task.progress = 40.0
                    self._notify_progress(task)
                except Exception as e:
                    raise ValueError(f"CSV文件读取失败: {e}")

                # 在线程池中执行CPU密集型的转换任务
                loop = asyncio.get_event_loop()
                result_path = await loop.run_in_executor(
                    self.executor,
                    self._convert_sync,
                    task.csv_file,
                    task.output_path,
                    task.template_type
                )

                # 任务完成
                task.status = TaskStatus.COMPLETED
                task.end_time = time.time()
                task.progress = 100.0
                task.metadata['output_file'] = result_path
                
                self.logger.info(f"任务完成 {task.task_id}: {result_path}")
                self._notify_progress(task)

                return task

            except Exception as e:
                # 错误处理
                task.status = TaskStatus.FAILED
                task.end_time = time.time()
                task.error_message = str(e)
                task.progress = 0.0
                
                self.logger.error(f"任务失败 {task.task_id}: {e}")
                self._notify_progress(task)

                # 判断是否需要重试
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.PENDING
                    self.logger.info(f"任务 {task.task_id} 将进行第 {task.retry_count} 次重试")

                return task

    async def add_task(self, 
                      csv_file: Path, 
                      output_path: Path,
                      template_type: str = "default",
                      task_id: Optional[str] = None,
                      max_retries: int = 3) -> str:
        """
        添加转换任务到队列

        Args:
            csv_file: CSV文件路径
            output_path: 输出文件路径
            template_type: 模板类型
            task_id: 任务ID（可选，自动生成）
            max_retries: 最大重试次数

        Returns:
            str: 任务ID
        """
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000)}_{len(self.tasks)}"

        task = ConversionTask(
            task_id=task_id,
            csv_file=Path(csv_file),
            output_path=Path(output_path),
            template_type=template_type,
            max_retries=max_retries
        )

        self.tasks[task_id] = task
        await self.task_queue.put(task)
        
        self.logger.info(f"添加任务 {task_id}: {csv_file} -> {output_path}")
        return task_id

    async def process_all_tasks(self) -> Dict[str, ConversionTask]:
        """
        处理队列中的所有任务

        Returns:
            Dict[str, ConversionTask]: 所有任务的执行结果
        """
        if self.task_queue.empty():
            self.logger.warning("任务队列为空")
            return {}

        self.logger.info(f"开始处理 {self.task_queue.qsize()} 个任务")

        # 创建任务协程列表
        tasks_to_process = []
        while not self.task_queue.empty():
            task = await self.task_queue.get()
            tasks_to_process.append(self._process_single_task(task))

        # 并发执行所有任务
        try:
            completed_tasks = await asyncio.gather(*tasks_to_process, return_exceptions=True)
            
            # 处理结果
            results = {}
            for result in completed_tasks:
                if isinstance(result, ConversionTask):
                    results[result.task_id] = result
                elif isinstance(result, Exception):
                    self.logger.error(f"任务执行异常: {result}")

            return results

        except Exception as e:
            self.logger.error(f"批量任务处理失败: {e}")
            raise

    def get_task_status(self, task_id: str) -> Optional[ConversionTask]:
        """
        获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            Optional[ConversionTask]: 任务对象，不存在则返回None
        """
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> Dict[str, ConversionTask]:
        """
        获取所有任务状态

        Returns:
            Dict[str, ConversionTask]: 所有任务字典
        """
        return self.tasks.copy()

    def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否成功取消
        """
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            self.logger.info(f"任务已取消: {task_id}")
            return True
        return False

    async def shutdown(self) -> None:
        """
        关闭转换器，清理资源
        """
        self.logger.info("正在关闭异步转换器...")
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        # 清理任务队列
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.CANCELLED
            except asyncio.QueueEmpty:
                break

        self.logger.info("异步转换器已关闭")

    def __del__(self):
        """析构函数，确保资源清理"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)