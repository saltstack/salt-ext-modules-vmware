# Salt Extension Modules for VMware

This is a collection of Salt-maintained extension modules for use with VMware
vSphere, vCenter, ESXi, and friends.

## Security

If you think you've found a security vulnerability, see [Salt's security guide][security].


## Contributing

The salt-ext-modules-vmware project team welcomes contributions from the community. If you wish to contribute code and you have not signed our contributor license agreement (CLA), our bot will update the issue when you open a Pull Request. For any questions about the CLA process, please refer to our [FAQ](https://cla.vmware.com/faq).

The [Salt Contributing guide][salt-contributing] has a lot of relevant information, but if you'd like to jump right in here's how to get started:

    # Clone the repo
    git clone --origin salt git@github.com:saltstack/salt-ext-modules-vmware.git

    # Change to the repo dir
    cd salt-ext-modules-vmware

    # Create a new venv
    python3 -m venv env --prompt vmw-ext
    source env/bin/activate

    # On mac, you may need to upgrade pip
    python -m pip install --upgrade pip

    # On WSL or some flavors of linux you may need to install the `enchant`
    # library in order to build the docs
    sudo apt-get install -y enchant

    # Install extension + test/dev/doc dependencies into your environment
    python -m pip install -e .[tests,dev,docs]

    # Run tests!
    python -m nox -e tests-3

    # skip requirements install for next time
    export SKIP_REQUIREMENTS_INSTALL=1

    # Build the docs, serve, and view in your web browser:
    python -m nox -e docs && (cd docs/_build/html; python -m webbrowser localhost:8000; python -m http.server; cd -)

    # If you want to run tests against an actual vCenter, make
    # a local salt dir
    mkdir -p local/etc/salt

    # Create a minion config
    cat << EOF> local/etc/salt/minion
    user: $(whoami)
    root_dir: $PWD/local/
    file_root: $PWD/local
    master: localhost
    id: saltdev
    master_port: 55506
    EOF

    # Create a test config file:
    python tools/test_value_scraper.py -c local/vcenter.conf


Of course, writing code isn't the only way to contribute! We value
contributions in any of these areas:

- Documentation - especially examples of how to use this module to solve
  specific problems.
- Triaging [issues][issues] and participating in [discussions][discussions]
- Reviewing [Pull Requests][PRs] (we really like [Conventional
  Comments][comments]!)

You could also contribute in other ways:

- Writing blog posts
- Posting on social media about how you used Salt+VMware to solve your
  problems, including videos
- Giving talks at conferences
- Publishing videos
- Asking/answering questions in IRC, Slack, or email groups

Any of these things are super valuable to our community, and we sincerely
appreciate every contribution!


For more information, build the docs and head over to http://localhost:8000/ —
that's where you'll find the rest of the documentation.


[security]: https://github.com/saltstack/salt/blob/master/SECURITY.md
[salt-contributing]: https://docs.saltproject.io/en/master/topics/development/contributing.html
[issues]: https://github.com/saltstack/salt-ext-modules-vmware/issues
[PRs]: https://github.com/saltstack/salt-ext-modules-vmware/pulls
[discussions]: https://github.com/saltstack/salt-ext-modules-vmware/discussions
[comments]: https://conventionalcomments.org/
