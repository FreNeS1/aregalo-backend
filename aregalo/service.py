import http
from typing import List
from fastapi import HTTPException

from .schema import Present, UserData, PresentWishData, PresentGiftData, PresentCreateData
from .store import Store


class Service:
    """Interface for the service of the application."""

    def get_all_users(self) -> List[UserData]:
        """
        Retrieves all user data from the service.
        :return: The data of all the retrieved users.
        """
        raise NotImplementedError()

    def get_user_data(self, user: str) -> UserData:
        """
        Retrieve the user data from the service.
        :param user: The name of the user to retrieve.
        :return: The data of the retrieved user.
        """
        raise NotImplementedError()

    def get_user_present_wish_list(self, user: str) -> List[PresentWishData]:
        """
        Retrieve the present list of an user.
        :param user: The name of the user of the present list.
        :return: The present list of the user as expected by wishers.
        """
        raise NotImplementedError()

    def get_user_present_gift_list(self, user: str) -> List[PresentGiftData]:
        """
        Retrieve the present list of an user.
        :param user: The name of the user of the present list.
        :return: The present list of the user as expected by gifters.
        """
        raise NotImplementedError()

    def create_present(self, user: str, present: PresentCreateData) -> List[PresentWishData]:
        """
        Creates a present and saves it.
        :param user: The name of the user of the present list.
        :param present: The present data of the new present.
        :return: The new present list for the user.
        """
        raise NotImplementedError()

    def update_present(self, user: str, present_id: int, present: PresentWishData) -> List[PresentWishData]:
        """
        Updates a present.
        :param user: The name of the user of the present list.
        :param present_id: The id of the present to update.
        :param present: The present data of the new present.
        :return: The new present list for the user.
        """
        raise NotImplementedError()

    def delete_present(self, user: str, present_id: int) -> List[PresentWishData]:
        """
        Deletes a present.
        :param user: The name of the user of the present list.
        :param present_id: The id of the present to delete.
        :return: The new present list for the user.
        """
        raise NotImplementedError()

    def assign_user_to_present(self, user: str, present_id: int, gifter: str) -> List[PresentGiftData]:
        """
        Assigns an user as a gifter for a present of another user.
        :param user: The name of the user of the present list.
        :param present_id: The id of the present to assign the gifter.
        :param gifter: The name of the gifter user.
        :return: The new present list for the gifter user.
        """
        raise NotImplementedError()

    def remove_user_from_present(self, user: str, present_id: int, gifter: str) -> List[PresentGiftData]:
        """
        Removes an user as a gifter for a present of another user.
        :param user: The name of the user of the present list.
        :param present_id: The id of the present to assign the gifter.
        :param gifter: The name of the gifter user.
        :return: The new present list for the gifter user.
        """
        raise NotImplementedError()


class StoreService(Service):
    """Service implementation that handles requests with a store."""

    def __init__(self, store: Store):
        self._store = store

    def get_all_users(self) -> List[UserData]:
        return [user.to_user_data() for user in self._store.get_users()]

    def get_user_data(self, user: str) -> UserData:
        store_user = self._store.get_user(user)
        if store_user is None:
            raise HTTPException(detail=f"No user with name \"{user}\"", status_code=http.HTTPStatus.NOT_FOUND)
        return store_user.to_user_data()

    def get_user_present_wish_list(self, user: str) -> List[PresentWishData]:
        store_presents = self._store.get_presents(user)
        if store_presents is None:
            raise HTTPException(detail=f"No user with name \"{user}\"", status_code=http.HTTPStatus.NOT_FOUND)
        return [present.to_present_wish_response() for present in store_presents]

    def get_user_present_gift_list(self, user: str) -> List[PresentGiftData]:
        store_presents = self._store.get_presents(user)
        if store_presents is None:
            raise HTTPException(detail=f"No user with name \"{user}\"", status_code=http.HTTPStatus.NOT_FOUND)
        return [present.to_present_gift_response() for present in store_presents]

    def create_present(self, user: str, present: PresentCreateData) -> List[PresentWishData]:
        wish_user = self._store.get_user(user)
        present_id = wish_user.present_id
        wish_user.present_id = present_id + 1
        self._store.upsert_user(wish_user)

        presents = self._store.get_presents(user)
        presents.append(present.to_present(present_id, assigned_to=[]))
        self._store.upsert_presents(user, presents)
        return [present.to_present_wish_response() for present in presents]

    def update_present(self, user: str, present_id: int, present: PresentWishData) -> List[PresentWishData]:
        presents, found_present, found_present_index = self.find_present_in_list_by_id(user, present_id)
        presents[found_present_index] = present.to_present(found_present.assigned_to)
        self._store.upsert_presents(user, presents)
        return [present.to_present_wish_response() for present in presents]

    def delete_present(self, user: str, present_id: int) -> List[PresentWishData]:
        presents, found_present, found_present_index = self.find_present_in_list_by_id(user, present_id)
        del presents[found_present_index]
        self._store.upsert_presents(user, presents)
        return [present.to_present_wish_response() for present in presents]

    def assign_user_to_present(self, user: str, present_id: int, gifter: str) -> List[PresentGiftData]:
        presents, found_present, found_present_index = self.find_present_in_list_by_id(user, present_id)
        if gifter not in presents[found_present_index].assigned_to:
            presents[found_present_index].assigned_to.append(gifter)
            self._store.upsert_presents(user, presents)
        return [present.to_present_gift_response() for present in presents]

    def remove_user_from_present(self, user: str, present_id: int, gifter: str) -> List[PresentGiftData]:
        presents, found_present, found_present_index = self.find_present_in_list_by_id(user, present_id)
        if gifter in presents[found_present_index].assigned_to:
            presents[found_present_index].assigned_to.remove(gifter)
            self._store.upsert_presents(user, presents)
        return [present.to_present_gift_response() for present in presents]

    def find_present_in_list_by_id(self, user: str, present_id: int) -> (List[Present], Present, int):
        """
        Auxiliary method to retrieve the presents of an user and select one by id.
        :param user: The name of the user of the present list.
        :param present_id: The id of the present to find.
        :return: The list of presents, the found present, and its index.
        """
        presents = self._store.get_presents(user)
        found_present = next(filter(lambda p: p.id == present_id, presents), None)
        if found_present is None:
            raise HTTPException(detail=f"No present with id \"{present_id}\" for user \"{user}\"", status_code=http.HTTPStatus.NOT_FOUND)
        return presents, found_present, presents.index(found_present)
