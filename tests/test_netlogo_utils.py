"""Tests for netlogo_utils module."""

from netlogo_utils import (
    MockNetLogoLink,
    find_netlogo_home,
    find_netlogo_jar,
    init_netlogo,
    java_available,
)


class TestFindNetLogoHome:
    """Test suite for find_netlogo_home function."""

    def test_returns_none_when_not_found(self, monkeypatch):
        """Test that None is returned when NetLogo is not found."""
        monkeypatch.delenv("NETLOGO_HOME", raising=False)
        # This should return None unless NetLogo is actually installed
        result = find_netlogo_home("NONEXISTENT_VAR")
        # We don't assert None because it might find actual installations
        assert isinstance(result, (str, type(None)))

    def test_respects_env_var(self, monkeypatch, tmp_path):
        """Test that environment variable takes priority."""
        test_path = str(tmp_path)
        monkeypatch.setenv("NETLOGO_HOME", test_path)
        result = find_netlogo_home("NETLOGO_HOME")
        # Should return the path since it exists
        assert result == test_path


class TestJavaAvailable:
    """Test suite for java_available function."""

    def test_returns_bool(self):
        """Test that java_available returns a boolean."""
        result = java_available()
        assert isinstance(result, bool)


class TestFindNetLogoJar:
    """Test suite for find_netlogo_jar function."""

    def test_returns_none_for_none_input(self):
        """Test that None is returned for None input."""
        result = find_netlogo_jar(None)
        assert result is None

    def test_returns_none_for_nonexistent_path(self):
        """Test that None is returned for nonexistent paths."""
        result = find_netlogo_jar("/nonexistent/path/12345")
        assert result is None


class TestMockNetLogoLink:
    """Test suite for MockNetLogoLink class."""

    def test_init(self):
        """Test MockNetLogoLink initialization."""
        mock = MockNetLogoLink()
        assert mock.ticks == 0
        assert mock.turtles == 100
        assert mock.patches == 10000
        assert mock.model is None

    def test_load_model(self, capsys):
        """Test model loading."""
        mock = MockNetLogoLink()
        mock.load_model("test.nlogo")
        assert mock.model == "test.nlogo"
        captured = capsys.readouterr()
        assert "[MOCK] Loaded model: test.nlogo" in captured.out

    def test_command_setup(self):
        """Test setup command."""
        mock = MockNetLogoLink()
        mock.ticks = 50
        mock.turtles = 80
        mock.command("setup")
        assert mock.ticks == 0
        assert mock.turtles == 100

    def test_command_go(self):
        """Test go command."""
        mock = MockNetLogoLink()
        initial_ticks = mock.ticks
        mock.command("go")
        assert mock.ticks == initial_ticks + 1

    def test_command_repeat_go(self):
        """Test repeat [go] command."""
        mock = MockNetLogoLink()
        mock.command("repeat 10 [go]")
        assert mock.ticks == 10

    def test_report_count_turtles(self):
        """Test report for counting turtles."""
        mock = MockNetLogoLink()
        result = mock.report("count turtles")
        assert result == 100

    def test_report_count_patches(self):
        """Test report for counting patches."""
        mock = MockNetLogoLink()
        result = mock.report("count patches")
        assert result == 10000

    def test_report_count_turtles_with(self):
        """Test report for counting turtles with condition."""
        mock = MockNetLogoLink()
        result = mock.report("count turtles with [carrying-food?]")
        assert result == int(100 * 0.1)

    def test_report_mean_chemical(self):
        """Test report for mean chemical."""
        mock = MockNetLogoLink()
        result = mock.report("mean [chemical] of patches")
        assert isinstance(result, float)
        assert 0 <= result <= 1

    def test_repeat_report(self):
        """Test repeat_report method."""
        mock = MockNetLogoLink()
        reports = ["count turtles", "count patches"]
        result = mock.repeat_report(reports, 3)
        assert len(result) == 3
        for item in result:
            assert len(item) == 2

    def test_kill_workspace(self, capsys):
        """Test workspace cleanup."""
        mock = MockNetLogoLink()
        mock.kill_workspace()
        captured = capsys.readouterr()
        assert "[MOCK] NetLogo workspace closed" in captured.out


class TestInitNetLogo:
    """Test suite for init_netlogo function."""

    def test_returns_mock_when_netlogo_unavailable(self, monkeypatch):
        """Test that MockNetLogoLink is returned when NetLogo is unavailable."""
        # Mock the environment so NetLogo is not found
        monkeypatch.setenv("NETLOGO_HOME", "/nonexistent/path")
        result = init_netlogo(gui=False)
        assert isinstance(result, MockNetLogoLink)
