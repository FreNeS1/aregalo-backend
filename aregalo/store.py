import os.path
from dataclasses import asdict
from typing import List, Dict, Optional

import yaml

from .schema import User, Present

USERS_FILE = "users.yml"
PRESENTS_FILE = "presents.yml"


class Store:
    """Interface for a data store in the application. Should handle users and present lists."""

    def get_users(self) -> list[User]:
        """
        Retrieve all users.
        :return: The retrieved users.
        """
        raise NotImplementedError()

    def get_user(self, name: str) -> Optional[User]:
        """
        Retrieve user data by name.
        :param name: The name of the user to retrieve.
        :return: The retrieved user. None if not found.
        """
        raise NotImplementedError()

    def upsert_user(self, user: User) -> None:
        """
        Create or update an user. Will persist changes.
        :param user: The user to update or create.
        """
        raise NotImplementedError()

    def delete_user(self, name: str) -> None:
        """
        Delete an user. Will persist changes. Will do nothing if user does not exist.
        :param name: The name of the user to delete.
        :raises ApplicationError: If user does not exist.
        """
        raise NotImplementedError()

    def get_presents(self, name: str) -> Optional[List[Present]]:
        """
        Retrieve the present list of an user by name.
        :param name: The name of the user of the present list.
        :return: The retrieved present list of the user. None if not found.
        """
        raise NotImplementedError()

    def upsert_presents(self, name: str, presents: List[Present]) -> None:
        """
        Create or update an user. Will persist changes.
        :param name: The name of the user of the present list.
        :param presents: The present list of the user to update or insert.
        """
        raise NotImplementedError()

    def delete_presents(self, name: str) -> None:
        """
        Delete an user. Will persist changes. Will do nothing if user does not have a present list.
        :param name: The name of the user of the present list to delete.
        """
        raise NotImplementedError()


class FileStore(Store):
    """A simple store capable of loading and saving data to a file."""

    def __init__(self, base_path: str):
        """
        Initialize a store and load the users and presents stored.
        :param base_path: The base path to the saved data files.
        """
        self._base_path: str = base_path
        self._users: Dict[str, User] = {}
        self._presents: Dict[str, List[Present]] = {}
        self._load_users()
        self._load_presents()

    def get_users(self) -> List[User]:
        return [user for _, user in self._users.items()]

    def get_user(self, name: str) -> Optional[User]:
        return self._users[name] if name in self._users else None

    def upsert_user(self, user: User) -> None:
        self._users[user.name] = user
        self._save_users()

    def delete_user(self, name: str) -> None:
        if name in self._users:
            del self._users[name]
            self._save_users()

    def get_presents(self, name: str) -> Optional[List[Present]]:
        return self._presents[name] if name in self._presents else None

    def upsert_presents(self, name: str, presents: List[Present]) -> None:
        self._presents[name] = presents
        self._save_presents()

    def delete_presents(self, name: str) -> None:
        if name in self._presents:
            del self._presents[name]
            self._save_presents()

    def _load_users(self) -> None:
        """Utility method to load the users from the users file. Should not be called directly."""
        with open(os.path.join(self._base_path, USERS_FILE), "r", encoding="utf-8") as user_file:
            raw_users = yaml.safe_load(user_file)
            self._users = {name: User(**user) for name, user in raw_users["users"].items()}

    def _save_users(self) -> None:
        """Utility method to save the users to the users file. Should not be called directly."""
        with open(os.path.join(self._base_path, USERS_FILE), "w", encoding="utf-8") as user_file:
            users = {name: asdict(user) for name, user in self._users.items()}
            yaml.safe_dump({"users": users}, user_file, allow_unicode=True)

    def _load_presents(self) -> None:
        """Utility method to load the presents from the presents file. Should not be called directly."""
        with open(os.path.join(self._base_path, PRESENTS_FILE), "r", encoding="utf-8") as presents_file:
            raw_presents = yaml.safe_load(presents_file)
            self._presents = {name: [Present(**present) for present in present_list] for name, present_list in raw_presents["presents"].items()}

    def _save_presents(self) -> None:
        """Utility method to save the presents to the presents file. Should not be called directly."""
        with open(os.path.join(self._base_path, PRESENTS_FILE), "w", encoding="utf-8") as presents_file:
            presents = {name: [asdict(present) for present in present_list] for name, present_list in self._presents.items()}
            yaml.safe_dump({"presents": presents}, presents_file, allow_unicode=True)
