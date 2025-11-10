import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell
from auto_dashboards.handlers import (
    RouteHandler, ModelInfoHandler, TranslateHandler, setup_handlers
)


class TestRouteHandler:
    def setup_method(self):
        self.handler = RouteHandler(application=Mock(), request=Mock())
        self.handler.finish = Mock()
        self.handler.get_json_body = Mock()

    @patch('auto_dashboards.handlers.DashboardManager')
    def test_get_empty_list(self, mock_manager):
        mock_instance = Mock()
        mock_instance.list.return_value = {}
        mock_manager.instance.return_value = mock_instance
        self.handler.get()
        result = json.loads(self.handler.finish.call_args[0][0])
        assert result == {}

    @patch('auto_dashboards.handlers.DashboardManager')
    def test_post_start_streamlit(self, mock_manager):
        mock_app = Mock()
        mock_app.port = "8501"
        mock_instance = Mock()
        mock_instance.start.return_value = mock_app
        mock_manager.instance.return_value = mock_instance
        self.handler.get_json_body.return_value = {
            "file": "/test/app.py", "type": "streamlit"
        }
        self.handler.post()
        result = json.loads(self.handler.finish.call_args[0][0])
        assert result["url"] == "/proxy/8501/"

    @patch('auto_dashboards.handlers.DashboardManager')
    def test_delete_stop_dashboard(self, mock_manager):
        mock_instance = Mock()
        mock_manager.instance.return_value = mock_instance
        self.handler.get_json_body.return_value = {"file": "/test/app.py"}
        self.handler.delete()
        mock_instance.stop.assert_called_once_with(path="/test/app.py")


class TestModelInfoHandler:
    def setup_method(self):
        self.handler = ModelInfoHandler(application=Mock(), request=Mock())
        self.handler.finish = Mock()
        self.handler.set_status = Mock()
        self.handler.log = Mock()

    def test_get_default_openai_model(self):
        with patch.dict(os.environ, {}, clear=True):
            self.handler.get()
            result = json.loads(self.handler.finish.call_args[0][0])
            assert result["model_name"] == "gpt-4o-mini"
            assert result["model_provider"] == "openai"
            assert result["is_local"] is False

    def test_get_ollama_model_by_url(self):
        with patch.dict(os.environ, {
            "OPENAI_MODEL": "llama2",
            "OPENAI_API_URL": "http://localhost:11434/v1"
        }, clear=True):
            self.handler.get()
            result = json.loads(self.handler.finish.call_args[0][0])
            assert result["model_provider"] == "ollama"
            assert result["is_local"] is True

    def test_get_ollama_model_by_name(self):
        with patch.dict(os.environ, {"OPENAI_MODEL": "llama3:latest"}, clear=True):
            self.handler.get()
            result = json.loads(self.handler.finish.call_args[0][0])
            assert result["model_provider"] == "ollama"


class TestTranslateHandler:
    def setup_method(self):
        self.handler = TranslateHandler(application=Mock(), request=Mock())
        self.handler.finish = Mock()
        self.handler.set_status = Mock()
        self.handler.get_json_body = Mock()
        self.handler.log = Mock()

    def test_post_missing_json_payload(self):
        self.handler.get_json_body.side_effect = Exception("Invalid JSON")
        self.handler.post()
        self.handler.set_status.assert_called_with(500)
        result = json.loads(self.handler.finish.call_args[0][0])
        assert "error" in result

    @patch('auto_dashboards.handlers.nbformat.read')
    def test_post_invalid_notebook_path(self, mock_read):
        mock_read.side_effect = FileNotFoundError("File not found")
        self.handler.get_json_body.return_value = {
            "file": "/nonexistent/notebook.ipynb", "type": "streamlit"
        }
        self.handler.post()
        self.handler.set_status.assert_called_with(500)

    @patch('auto_dashboards.handlers.DashboardManager')
    @patch('auto_dashboards.handlers.OpenAI')
    @patch('builtins.open', new_callable=mock_open)
    @patch('auto_dashboards.handlers.nbformat.read')
    def test_post_translate_streamlit_success(self, mock_read, _mock_file, 
                                              mock_openai, mock_manager):
        nb = new_notebook()
        nb.cells.append(new_code_cell("import pandas as pd"))
        mock_read.return_value = nb
        
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(
            content="import streamlit as st\nst.write('Hello')"))]
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        mock_app = Mock()
        mock_app.port = "8501"
        mock_instance = Mock()
        mock_instance.start.return_value = mock_app
        mock_manager.instance.return_value = mock_instance
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            self.handler.get_json_body.return_value = {
                "file": "/test/notebook.ipynb", "type": "streamlit"
            }
            self.handler.post()
            result = json.loads(self.handler.finish.call_args[0][0])
            assert result["url"] == "/proxy/8501/"

    @patch('auto_dashboards.handlers.OpenAI')
    @patch('auto_dashboards.handlers.nbformat.read')
    def test_post_missing_api_credentials(self, mock_read, _mock_openai):
        nb = new_notebook()
        nb.cells.append(new_code_cell("x = 1"))
        mock_read.return_value = nb
        
        with patch.dict(os.environ, {}, clear=True):
            self.handler.get_json_body.return_value = {
                "file": "/test/notebook.ipynb", "type": "streamlit"
            }
            self.handler.post()
            self.handler.set_status.assert_called_with(500)


class TestSetupHandlers:
    def test_setup_handlers_registers_routes(self):
        mock_web_app = Mock()
        mock_web_app.settings = {"base_url": "/"}
        setup_handlers(mock_web_app)
        mock_web_app.add_handlers.assert_called_once()
        call_args = mock_web_app.add_handlers.call_args
        handlers = call_args[0][1]
        assert len(handlers) == 3