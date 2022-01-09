import builtins
import pathlib
import pytest
import tempfile

import upload_all


def test_get_serial_port_none():
    with pytest.raises(AssertionError):
        upload_all.get_serial_port()


def test_get_serial_port_one(mocker):
    mocker.patch('upload_all.serial.tools.list_ports.comports',
                 return_value=[('COM99', None, None)])
    assert upload_all.get_serial_port() == 'COM99'


def test_get_serial_port_multiple(mocker):
    test_ports = ['COM99', 'COM19', 'COM9']
    mocker.patch('upload_all.serial.tools.list_ports.comports',
                 return_value=[(port, None, None) for port in test_ports])

    inputs = ['invalid', '0', '9', '-1', '2', '1']

    mocker.patch.object(builtins, 'input', lambda _, : inputs.pop(0))
    sorted_ports = sorted(test_ports)  # ports are sorted in upload_all()
    assert upload_all.get_serial_port() == sorted_ports[0]
    assert upload_all.get_serial_port() == sorted_ports[2]
    assert upload_all.get_serial_port() == sorted_ports[1]


def test_failed_to_open(capsys, mocker):
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = pathlib.Path(tmpdirname)
        with pytest.raises(AssertionError):
            upload_all.get_synchronizer('unknown', tmpdir)

        synchronizer = upload_all.get_synchronizer('COM99', tmpdir)
        mocker.patch('upload_all.subprocess.Popen', return_value='TODO')
        captured = capsys.readouterr()
        with pytest.raises(AssertionError):
            file = tmpdir / 'tmp.py'
            with open(file, 'w'):
                pass
            synchronizer.upload(file)
        #assert 'Failed to open: ser: COM99' in captured.out
