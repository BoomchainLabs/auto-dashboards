/*
 * Copyright 2017-2023 Elyra Authors
 * Copyright 2025 Orange Bricks
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { LabIcon } from '@jupyterlab/ui-components';

import streamlitIconSvg from '../style/streamlit-logo.svg';
import solaraIconSvg from '../style/solara-logo.svg';

export const CommandIDs = {
  open: 'streamlit:open',
  openFromBrowser: 'streamlit:open-browser',
  openFromEditor: 'streamlit:open-file',
  translateBase: 'streamlit:translate-base',
  translateToStreamlit: 'streamlit:translate-streamlit',
  translateToSolara: 'streamlit:translate-solara',
};

export const streamlitIcon = new LabIcon({
  name: 'streamlit:icon',
  svgstr: streamlitIconSvg
});

export const solaraIcon = new LabIcon({
  name: 'solara:icon',
  svgstr: solaraIconSvg
});

export const getCookie = (key: string): string =>
  document.cookie.match('(^|;)\\s*' + key + '\\s*=\\s*([^;]+)')?.pop() || '';

export const isNotebook = (filePath: string): boolean => {
    return filePath.endsWith('.ipynb');
}
