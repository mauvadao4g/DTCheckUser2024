from unittest.mock import Mock
from datetime import datetime, timedelta
from checkuser.data.connection import ConnectionMemory
from checkuser.data.repository import DeviceRepositoryMemory, UserRepositoryMemory


from checkuser.domain.user import User
from checkuser.domain.use_case import CheckUserUseCase, KillConnectionUseCase
from checkuser.infra.controller import HttpRequest
from checkuser.infra.controllers.check_user import CheckUserController
from checkuser.infra.controllers.kill_connection import KillConnectionController


def test_should_check_user():
    user_repository = UserRepositoryMemory()
    device_repository = DeviceRepositoryMemory()
    connection = ConnectionMemory()

    use_case = CheckUserUseCase(user_repository, device_repository, connection)
    controller = CheckUserController(use_case)
    response = controller.handle(
        HttpRequest(
            query={
                'username': 'test1',
                'deviceId': 'test',
            },
            body={},
        )
    )

    assert response.status_code == 200
    assert response.body['id'] == 1000


def test_should_kill_connection():
    connection1 = ConnectionMemory()
    connection2 = ConnectionMemory()
    connection2.set_next_handler(connection1)

    use_case = KillConnectionUseCase(connection2)
    controller = KillConnectionController(use_case)

    controller.handle(HttpRequest(query={'username': 'test'}, body={}))

    assert connection1.users[0]['killed']
    assert connection2.users[0]['killed']
