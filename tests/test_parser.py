import os
import stat

import pytest

from monstermash.parser import ConfigManager


def _make_config(path):
    manager = ConfigManager(str(path))
    config = manager.read()
    config['default'] = {'private_key': 'abc', 'public_key': 'def'}
    manager.write(config)
    return manager


@pytest.mark.skipif(os.name != 'posix', reason='POSIX file permissions only')
def test_write_creates_owner_only_file(tmp_path):
    cfg = tmp_path / 'cfg'
    _make_config(cfg)
    mode = stat.S_IMODE(os.stat(cfg).st_mode)
    assert mode == 0o600


@pytest.mark.skipif(os.name != 'posix', reason='POSIX file permissions only')
def test_read_rejects_loose_permissions(tmp_path):
    cfg = tmp_path / 'cfg'
    manager = _make_config(cfg)
    os.chmod(cfg, 0o644)
    with pytest.raises(ValueError, match='accessible by group/others'):
        manager.read()


def test_read_missing_file_is_noop(tmp_path):
    manager = ConfigManager(str(tmp_path / 'absent'))
    config = manager.read()
    assert config.sections() == []
