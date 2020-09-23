import pytest

from snews import __version__


@pytest.mark.script_launch_mode("subprocess")
def test_cli_snews(script_runner):
    ret = script_runner.run("snews", "--help")
    assert ret.success

    ret = script_runner.run("snews", "--version")
    assert ret.success

    assert ret.stdout == f"snews version {__version__}\n"
    assert ret.stderr == ""


def test_cli_generate(script_runner):
    ret = script_runner.run("snews", "generate", "--help")
    assert ret.success
    assert ret.stderr == ""


def test_cli_model(script_runner):
    ret = script_runner.run("snews", "model", "--help")
    assert ret.success
    assert ret.stderr == ""
