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

import { CommandToolbarButton } from '@jupyterlab/apputils';
import { DocumentRegistry, DocumentWidget } from '@jupyterlab/docregistry';
import { CommandRegistry } from '@lumino/commands';
import { IDisposable, DisposableDelegate } from '@lumino/disposable';

import { CommandIDs, streamlitIcon, solaraIcon } from './utils';

export class StreamlitButtonExtension
  implements
    DocumentRegistry.IWidgetExtension<DocumentWidget, DocumentRegistry.IModel>
{
  commands: CommandRegistry;
  constructor(commands: CommandRegistry) {
    this.commands = commands;
  }
  createNew(widget: DocumentWidget): IDisposable {
    let streamlitButton: CommandToolbarButton | undefined;
    let solaraButton: CommandToolbarButton | undefined;
    const filePath = widget.context.path;

    if (filePath.endsWith('.py')) {
      streamlitButton = new CommandToolbarButton({
        commands: this.commands,
        id: CommandIDs.openFromEditor,
        label: '',
        icon: streamlitIcon,
        args: { file: widget.context.path, type: 'streamlit' }
      });
      solaraButton = new CommandToolbarButton({
        commands: this.commands,
        id: CommandIDs.openFromEditor,
        label: '',
        icon: solaraIcon,
        args: { file: widget.context.path, type: 'solara' }
      });
    } else if (filePath.endsWith('.ipynb')) {
      streamlitButton = new CommandToolbarButton({
        commands: this.commands,
        id: CommandIDs.translateToStreamlit,
        label: '',
        icon: streamlitIcon,
      });
      solaraButton = new CommandToolbarButton({
        commands: this.commands,
        id: CommandIDs.translateToSolara,
        label: '',
        icon: solaraIcon,
      });
    } else {
      
    }
    if (streamlitButton) {
      widget.toolbar.insertItem(99, 'streamlit', streamlitButton);
    }
    if (solaraButton) {
      widget.toolbar.insertItem(100, 'solara', solaraButton);
    }

    return new DisposableDelegate(() => {
      streamlitButton?.dispose();
      solaraButton?.dispose();
    });
  }
}
