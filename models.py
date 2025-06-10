from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class TimerState(Enum):
    """Enum representing the current state of the timer"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    CANCELLED = "cancelled"


@dataclass
class PastaInfo:
    """Data class representing pasta information"""
    name: str
    min_time: int
    max_time: int
    is_custom: bool = False
    usage_count: int = 0
    created_date: Optional[str] = None
    
    @property
    def time_range(self) -> Tuple[int, int]:
        return (self.min_time, self.max_time)
    
    def is_valid_time(self, minutes: float) -> bool:
        return self.min_time <= minutes <= self.max_time
    
    def increment_usage(self) -> None:
        """Increment usage count for tracking"""
        self.usage_count += 1


@dataclass
class TimerEvent:
    """Data class representing timer events"""
    event_type: str
    remaining_seconds: int
    pasta_type: str
    additional_data: Optional[Dict] = None
    
    @property
    def minutes(self) -> int:
        return self.remaining_seconds // 60
    
    @property
    def seconds(self) -> int:
        return self.remaining_seconds % 60
