"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const child_process_1 = require("child_process");
const vscode_1 = require("vscode");
class Terminal {
    constructor(command, args, options = {}) {
        this.writeEmitter = new vscode_1.EventEmitter();
        this.closeEmitter = new vscode_1.EventEmitter();
        this.onDidWrite = this.writeEmitter.event;
        this.onDidClose = this.closeEmitter.event;
        this.command = `${command} ${args.join(' ')}`;
        this.options = options;
    }
    static line(content) {
        if (process.platform === 'win32') {
            return `${content.replace(/\r?\n/g, '\r\n')}\r\n`;
        }
        return `${content}\n`;
    }
    error(title, description) {
        this.writeEmitter.fire('\x1b[31merror ' + Terminal.line(title) + '\x1b[0m' + Terminal.line(description));
        this.closeEmitter.fire(1);
    }
    success(message) {
        this.writeEmitter.fire('\x1b[32msuccess \x1b[0m' + Terminal.line(message));
        this.closeEmitter.fire(0);
    }
    open() {
        this.writeEmitter.fire(Terminal.line(`$ ${this.command}`));
        child_process_1.exec(this.command, this.options, (_, __, stderr) => {
            if (stderr) {
                this.error('Compilation failed', stderr);
            }
            else {
                this.success('Compiled successfully');
            }
        });
    }
    close() { }
}
exports.default = Terminal;
//# sourceMappingURL=terminal.js.map