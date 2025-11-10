import pytest
from unittest.mock import Mock, patch
from auto_dashboards.process_manager import (
    DashboardManager, StreamlitApplication, SolaraApplication,
    DashApplication, extract_url, get_open_port
)


class TestExtractUrl:
    def test_extract_url_simple_http(self):
        text = "Server running at http://localhost:8080"
        result = extract_url(text)
        assert result == "http://localhost:8080"

    def test_extract_url_with_port(self):
        text = "Running on http://127.0.0.1:5000/"
        result = extract_url(text)
        assert result == "http://127.0.0.1:5000/"

    def test_extract_url_no_url(self):
        text = "No URL here"
        result = extract_url(text)
        assert result is None

    def test_extract_url_multiple_urls(self):
        text = "Visit http://first.com or http://second.com"
        result = extract_url(text)
        assert result == "http://first.com"


class TestGetOpenPort:
    def test_get_open_port_returns_string(self):
        port = get_open_port()
        assert isinstance(port, str)

    def test_get_open_port_returns_valid_port(self):
        port = get_open_port()
        port_int = int(port)
        assert 1024 <= port_int <= 65535


class TestDashboardManager:
    def setup_method(self):
        DashboardManager._instance = None

    def test_dashboard_manager_singleton(self):
        manager1 = DashboardManager.instance()
        manager2 = DashboardManager.instance()
        assert manager1 is manager2

    def test_dashboard_manager_initialization(self):
        manager = DashboardManager.instance()
        assert hasattr(manager, 'dashboard_instances')
        assert isinstance(manager.dashboard_instances, dict)

    @patch('auto_dashboards.process_manager.StreamlitApplication')
    def test_dashboard_manager_start_streamlit(self, mock_streamlit):
        manager = DashboardManager.instance()
        mock_app = Mock()
        mock_streamlit.return_value = mock_app
        result = manager.start(path="/test/app.py", app="streamlit")
        mock_streamlit.assert_called_once_with(path="/test/app.py")
        mock_app.start.assert_called_once()
        assert result == mock_app

    @patch('auto_dashboards.process_manager.SolaraApplication')
    def test_dashboard_manager_start_solara(self, mock_solara):
        manager = DashboardManager.instance()
        mock_app = Mock()
        mock_solara.return_value = mock_app
        result = manager.start(path="/test/app.py", app="solara")
        mock_solara.assert_called_once_with(path="/test/app.py")
        assert result == mock_app

    @patch('auto_dashboards.process_manager.DashApplication')
    def test_dashboard_manager_start_dash(self, mock_dash):
        manager = DashboardManager.instance()
        mock_app = Mock()
        mock_dash.return_value = mock_app
        result = manager.start(path="/test/app.py", app="dash")
        mock_dash.assert_called_once_with(path="/test/app.py")
        assert result == mock_app

    def test_dashboard_manager_start_invalid_type(self):
        manager = DashboardManager.instance()
        with pytest.raises(ValueError, match="Invalid dashboard application type"):
            manager.start(path="/test/app.py", app="invalid")

    @patch('auto_dashboards.process_manager.StreamlitApplication')
    def test_dashboard_manager_start_existing(self, mock_streamlit):
        manager = DashboardManager.instance()
        mock_app = Mock()
        mock_streamlit.return_value = mock_app
        result1 = manager.start(path="/test/app.py", app="streamlit")
        result2 = manager.start(path="/test/app.py", app="streamlit")
        assert result1 == result2
        mock_streamlit.assert_called_once()

    @patch('auto_dashboards.process_manager.StreamlitApplication')
    def test_dashboard_manager_stop(self, mock_streamlit):
        manager = DashboardManager.instance()
        mock_app = Mock()
        mock_streamlit.return_value = mock_app
        manager.start(path="/test/app.py", app="streamlit")
        manager.stop(path="/test/app.py")
        mock_app.stop.assert_called_once()
        assert "/test/app.py" not in manager.dashboard_instances


class TestStreamlitApplication:
    @patch('auto_dashboards.process_manager.get_open_port')
    def test_streamlit_initialization(self, mock_port):
        mock_port.return_value = "8501"
        app = StreamlitApplication(path="/test/dir/app.py")
        assert app.path == "/test/dir/app.py"
        assert app.app_basename == "app.py"
        assert app.port == "8501"

    @patch('auto_dashboards.process_manager.get_open_port')
    def test_streamlit_get_run_command(self, mock_port):
        mock_port.return_value = "8501"
        app = StreamlitApplication(path="/test/app.py")
        cmd = app.get_run_command()
        assert "streamlit" in cmd
        assert "run" in cmd
        assert "--server.port" in cmd
        assert "8501" in cmd


class TestSolaraApplication:
    @patch('auto_dashboards.process_manager.get_open_port')
    def test_solara_initialization(self, mock_port):
        mock_port.return_value = "8765"
        app = SolaraApplication(path="/test/app.py")
        assert app.port == "8765"

    @patch('auto_dashboards.process_manager.get_open_port')
    def test_solara_get_run_command(self, mock_port):
        mock_port.return_value = "8765"
        app = SolaraApplication(path="/test/app.py")
        cmd = app.get_run_command()
        assert "solara" in cmd
        assert "--port" in cmd
        assert "--production" in cmd


class TestDashApplication:
    @patch('auto_dashboards.process_manager.get_open_port')
    def test_dash_initialization(self, mock_port):
        mock_port.return_value = "8050"
        app = DashApplication(path="/test/app.py")
        assert app.port == "8050"

    @patch('auto_dashboards.process_manager.get_open_port')
    def test_dash_get_run_command(self, mock_port):
        mock_port.return_value = "8050"
        app = DashApplication(path="/test/app.py")
        cmd = app.get_run_command()
        assert "--port" in cmd
        assert "8050" in cmd