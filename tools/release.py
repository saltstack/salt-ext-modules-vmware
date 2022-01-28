#!/usr/bin/env python3
"""
salt-ext-modules-vmware release script

The goal of this script is to simplify the release process, such that anyone
with the proper permissions should be able to run this script to generate a
release.

Release artifacts:
- wheel
- wheel.asc signature

When the wheel & sig file are tested & validated, then we want to tag the git revision and push it all to the places.

Would it be so wrong to update the version and commit before building? Or I suppose correctly we should ask.

"We're about to run tests for version X - would you like to continue?"

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
DEBUG_FORCE = True

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
        # TODO: need a better way to gpg sign releases
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
        # run_and_log_cmd(str(test_python), '-m', 'nox', '-f', f'{REPO_ROOT}/noxfile.py', '-e', 'tests-3')
        ret = run_and_log_cmd(
            str(test_python),
            "-m",
            "pytest",
            f"{REPO_ROOT}/tests/unit",  # TODO: not unit
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
    with msg_wrap("Generating changelog"):
        ret = run_and_log_cmd(
            str(VENV_PYTHON.with_name("towncrier")),
            "build",
            "--draft",
        )
        with open(f"changelog-{version}.txt", "w") as f:
            f.write(ret.stdout)
        if "No significant changes" in ret.stdout:
            keep_going = (
                input("Towncrier detected no changes. Continue deployment? [y/N]: ").strip().lower()
                in YES
            )
            if not keep_going:
                exit("abort")
        ret = run_and_log_cmd(
            str(VENV_PYTHON.with_name("towncrier")),
            "build",
        )
        ret = run_and_log_cmd


def twine_check_package(*, dist_dir, version):
    with msg_wrap("Running twine check on saltext.vmware package"):
        ret = run_and_log_cmd(
            str(VENV_PYTHON.with_name("twine")),
            "check",
            str(dist_dir / f"saltext.vmware-{version}-py2.py3-none-any.whl"),
        )
        if f"saltext.vmware-{version}-py2.py3-none-any.whl: PASSED" not in ret.stdout:
            exit("Twine check failed")


def deploy_to_test_pypi(*, diist_dir, version):
    return  # TODO REMOVEME
    with msg_wrap("Deploying to test pypi"):
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
    return  # TODO REMOVEME
    with msg_wrap("Deploying to REAL pypi"):
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
    with msg_wrap(f"Tagging version {version}"):
        ret = run_and_log_cmd(
            "git", "-C", str(REPO_ROOT), "tag", "-F", f"changelog-{version}.txt", "-a", version
        )
        if ret.returncode:
            exit(1)


def push_tag_to_salt(*, version):
    with msg_wrap(f"Pushing tag {version} to salt repo"):
        # TODO: salt not wayne
        ret = run_and_log_cmd(
            "git", "push", "git+ssh://git@github.com/waynew/salt-ext-modules-vmware.git", version
        )
        if ret.returncode:
            exit("Pushing tag failed")


#########################
# End Release Functions #
#########################


def do_it(non_interactive=False):  # Shia LeBeouf!
    """
    Actually cut a release. Use non_interactive to try and run in a one-shot
    process. Might fail if lacking gpg-agent or something.
    """
    pwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tempdir:
        dist_dir = pathlib.Path(tempdir) / "dist"
        dist_dir.mkdir(parents=True, exist_ok=True)

        os.chdir(tempdir)
        print(f"To see more information, run `tail -f {tempdir}/release.log`")
        log.setLevel(logging.DEBUG)
        log.addHandler(logging.FileHandler("release.log"))

        # None of these make system changes. Can totally bail out without
        # screwing anything up here.
        version = check_mod_version()
        print("Releasing version {version}")
        print(f"Path to venv python: {VENV_PYTHON}")
        check_python_env()
        check_pypirc()
        check_git_status()
        check_gpg()

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
        deploy_to_test_pypi(dist_dir=dist_dir, version=version)
        deploy_to_real_pypi(dist_dir=dist_dir, version=version)
        tag_deployment(version=version)
        push_tag_to_salt(version=version)

        input(f"enter to finish and cleanup - {tempdir} will be deleted")

    os.chdir(pwd)


def fake_it():
    import time

    keep_going = input("Building release version 22.01.06, continue? [y/N]: ")
    with msg_wrap("Generating changelog/release for commit"):
        time.sleep(0.5)

    with msg_wrap("Creating dev dir"):
        time.sleep(0.5)

    with msg_wrap("Creating venv for tests"):
        time.sleep(0.5)

    with msg_wrap("Building package wheels"):
        time.sleep(0.5)

    with msg_wrap("Installing saltext.vmware"):
        time.sleep(1)

    with msg_wrap("Running full test suite via nox"):
        time.sleep(1)

    with msg_wrap("Running tests via pytest"):
        time.sleep(5)

    keep_going = input("Tests are passing. Continue to sign package, deploy to dev pypi? [y/N]: ")

    with msg_wrap("Signing .whl"):
        time.sleep(0.5)

    with msg_wrap("Deploying build and signature to dev pypi"):
        time.sleep(2)

    print(
        "Deploy to dev pypi successful. See https://test.pypi.org/project/saltext.vmware/ to confirm."
    )

    keep_going = input("Deploy to prod pypi? [y/N]: ")

    with msg_wrap("Deploying build and signature to prod pypi"):
        time.sleep(2)

    with msg_wrap("Tagging release commit"):
        time.sleep(0.5)

    with msg_wrap("Pushing release tag to GitHub"):
        time.sleep(2)

    keep_artifacts = input("Release complete! Keep build artifacts around? [Y/n]: ")
    print("All done, good job!")


if __name__ == "__main__":
    do_it()
    # fake_it()
