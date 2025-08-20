from abc import ABC, abstractmethod


class AbstractMenu(ABC):
    @abstractmethod
    def show():
        pass
