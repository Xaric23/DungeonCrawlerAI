"""
Behavior Tree implementation for AI decision-making.
Provides a flexible framework for the hero AI to make intelligent decisions.
"""
from enum import Enum
from typing import Any, Callable, List, Optional
from abc import ABC, abstractmethod


class NodeStatus(Enum):
    """Status of a behavior tree node"""
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"


class BehaviorNode(ABC):
    """Base class for all behavior tree nodes"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def tick(self, context: Any) -> NodeStatus:
        """Execute the node and return its status"""
        pass


class ActionNode(BehaviorNode):
    """Leaf node that performs an action"""
    
    def __init__(self, name: str, action: Callable[[Any], NodeStatus]):
        super().__init__(name)
        self.action = action
    
    def tick(self, context: Any) -> NodeStatus:
        return self.action(context)


class ConditionNode(BehaviorNode):
    """Leaf node that checks a condition"""
    
    def __init__(self, name: str, condition: Callable[[Any], bool]):
        super().__init__(name)
        self.condition = condition
    
    def tick(self, context: Any) -> NodeStatus:
        return NodeStatus.SUCCESS if self.condition(context) else NodeStatus.FAILURE


class SequenceNode(BehaviorNode):
    """Composite node that executes children in sequence until one fails"""
    
    def __init__(self, name: str, children: Optional[List[BehaviorNode]] = None):
        super().__init__(name)
        self.children = children or []
    
    def add_child(self, child: BehaviorNode):
        self.children.append(child)
    
    def tick(self, context: Any) -> NodeStatus:
        for child in self.children:
            status = child.tick(context)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS


class SelectorNode(BehaviorNode):
    """Composite node that executes children until one succeeds"""
    
    def __init__(self, name: str, children: Optional[List[BehaviorNode]] = None):
        super().__init__(name)
        self.children = children or []
    
    def add_child(self, child: BehaviorNode):
        self.children.append(child)
    
    def tick(self, context: Any) -> NodeStatus:
        for child in self.children:
            status = child.tick(context)
            if status != NodeStatus.FAILURE:
                return status
        return NodeStatus.FAILURE


class DecoratorNode(BehaviorNode):
    """Node that modifies the behavior of a child node"""
    
    def __init__(self, name: str, child: BehaviorNode):
        super().__init__(name)
        self.child = child
    
    @abstractmethod
    def tick(self, context: Any) -> NodeStatus:
        pass


class InverterNode(DecoratorNode):
    """Inverts the result of its child"""
    
    def tick(self, context: Any) -> NodeStatus:
        status = self.child.tick(context)
        if status == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        elif status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        return status


class RepeaterNode(DecoratorNode):
    """Repeats its child a specified number of times"""
    
    def __init__(self, name: str, child: BehaviorNode, times: int):
        super().__init__(name, child)
        self.times = times
    
    def tick(self, context: Any) -> NodeStatus:
        for _ in range(self.times):
            status = self.child.tick(context)
            if status == NodeStatus.FAILURE:
                return NodeStatus.FAILURE
        return NodeStatus.SUCCESS


class BehaviorTree:
    """Main behavior tree class"""
    
    def __init__(self, root: BehaviorNode):
        self.root = root
    
    def tick(self, context: Any) -> NodeStatus:
        """Execute the behavior tree"""
        return self.root.tick(context)
