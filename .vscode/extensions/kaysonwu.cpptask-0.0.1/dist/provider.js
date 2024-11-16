"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const path_1 = require("path");
const fs_1 = require("fs");
const vscode_1 = require("vscode");
const globby = require("globby");
// @ts-ignore: default export.
const slash = require("slash");
const utils_1 = require("./utils");
const terminal_1 = require("./terminal");
class CppTaskProvider {
    static async parseSources(patterns, cwd) {
        const files = await globby(utils_1.normalizePatterns(patterns), { cwd, expandDirectories: false, onlyFiles: true });
        // Mainly used to shorten command parameters
        if (cwd) {
            return utils_1.relatives(cwd, files);
        }
        return files;
    }
    static async parseLibraies(patterns, output, cwd) {
        const files = await globby(utils_1.normalizePatterns(patterns), { cwd, expandDirectories: false, onlyFiles: true });
        const directories = [];
        const names = [];
        files.forEach(file => {
            const { dir, base, name } = path_1.parse(file);
            names.push(name);
            try {
                fs_1.symlinkSync(file, path_1.join(output, base));
            }
            catch (_a) { }
            if (!directories.includes(dir)) {
                directories.push(dir);
            }
        });
        return [directories, names];
    }
    static async parseDefinition({ compilerPath, compilerArgs, sources, output, includePath, libraryPath, options: { cwd, env } = {}, }) {
        const { dir } = path_1.parse(output);
        const options = { cwd, env: Object.assign({}, env) };
        const args = await CppTaskProvider.parseSources(sources, cwd);
        // Always try to create the output directory.
        fs_1.mkdirSync(dir, { recursive: true });
        if (includePath) {
            options.env.CPATH = (await globby(utils_1.normalizePatterns(includePath), { cwd, expandDirectories: false, onlyDirectories: true })).join(';');
        }
        if (libraryPath) {
            const [directories, names] = await CppTaskProvider.parseLibraies(libraryPath, dir, cwd);
            options.env.LIBRARY_PATH = directories.join(';');
            names.forEach(name => args.unshift('-l', name));
        }
        args.unshift(...compilerArgs, '-o', slash(output));
        return [compilerPath, args, options];
    }
    provideTasks() {
        return undefined;
    }
    resolveTask(task) {
        const definition = utils_1.mergeDefinition(task.definition);
        const { sources, output } = definition;
        if (sources && output) {
            return new vscode_1.Task(definition, vscode_1.TaskScope.Workspace, 'cpp', 'cpp', 
            // @ts-ignore
            new vscode_1.CustomExecution(async (definition) => new terminal_1.default(...(await CppTaskProvider.parseDefinition(definition)))));
        }
        return undefined;
    }
}
exports.default = CppTaskProvider;
//# sourceMappingURL=provider.js.map