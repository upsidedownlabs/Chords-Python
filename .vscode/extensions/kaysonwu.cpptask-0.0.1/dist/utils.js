"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.relatives = exports.normalizePatterns = exports.mergeDefinition = void 0;
const path_1 = require("path");
// @ts-ignore: default export.
const slash = require("slash");
// @ts-ignore: default export.
const merge = require("lodash.merge");
/**
 * If the given value is not an array and not null, wrap it in one.
 *
 * @param   {T | T[]} value
 * @returns {T[]}
 */
function wrap(value) {
    return Array.isArray(value) ? value : [value];
}
function normalizePlatform(platform) {
    switch (platform) {
        case 'win32':
            return 'windows';
        case 'linux':
            return 'linux';
        case 'darwin':
            return 'osx';
        default:
            return platform;
    }
}
function mergeDefinition(definition, platform = process.platform) {
    const name = normalizePlatform(platform);
    if (Object.prototype.hasOwnProperty.call(definition, name)) {
        return merge({}, definition, definition[name]);
    }
    return definition;
}
exports.mergeDefinition = mergeDefinition;
function normalizePatterns(patterns) {
    if (process.platform === 'win32') {
        return wrap(patterns).map(slash);
    }
    return patterns;
}
exports.normalizePatterns = normalizePatterns;
function relatives(from, to) {
    return to.map(file => {
        const path = path_1.relative(from, file);
        return process.platform === 'win32' ? slash(path) : path;
    });
}
exports.relatives = relatives;
//# sourceMappingURL=utils.js.map