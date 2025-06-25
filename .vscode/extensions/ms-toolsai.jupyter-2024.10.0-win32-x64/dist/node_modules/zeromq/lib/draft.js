"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Datagram = exports.Scatter = exports.Gather = exports.Dish = exports.Radio = exports.Client = exports.Server = void 0;
const native_1 = require("./native");
const util_1 = require("./util");
class Server extends native_1.Socket {
    constructor(options) {
        super(12 /* SocketType.Server */, options);
    }
}
exports.Server = Server;
(0, util_1.allowMethods)(Server.prototype, ["send", "receive"]);
class Client extends native_1.Socket {
    constructor(options) {
        super(13 /* SocketType.Client */, options);
    }
}
exports.Client = Client;
(0, util_1.allowMethods)(Client.prototype, ["send", "receive"]);
class Radio extends native_1.Socket {
    constructor(options) {
        super(14 /* SocketType.Radio */, options);
    }
}
exports.Radio = Radio;
(0, util_1.allowMethods)(Radio.prototype, ["send"]);
const join = native_1.Socket.prototype.join;
const leave = native_1.Socket.prototype.leave;
class Dish extends native_1.Socket {
    constructor(options) {
        super(15 /* SocketType.Dish */, options);
    }
    /* TODO: These methods might accept arrays in their C++ implementation for
       the sake of simplicity. */
    join(...values) {
        for (const value of values) {
            join(value);
        }
    }
    leave(...values) {
        for (const value of values) {
            leave(value);
        }
    }
}
exports.Dish = Dish;
(0, util_1.allowMethods)(Dish.prototype, ["receive", "join", "leave"]);
class Gather extends native_1.Socket {
    constructor(options) {
        super(16 /* SocketType.Gather */, options);
    }
}
exports.Gather = Gather;
(0, util_1.allowMethods)(Gather.prototype, ["receive"]);
class Scatter extends native_1.Socket {
    constructor(options) {
        super(17 /* SocketType.Scatter */, options);
    }
}
exports.Scatter = Scatter;
(0, util_1.allowMethods)(Scatter.prototype, ["send"]);
class Datagram extends native_1.Socket {
    constructor(options) {
        super(18 /* SocketType.Datagram */, options);
    }
}
exports.Datagram = Datagram;
(0, util_1.allowMethods)(Datagram.prototype, ["send", "receive"]);
//# sourceMappingURL=draft.js.map