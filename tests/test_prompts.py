import pytest
from auto_dashboards.prompts import streamlit_prompt, solara_prompt, dash_prompt


class TestStreamlitPrompt:
    def test_streamlit_prompt_basic_code(self):
        code = "print('Hello, World!')"
        result = streamlit_prompt(code)
        assert "Translate the following Python code to Streamlit dashboard" in result
        assert "```python" in result
        assert code in result

    def test_streamlit_prompt_empty_code(self):
        code = ""
        result = streamlit_prompt(code)
        assert "Translate the following Python code to Streamlit dashboard" in result
        assert "```python" in result

    def test_streamlit_prompt_multiline_code(self):
        code = "import pandas as pd\ndf = pd.DataFrame()"
        result = streamlit_prompt(code)
        assert code in result

class TestSolaraPrompt:
    def test_solara_prompt_basic_code(self):
        code = "print('Hello')"
        result = solara_prompt(code)
        assert "Translate the following Python code to Solara dashboard" in result
        assert "import solara" in result

    def test_solara_prompt_includes_example(self):
        code = "x = 1"
        result = solara_prompt(code)
        assert "solara.reactive" in result
        assert "@solara.component" in result

class TestDashPrompt:
    def test_dash_prompt_basic_code(self):
        code = "print('Hello')"
        result = dash_prompt(code)
        assert "Translate the following Python code to a Plotly Dash dashboard" in result
        assert "from dash import Dash" in result

    def test_dash_prompt_includes_cli_args(self):
        code = "x = 1"
        result = dash_prompt(code)
        assert "app.run_server" in result
        assert "command-line arguments" in result

class TestPromptComparison:
    def test_all_prompts_handle_same_code(self):
        code = "import pandas as pd"
        streamlit_result = streamlit_prompt(code)
        solara_result = solara_prompt(code)
        dash_result = dash_prompt(code)
        assert code in streamlit_result
        assert code in solara_result
        assert code in dash_result

    def test_all_prompts_are_distinct(self):
        code = "x = 1"
        streamlit_result = streamlit_prompt(code)
        solara_result = solara_prompt(code)
        dash_result = dash_prompt(code)
        assert "Streamlit" in streamlit_result
        assert "Solara" in solara_result
        assert "Dash" in dash_result