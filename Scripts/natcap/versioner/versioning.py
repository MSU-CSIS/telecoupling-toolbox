import logging
import os
import re
import subprocess

LOGGER = logging.getLogger('natcap.versioner.versioning')
LOGGER.setLevel(logging.ERROR)


class VCSQuerier(object):
    is_archive = False

    def __init__(self, repo_path):
        self._repo_path = repo_path

    def _run_command(self, cmd, cwd=None):
        """Run a subprocess.Popen command.

        All output to stdout, stdin and stderr will be treated as stdout,
        captured, and returned.  Commands are executed as shell commands.

        Parameters:
            cmd (string) - a python string to be executed in the shell.
            cwd=None (string or None) - the string path to the directory on
                disk to use as the CWD.  If None, the current CWD will be
                used.

        Returns:
            A python bytestring of the output of the given command."""
        p = subprocess.check_output(
            cmd, shell=True, stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd)
        return p.strip()  # output without leading/trailing newlines

    @property
    def tag_distance(self):
        raise NotImplementedError

    @property
    def build_id(self):
        raise NotImplementedError

    @property
    def latest_tag(self):
        raise NotImplementedError

    @property
    def branch(self):
        raise NotImplementedError

    @property
    def node(self):
        raise NotImplementedError

    @property
    def release_version(self):
        """This function gets the release version.  Returns either the latest tag
        (if we're on a release tag) or None, if we're on a dev changeset."""
        if self.tag_distance == 0:
            return self.latest_tag
        return None

    @property
    def version(self):
        """This function gets the module's version string.  This will be either the
        dev build ID (if we're on a dev build) or the current tag if we're on a
        known tag.  Either way, the return type is a string."""
        release_version = self.release_version
        if release_version is None:
            return self.build_dev_id(self.build_id)
        return release_version

    def build_dev_id(self, build_id=None):
        """This function builds the dev version string.  Returns a string."""
        if build_id is None:
            build_id = self.build_id
        return 'dev%s' % (build_id)

    def pep440(self, branch=True, method='post'):
        assert method in ['pre', 'post'], ('Versioning method %s '
                                           'not valid') % method

        # If we're at a tag, return the tag only.
        if self.tag_distance == 0:
            return self.latest_tag

        template_string = "%(latesttag)s.%(method)s%(tagdist)s+n%(node)s"
        if branch is True:
            template_string += "-%(branch)s"

        latest_tag = self.latest_tag
        if method == 'pre':
            latest_tag = _increment_tag(latest_tag)

        data = {
            'tagdist': self.tag_distance,
            'latesttag': latest_tag,
            'node': self.node,
            'branch': self.branch,
            'method': method,
        }
        version_string = template_string % data

        return version_string


class HgArchive(VCSQuerier):
    shortnode_len = 12
    is_archive = True
    repo_data_location = '.hg_archival.txt'

    @property
    def build_id(self):
        attrs = _get_archive_attrs(self._repo_path)
        return '{latesttagdistance}:{latesttag} [{node}]'.format(
            latesttagdistance=attrs['latesttagdistance'],
            latesttag=attrs['latesttag'],
            node=attrs['node'][:self.shortnode_len],
        )

    @property
    def tag_distance(self):
        try:
            return _get_archive_attrs(self._repo_path)['latesttagdistance']
        except KeyError:
            # This happens when we are at a tag.
            return 0

    @property
    def latest_tag(self):
        attrs = _get_archive_attrs(self._repo_path)
        try:
            return unicode(attrs['latesttag'])
        except KeyError:
            # This happens when we are at a tag.
            return unicode(attrs['tag'])

    @property
    def branch(self):
        return _get_archive_attrs(self._repo_path)['branch']

    @property
    def node(self):
        return _get_archive_attrs(self._repo_path)['node'][:self.shortnode_len]


