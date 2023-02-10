from raffles.shared.repositories import UserRepository
from raffles.shared.models import UserFavourite
from shared.api.authentication import SignedUser
from raffles.shared.exceptions import ForbiddenException


class UserService:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    def get_favourites(self, user: SignedUser) -> list[str]:
        favourites = self._repo.get_favourites(user.account_id)
        return [f.raffle_id for f in favourites if f.is_favourite]

    def _set_favourite_state(self, user: SignedUser, raffle_id: str, is_favourite: bool):
        favourites = self._repo.get_favourites(user.account_id)

        current_record = next(
            (f for f in favourites if f.raffle_id == raffle_id), None)
        if current_record is not None:
            if current_record.last_updated >= user.timestamp:
                raise ForbiddenException("Invalid timestamp")

        self._repo.set_favourites(user.account_id, [
            *[f for f in favourites if f.raffle_id != raffle_id],
            UserFavourite(raffle_id, is_favourite, user.timestamp)
        ])

    def add_favourite(self, user: SignedUser, raffle_id: str):
        # TODO: Check if raffle exists
        return self._set_favourite_state(user, raffle_id, True)

    def remove_favourite(self, user: SignedUser, raffle_id: str):
        return self._set_favourite_state(user, raffle_id, False)
