import os
import sys
import pkg_resources
import importlib
import logging

LOGGER = logging.getLogger('natcap.versioner')
LOGGER.setLevel(logging.ERROR)


class VersionNotFound(RuntimeError):
    """
    A custom exception for when the version is not found.
    """
    pass


__version__ = '0.4.0'
SCM_ALLOW = 'allow scm fallback'
SCM_DISALLOW = 'disallow scm fallback'
SCM_NOTFROZEN = 'allow scm in non-frozen enviroments (disallow when frozen)'


def get_version(package, root='.', ver_module=None, allow_scm=SCM_NOTFROZEN):
    """
    Get the version string for the target package.

    If `package` is not available for import, check the root for git or hg.

    Parameters:
        package (string): The package name to check for (e.g. 'natcap.invest')
        root='.' (string): The path to the directory to check for a DVCS
            repository.
        ver_module=None (string): The versioning module name, relative to
            `package`.
        allow_scm=SCM_NOTFROZEN (string): Whether to allow fallback to SCM.
            Must be one of SCM_ALLOW, SCM_DISALLOW, or SCM_NOTFROZEN.

    Returns:
        A DVCS-aware versioning string.
    """

    if ver_module is None:
        ver_module = 'version'

    # Prefer to import the version file
    full_module = '.'.join([package, ver_module])
    try:
        module = importlib.import_module(full_module)
        return module.version
    except ImportError:
        pass

    # Next, try to get the info from installed package metadata
    try:
        return pkg_resources.require(package)[0].version
    except pkg_resources.DistributionNotFound:
        pass

    if allow_scm == SCM_DISALLOW:
        raise VersionNotFound((
            'Version module %s not found and SCM fallback '
            'disallowed') % full_module)

    # If we're in a frozen environment and the user is not allowing the use of
    # SCM in a frozen environment, raise VersionNotFrozen.
    is_frozen = hasattr(sys, '_MEIPASS') or hasattr(sys, 'frozen')
    if is_frozen and allow_scm != SCM_NOTFROZEN:
        # we're in a pyinstaller or py2app/py2exe binary, so the target
        # package's version module was not included as a hiddenimport.
        raise VersionNotFound(
            ('The version module %s was not found in the frozen distribution. '
             'Perhaps it needs to be added as a hiddenimport?') % full_module)

    # Lastly, get the version from source control
    return vcs_version(root)


def parse_version(root='.'):
    """
    Determine the correct source from which to parse the version.

    If PKG-INFO exists, then we're in a source or binary distribution so prefer
    to extract this metadata first.  Otherwise, If we're in an hg or git repo,
    get the version from SCM.

    Parameters:
        root='.' (string): The root directory to search for vcs information.
            This should be the path to the repository root.

    Returns:
        A versioning string.
    """

    pkginfo_filepath = os.path.join(root, 'PKG-INFO')
    if os.path.exists(pkginfo_filepath):
        with open(pkginfo_filepath) as pkginfo_file:
            for line in pkginfo_file:
                if line.startswith('Version'):
                    return line.split(': ')[1].rstrip()

    return vcs_version(root)


ERROR_RAISE = 'raise exception on error'
ERROR_RETURN = 'return a string error message on error'


def vcs_version(root='.', on_error=ERROR_RAISE):
    """
    Get the version string from your VCS.

    Parameters:
        root='.' (string): The root directory to search for vcs information.
            This should be the path to the repository root.
        on_error=ERROR_RAISE (string): What to do when an exception is
            encountered in the SCM version parsing.  One of ERROR_RAISE,
            ERROR_RETURN.  If ERROR_RAISE, VersionNotFound will be raised.
            If ERROR_RETURN, a string message will be returned instead.
    """
    from versioning import HgArchive, HgRepo, GitRepo

    error = False
    try:
        for scm_class in [HgArchive, HgRepo, GitRepo]:
            repo_data = os.path.join(root, scm_class.repo_data_location)
            if os.path.exists(repo_data):
                break
        repo = scm_class(root)
        version = repo.pep440(branch=False)
    except Exception as error:
        LOGGER.exception(error)
        version = 'UNKNOWN'
        error = True

    if error and on_error == ERROR_RAISE:
        root_path = os.path.abspath(root)
        raise VersionNotFound((
            'A version could not be loaded from scm in %s' % root_path))

    return version
