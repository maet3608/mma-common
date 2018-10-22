"""
.. module:: filesys
   :synopsis: File system utilities.
"""

import glob
import os
import os.path as op
import shutil
import uuid
import errno

TEMP_FOLDER = 'temp'


def create_filename(prefix='', ext=''):
    """
    Create a unique filename.

    :param str prefix: Prefix to add to filename.
    :param str ext: Extension to append to filename, e.g. 'jpg'
    :return: Unique filename.
    :rtype: str
    """
    suffix = '.' + ext if ext else ''
    return prefix + str(uuid.uuid4()) + suffix


def create_temp_filepath(prefix='', ext='', relative=True):
    """
    Create a temporary folder under :py:data:`TEMP_FOLDER`.

    If the folder already exists do nothing. Return relative (default) or
    absolute path to a temp file with a unique name.

    See related function :func:`.create_filename`.

    :param str prefix: Prefix to add to filename.
    :param str ext: Extension to append to filename, e.g. 'jpg'
    :param bool relative: True: return relative path, otherwise absolute path.
    :return: Path to file with unique name in temp folder.
    :rtype: str
    """
    create_folders(TEMP_FOLDER)
    rel_path = op.join(TEMP_FOLDER, create_filename(prefix, ext))
    return rel_path if relative else op.abspath(rel_path)


def create_folders(path, mode=0o777):
    """
    Create folder(s). Don't fail if already existing.

    See related functions :func:`.delete_folders` and :func:`.clear_folder`.

    :param str path: Path of folders to create, e.g. 'foo/bar'
    :param int mode: File creation mode, e.g. 0o777
    """
    if not os.path.exists(path):
        os.makedirs(path, mode)


def delete_file(path):
    """
    Remove file at given path. Don't fail if non-existing.

    :param str path: Path to file to delete, e.g. 'foo/bar/file.txt'
    """
    if os.path.exists(path):
        os.remove(path)


def delete_folders(path):
    """
    Remove folder and sub-folders. Don't fail if non-existing or not empty.

    :param str path: Path of folders to delete, e.g. 'foo/bar'
    """
    if os.path.exists(path):
        shutil.rmtree(path)


def delete_temp_data():
    """
    Remove :py:data:`TEMP_FOLDER` and all its contents.
    """
    delete_folders(TEMP_FOLDER)


def clear_folder(path):
    """
    Remove all content (files and folders) within the specified folder.

    :param str path: Path of folder to clear.
    """
    for sub_path in glob.glob(op.join(path, "*")):
        if os.path.isfile(sub_path):
            os.remove(sub_path)
        else:
            shutil.rmtree(sub_path)


def findpath(filepath, top='.'):
    """
    Return full path for given filepath.

    Finds full path by searching the entire directory tree for the filepath.

    :param str filepath: Name of file or partial path to file.
    :param str top: Name of directory to start search from.
    :return: Full path to file
    :rtype: str
    :raise: IOError if file cannot be found.
    """

    def normalize(path):
        """Normalize path separators"""
        if not path:
            return '/'
        path = path.replace('\\', '/')
        path = path[2:] if path.startswith('./') else path
        return '/' + path + '/'

    basepath, filename = op.split(filepath)
    basepath = normalize(basepath)
    for root, _, files in os.walk(top):
        abspath = normalize(op.abspath(root))
        if abspath.endswith(basepath):
            for name in files:
                if name == filename:
                    return op.abspath(op.join(root, name))
    raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)
