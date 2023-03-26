import datetime
import sqlite3

from typing import List, Union

from checkuser.domain.user import Device, User
from checkuser.domain.repository import UserRepository, DeviceRepository
from checkuser.data.driver import Driver


class UserRepositoryMemory(UserRepository):
    def __init__(self):
        self.users = [
            User(1000, 'test1', datetime.datetime(2023, 1, 1), 10),
            User(1002, 'test2', datetime.datetime(2023, 1, 1), 10),
            User(1003, 'test3', datetime.datetime(2023, 1, 1), 1),
        ]

    def get(self, username: str) -> User:
        try:
            return next(user for user in self.users if user.username == username)
        except StopIteration:
            raise ValueError('User not found')

    def get_all(self) -> List[User]:
        return self.users

    def save(self, user: User) -> None:
        self.users.append(user)


class UserRepositoryImpl(UserRepository):
    def __init__(self, driver: Driver):
        self.driver = driver

    def get(self, username: str) -> User:
        user_id = self.driver.get_id(username)
        expiration_date = self.driver.get_expiration_date(username)
        connection_limit = self.driver.get_connection_limit(username)
        user = User(user_id, username, expiration_date, connection_limit)
        return user

    def get_all(self) -> List[User]:
        users = self.driver.get_users()
        return [self.get_by_username(user) for user in users]


class DeviceRepositorySQL(DeviceRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.sqlite = conn

    def get_by_id(self, id: str) -> Device | None:
        cmd = 'SELECT * FROM devices WHERE id = ?'
        data = self.sqlite.execute(cmd, (id,)).fetchall()
        return Device(data[0][0], data[0][1]) if data else None

    def save(self, device: Device) -> None:
        cmd = 'INSERT INTO devices (id, username) VALUES (?,?)'
        self.sqlite.execute(cmd, (device.id, device.username))
        self.sqlite.commit()

    def get_by_username(self, username: str) -> List[Device]:
        cmd = 'SELECT * FROM devices WHERE username =?'
        data = self.sqlite.execute(cmd, (username,)).fetchall()
        if not data:
            raise ValueError('Device not found')
        return [Device(device[0], device[1]) for device in data]

    def count(self, username: str) -> int:
        cmd = 'SELECT COUNT(*) FROM devices WHERE username =?'
        return self.sqlite.execute(cmd, (username,)).fetchone()[0]


class DeviceRepositoryMemory(DeviceRepository):
    def __init__(self):
        self.devices: List[Device] = []

    def save(self, device: Device) -> None:
        self.devices.append(device)

    def get_by_id(self, id: str) -> Union[Device, None]:
        return next((device for device in self.devices if device.id == id), None)

    def get_by_username(self, username: str) -> List[Device]:
        return [device for device in self.devices if device.username == username]

    def count(self, username: str) -> int:
        return len([device for device in self.devices if device.username == username])
