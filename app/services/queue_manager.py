import asyncio
from typing import Any, Callable, Dict, Optional, Set
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
        # Set of resources currently being processed
        self.processing_resources: Set[str] = set()
        
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
                    # Mark resource as being processed
                    self.processing_resources.add(resource_key)
                    
                    # Execute the operation
                    result = await operation(*args, **kwargs)
                    
                    # Update last processed timestamp
                    self.last_processed[resource_key] = datetime.now(timezone.utc)
                    
                    # Set the result
                    future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                # Remove from processing set
                self.processing_resources.remove(resource_key)
                
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
    
    def is_resource_processing(self, resource_type: str, resource_id: UUID) -> bool:
        """Check if a resource is currently being processed."""
        resource_key = f"{resource_type}:{resource_id}"
        return resource_key in self.processing_resources 