#!/usr/bin/env python3
"""
salt-ext-modules-vmware release script

This script automates the release process, such that anyone who has a correctly
configured system may deploy saltext.vmware. A correctly configured virtual
environment, gpg, and pypirc are required. Before running this script `python
-m nox -e tests-3` should pass all tests.

This build process will take place in a temporary directory. The output of this
script is:

- an updated changelog, committed to git
- the signed release uploaded to test.pypi.org
- the signed release uploaded to pypi.org
- the released commit tagged and pushed to saltstack/salt-ext-modules-vmware
- a /tmp/saltext.vmware-build-{version}.tar.gz file, containing the output of
  the release process
"""
import ast
import configparser
import contextlib
import logging
import os
import pathlib
import subprocess
import sys
import tempfile

DEBUG_FORCE = False

log = logging.getLogger("extmod-release")
REPO_ROOT = pathlib.Path(__file__).parent.parent
TYPICAL_ENV = REPO_ROOT / "env" / "bin" / "python"
VENV_PYTHON = pathlib.Path(os.environ.get("VMWARE_VENV_PATH", TYPICAL_ENV))
YES = ("y", "yes", "si", "sim", "ja", "oui")


####################
# Helper Functions #
####################


def run_and_log_cmd(*cmd):
    log.debug("Running command %r", cmd)
    ret = subprocess.run(cmd, capture_output=True)
    log.debug(f"git status return code: %r", ret.returncode)
    log.debug(f"git status stdout: \n%s", ret.stdout.decode() or "<No stdout>")
    log.debug(f"git status stderr: \n%s", ret.stderr.decode() or "<No stderr>")
    return ret


@contextlib.contextmanager
def msg_wrap(msg):
    print(f"{msg}...", end="")
    sys.stdout.flush()
    try:
        yield
    except:
        print("FAIL")
        log.exception("Inner command failed")
        raise
    else:
        print("OK")


@contextlib.contextmanager
def make_archive(path):
    try:
        yield
    finally:
        run_and_log_cmd("tar", "-czf", path, "-C", os.getcwd(), ".")


########################
# End Helper Functions #
########################


###################
# Check Functions #
###################

# These are to ensure that the system has the required bits to run the release


def check_python_env():
    with msg_wrap("Checking python environment"):
        if sys.base_prefix != sys.prefix:
            exit(
                f"This python {sys.executable} is in a venv - deactivate and run using system python."
            )
        if not VENV_PYTHON.exists():
            exit(
                f"Python venv {VENV_PYTHON} does not exist. Set VMWARE_VENV_PATH environment variable, or run `python -m venv --prompt vmw-ext {TYPICAL_ENV.parent.parent}` to create a new virtualenv"
            )


def check_pypirc():
    with msg_wrap("Checking ~/.pypirc"):
        pypirc_path = pathlib.Path("~/.pypirc").expanduser()
        if not pypirc_path.exists():
            exit("No ~/.pypirc - will not be able to upload with twine")
        else:
            config = configparser.ConfigParser()
            config.read(pypirc_path)
            servers = [x for x in config["distutils"]["index-servers"].splitlines() if x]
            if "saltext_vmware" not in servers:
                exit("No saltext_vmware in pypirc, unable to do a prod deploy")
            elif "test_saltext_vmware" not in servers:
                exit("No test_saltext_vmware in pypirc, unable to do a test deploy")


def check_git_status():
    with msg_wrap("Checking git status"):
        ret = run_and_log_cmd("git", "-C", str(REPO_ROOT), "status", "--porcelain")
        if ret.stdout and not DEBUG_FORCE:
            exit("You currently have changes in your repo. Stash or otherwise clear your changes.")


def check_gpg():
    with msg_wrap("Checking gpg/gpg agent"):
        with open("fnord.txt", "w") as f:
            f.write("contents")
        # We need a better way to gpg sign releases -- not just individuals
        ret = run_and_log_cmd("gpg", "--armor", "--detach-sign", "fnord.txt")
        if ret.returncode:
            exit("Unable to use gpg --detach-sign. Check your gpg-agent and try again.")

        ret = run_and_log_cmd("gpg", "--verify", "fnord.txt.asc", "fnord.txt")
        if ret.returncode:
            exit(
                "Unable to verify gpg signature. Can you run `echo hello | gpg --armor --clear-sign | gpg --verify`?"
            )


def check_mod_version():
    version_file = REPO_ROOT / "src" / "saltext" / "vmware" / "version.py"
    with version_file.open() as f:
        for line in f:
            if line.startswith("__version__"):
                p = ast.parse(line)
                version = p.body[0].value.value
    return version


#######################
# End Check Functions #
#######################


