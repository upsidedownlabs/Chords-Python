"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const hView_js_1 = require("./hView.js");
var path = require('path');
let currentPath;
let currentOutputPanel;
let htmlView;
let docHTML;
let docJS;
let docCSS;
let emptyHTML = '';
let emptyJS = '';
let emptyCSS = '';
function openDocument(fileName, path) {
    return __awaiter(this, void 0, void 0, function* () {
        const filePath = vscode.Uri.file(path + '/' + fileName);
        /*
        const wsedit = new vscode.WorkspaceEdit();
        wsedit.createFile(filePath, { ignoreIfExists: false });
        await vscode.workspace.applyEdit(wsedit);
        */
        let doc;
        return yield vscode.workspace.openTextDocument(filePath).then((doc) => {
            return (doc);
        }, () => {
            return (undefined);
        });
        //return doc;
    });
}
function openDefaultFiles(path) {
    return __awaiter(this, void 0, void 0, function* () {
        docHTML = yield openDocument("index.html", path);
        docJS = yield openDocument("script.js", path);
        docCSS = yield openDocument("style.css", path);
    });
}
function debounce(fn, delay) {
    var timer;
    return function () {
        var context = this;
        var args = arguments;
        clearTimeout(timer); // 清除定义时，保证不执行fn
        timer = setTimeout(function () {
            fn.apply(context, args);
        }, delay);
    };
}
function getFilePath(v) {
    return path.dirname(v);
}
function getFileName(v) {
    return path.basename(v);
}
function loadFiles(pathName, fileName) {
    return __awaiter(this, void 0, void 0, function* () {
        if (fileName === 'index.html' || fileName === 'script.js' || fileName === 'style.css') {
            yield openDefaultFiles(pathName);
        }
        else {
            if (/\.html$/.test(fileName)) {
                docHTML = yield openDocument(fileName, pathName);
                docJS = emptyJS;
                docCSS = emptyCSS;
            }
            else if (/\.js$/.test(fileName)) {
                docHTML = emptyHTML;
                docJS = yield openDocument(fileName, pathName);
                ;
                docCSS = emptyCSS;
            }
            else if (/\.css$/.test(fileName)) {
                docHTML = emptyHTML;
                docJS = emptyJS;
                docCSS = yield openDocument(fileName, pathName);
            }
            else {
                // not .html .js .css file
                yield openDefaultFiles(pathName);
            }
        }
        htmlView.setHtml(docHTML ? docHTML.getText() : "");
        htmlView.setJs(docJS ? docJS.getText() : "");
        htmlView.setCss(docCSS ? docCSS.getText() : "");
        htmlView.createHTML();
    });
}
function activate(context) {
    return __awaiter(this, void 0, void 0, function* () {
        context.subscriptions.push(vscode.workspace.onDidChangeTextDocument(// 文件修改时触发
        debounce((e) => {
            if (e.document === docHTML) {
                htmlView.setHtml(docHTML.getText());
            }
            else if (e.document === docJS) {
                htmlView.setJs(docJS.getText());
            }
            else if (e.document === docCSS) {
                htmlView.setCss(docCSS.getText());
            }
            htmlView.createHTML();
        }, 500)));
        let disposable = vscode.window.onDidChangeActiveTextEditor((editor) => __awaiter(this, void 0, void 0, function* () {
            if (!vscode.window.activeTextEditor) {
                return;
            }
            let fsPath = vscode.window.activeTextEditor.document.uri.fsPath;
            let fileName = getFileName(fsPath);
            let pathName = getFilePath(fsPath);
            if (currentOutputPanel) {
                yield loadFiles(pathName, fileName);
                // await openDefaultFiles(p);
                //const htmlView = new HTMLView(currentOutputPanel.webview, context);
                // htmlView = new hView(currentOutputPanel.webview, context);
                // htmlView.setHtml(docHTML ? docHTML.getText() : "");
                // htmlView.setJs(docJS ? docJS.getText() : "");
                // htmlView.setCss(docCSS ? docCSS.getText() : "");
            }
        }));
        context.subscriptions.push(disposable);
        vscode.window.onDidChangeActiveTextEditor(function (editor) {
            //console.log("onDidChangeActiveTextEditor" + editor.document.fileName);
            console.log("change");
        });
        context.subscriptions.push(vscode.commands.registerCommand("htmlplay.play", (openAsFolder) => __awaiter(this, void 0, void 0, function* () {
            var pathName;
            var fileName;
            if (vscode.window.activeTextEditor) {
                let fsPath = vscode.window.activeTextEditor.document.uri.fsPath;
                fileName = getFileName(fsPath);
                pathName = getFilePath(fsPath);
            }
            else {
                vscode.window.showInformationMessage("please open a file");
                return;
            }
            currentPath = pathName;
            if (currentOutputPanel) {
                currentOutputPanel.dispose();
            }
            else {
                yield openDefaultFiles(currentPath);
                //await myprepareWorkspace(currentPath);
                currentOutputPanel = vscode.window.createWebviewPanel("HtmlPlayOutput", "Output", { viewColumn: vscode.ViewColumn.Beside, preserveFocus: true }, 
                //{ viewColumn: vscode.ViewColumn.Two, preserveFocus: true },
                { enableScripts: true });
                currentOutputPanel.onDidDispose(() => {
                    currentOutputPanel = undefined;
                    //vscode.window.showInformationMessage("webview closed");
                }, null, context.subscriptions);
                htmlView = new hView_js_1.hView(currentOutputPanel.webview, context);
                yield loadFiles(pathName, fileName);
            }
            return;
        })));
    });
}
exports.activate = activate;
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map