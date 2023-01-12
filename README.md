# Salt Extension Modules for VMware

This is a collection of Salt-maintained extension modules for use with VMware
vSphere, vCenter, ESXi, and friends.

## Security

If you think you've found a security vulnerability, see [Salt's security guide][security].

## User Documentation

This README is more for contributing to the project. If you just want to get
started, check out the [User Documentation][docs]. Note: See the [Managing VMC SDDC with Salt][vmc-docs] section
for more information about how to configure `properties required for VMC operations`


## Contributing

The salt-ext-modules-vmware project team welcomes contributions from the community. If you wish to contribute code and you have not signed our contributor license agreement (CLA), our bot will update the issue when you open a Pull Request. For any questions about the CLA process, please refer to our [FAQ](https://cla.vmware.com/faq).

The [Salt Contributing guide][salt-contributing] has a lot of relevant information, but if you'd like to jump right in here's how to get started:

    # Clone the repo
    git clone --origin salt git@github.com:saltstack/salt-ext-modules-vmware.git

    # Change to the repo dir
    cd salt-ext-modules-vmware

    # Create a new venv, after sourcing activate `python` will refer to python3.
    python3 -m venv env --prompt vmw-ext
    source env/bin/activate

    # On mac, you may need to upgrade pip
    python -m pip install --upgrade pip

    # On WSL or some flavors of linux you may need to install the `enchant`
    # library in order to build the docs
    sudo apt-get install -y enchant

    # Install extension + test/dev/doc dependencies into your environment
    python -m pip install -e .\[tests,dev,docs\]

    # Run tests!
    python -m nox -e tests-3

    # skip requirements install for next time
    export SKIP_REQUIREMENTS_INSTALL=1

    # Build the docs, serve, and view in your web browser:
    python -m nox -e docs && (cd docs/_build/html; python -m webbrowser localhost:8000; python -m http.server; cd -)

    # If you want to run tests against an actual vCenter:

    # 1. Make a local salt dir
    mkdir -p local/etc/salt

    # 2. Make a local dir for salt state files
    mkdir -p local/srv/salt

    # 3. Make a local dir for salt pillar files
    mkdir -p local/srv/pillar

    # 4. Create a minion config
    cat << EOF> local/etc/salt/minion
    user: $(whoami)
    root_dir: $PWD/local/
    file_root: $PWD/local
    master: localhost
    id: saltdev
    master_port: 55506
    pillar_roots:
      base:
        - $PWD/local/srv/pillar
    EOF

    # 5. Make a Saltfile
    cat << EOF> Saltfile
    salt-call:
      local: true
      config_dir: local/etc/salt
    EOF

    # 6. Create a pillar file for you configuration
    cat << EOF> local/srv/my_vsphere_conf.sls
    # vCenter
    saltext.vmware:
      # Or use IP address, e.g. 203.0.113.42
      host: vsphere.example.com
      password: CorrectHorseBatteryStaple
      user: BobbyTables
    EOF

    # 7. Create a pillar top file
    cat << EOF>  local/srv/pillar.sls
    base:
      saltdev:
        - my_vsphere_conf
    EOF

    # 8. (deprecated but not removed yet) If you're contributing to the project and need to run the tests, create a test config file:
    python tools/test_value_scraper.py -c local/vcenter.conf

    # 9. (deprecated but not removed yet) Create a test config file for VMC:
    python tools/test_value_scraper_vmc.py --help
    This command will return the required information.


For code contributions, as part of VMware we require [a signed CLA][cla-faq].
If you've already signed the VMware CLA, you're probably good to go.

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
[cla-faq]: https://cla.vmware.com/faq
[docs]: https://docs.saltproject.io/salt/extensions/salt-ext-modules-vmware/en/latest/index.html
[vmc-docs]: https://docs.saltproject.io/salt/extensions/salt-ext-modules-vmware/en/latest/vmc.html
