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

import {
  ILayoutRestorer,
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import {
  Dialog,
  IFrame,
  MainAreaWidget,
  showDialog,
  showErrorMessage,
  WidgetTracker,
  Notification
} from '@jupyterlab/apputils';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { IEditorTracker } from '@jupyterlab/fileeditor';
import { find } from '@lumino/algorithm';

import path from 'path';
import { StreamlitButtonExtension } from './button';

import { requestAPI } from './handler';
import { CommandIDs, getCookie, isNotebook, streamlitIcon } from './utils';

const NAMESPACE = '@orbrx/auto-dashboards';

const serverErrorMessage =
  'There was an issue with the auto_dashboards server extension.';

export const syncXsrfCookie = (): void => {
  const xsrf = getCookie('_xsrf');
  const jupyterlab_xsrf = getCookie('jupyterlab_xsrf');
  // Initialize or update jupyterlab_xsrf to duplicate _xsrf
  if (xsrf && (!jupyterlab_xsrf || xsrf !== jupyterlab_xsrf)) {
    document.cookie = 'jupyterlab_xsrf=' + xsrf;
  }
  // Restore _xsrf if deleted
  if (jupyterlab_xsrf && !xsrf) {
    document.cookie = '_xsrf=' + jupyterlab_xsrf;
  }
};

export const checkCookie = (function () {
  syncXsrfCookie();
  let previousCookie = document.cookie;
  return () => {
    const currentCookie = document.cookie;
    if (currentCookie !== previousCookie) {
      syncXsrfCookie();
      previousCookie = currentCookie;
    }
  };
})();

const getDashboardApp = async (file: string, type: string): Promise<string | undefined> => {
  try {
    const data = await requestAPI<any>('app', {
      method: 'POST',
      body: JSON.stringify({ file, type })
    });
    return data.url;
  } catch (reason) {
    console.error(`${serverErrorMessage}\n${reason}`);
    return undefined;
  }
};

const stopDashboardApp = async (file: string): Promise<void> => {
  try {
    await requestAPI<any>('app', {
      method: 'DELETE',
      body: JSON.stringify({ file })
    });
  } catch (reason) {
    console.error(`${serverErrorMessage}\n${reason}`);
  }
};

const translateNotebook = async (
  file: string,
  type: string,
  id: string
): Promise<string | undefined> => {
  try {
    console.log('translateNotebook called with file:', file);
    const data = await requestAPI<any>('translate', {
      method: 'POST',
      body: JSON.stringify({ file, type })
    });
    console.log('translateNotebook response:', data);
    Notification.update({
      id,
      message: 'Dashboard is ready',
      type: 'success',
      autoClose: 2000
    });
    return data.url;
  } catch (reason) {
    console.error(`${serverErrorMessage}\n${reason}`);
    if (reason instanceof Error) {
      showErrorMessage('Error translating notebook', reason);
    } else {
      showErrorMessage('Error translating notebook', new Error(String(reason)));
    }
    Notification.update({
      id,
      message: `Error translating notebook: ${reason}`,
      type: 'error',
      autoClose: false
    });
    return undefined;
  }
};

/**
 * Initialization data for the auto-dashboardsextension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: NAMESPACE,
  autoStart: true,
  requires: [IEditorTracker, IFileBrowserFactory],
  optional: [ILayoutRestorer],
  activate: (
    app: JupyterFrontEnd,
    editorTracker: IEditorTracker,
    factory: IFileBrowserFactory,
    restorer: ILayoutRestorer | null
  ) => {
    console.log('JupyterLab extension auto-dashboards is activated!');

    requestAPI<any>('app')
      .then(data => {
        console.log(
          'auto_dashboards server extension successfully started'
        );
      })
      .catch(reason => {
        console.error(`${serverErrorMessage}\n${reason}`);
      });

    const tracker = new WidgetTracker<MainAreaWidget<IFrame>>({
      namespace: NAMESPACE
    });

    // Handle state restoration
    if (restorer) {
      void restorer.restore(tracker, {
        command: CommandIDs.open,
        args: widget => ({
          file: widget.id.split(':')[1],
          type: 'streamlit'
        }),
        name: widget => widget.id
      });
    }

    app.commands.addCommand(CommandIDs.translateBase, {
      execute: async (args: any) => {
        const widget = app.shell.currentWidget;
        if (!widget) {
          console.log('No active widget found');
          return;
        }
        let filePath: string;
        // Use context.path if available for notebook panels, otherwise fallback to widget.id splitting
        if ((widget as any).context && (widget as any).context.path) {
          filePath = (widget as any).context.path;
        } else {
          filePath = widget.id.split(':')[1];
        }
        if (!isNotebook(filePath)) {
          console.log('No notebook found');
          return;
        }
        console.log('Calling translateNotebook with path:', filePath);

        const id = Notification.emit('Creating dashboard...', 'in-progress', {
          autoClose: false
        });

        const url = await translateNotebook(filePath, args.type, id);
        console.log('translateNotebook returned URL:', url);
        if (url) {
          const translatedFilePath = filePath.replace(/\.ipynb$/, '.py');
          await app.commands.execute(
            CommandIDs.open, 
            { 
              file: translatedFilePath,
              type: args.type
            });
          Notification.dismiss(id);
        }
      },
    });

    app.commands.addCommand(CommandIDs.translateToStreamlit, {
      label: 'Translate Notebook to Streamlit',
      icon: streamlitIcon,
      execute: async () => {
        await app.commands.execute(
          CommandIDs.translateBase, { type: 'streamlit' }
        );
      }
    });

    app.commands.addCommand(CommandIDs.translateToSolara, {
      label: 'Translate Notebook to Solara',
      icon: streamlitIcon,
      execute: async () => {
        await app.commands.execute(
          CommandIDs.translateBase, { type: 'solara' }
        );
      }
    });

    app.commands.addCommand(CommandIDs.open, {
      label: 'Streamlit',
      execute: async (args: any) => {
        const widgetId = `${NAMESPACE}:${args.file}`;
        const openWidget = find(app.shell.widgets('main'), (widget, index) => {
          return widget.id === widgetId;
        });
        if (openWidget) {
          app.shell.activateById(widgetId);
          return;
        }

        const urlPromise = getDashboardApp(args.file, args.type);

        const widget = new IFrame({
          sandbox: [
            'allow-same-origin',
            'allow-scripts',
            'allow-popups',
            'allow-forms'
          ]
        });
        const main = new MainAreaWidget({ content: widget });
        main.title.label = path.basename(args.file);
        main.title.icon = streamlitIcon;
        main.title.caption = widget.title.label;
        main.id = widgetId;
        main.disposed.connect(() => {
          stopDashboardApp(args.file);
        });

        await tracker.add(main);
        app.shell.add(main, 'main', { mode: 'split-right' });

        // Set iframe url last to not block widget creation on webapp startup
        const url = await urlPromise;
        // When iframe src=undefined the lab instance is shown instead
        // In this case we want to close the widget rather than set the url
        if (url === undefined) {
          main.dispose();
          void showDialog({
            title: 'Streamlit application failed to start',
            body: 'Check the logs for more information.',
            buttons: [Dialog.okButton()]
          });
        } else {
          widget.url = url;
        }
      }
    });

    app.commands.addCommand(CommandIDs.openFromBrowser, {
      label: 'Run in Streamlit',
      icon: streamlitIcon,
      isVisible: () => 
        !!factory.tracker.currentWidget &&
        factory.tracker.currentWidget.selectedItems().next !== undefined,
      execute: async () => {
        const currentWidget = factory.tracker.currentWidget;
        if (!currentWidget) {
          return;
        }
        const result = currentWidget.selectedItems().next();
        if (result.done || !result.value) {
          return;
        }
        const item = result.value;
        await app.commands.execute(CommandIDs.open, {
          file: item.path,
          type: 'streamlit'
        });
      }
    });

    app.commands.addCommand(CommandIDs.openFromEditor, {
      execute: (args: any) => {
        const widget = editorTracker.currentWidget;
        if (!widget) {
          return;
        }
        const path = widget.context.path;
        return app.commands.execute(CommandIDs.open, { 
          file: path,
          type: args.type
        });
      },
      label: 'Run in Dashboard'
    });

    app.docRegistry.addWidgetExtension(
      'Editor',
      new StreamlitButtonExtension(app.commands)
    );
    app.docRegistry.addWidgetExtension(
      'Notebook',
      new StreamlitButtonExtension(app.commands)
    );

    app.contextMenu.addItem({
      selector: '[data-file-type="python"]',
      command: CommandIDs.openFromBrowser,
      rank: 999
    });

    app.contextMenu.addItem({
      selector: '.jp-FileEditor',
      command: CommandIDs.openFromEditor,
      rank: 999
    });

  app.contextMenu.addItem({
    selector: '.jp-Notebook',
    command: CommandIDs.translateToStreamlit,
    rank: 999
  });

  app.contextMenu.addItem({
    selector: '.jp-Notebook',
    command: CommandIDs.translateToSolara,
    rank: 999
  });

    // Poll changes to cookies and prevent the deletion of _xsrf by Streamlit
    // _xsrf deletion issue: https://github.com/streamlit/streamlit/issues/2517
    window.setInterval(checkCookie, 100); // run every 100 ms
  }
};

export default plugin;
