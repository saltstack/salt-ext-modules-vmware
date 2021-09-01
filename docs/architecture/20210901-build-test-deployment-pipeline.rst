2021-09-01 Build/Test/Deployment Pipeline
=========================================

Status
------

Discussion/Development

Context
-------

The motivations behind our CI/CD pipeline are:

* quick tests
* full confidence on deploys
* "nightly" builds

We want our tests to run as fast as reasonably possible. At the current time,
TODO has a unit test suite that runs TODO tests in about 15 minutes. This is
an entirely reasonable amount of time to wait for tests to run. Much longer and
the feedback cycle takes much too long.

Of course the reason that we want tests in the first place is that
well-written, meaningful tests allow us to deploy the most reasonably reliable
software we can. Obviously perfect reliability is unattainable, but there are a
lot of things that we can do to improve reliability for a reasonable amount of
effort.

We also want to provide users the ability to continually check our development
against their own environments, by producing "nightly" builds. The quotation
marks are there because maybe it's not nightly, maybe it's weekly. Or some
other sensible, frequent period of releases. Nightly would be fine if we need
to build that often.

Murphy's Law
------------

> Anything that can go wrong will go wrong.

This principle is baked into the design of the pipeline. At each step it should
fail safe and be *possible* to re-start at that step of the pipeline. That way,
if something fails for an external reason (power outage, DNS failure, gamma
rays), we will be able to resume where we left off, instead of having to do
something like create a new PR to launch the whole process again. As long as
successful artifacts exist from the previous step in the pipeline, each step
should be able to be re-started.

Details
-------

Local Pre-Commit Hooks, Tests, and Docs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Running pre-commit hooks locally will help ensure before a PR is submitted that
it looks reasonable at first glance. There may be more underlying issues, but
the pre-commit hooks will catch things like formatting issues, lint issues,
completely missing docs, etc.

Running the tests and building/viewing the documentation locally is the next
step - this is the last step for contributors to check that their code,
documentation, and tests are organized and ready to open a PR. This step is an
essential part of the pipeline, since updates require test coverage and
documentation.

Unit Tests (and More) On Pull Requests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every pull request will check the pre-commit hooks, build the docs, and run the
unit test suite. We may want to enable certain integration tests to run on pull
requests, or define a manual(ish) process to run the integration tests on PRs,
but at minimum the PR will run:

* pre-commit hooks
* docs build
* unit test suite

Any failure here MUST be addressed before the PR may be merged. The entire unit
test suite must be green before the PR is merged. Merging also requires that
the main branch tests are green. Otherwise, PRs should not be merged (unless of
course they're fixing the full test suite)

Integration (Post-Merge) Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because the unit test suite is very narrow - isolating against many of the
extension module dependencies - we want more broad, comprehensive tests. While
the unit tests will trust that things work as expected, the integration tests
will verify that things work as expected. Correctly running integration tests
will give us confidence that the assumptions made in the unit test suite are
safe assumptions.

Integration tests should not only run against the current/latest merge to
master with the specified dependencies, but they should also run against the
newest versions of as many dependencies as possible. Running against several
different versions of Salt (including the latest code in git) and other
dependencies will ensure that as APIs change that we learn of it sooner rather
than later, and can anticipate breaking changes rather than react to them.

Both the unit and integration tests in the pipeline environment should build
the module, intall it, and run the tests against the installed version. This
will help ensure that any potential packaging issues are caught earlier rather
than later.

The artifact of successful integration tests will be a .whl package of the
library. For nightly builds, these pre-release pacakges should be kept for 30
days minimum, and at least the last 30 builds. For instance, if 20 builds
happened across 2 months then all 20 builds would be kept. If 10 more builds
happened the next month, all 30 builds would be kept, despite some of them
being over 30 days old. With each subsequent build, however, the oldest build
would be removed. Or alternatively, if 40 builds happened within 29 days, all
40 builds would be kept. On day 31, the first 10 builds could be deleted.

All of these artifacts should be made public - perhaps via pypi or GitHub. PyPI
would be easy, but we would be increasing the load on PyPI - if we did that we
should investigate helping to fund PyPI.

A test failure here *is* an **EMERGENCY**. Failures here should be treated with
the utmost importance. Failures here should lead to the creation of a new unit
test that exhibits the same failure that halted the integration test so that
behavior can be accounted for in the module code. It would be a good idea for
failures in this step to automatically create a GitHub issue based on the test
name, or re-open an existing test failure issue. That would allow flaky
integration tests to be identified and either flakiness addressed or tests
completely removed.

Because these tests run against private cloud infrastructure, they must be
designed to take advantage of config files that can be provided either at a
relative location or a configurable location in the filesystem. That allows the
CI pipeline the ability to provide connection secrets in a way that is unlikely
to leak in any test logging.

Tagging and Release
^^^^^^^^^^^^^^^^^^^

Assuming that all tests continue to stay green, a Release Candidate (RC) will
be released. These will always be deployed to PyPI - the version specifier will
ensure that pip installs only upgrade to the RC when the ``--pre`` flag is
passed, but will make it trivial for interested users to test the latest
version.

Because the only difference between a regular build and a RC/final release
build is tagging and potentially documentation, the release will follow the
same process as any other build. Our confidence should be high that our test
suite and full pipeline will suceed, with such trivial non-code changes.


Pipeline Overview
^^^^^^^^^^^^^^^^^


.. ::

    *optional


    local pre-commit hooks <-,----------,
              |               `\         `|
              |                 |         |
            ./^\___,------------'         |
            |                             |
            `\,                           |
              |                           |
              V                           |
    local unit/integration* <-,           |
          test run            |           |
              |             ,/'           |
              |            /              |
            ./^\___,------'               |
            |                             |
            `\,                           |
              |                           |
              V                           |
    ---- local/PR line ------             |
              |                           |
              |                           |
              |                           |
              V                           |
        PR: pre-commit hooks,             |
            docs/pkg build/install,       |
            unit tests run                |
              |                           |
              |                           |
            ./^\                          |
            |   `\                        |
            `\,   `-( tests/any failure )-'
              |
              V
    ---- PR/merge line -----
              |
              |
              V
       Integration/full test suite
              |
              |
            ./^\,___.-->=( on fail, new PR to fix failure )
            |
            `\,
              |
              V
       Release nightly build internal/GitHub
       Release RC/final/post relase PyPI



Consequences
------------

The optimistic result is that deploying new releases will be as simple as
pushing a new tag to the repository.

There will be consequences in terms of build times - both blocking PRs as well
as post merge for the full test runs. Also, this infrastructure is code, and
code must be maintained, so there will be a maintenance cost to the
infrastructure.

But ultimately, this should result in reliable deployments with feedback coming
as early in the cycle as possible.