class HgRepo(VCSQuerier):
    is_archive = False
    repo_data_location = '.hg'

    def _log_template(self, template_string):
        hg_call = 'hg log -R %s -r . --config ui.report_untrusted=False'
        cmd = (hg_call + ' --template="%s"') % (self._repo_path,
                                                template_string)
        return self._run_command(cmd)

    @property
    def build_id(self):
        """Call mercurial with a template argument to get the build ID.  Returns a
        python bytestring."""
        return self._log_template('{latesttagdistance}:{latesttag} '
                                  '[{node|short}]')

    @property
    def tag_distance(self):
        """Call mercurial with a template argument to get the distance to the latest
        tag.  Returns an int."""
        return int(self._log_template('{latesttagdistance}'))

    @property
    def latest_tag(self):
        """Call mercurial with a template argument to get the latest tag.  Returns a
        python bytestring."""
        return self._log_template('{latesttag}')

    @property
    def branch(self):
        """Get the current branch from hg."""
        return self._log_template('{branch}')

    @property
    def node(self):
        return self._log_template('{node|short}')


class GitRepo(VCSQuerier):
    repo_data_location = '.git'

    def __init__(self, repo_uri):
        VCSQuerier.__init__(self, repo_uri)
        self._tag_distance = None
        self._latest_tag = None
        self._commit_hash = None

    def _run_command(self, cmd):
        return VCSQuerier._run_command(self, cmd, self._repo_path)

    @property
    def branch(self):
        branch_cmd = 'git branch'
        current_branches = self._run_command(branch_cmd)
        for line in current_branches.split('\n'):
            if line.startswith('* '):
                return line.replace('* ', '').strip()
        raise IOError('Could not detect current branch')

    def _describe_current_rev(self):
        self._tag_distance = None
        self._latest_tag = None
        self._commit_hash = None

        current_branch = self.branch
        try:
            data = self._run_command('git describe --tags')
        except subprocess.CalledProcessError:
            # when there are no tags
            self._latest_tag = 'null'

            num_commits_cmd = 'git rev-list %s --count' % current_branch
            self._tag_distance = self._run_command(num_commits_cmd)

            commit_hash_cmd = 'git log -1 --pretty="format:%h"'
            self._commit_hash = self._run_command(commit_hash_cmd)
        else:
            if '-' not in data:
                # then we're at a tag
                self._latest_tag = str(data)
                self._tag_distance = 0

                commit_hash_cmd = 'git log -1 --pretty="format:%h"'
                self._commit_hash = self._run_command(commit_hash_cmd)
            else:
                # we're not at a tag, so data has the format:
                # data = tagname-tagdistange-commit_hash
                tagname, tag_dist, _commit_hash = data.split('-')
                self._tag_distance = int(tag_dist)
                self._latest_tag = tagname
                self._commit_hash = self.node

    @property
    def build_id(self):
        self._describe_current_rev()
        return "%s:%s [%s]" % (self._tag_distance, self._latest_tag,
                               self._commit_hash)

    @property
    def tag_distance(self):
        self._describe_current_rev()
        return self._tag_distance

    @property
    def latest_tag(self):
        self._describe_current_rev()
        return self._latest_tag

    @property
    def node(self):
        return self._run_command('git rev-parse HEAD').strip()[:8]

    @property
    def is_archive(self):
        # Archives are a mercurial feature.
        return False


def _increment_tag(version_string):
    assert len(re.findall('([0-9].?)+', version_string)) >= 1, (
        'Version string must be a release')

    # increment the minor version number and not the update num.
    tag = [int(s) for s in version_string.split('.')]
    tag[-1] += 1
    return '.'.join([str(i) for i in tag])


def _get_archive_attrs(archive_path):
    """
    If we're in an hg archive, there will be a file '.hg_archival.txt' in the
    repo root.  If this is the case, we can fetch relevant build information
    from this file that we might normally be able to get directly from hg.

    Parameters:
        attr (string): The archive attr to fetch.  One of
        "repo"|"node"|"branch"|"latesttag"|"latesttagdistance"|"changessincelatesttag"
        archive_path (string): The path to the mercurial archive.
            The .hg_archival.txt file must exist right inside this directory.

    Returns:
        A dict of the attributes within the .hg_archival file.

    Raises:
        IOError when the .hg_archival.txt file cannot be found.
        KeyError when `attr` is not in .hg_archival.txt
    """
    archival_filepath = os.path.join(archive_path, '.hg_archival.txt')
    attributes = {}
    with open(archival_filepath) as archival_file:
        for line in archival_file:
            attr_name, value = line.strip().split(': ')

            # Try to cast the attribute to an int (since it might be a
            # revision number).  If it doesn't cast, leave it as a string.
            try:
                 value = int(value)
            except ValueError:
                pass
            attributes[attr_name] = value

    return attributes
