"""Upload all files listed to a ESP device."""
import argparse
import colorama
import filecmp
import getpass
import pathlib
import re
import shutil
import subprocess
import serial.tools.list_ports


def get_serial_port():
    ports = serial.tools.list_ports.comports()
    assert len(ports), "No COM ports found!"
    choice = '0'
    if len(ports) > 1:
        for i, (port, desc, hw_id) in enumerate(sorted(ports)):
            print(f'{i}) {port}: {desc} [{hw_id}]')
        while (choice := input(f'Specify nr 0..{len(ports)-1}:')) not in [f'{nr}' for nr in range(len(ports))]:
            pass
    return sorted(ports)[int(choice)][0]


class Synchronizer:
    def __init__(self, cache: pathlib.Path):
        self.cache = cache

    def upload(self, file: pathlib.Path, destination: str = '') -> bool:
        """Upload the specified file to the given destination on the device.

        Args:
            file: source file.
            destination: destination path on the device.

        Returns:
            True if the file is updated, False if the file did not change.
        """
        assert file.exists(), f'{file} does not exist!'
        cache_filename = self.cache / destination / file.name
        if cache_filename.exists() and filecmp.cmp(file, cache_filename):
            return False
        mk_dir = not cache_filename.parent.exists()

        self._upload(file, destination, mk_dir)
        cache_filename.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, cache_filename)
        return True

    def _upload(self, file: pathlib.Path, destination: str, mk_dir: bool):
        raise NotImplementedError


class SerialSynchronizer(Synchronizer):
    def __init__(self, port: str, cache: pathlib.Path):
        super().__init__(cache / f'.{port}')
        self.port = port

    def _upload(self, file: pathlib.Path, destination: str, mk_dir: bool):
        addition = f'md {destination}; ' if mk_dir else ''
        print(f'COPY: {file} to {self.port}: {destination}/{file.name}')
        process = subprocess.Popen(f'mpfshell -n -c "open {self.port}; {addition}put {file.name} {destination}/{file.name}"',
                                   cwd=file.parent,
                                   universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode or 'Failed' in stdout:
            if stdout:
                print(colorama.Fore.RED + stdout + colorama.Style.NORMAL)
            if stderr:
                print(colorama.Fore.RED + stderr + colorama.Style.NORMAL)
            assert False, 'Upload failed!'


def get_synchronizer(destination: str, cache: pathlib.Path) -> Synchronizer:
    # TODO: add support for webrepl
    assert destination.startswith('COM'), f'destination: "{destination}" not yet supported!'
    return SerialSynchronizer(destination, cache)


def upload_all(list_file: pathlib.Path, synchronizer: Synchronizer):
    splitter = re.compile(r'^(\")?([^\"]+)?\1? (\")?([^\"]*)?\3?$')
    source_folder = list_file.parent
    updates_pending = False
    with open(list_file) as fh:
        for line in fh:
            if (line := line.strip()) and not line.startswith('#'):  # Skip empty and comment lines
                if match := splitter.match(line):
                    _, source, _, target = match.groups()
                    for source_file in source_folder.glob(source):
                        updates_pending |= synchronizer.upload(source_file, target)
                else:
                    updates_pending |= upload_all(source_folder / line.strip(), synchronizer)
    return updates_pending


def main():
    """Main script interface."""
    parser = argparse.ArgumentParser(description='Upload files to ESP device.')
    parser.add_argument('source', type=pathlib.Path,
                        help='Source file containing a list of files to upload to the device')
    parser.add_argument('--destination', default=None,
                        help='Destination port or ip-address of the ESP device.')
    parser.add_argument('--auto_network_config', default=None,
                        help='Destination port or ip-address of the ESP device.')
    args = parser.parse_args()

    assert args.source.is_file(), '{args.source} is not a file!'

    source_folder = args.source.parent
    synchronizer = SerialSynchronizer(args.destination or get_serial_port(), source_folder / '__cache__')

    updates_pending = False
    if args.auto_network_config:
        path = source_folder / 'network_config.json'
        if not path.exists():
            generic_path = pathlib.Path(__name__).parent / 'network_config.json'
            if generic_path.exists():
                path = generic_path
            else:
                # create a network_config.json file
                with open(path, 'w') as fh:
                    ssid = input('Network ssid')
                    pw = getpass.getpass(prompt='Network password: ')
                    fh.write(f'{"ssid": "{ssid}", "__password": "{pw}"}')
        updates_pending |= synchronizer.upload(path)

    updates_pending |= upload_all(args.source, synchronizer)

    if updates_pending:
        print(colorama.Fore.RED + 'Reboot the device to activate the changes!',
              colorama.Fore.YELLOW + 'import machine; machine.reset()',
              colorama.Fore.RED + 'or Ctrl-d in the micropython shell.' + colorama.Style.RESET_ALL,
              sep='\n')


if __name__ == '__main__':
    colorama.init()
    main()
