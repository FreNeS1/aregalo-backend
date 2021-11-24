from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class User:
    """An user of the application"""
    name: str
    alias: str
    icon: str
    present_id: int

    def to_user_data(self) -> UserData:
        return UserData(
            name=self.name,
            alias=self.alias,
            icon=self.icon,
        )


@dataclass
class Present:
    """A present item with all data"""
    id: int
    title: str
    description: str = ""
    link: Optional[str] = ""
    price: Optional[int] = None
    favourite: bool = False
    assigned_to: List[str] = field(default_factory=list)

    def to_present_wish_response(self) -> PresentWishData:
        return PresentWishData(
            id=self.id,
            title=self.title,
            description=self.description,
            link=self.link,
            price=self.price,
            favourite=self.favourite,
        )

    def to_present_gift_response(self) -> PresentGiftData:
        return PresentGiftData(
            id=self.id,
            title=self.title,
            description=self.description,
            link=self.link,
            price=self.price,
            favourite=self.favourite,
            assigned_to=self.assigned_to,
        )


@dataclass
class UserData:
    """User data as returned by the API."""
    name: str
    alias: str
    icon: str

    def to_user(self, present_id: int) -> User:
        return User(
            name=self.name,
            alias=self.alias,
            icon=self.icon,
            present_id=present_id,
        )


@dataclass
class PresentCreateData:
    """Present data as returned by the API for present creation."""
    title: str
    description: str = ""
    link: Optional[str] = ""
    price: Optional[int] = None
    favourite: bool = False

    def to_present(self, id: int, assigned_to: List[str]) -> Present:
        return Present(
            id=id,
            title=self.title,
            description=self.description,
            link=self.link,
            price=self.price,
            favourite=self.favourite,
            assigned_to=assigned_to,
        )


@dataclass
class PresentWishData:
    """Present data as returned by the API for wisher users."""
    id: int
    title: str
    description: str = ""
    link: Optional[str] = ""
    price: Optional[int] = None
    favourite: bool = False

    def to_present(self, assigned_to: List[str]) -> Present:
        return Present(
            id=self.id,
            title=self.title,
            description=self.description,
            link=self.link,
            price=self.price,
            favourite=self.favourite,
            assigned_to=assigned_to,
        )


@dataclass
class PresentGiftData:
    """Present data as returned by the API for gifter users."""
    id: int
    title: str
    description: str = ""
    link: Optional[str] = ""
    price: Optional[int] = None
    favourite: bool = False
    assigned_to: List[str] = field(default_factory=list)

    def to_present(self) -> Present:
        return Present(
            id=self.id,
            title=self.title,
            description=self.description,
            link=self.link,
            price=self.price,
            favourite=self.favourite,
            assigned_to=self.assigned_to,
        )