#####################
# Release Functions #
#####################

# These functions are for actually making changes that are part of the release.
# These changes should not be really destructive, but users should still be
# able to bail out with minimal changes to their systems!


def ensure_venv_deps():
    with msg_wrap("Ensuring build/release deps are installed in venv"):
        run_and_log_cmd(
            str(VENV_PYTHON), "-m", "pip", "install", "-e", f"{REPO_ROOT}[dev,tests,release]"
        )


def build_package(*, dist_dir):
    with msg_wrap("Building the current package"):
        run_and_log_cmd(
            str(VENV_PYTHON),
            "-m",
            "pip",
            "wheel",
            "--wheel-dir",
            str(dist_dir),
            f"{REPO_ROOT}[dev,tests]",
        )


def test_package(*, tempdir, dist_dir):
    test_virtualenv_path = pathlib.Path(tempdir) / "test_env"
    test_python = test_virtualenv_path / "bin" / "python"
    release_virtualenv_path = test_virtualenv_path.parent / "release_env"

    with msg_wrap("Creating a new virtualenv for testing"):
        run_and_log_cmd(
            sys.executable, "-m", "venv", "--prompt", "test_env", str(test_virtualenv_path)
        )

    with msg_wrap("Installing dev version of mod in test virtualenv"):
        run_and_log_cmd(
            str(test_python),
            "-m",
            "pip",
            "install",
            "saltext.vmware[dev,tests]",
            "--no-index",
            "--find-links",
            str(dist_dir),
        )

    with msg_wrap("Getting saltext version"):
        ret = run_and_log_cmd(str(test_python.parent / "salt"), "--versions-report")
        version = next(
            line
            for line in ret.stdout.decode().splitlines()
            if line.strip().startswith("saltext.vmware: ")
        ).partition(": ")[-1]

    with msg_wrap(f"Running tests for version {version}"):
        ret = run_and_log_cmd(
            str(test_python),
            "-m",
            "pytest",
            f"{REPO_ROOT}/tests/",
        )
        if ret.returncode:
            exit("Test run failed")


def prepare_deployment(*, dist_dir, version):
    with msg_wrap("Signing saltext wheel"):
        ret = run_and_log_cmd(
            "gpg",
            "--armor",
            "--detach-sign",
            str(dist_dir / f"saltext.vmware-{version}-py2.py3-none-any.whl"),
        )

    with msg_wrap("Verifying signature"):
        ret = run_and_log_cmd(
            "gpg",
            "--verify",
            str(dist_dir / f"saltext.vmware-{version}-py2.py3-none-any.whl.asc"),
            str(dist_dir / f"saltext.vmware-{version}-py2.py3-none-any.whl"),
        )


def commit_changlog_entries(*, version):
    # 1.2.3rc1 will return False (non-normal) while 1.2.3 will be True
    is_normal_release = version.replace(".", "").isnumeric()
    with msg_wrap("Generating changelog"):
        pwd = os.getcwd()
        version_args = () if is_normal_release else ("--version", f"{version} (Unreleased)")
        try:
            os.chdir(REPO_ROOT)
            ret = run_and_log_cmd(
                str(VENV_PYTHON.with_name("towncrier")),
                "build",
                "--draft",
                *version_args,
            )
        finally:
            os.chdir(pwd)
        with open(f"changelog-{version}.txt", "wb") as f:
            f.write(ret.stdout)
        if b"No significant changes" in ret.stdout:
            keep_going = (
                input("Towncrier detected no changes. Continue deployment? [y/N]: ").strip().lower()
                in YES
            )
            if not keep_going:
                exit("abort")
        # For unreleased versions we won't update the changelog
        if is_normal_release:
            try:
                os.chdir(REPO_ROOT)
                ret = run_and_log_cmd(
                    str(VENV_PYTHON.with_name("towncrier")),
                    "build",
                )
            finally:
                os.chdir(pwd)
            ret = run_and_log_cmd(
                "git",
                "-C",
                str(REPO_ROOT),
                "commit",
                "-m",
                f"Changelog for release {version}",
            )


def twine_check_package(*, dist_dir, version):
    with msg_wrap("Running twine check on saltext.vmware package"):
        ret = run_and_log_cmd(
            str(VENV_PYTHON.with_name("twine")),
            "check",
            str(dist_dir / f"saltext.vmware-{version}-py2.py3-none-any.whl"),
        )
        if f"PASSED" not in "".join(ret.stdout.decode().split("\n")):
            exit("Twine check failed")


