// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import * as vscode from 'vscode';
import * as json from './json';

enum SlideShowType {
    slide = 'slide',
    subslide = 'subslide',
    fragment = 'fragment',
    skip = 'skip',
    notes = 'notes',
    none = 'none'
}

export class CellSlideShowStatusBarProvider implements vscode.NotebookCellStatusBarItemProvider {
    provideCellStatusBarItems(
        cell: vscode.NotebookCell,
        token: vscode.CancellationToken
    ): vscode.ProviderResult<vscode.NotebookCellStatusBarItem[]> {
        const items: vscode.NotebookCellStatusBarItem[] = [];
        const slideType = getSlideType(cell);

        if (slideType) {
            items.push({
                text: `Slide Type: ${slideType}`,
                tooltip: `Slide Type: ${slideType}`,
                command: 'jupyter-slideshow.switchSlideType',
                alignment: vscode.NotebookCellStatusBarAlignment.Right
            });
        }

        return items;
    }
}

export function getActiveCell() {
    // find active cell
    const editor = vscode.window.activeNotebookEditor;
    if (!editor) {
        return;
    }

    return editor.notebook.cellAt(editor.selections[0].start);
}

export function reviveCell(args: vscode.NotebookCell | vscode.Uri | undefined): vscode.NotebookCell | undefined {
    if (!args) {
        return getActiveCell();
    }

    if (args && 'index' in args && 'kind' in args && 'notebook' in args && 'document' in args) {
        return args as vscode.NotebookCell;
    }

    if (args && 'scheme' in args && 'path' in args) {
        const cellUri = vscode.Uri.from(args);
        const cellUriStr = cellUri.toString();
        let activeCell: vscode.NotebookCell | undefined = undefined;

        for (const document of vscode.workspace.notebookDocuments) {
            for (const cell of document.getCells()) {
                if (cell.document.uri.toString() === cellUriStr) {
                    activeCell = cell;
                    break;
                }
            }

            if (activeCell) {
                break;
            }
        }

        return activeCell;
    }

    return undefined;
}

export function register(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.notebooks.registerNotebookCellStatusBarItemProvider(
            'jupyter-notebook',
            new CellSlideShowStatusBarProvider()
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            'jupyter-slideshow.switchSlideType',
            async (cell: vscode.NotebookCell | vscode.Uri | undefined) => {
                cell = reviveCell(cell);
                if (!cell) {
                    return;
                }

                // create quick pick items for each slide type
                const items: vscode.QuickPickItem[] = [];
                for (const type in SlideShowType) {
                    items.push({
                        label: type
                    });
                }

                // show quick pick
                const selected = await vscode.window.showQuickPick(items);
                // update cell metadata with this slide type
                if (selected) {
                    const selectedType = selected.label === SlideShowType.none ? undefined : selected.label;
                    await updateSlideType(cell, selectedType);
                }
            }
        )
    );

    context.subscriptions.push(
        vscode.commands.registerCommand(
            'jupyter-slideshow.editSlideShowInJSON',
            async (cell: vscode.NotebookCell | vscode.Uri | undefined) => {
                cell = reviveCell(cell);
                if (!cell) {
                    return;
                }

                const resourceUri = cell.notebook.uri;
                const document = await vscode.workspace.openTextDocument(resourceUri);
                const tree = json.parseTree(document.getText());
                const cells = json.findNodeAtLocation(tree, ['cells']);
                if (cells && cells.children && cells.children[cell.index]) {
                    const cellNode = cells.children[cell.index];
                    const metadata = json.findNodeAtLocation(cellNode, ['metadata']);
                    if (metadata) {
                        const slideshow = json.findNodeAtLocation(metadata, ['slideshow']);
                        if (slideshow) {
                            const range = new vscode.Range(
                                document.positionAt(slideshow.offset),
                                document.positionAt(slideshow.offset + slideshow.length)
                            );
                            await vscode.window.showTextDocument(document, {
                                selection: range,
                                viewColumn: vscode.ViewColumn.Beside
                            });
                        } else {
                            const range = new vscode.Range(
                                document.positionAt(metadata.offset),
                                document.positionAt(metadata.offset + metadata.length)
                            );
                            await vscode.window.showTextDocument(document, {
                                selection: range,
                                viewColumn: vscode.ViewColumn.Beside
                            });
                        }
                    } else {
                        const range = new vscode.Range(
                            document.positionAt(cellNode.offset),
                            document.positionAt(cellNode.offset + cellNode.length)
                        );
                        await vscode.window.showTextDocument(document, {
                            selection: range,
                            viewColumn: vscode.ViewColumn.Beside
                        });
                    }
                }
            }
        )
    );
}

export function getSlideType(cell: vscode.NotebookCell): SlideShowType | undefined {
    const slideshow: { slide_type: SlideShowType } | undefined =
        (useCustomMetadata() ? cell.metadata.custom?.metadata?.slideshow : cell.metadata.metadata?.slideshow) ??
        undefined;
    return slideshow?.slide_type;
}
export async function updateSlideType(cell: vscode.NotebookCell, slideType?: string) {
    if (!slideType && !getSlideType(cell)) {
        return;
    }

    const metadata = JSON.parse(JSON.stringify(cell.metadata));
    if (useCustomMetadata()) {
        metadata.custom = metadata.custom || {};
        metadata.custom.metadata = metadata.custom.metadata || {};
        if (!slideType) {
            if (metadata.custom.metadata.slideshow) {
                delete metadata.custom.metadata.slideshow;
            }
        } else {
            metadata.custom.metadata.slideshow = metadata.custom.metadata.slideshow || {};
            metadata.custom.metadata.slideshow.slide_type = slideType;
        }
    } else {
        metadata.metadata = metadata.metadata || {};
        if (!slideType) {
            if (metadata.metadata.slideshow) {
                delete metadata.metadata.slideshow;
            }
        } else {
            metadata.metadata.slideshow = metadata.metadata.slideshow || {};
            metadata.metadata.slideshow.slide_type = slideType;
        }
    }
    const edit = new vscode.WorkspaceEdit();
    const nbEdit = vscode.NotebookEdit.updateCellMetadata(cell.index, sortObjectPropertiesRecursively(metadata));
    edit.set(cell.notebook.uri, [nbEdit]);
    await vscode.workspace.applyEdit(edit);
}

function useCustomMetadata() {
    if (vscode.extensions.getExtension('vscode.ipynb')?.exports.dropCustomMetadata) {
        return false;
    }
    return true;
}


/**
 * Sort the JSON to minimize unnecessary SCM changes.
 * Jupyter notbeooks/labs sorts the JSON keys in alphabetical order.
 * https://github.com/microsoft/vscode/issues/208137
 */
function sortObjectPropertiesRecursively(obj: any): any {
	if (Array.isArray(obj)) {
		return obj.map(sortObjectPropertiesRecursively);
	}
	if (obj !== undefined && obj !== null && typeof obj === 'object' && Object.keys(obj).length > 0) {
		return (
			Object.keys(obj)
				.sort()
				.reduce<Record<string, any>>((sortedObj, prop) => {
					sortedObj[prop] = sortObjectPropertiesRecursively(obj[prop]);
					return sortedObj;
				}, {}) as any
		);
	}
	return obj;
}
