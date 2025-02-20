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

from abc import ABC, ABCMeta, abstractmethod
import os
import sys
import socket
from subprocess import Popen, CalledProcessError, PIPE
from typing import Dict
from traitlets.config import SingletonConfigurable, LoggingConfigurable
from urllib.parse import urlparse

# Combined metaclass for BaseDashboard
class DashboardMeta(ABCMeta, type(LoggingConfigurable)):
    pass


class DashboardManager(SingletonConfigurable):
    """Singleton class to keep track of dashboard instances and manage
    their lifecycles
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dashboard_instances = {}

    def list(self) -> Dict:
        return self.dashboard_instances

    def start(self, path: str) -> 'BaseDashboard':
        if path in self.dashboard_instances.keys():
            return self.dashboard_instances[path]
        dashboard_app = StreamlitApplication(path=path)
        dashboard_app.start()
        self.dashboard_instances[path] = dashboard_app
        return dashboard_app

    def stop(self, path: str) -> None:
        dashboard_app = self.dashboard_instances.get(path)
        if dashboard_app:
            dashboard_app.stop()
            del self.dashboard_instances[path]
        else:
            self.log.info(
                "Unable to find running instance of ",
                f"{path} application"
            )

    def restart(self, path: str) -> None:
        """
        Forces a restart of a streamlit application.
        NOTE: does not restart a "stopped" application process
        :param streamlit_app_filepath:
        :return:
        """
        dashboard_app = self.dashboard_instances.get(path)
        if dashboard_app:
            dashboard_app.stop()
            dashboard_app.start()
        else:
            self.log.info(
                "Unable to find running instance of ",
                f"{path} application"
            )

class BaseDashboard(LoggingConfigurable, metaclass=DashboardMeta):
    """
    Abstract base class for all dashboards
    """
    def __init__(self, path: str, **kwargs):
        """
        :param path: the path to the dashboard application
        """
        super().__init__(**kwargs)
        self.path = path
        self.app_start_dir = os.path.dirname(path)
        self.app_basename = os.path.basename(path)
        self.port = get_open_port()
        self.process = None
        self.internal_host = {}
        self.external_host = {}

    @abstractmethod
    def get_run_command(self) -> list:
        """
        Return the start command as a list to launch the dashboard application.
        """
        pass

    def start(self) -> None:
        """
        Start the dashboard application
        """
        if not self.process or not self.is_alive():
            self.log.info(
                f"Starting dashboard '{self.app_basename}' ",
                f"on port {self.port}"
            )
            cmd = self.get_run_command()
            try:
                if self.app_start_dir:
                    self.process = Popen(cmd, cwd=self.app_start_dir, stdout=PIPE)
                else:
                    self.process = Popen(cmd, stdout=PIPE)
            except CalledProcessError as error:
                self.log.info(
                    "Failed to start dashboard ",
                    f"on port {self.port} due to {error}"
                )

            # Voodoo magic, needs to 'hit' the process otherwise server will
            # not serve
            for i in range(3):
                self.process.stdout.readline()
            internal_url_line = self.process.stdout.readline().decode('utf-8')
            external_url_line = self.process.stdout.readline().decode('utf-8')
            self.internal_host = parse_hostname(internal_url_line)
            self.external_host = parse_hostname(external_url_line)
    
    def stop(self) -> None:
        """
        Stop the dashboard application
        """
        if self.process:
            self.log.info(
                f"Stopping dashboard '{self.app_basename}' ",
                f"on port {self.port}"
            )
            self.process.terminate()
            self.process = None
        else:
            self.log.info(
                f"Dashboard '{self.app_basename}' is not running"
            )

    def is_alive(self) -> bool:
        """
        Check if child process has terminated.
        """
        if self.process:
            return False if self.process.poll() else True
        else:
            return False


class StreamlitApplication(BaseDashboard):
    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)

    def get_run_command(self) -> list:
        return [
            sys.executable, "-m", "streamlit", "run", self.app_basename,
            "--browser.gatherUsageStats=false",  # turn off usage stats upload
            "--server.runOnSave=true",  # auto refresh app on save
            "--server.headless=true",  # run headless, avoids email sign up
            "--server.port", self.port
        ]


def get_open_port() -> str:
    """
    Returns an open port on the application host
    :return:
    """
    sock = socket.socket()
    sock.bind(('', 0))
    return str(sock.getsockname()[1])


def parse_hostname(parse_line: str) -> Dict:
    """
    Fragile function to parse out the URL from the output log
    :param parse_line:
    :return:
    """
    remove_newlines_line = parse_line.rstrip('\n')
    strip_line = remove_newlines_line.strip()
    tokenize_line = strip_line.split(" ")[2]
    url_obj = urlparse(tokenize_line)
    return {
        "host": url_obj.hostname,
        "scheme": url_obj.scheme
    }