def deploy_to_test_pypi(*, dist_dir, version):
    with msg_wrap("Deploying to TEST PyPI"):
        ret = run_and_log_cmd(
            str(VENV_PYTHON.with_name("twine")),
            "upload",
            "-r",
            "test_saltext_vmware",
            str(dist_dir / f"saltext.vmware-{version}-py2.py3-none-any.whl"),
            str(dist_dir / f"saltext.vmware-{version}-py2.py3-none-any.whl.asc"),
        )
        if ret.returncode:
            exit("Deploy to test pypi failed")


def deploy_to_real_pypi(*, dist_dir, version):
    with msg_wrap("Deploying to REAL PyPI"):
        ret = run_and_log_cmd(
            str(VENV_PYTHON.with_name("twine")),
            "upload",
            "-r",
            "saltext_vmware",
            str(dist_dir / f"saltext.vmware-{version}-py2.py3-none-any.whl"),
            str(dist_dir / f"saltext.vmware-{version}-py2.py3-none-any.whl.asc"),
        )
        if ret.returncode:
            exit("Deploy to real pypi failed")


def tag_deployment(*, version):
    changelog_path = pathlib.Path(f"changelog-{version}.txt").resolve()
    with msg_wrap(f"Tagging version {version}"):
        ret = run_and_log_cmd(
            "git", "-C", str(REPO_ROOT), "tag", "-F", str(changelog_path), "-a", version
        )
        if ret.returncode:
            exit(1)


def push_tag_to_salt(*, version):
    with msg_wrap(f"Pushing tag {version} to salt repo"):
        ret = run_and_log_cmd(
            "git",
            "-C",
            str(REPO_ROOT),
            "push",
            "git+ssh://git@github.com/saltstack/salt-ext-modules-vmware.git",
            version,
        )
        if ret.returncode:
            exit("Pushing tag failed")


#########################
# End Release Functions #
#########################


@contextlib.contextmanager
def tempdir_and_save_log_on_error():
    with tempfile.TemporaryDirectory() as tempdir:
        logfile = pathlib.Path(tempdir) / "release.log"
        try:
            yield tempdir
        except:
            with tempfile.NamedTemporaryFile(
                delete=False, prefix="release_", suffix=".log"
            ) as savelog:
                savefile = pathlib.Path(savelog.name)
            savefile.parent.mkdir(parents=True, exist_ok=True)
            logfile.rename(savefile)
            print("Failure detected - log saved to", str(savefile))


def do_it(non_interactive=False):  # Shia LeBeouf!
    """
    Actually cut a release. Use non_interactive to try and run in a one-shot
    process. Might fail if lacking gpg-agent or something.
    """
    pwd = os.getcwd()
    with tempdir_and_save_log_on_error() as tempdir:
        dist_dir = pathlib.Path(tempdir) / "dist"
        dist_dir.mkdir(parents=True, exist_ok=True)

        os.chdir(tempdir)
        print(f"To see more information, run `tail -f {tempdir}/release.log`")
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.FileHandler("release.log"))

        # None of these make system changes. Can totally bail out without
        # screwing anything up here.
        version = check_mod_version()
        with make_archive(f"/tmp/saltext.vmware-build-{version}.tar.gz"):
            print(f"Releasing version {version}")
            print(f"Path to venv python: {VENV_PYTHON}")
            check_python_env()
            check_pypirc()
            check_git_status()
            check_gpg()

            print()
            print("***ACTUAL DEPLOY AHEAD!***")
            print()
            print(
                "If your system is correctly configured, choosing to continue will result in a real live deploy of saltext.vmware! Are you ready?"
            )
            print()
            # Here's where we start to make changes!
            keep_going = (
                non_interactive
                or input(f"Continue to build and test saltext.vmware version {version}? [y/N]: ")
                .lower()
                .strip()
                in YES
            )
            if not keep_going:
                exit("Abort")

            ensure_venv_deps()
            commit_changlog_entries(version=version)
            build_package(dist_dir=dist_dir)
            twine_check_package(dist_dir=dist_dir, version=version)
            test_package(tempdir=tempdir, dist_dir=dist_dir)
            prepare_deployment(dist_dir=dist_dir, version=version)
            really_deploy = input(
                f'WARNING: This will really upload saltext.vmware version {version} to pypi. There is no going back from this point. \nEnter "deploy" without quotes to really deploy: '
            )
            if really_deploy != "deploy":
                exit(f"Aborting version {version} deploy")
            deploy_to_test_pypi(dist_dir=dist_dir, version=version)
            deploy_to_real_pypi(dist_dir=dist_dir, version=version)
            tag_deployment(version=version)
            push_tag_to_salt(version=version)

            input(
                f"<enter> to finish and cleanup - {tempdir} will be archived at /tmp/saltext.vmware-build-{version}.tar.gz"
            )

    os.chdir(pwd)


if __name__ == "__main__":
    do_it()
