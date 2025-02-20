#
# Copyright 2017-2023 Elyra Authors
# Copyright 2025 Orange Bricks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import os
from pathlib import Path

import nbformat
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from openai import OpenAI
from auto_dashboards.process_manager import DashboardManager
import tornado


class RouteHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        appList = DashboardManager.instance().list()
        instances = {}
        for key in appList:
            instances[key] = appList[key].internal_host_url
        self.finish(json.dumps(instances))

    @tornado.web.authenticated
    def post(self):
        # parse filename and location
        json_payload = self.get_json_body()
        streamlit_app_filepath = json_payload['file']

        streamlit_app = DashboardManager.instance().start(
            path=streamlit_app_filepath
        )

        self.finish(json.dumps({
            "url": f"/proxy/{streamlit_app.port}/"
        }))

    @tornado.web.authenticated
    def delete(self):
        # parse filename and location
        json_payload = self.get_json_body()
        streamlit_app_filepath = json_payload['file']

        DashboardManager.instance().stop(
            path=streamlit_app_filepath
        )


class TranslateHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        # Get notebook path from request body
        try:
            json_payload = self.get_json_body()
            notebook_path = json_payload['file']
        except Exception as e:
            self.log.error(f"Error getting JSON payload: {e}")
            self.set_status(500)
            self.finish(json.dumps({"error": f"Error getting JSON payload: {e}"}))
            return

        # Read notebook content
        try:
            nb = nbformat.read(notebook_path, as_version=4)
            self.log.debug(f"Successfully read notebook: {notebook_path}")
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": f"Error reading notebook: {e}"}))
            return

        # Construct prompt for LLM
        prompt = "Translate the following Python code to Streamlit dashboard:\n\n"
        prompt += "```python\n"
        for cell in nb.cells:
            if cell.source.strip():
                if cell.cell_type == 'code':
                    prompt += cell.source + "\n\n"
                elif cell.cell_type == 'markdown':
                    prompt += '# ' + cell.source.replace('\n', '\n# ') + "\n\n"
        prompt += "```\n"
        prompt += "Only output the Streamlit code and no comments or explanations."

        # Call LLM API
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set.")
            client = OpenAI(api_key=api_key)

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="gpt-4o-mini",
            )
            generated_code = chat_completion.choices[0].message.content.strip()

            # Remove markdown code block backticks with optional language identifiers
            if generated_code.startswith("```"):
                # Split the lines
                lines = generated_code.splitlines()
                # Check if the first line is a backtick line with an optional language identifier
                if len(lines) > 1:
                    generated_code = "\n".join(lines[1:-1]).strip()

            self.log.debug("Successfully called LLM API")
        except Exception as e:
            self.log.error(f"Error calling LLM API: {e}")
            self.set_status(500)
            self.finish(json.dumps({"error": f"Error calling LLM API: {e}"}))
            return

        # Construct output filepath
        output_path = str(Path(notebook_path).with_suffix('.py'))

        # Write generated code to file
        try:
            with open(output_path, 'w') as f:
                f.write(generated_code)
            self.log.debug(f"Successfully wrote Streamlit code to: {output_path}")

        except Exception as e:
            self.log.error(f"Error writing output file: {e}")
            self.set_status(500)
            self.finish(json.dumps({"error": f"Error writing output file: {e}"}))
            return

        # Start Streamlit app
        try:
            streamlit_app = DashboardManager.instance().start(
                path=output_path
            )
            self.log.debug(f"Successfully started Streamlit app at: {streamlit_app.port}")
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": f"Error starting Streamlit app: {e}"}))
            return

        # Return app URL
        self.finish(json.dumps({
            "url": f"/proxy/{streamlit_app.port}/"
        }))


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "streamlit", "app")
    translate_route_pattern = url_path_join(base_url, "streamlit", "translate")
    handlers = [(route_pattern, RouteHandler), (translate_route_pattern, TranslateHandler)]
    web_app.add_handlers(host_pattern, handlers)
