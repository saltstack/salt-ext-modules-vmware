"""
These are high-level "thin red line" tests for the module. Essentially, they
can be run against a configured vCenter instance to ensure that from a high
level, functionality has not been destroyed. These tests may take a longer
time to run. Completeness is more important than granularity. In other words,
if a test fails here we may not know exactly why, but any bug that is released
must have an accompanying test here to expose that bug.
"""


def test_this_needs_to_be_changed(service_instance):
    # This is not a real test - we're not using our extension at all.
    # But it *does* use the service_instance with a config, so... bonus!
    expected_name = "tiny_cent"
    root_folder = service_instance.RetrieveContent().rootFolder
    view = service_instance.content.viewManager.CreateContainerView(root_folder, recursive=True)
    names = [item.name for item in view.view]
    print(names)
    assert expected_name in names
