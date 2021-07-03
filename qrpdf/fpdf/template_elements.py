""" Dataclasses for fpdf2 Template handlers """

__author__ = "Arthur Moore <Arthur.Moore.git@cd-net.net>"
__copyright__ = "Copyright (C) 2021 Arthur Moore"
__license__ = "MIT"

from dataclasses import dataclass, asdict, field as dfield
from typing import Any, Union, Optional


@dataclass
class TemplateElementBase:
    """
    This is the minimum that fpdf.Template.render looks for

    Note: This has special logic, since rotate is optional
    """
    name: str
    priority: int
    text: Any  # Default if the element is not set for a page.
    type: str = dfield(default_factory=NotImplementedError("You must set a type"))
    rotate: float = dfield(default=0, metadata={"optional": True})  # Optional, and causes PDF bloat if included!
    x1: Union[int, float] = 0  # Required if rotate is set.
    y1: Union[int, float] = 0  # Required if rotate is set.

    @staticmethod
    def dict_factory(data):
        """ Special dict_factory to remove "rotate" if unused """
        out = dict(data)
        if out["rotate"] == 0:
            del out["rotate"]
        return out

    def asdict(self):
        """ Special implementation of asdict to remove "rotate" if it is unused. """
        return asdict(self, dict_factory=self.dict_factory)

    def __getattr__(self, item):
        """ Freeze certain fields """
        if item in getattr(self, "__dataclass_fields__").keys():
            field = getattr(self, "__dataclass_fields__")[item]
            if field.metadata.get("frozen", False):
                return field.default
        return super().__getattr__(item)


@dataclass
class TextElement(TemplateElementBase):
    """ For fpdf.template.Template.text """
    x1: float = 0
    y1: float = 0
    x2: float = 0
    y2: float = 0
    text: str = ""
    font: str = "helvetica"
    size: int = 10
    bold: bool = False
    italic: bool = False
    underline: bool = False
    align: str = ""  # Literal["L", "R", "D", "C", ""]
    foreground: int = 0
    backgroud: int = 65535  # TODO: File a bug report for the spelling
    multiline: Optional[bool] = None


@dataclass
class ImageElement(TemplateElementBase):
    """ For fpdf.template.Template.image """
    type: str = dfield(default="I", metadata={"frozen": True})
    x1: float = 0
    y1: float = 0
    x2: float = 0
    y2: float = 0
    text: Any = ""
