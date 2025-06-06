import asyncio
from typing import Any, Callable, Dict, Optional
from uuid import UUID
import logging
from datetime import datetime, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)

class QueueManager:
    """Manages request queues for ordered processing of concurrent operations."""
    
    def __init__(self):
        # Dictionary to store queues for each resource type
        self.queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        # Dictionary to store locks for each resource
        self.locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        # Dictionary to store the last processed timestamp for each resource
        self.last_processed: Dict[str, datetime] = defaultdict(lambda: datetime.min.replace(tzinfo=timezone.utc))
        
    async def enqueue_operation(
        self,
        resource_type: str,
        resource_id: UUID,
        operation: Callable,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Enqueue an operation for a specific resource.
        
        Args:
            resource_type: Type of resource (e.g., 'library', 'document')
            resource_id: ID of the resource
            operation: Async function to execute
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
        """
        resource_key = f"{resource_type}:{resource_id}"
        queue = self.queues[resource_key]
        lock = self.locks[resource_key]
        
        # Create a future to store the result
        future = asyncio.Future()
        
        # Create operation wrapper
        async def operation_wrapper():
            try:
                async with lock:
                    # Execute the operation
                    result = await operation(*args, **kwargs)
                    # Update last processed timestamp
                    self.last_processed[resource_key] = datetime.now(timezone.utc)
                    # Set the result
                    future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                # Clean up if this is the last operation in the queue
                if queue.empty():
                    del self.queues[resource_key]
                    del self.locks[resource_key]
        
        # Add operation to queue
        await queue.put(operation_wrapper)
        
        # Start processing if this is the only operation in the queue
        if queue.qsize() == 1:
            asyncio.create_task(self._process_queue(resource_key))
        
        # Wait for the operation to complete
        return await future
    
    async def _process_queue(self, resource_key: str):
        """Process operations in the queue for a specific resource."""
        queue = self.queues[resource_key]
        
        while not queue.empty():
            operation = await queue.get()
            try:
                await operation()
            except Exception as e:
                logger.error(f"Error processing operation for {resource_key}: {str(e)}")
            finally:
                queue.task_done()
    
    def get_queue_size(self, resource_type: str, resource_id: UUID) -> int:
        """Get the current queue size for a resource."""
        resource_key = f"{resource_type}:{resource_id}"
        return self.queues[resource_key].qsize() if resource_key in self.queues else 0
    
    def get_last_processed_time(self, resource_type: str, resource_id: UUID) -> datetime:
        """Get the last processed timestamp for a resource."""
        resource_key = f"{resource_type}:{resource_id}"
        return self.last_processed[resource_key] 