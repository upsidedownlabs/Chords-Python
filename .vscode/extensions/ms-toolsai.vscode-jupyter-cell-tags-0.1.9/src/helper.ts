// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

import * as vscode from 'vscode';

export function getCellTags(cell: vscode.NotebookCell): string[] {
    const currentTags =
        (useCustomMetadata() ? cell.metadata.custom?.metadata?.tags : cell.metadata.metadata?.tags) ?? [];
    return [...currentTags];
}

export async function updateCellTags(cell: vscode.NotebookCell, tags: string[]) {
    const metadata = JSON.parse(JSON.stringify(cell.metadata));
    if (useCustomMetadata()) {
        metadata.custom = metadata.custom || {};
        metadata.custom.metadata = metadata.custom.metadata || {};
        metadata.custom.metadata.tags = tags;
        if (tags.length === 0) {
            delete metadata.custom.metadata.tags;
        }
    } else {
        metadata.metadata = metadata.metadata || {};
        metadata.metadata.tags = tags;
        if (tags.length === 0) {
            delete metadata.metadata.tags;
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
