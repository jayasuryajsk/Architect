"""
Advanced Execution Engine with Parallel Processing and Resource Management
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from queue import PriorityQueue
import traceback

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents an executable task"""
    id: str
    priority: int
    func: Callable
    args: tuple
    kwargs: dict
    dependencies: Set[str]
    timeout: float
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        return self.priority > other.priority  # Higher priority first


class ResourceManager:
    """Manages system resources to prevent overload"""
    
    def __init__(self, max_memory_percent: float = 80.0, max_cpu_percent: float = 70.0):
        self.max_memory_percent = max_memory_percent
        self.max_cpu_percent = max_cpu_percent
        self.resource_locks = asyncio.Semaphore(multiprocessing.cpu_count())
        
    async def check_resources(self) -> bool:
        """Check if resources are available"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        memory_ok = memory.percent < self.max_memory_percent
        cpu_ok = cpu < self.max_cpu_percent
        
        if not memory_ok:
            logger.warning(f"Memory usage high: {memory.percent:.1f}%")
        if not cpu_ok:
            logger.warning(f"CPU usage high: {cpu:.1f}%")
            
        return memory_ok and cpu_ok
    
    async def wait_for_resources(self):
        """Wait until resources are available"""
        while not await self.check_resources():
            await asyncio.sleep(1)
            
    def get_optimal_worker_count(self) -> int:
        """Get optimal number of workers based on system resources"""
        cpu_count = multiprocessing.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        
        # Rule of thumb: 1 worker per 2 GB RAM, max CPU count
        memory_based = int(memory_gb / 2)
        return min(cpu_count, max(2, memory_based))


class ExecutionEngine:
    """Handles parallel execution of tasks with resource management"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.resource_manager = ResourceManager()
        self.max_workers = max_workers or self.resource_manager.get_optimal_worker_count()
        self.task_queue = PriorityQueue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Any] = {}
        self.failed_tasks: Dict[str, Exception] = {}
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self._running = False
        
        logger.info(f"🚀 Execution engine initialized with {self.max_workers} workers")
        
    async def submit_task(self, task_id: str, func: Callable, *args,
                          priority: int = 5, dependencies: Set[str] = None,
                          timeout: float = 300, **kwargs) -> str:
        """Submit a task for execution"""
        task = Task(
            id=task_id,
            priority=priority,
            func=func,
            args=args,
            kwargs=kwargs,
            dependencies=dependencies or set(),
            timeout=timeout
        )
        
        await self.task_queue.put(task)
        logger.info(f"📥 Task {task_id} submitted (priority: {priority})")
        
        # Start processing if not already running
        if not self._running:
            asyncio.create_task(self._process_tasks())
            
        return task_id
    
    async def execute_parallel(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple tasks in parallel"""
        task_ids = []
        
        for task_def in tasks:
            task_id = await self.submit_task(
                task_id=task_def['id'],
                func=task_def['func'],
                *task_def.get('args', []),
                priority=task_def.get('priority', 5),
                dependencies=set(task_def.get('dependencies', [])),
                timeout=task_def.get('timeout', 300),
                **task_def.get('kwargs', {})
            )
            task_ids.append(task_id)
        
        # Wait for all tasks to complete
        results = await self.wait_for_tasks(task_ids)
        return results
    
    async def wait_for_tasks(self, task_ids: List[str], timeout: float = 3600) -> Dict[str, Any]:
        """Wait for specific tasks to complete"""
        start_time = time.time()
        results = {}
        
        while task_ids and (time.time() - start_time) < timeout:
            completed = []
            
            for task_id in task_ids:
                if task_id in self.completed_tasks:
                    results[task_id] = self.completed_tasks[task_id]
                    completed.append(task_id)
                elif task_id in self.failed_tasks:
                    results[task_id] = {'error': str(self.failed_tasks[task_id])}
                    completed.append(task_id)
            
            # Remove completed tasks
            for task_id in completed:
                task_ids.remove(task_id)
            
            if task_ids:
                await asyncio.sleep(0.1)
        
        # Handle timeouts
        for task_id in task_ids:
            results[task_id] = {'error': 'Timeout waiting for task completion'}
            
        return results
    
    async def _process_tasks(self):
        """Process tasks from the queue"""
        self._running = True
        
        try:
            while True:
                # Check if we have tasks
                if self.task_queue.empty() and not self.active_tasks:
                    await asyncio.sleep(0.1)
                    continue
                
                # Wait for resources
                await self.resource_manager.wait_for_resources()
                
                # Get next task if available
                if not self.task_queue.empty() and len(self.active_tasks) < self.max_workers:
                    task = await self.task_queue.get()
                    
                    # Check dependencies
                    if await self._check_dependencies(task):
                        # Execute task
                        asyncio_task = asyncio.create_task(self._execute_task(task))
                        self.active_tasks[task.id] = asyncio_task
                    else:
                        # Re-queue task if dependencies not met
                        await self.task_queue.put(task)
                        await asyncio.sleep(0.1)
                
                # Clean up completed tasks
                completed = []
                for task_id, asyncio_task in self.active_tasks.items():
                    if asyncio_task.done():
                        completed.append(task_id)
                
                for task_id in completed:
                    del self.active_tasks[task_id]
                    
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error in task processor: {e}")
            self._running = False
    
    async def _check_dependencies(self, task: Task) -> bool:
        """Check if task dependencies are satisfied"""
        for dep in task.dependencies:
            if dep not in self.completed_tasks:
                return False
        return True
    
    async def _execute_task(self, task: Task):
        """Execute a single task with timeout and retry logic"""
        logger.info(f"▶️ Executing task {task.id}")
        start_time = time.time()
        
        try:
            # Execute with timeout
            if asyncio.iscoroutinefunction(task.func):
                result = await asyncio.wait_for(
                    task.func(*task.args, **task.kwargs),
                    timeout=task.timeout
                )
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        self.executor,
                        task.func,
                        *task.args,
                        **task.kwargs
                    ),
                    timeout=task.timeout
                )
            
            execution_time = time.time() - start_time
            self.completed_tasks[task.id] = {
                'result': result,
                'execution_time': execution_time,
                'completed_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Task {task.id} completed in {execution_time:.2f}s")
            
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Task {task.id} timed out after {task.timeout}s")
            await self._handle_task_failure(task, TimeoutError(f"Task timed out after {task.timeout}s"))
            
        except Exception as e:
            logger.error(f"❌ Task {task.id} failed: {e}")
            await self._handle_task_failure(task, e)
    
    async def _handle_task_failure(self, task: Task, error: Exception):
        """Handle task failure with retry logic"""
        task.retry_count += 1
        
        if task.retry_count < task.max_retries:
            logger.info(f"🔄 Retrying task {task.id} (attempt {task.retry_count + 1}/{task.max_retries})")
            # Exponential backoff
            await asyncio.sleep(2 ** task.retry_count)
            await self.task_queue.put(task)
        else:
            self.failed_tasks[task.id] = error
            logger.error(f"💀 Task {task.id} failed after {task.max_retries} attempts")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current execution engine status"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        return {
            'active_tasks': len(self.active_tasks),
            'queued_tasks': self.task_queue.qsize(),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'max_workers': self.max_workers,
            'system_resources': {
                'memory_percent': memory.percent,
                'cpu_percent': cpu,
                'memory_available_gb': memory.available / (1024 ** 3)
            }
        }
    
    def shutdown(self):
        """Shutdown the execution engine"""
        logger.info("🛑 Shutting down execution engine")
        self._running = False
        self.executor.shutdown(wait=True)


class LongRunningTaskManager:
    """Manages tasks that can run for extended periods (12+ hours)"""
    
    def __init__(self):
        self.execution_engine = ExecutionEngine()
        self.checkpoints: Dict[str, Any] = {}
        self.progress_callbacks: Dict[str, Callable] = {}
        
    async def run_with_checkpoints(self, task_id: str, func: Callable,
                                   checkpoint_interval: float = 300,  # 5 minutes
                                   progress_callback: Optional[Callable] = None,
                                   *args, **kwargs):
        """Run a long task with periodic checkpoints"""
        
        if progress_callback:
            self.progress_callbacks[task_id] = progress_callback
            
        # Wrap the function to add checkpoint support
        async def wrapped_func(*args, **kwargs):
            last_checkpoint = time.time()
            
            # Create a context object for the task
            context = {
                'task_id': task_id,
                'checkpoints': self.checkpoints.get(task_id, {}),
                'save_checkpoint': lambda data: self._save_checkpoint(task_id, data),
                'report_progress': lambda progress: self._report_progress(task_id, progress)
            }
            
            kwargs['_context'] = context
            
            # Run the actual function
            result = await func(*args, **kwargs)
            
            # Save final checkpoint
            self._save_checkpoint(task_id, {'completed': True, 'result': result})
            
            return result
        
        # Submit the wrapped task
        return await self.execution_engine.submit_task(
            task_id=task_id,
            func=wrapped_func,
            *args,
            timeout=float('inf'),  # No timeout for long-running tasks
            **kwargs
        )
    
    def _save_checkpoint(self, task_id: str, data: Dict[str, Any]):
        """Save a checkpoint for a task"""
        if task_id not in self.checkpoints:
            self.checkpoints[task_id] = {}
            
        self.checkpoints[task_id].update(data)
        self.checkpoints[task_id]['last_checkpoint'] = datetime.utcnow().isoformat()
        
        logger.info(f"💾 Checkpoint saved for task {task_id}")
    
    def _report_progress(self, task_id: str, progress: Dict[str, Any]):
        """Report task progress"""
        if task_id in self.progress_callbacks:
            try:
                self.progress_callbacks[task_id](progress)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    async def resume_task(self, task_id: str, func: Callable, *args, **kwargs):
        """Resume a task from checkpoint"""
        checkpoint = self.checkpoints.get(task_id, {})
        
        if checkpoint.get('completed'):
            logger.info(f"Task {task_id} already completed")
            return checkpoint.get('result')
            
        kwargs['_resume_from_checkpoint'] = checkpoint
        
        return await self.run_with_checkpoints(task_id, func, *args, **kwargs)