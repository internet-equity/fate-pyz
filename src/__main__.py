# -*- coding: utf-8 -*-
"""Extend pyz entrypoint to set default archive extraction path."""
import os
import pathlib
import sys

import _bootstrap


#
# start: our insertion
#

def dir_writeable(path):
    """Whether the given Path `path` is writeable or createable.

    Returns whether the *extant portion* of the given path is writeable.
    If so, the path is either extant and writeable or its nearest extant
    parent is writeable (and as such the path may be created in a
    writeable form).

    """
    while not path.exists():
        parent = path.parent

        # reliably determine whether this is the root
        if parent == path:
            break

        path = parent

    return os.access(path, os.W_OK)


#
# support py38
#
def is_relative_to(path, root):
    """Return True if the path is relative to another path or False."""
    try:
        path.relative_to(root)
    except ValueError:
        return False
    else:
        return True


#
# see also! fate:src/fate/util/os.py
#
def system_path(path):
    """Whether the given Path `path` appears to be a non-user path.

    Returns bool – or None if called on an unsupported platform
    (_i.e._ implicitly False).

    """
    if sys.platform == 'linux':
        return not is_relative_to(path, '/home') and not is_relative_to(path, '/root')

    if sys.platform == 'darwin':
        return not is_relative_to(path, '/Users')


def custom_root(archive,
                build_id,
                system_base='/var/cache',
                user_base=os.getenv('XDG_CACHE_HOME', '~/.cache')):
    """Return an appropriate default extraction path.

    * If the archive is installed to a system path and `system_base` is
      either already populated or writeable by the current user:
      `system_base` will be used.

    * Otherwise: `user_base` will be used.

    """
    #
    # rather than ~/.shiv ...
    #

    archive_path = pathlib.Path(archive.filename).resolve()

    #
    # 1) let's see about /var/cache/
    #
    if system_path(archive_path):
        root = pathlib.Path(system_base) / archive_path.name

        cache = _bootstrap.cache_path(archive, str(root), build_id)
        site_packages = cache / 'site-packages'

        if site_packages.exists() or dir_writeable(cache):
            return root

    #
    # 2) at least let's try to respect XDG
    #
    return pathlib.Path(user_base) / archive_path.name


def bootstrap_root():
    """Set an appropriate extraction path if none has been set in the
    process environment or in the build.

    This dynamically overrides Shiv's default of `~/.shiv` according to
    `custom_root()`.

    """
    with _bootstrap.current_zipfile() as archive:
        envdata = archive.read('environment.json').decode()
        env = _bootstrap.Environment.from_json(envdata)

        if not env.root:
            # push our default down to bootstrap
            root = custom_root(archive, env.build_id)
            os.environ[env.ROOT] = str(root)


bootstrap_root()

#
# end: our insertion
#


_bootstrap.bootstrap()
