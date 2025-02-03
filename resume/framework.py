
from functools import cached_property
from typing import List

from dataclasses import dataclass


@dataclass
class Response:
    id: str
    skills: List[str]
    work_experiences: List[str]

    @cached_property
    def valid(self) -> bool:
        return self.skills_valid and self.work_experiences_valid and self.id_valid

    @cached_property
    def skills_valid(self) -> bool:
        return False if type(self.skills) != list else bool(self.skills) 
    
    @cached_property
    def work_experiences_valid(self) -> bool:
        return False if type(self.work_experiences) != list else bool(self.work_experiences) 
    
    @cached_property
    def id_valid(self) -> bool:
        return False if type(self.id) != str else bool(self.id)
