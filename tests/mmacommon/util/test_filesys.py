"""
.. module:: filesys
   :synopsis: Unit tests for filesys module
"""

import os
import os.path as op
import shutil

import mmacommon.util.filesys as mf
import pytest

from six.moves import range

@pytest.fixture()
def init_test_folders(request):
    """Remove folder 'foo' and sub-folders at setup and teardown."""
    path = op.join("tests/data", "foo")

    def cleanup():
        if os.path.exists(path):
            shutil.rmtree(path)

    cleanup()
    request.addfinalizer(cleanup)
    return path


def test_create_filename():
    assert len(mf.create_filename()) > 0
    assert mf.create_filename('prefix', '').startswith('prefix')
    assert mf.create_filename('', 'ext').endswith('.ext')


def test_create_filename_is_unique():
    # Create set of 100 file names and verify that they are unique.
    nameset = {mf.create_filename() for _ in range(100)}
    assert len(nameset) == 100


def test_create_temp_filepath():
    assert mf.create_temp_filepath().startswith(mf.TEMP_FOLDER)
    assert mf.create_temp_filepath(relative=False).startswith(os.getcwd())
    assert mf.create_temp_filepath('', 'ext').endswith('.ext')
    assert os.path.exists(mf.TEMP_FOLDER), "temp folder should exist"
    mf.delete_folders(mf.TEMP_FOLDER)  # cleaning up.


def test_delete_file():
    path = 'tests/data/' + mf.create_filename(ext='txt')
    mf.delete_file(path)  # file does not exist. Should be fine.
    with open(path, 'w') as f:
        f.write('foo')
    assert os.path.exists(path)
    mf.delete_file(path)
    assert not os.path.exists(path), "files should be deleted"


def test_create_folders(init_test_folders):
    path = init_test_folders
    mf.create_folders(path)  # make new folder.
    assert os.path.exists(path), "foo should exist"
    mf.create_folders(path)  # make foo again.
    assert os.path.exists(path), "foo should still exist"
    mf.create_folders(op.join(path, "bar"))
    assert os.path.exists(path), "foo/bar should exist"


def test_delete_folders(init_test_folders):
    path = init_test_folders
    mf.delete_folders(path)  # delete non-existing folder is fine.
    os.makedirs(path)
    mf.delete_folders(path)  # delete existing folder.
    assert not os.path.exists(path), "foo should not exist"
    os.makedirs(op.join(path, "bar"))
    mf.delete_folders(path)
    assert not os.path.exists(path), "foo should not exist"


def test_delete_temp_data():
    mf.create_folders(mf.TEMP_FOLDER)
    mf.delete_temp_data()
    assert not os.path.exists(mf.TEMP_FOLDER), "temp folder should not exist"


def test_clear_folder(init_test_folders):
    path = init_test_folders
    bardir, bazfile = op.join(path, "bar"), op.join(path, "baz.txt")
    os.makedirs(bardir)
    open(bazfile, "w").close()
    mf.clear_folder(path)
    assert os.path.exists(path), "foo folder should exist"
    assert not os.path.exists(bardir), "bar folder should not exist"
    assert not os.path.isfile(bazfile), "baz file should not exist"


def test_findpath():
    expected = os.path.join('mma-common', 'tests', 'data', 'data.csv')
    assert mf.findpath('data.csv').endswith(expected)
    assert mf.findpath('data/data.csv').endswith(expected)
    assert mf.findpath('tests/data/data.csv').endswith(expected)

    with pytest.raises(IOError) as ex:
        mf.findpath('ta/data.csv')
    assert str(ex.value).endswith("No such file or directory: 'ta/data.csv'")
