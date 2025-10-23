from typing import Generic, TypeVar, List, Optional

T = TypeVar("T")

"""
A basic bounded stack.
"""
class Stack(Generic[T]):
    def __init__(self, max_size: Optional[int] = None) -> None:
        """
        Initialize the stack with an optional size limit.
        If max_size is None, the stack grows without bound.
        """
        self._data: List[T] = []
        self._max_size = max_size

    def push(self, item: T) -> None:
        """Push an item onto the stack. If full, drop the oldest (bottom) item."""
        if self._max_size is not None and len(self._data) >= self._max_size:
            # Drop the oldest element (bottom of the stack)
            self._data.pop(0)
        self._data.append(item)

    def pop(self) -> Optional[T]:
        """Pop the top item off the stack. Returns None if empty."""
        if self._data:
            return self._data.pop()
        return None

    def peek(self) -> Optional[T]:
        """Return the top item without removing it."""
        if self._data:
            return self._data[-1]
        return None

    def is_empty(self) -> bool:
        """Check if the stack is empty."""
        return not self._data

    def size(self) -> int:
        """Return the number of elements in the stack."""
        return len(self._data)

    def clear(self) -> None:
        """Remove all elements from the stack."""
        self._data.clear()

    def __repr__(self) -> str:
        return f"Stack(max_size={self._max_size}, data={self._data})"
