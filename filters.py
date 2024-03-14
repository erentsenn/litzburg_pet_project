from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery
from typing import Union
from tools import find_admin


class AdminFilter(BoundFilter):
    """
    Check if the user is a bot admin
    """
    key = "admin"

    def __init__(self, admin: bool):
        self.admin = admin

    async def check(self, obj: Union[Message, CallbackQuery]):
        if find_admin(obj.from_user.username):
            return self.admin is True
        return self.admin is False


class ApproveFilter(BoundFilter):
    """
    Check if the user is a bot admin
    """
    key = "approve"

    def __init__(self, approve: bool):
        self.approve = approve

    async def check(self, obj: Message):
        if obj.chat.id == -1001602815932:
            return self.approve is True
        return self.approve is False
