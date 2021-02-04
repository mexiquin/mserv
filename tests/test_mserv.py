import os
from importlib.metadata import version
from mserv import mserv


def test_version():
    assert mserv.version_num == version('mserv')


def test_filename_extract1():
    networker = mserv.Networking(
        'https://launcher.mojang.com/v1/objects/1b557e7b033b583cd9f66746b7a9ab1ec1673ced/server.jar')
    filename = networker.extract_filename()

    assert filename == "server.jar"


def test_filename_extract2():
    networker = mserv.Networking('https://qjasper.com/images/whoami/avatar.jpg')
    filename = networker.extract_filename()

    assert filename == "avatar.jpg"


def test_prog_exists():
    fake_program = mserv.prog_exists('fake_prog')
    assert fake_program is False


def test_prog_exists_true():
    real_program = mserv.prog_exists('pip')
    assert real_program is True


# def test_server_setup(tmp_path):
#     print(tmp_path)
#     server_name = "TestServer"
#     mserv.__setup(debug=True, debug_dir=tmp_path, debug_name=server_name)
#     expected_path = os.path.join(tmp_path, server_name)
#     print(expected_path)
#     assert os.path.exists(os.path.join(tmp_path, server_name))
