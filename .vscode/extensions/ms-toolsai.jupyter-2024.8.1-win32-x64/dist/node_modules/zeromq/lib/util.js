"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.allowMethods = void 0;
/**
 * This function is used to remove the given methods from the given socket_prototype
 * to make the relevant socket types have only their relevant methods.
 * @param socketPrototype
 * @param methods
 */
function allowMethods(socketPrototype, methods) {
    const toDelete = ["send", "receive", "join", "leave"];
    for (const method of toDelete) {
        if (methods.includes(method)) {
            delete socketPrototype[method];
        }
    }
}
exports.allowMethods = allowMethods;
//# sourceMappingURL=util.js.map