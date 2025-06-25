"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Stream = exports.XSubscriber = exports.XPublisher = exports.Push = exports.Pull = exports.Router = exports.Dealer = exports.Reply = exports.Request = exports.Subscriber = exports.Publisher = exports.Pair = exports.Proxy = exports.Observer = exports.Socket = exports.Context = exports.version = exports.curveKeyPair = exports.context = exports.capability = void 0;
const util_1 = require("./util");
var native_1 = require("./native");
Object.defineProperty(exports, "capability", { enumerable: true, get: function () { return native_1.capability; } });
Object.defineProperty(exports, "context", { enumerable: true, get: function () { return native_1.context; } });
Object.defineProperty(exports, "curveKeyPair", { enumerable: true, get: function () { return native_1.curveKeyPair; } });
Object.defineProperty(exports, "version", { enumerable: true, get: function () { return native_1.version; } });
Object.defineProperty(exports, "Context", { enumerable: true, get: function () { return native_1.Context; } });
Object.defineProperty(exports, "Socket", { enumerable: true, get: function () { return native_1.Socket; } });
Object.defineProperty(exports, "Observer", { enumerable: true, get: function () { return native_1.Observer; } });
Object.defineProperty(exports, "Proxy", { enumerable: true, get: function () { return native_1.Proxy; } });
const native_2 = require("./native");
const draft = require("./draft");
/* Support async iteration over received messages. Implementing this in JS
   is faster as long as there is no C++ native API to chain promises. */
function asyncIterator() {
    return {
        next: async () => {
            if (this.closed) {
                /* Cast so we can omit 'value: undefined'. */
                return { done: true };
            }
            try {
                return { value: await this.receive(), done: false };
            }
            catch (err) {
                if (this.closed && err.code === "EAGAIN") {
                    /* Cast so we can omit 'value: undefined'. */
                    return { done: true };
                }
                else {
                    throw err;
                }
            }
        },
    };
}
Object.assign(native_2.Socket.prototype, { [Symbol.asyncIterator]: asyncIterator });
Object.assign(native_2.Observer.prototype, { [Symbol.asyncIterator]: asyncIterator });
if (!native_2.Observer.prototype.hasOwnProperty("emitter")) {
    Object.defineProperty(native_2.Observer.prototype, "emitter", {
        get: function emitter() {
            /* eslint-disable-next-line @typescript-eslint/no-var-requires */
            const events = require("events");
            const value = new events.EventEmitter();
            const boundReceive = this.receive.bind(this);
            Object.defineProperty(this, "receive", {
                get: () => {
                    throw new Error("Observer is in event emitter mode. " +
                        "After a call to events.on() it is not possible to read events " +
                        "with events.receive().");
                },
            });
            const run = async () => {
                while (!this.closed) {
                    const event = await boundReceive();
                    value.emit(event.type, event);
                }
            };
            run();
            Object.defineProperty(this, "emitter", { value });
            return value;
        },
    });
}
native_2.Observer.prototype.on = function on(...args) {
    return this.emitter.on(...args);
};
native_2.Observer.prototype.off = function off(...args) {
    return this.emitter.off(...args);
};
/* Concrete socket types. */
/**
 * A {@link Pair} socket can only be connected to one other {@link Pair} at any
 * one time. No message routing or filtering is performed on any messages.
 *
 * When a {@link Pair} socket enters the mute state due to having reached the
 * high water mark for the connected peer, or if no peer is connected, then any
 * {@link Writable.send}() operations on the socket shall block until the peer
 * becomes available for sending; messages are not discarded.
 *
 * While {@link Pair} sockets can be used over transports other than
 * `inproc://`, their inability to auto-reconnect coupled with the fact new
 * incoming connections will be terminated while any previous connections
 * (including ones in a closing state) exist makes them unsuitable for `tcp://`
 * in most cases.
 */
class Pair extends native_2.Socket {
    constructor(options) {
        super(0 /* SocketType.Pair */, options);
    }
}
exports.Pair = Pair;
(0, util_1.allowMethods)(Pair.prototype, ["send", "receive"]);
/**
 * A {@link Publisher} socket is used to distribute data to {@link Subscriber}s.
 * Messages sent are distributed in a fan out fashion to all connected peers.
 * This socket cannot receive messages.
 *
 * When a {@link Publisher} enters the mute state due to having reached the high
 * water mark for a connected {@link Subscriber}, then any messages that would
 * be sent to the subscriber in question shall instead be dropped until the mute
 * state ends. The {@link Writable.send}() method will never block.
 */
class Publisher extends native_2.Socket {
    constructor(options) {
        super(1 /* SocketType.Publisher */, options);
    }
}
exports.Publisher = Publisher;
(0, util_1.allowMethods)(Publisher.prototype, ["send"]);
/**
 * A {@link Subscriber} socket is used to subscribe to data distributed by a
 * {@link Publisher}. Initially a {@link Subscriber} is not subscribed to any
 * messages. Use {@link Subscriber.subscribe}() to specify which messages to
 * subscribe to. This socket cannot send messages.
 */
class Subscriber extends native_2.Socket {
    constructor(options) {
        super(2 /* SocketType.Subscriber */, options);
    }
    /**
     * Establish a new message filter. Newly created {@link Subsriber} sockets
     * will filtered out all incoming messages. Call this method to subscribe to
     * messages beginning with the given prefix.
     *
     * Multiple filters may be attached to a single socket, in which case a
     * message shall be accepted if it matches at least one filter. Subscribing
     * without any filters shall subscribe to **all** incoming messages.
     *
     * ```typescript
     * const sub = new Subscriber()
     *
     * // Listen to all messages beginning with 'foo'.
     * sub.subscribe("foo")
     *
     * // Listen to all incoming messages.
     * sub.subscribe()
     * ```
     *
     * @param prefixes The prefixes of messages to subscribe to.
     */
    subscribe(...prefixes) {
        if (prefixes.length === 0) {
            this.setStringOption(6, null);
        }
        else {
            for (const prefix of prefixes) {
                this.setStringOption(6, prefix);
            }
        }
    }
    /**
     * Remove an existing message filter which was previously established with
     * {@link subscribe}(). Stops receiving messages with the given prefix.
     *
     * Unsubscribing without any filters shall unsubscribe from the "subscribe
     * all" filter that is added by calling {@link subscribe}() without arguments.
     *
     * ```typescript
     * const sub = new Subscriber()
     *
     * // Listen to all messages beginning with 'foo'.
     * sub.subscribe("foo")
     * // ...
     *
     * // Stop listening to messages beginning with 'foo'.
     * sub.unsubscribe("foo")
     * ```
     *
     * @param prefixes The prefixes of messages to subscribe to.
     */
    unsubscribe(...prefixes) {
        if (prefixes.length === 0) {
            this.setStringOption(7, null);
        }
        else {
            for (const prefix of prefixes) {
                this.setStringOption(7, prefix);
            }
        }
    }
}
exports.Subscriber = Subscriber;
(0, util_1.allowMethods)(Subscriber.prototype, ["receive"]);
/**
 * A {@link Request} socket acts as a client to send requests to and receive
 * replies from a {@link Reply} socket. This socket allows only an alternating
 * sequence of {@link Writable.send}() and subsequent {@link Readable.receive}()
 * calls. Each request sent is round-robined among all services, and each reply
 * received is matched with the last issued request.
 *
 * If no services are available, then any send operation on the socket shall
 * block until at least one service becomes available. The REQ socket shall not
 * discard messages.
 */
class Request extends native_2.Socket {
    constructor(options) {
        super(3 /* SocketType.Request */, options);
    }
}
exports.Request = Request;
(0, util_1.allowMethods)(Request.prototype, ["send", "receive"]);
/**
 * A {@link Reply} socket can act as a server which receives requests from and
 * sends replies to a {@link Request} socket. This socket type allows only an
 * alternating sequence of {@link Readable.receive}() and subsequent
 * {@link Writable.send}() calls. Each request received is fair-queued from
 * among all clients, and each reply sent is routed to the client that issued
 * the last request. If the original requester does not exist any more the reply
 * is silently discarded.
 */
class Reply extends native_2.Socket {
    constructor(options) {
        super(4 /* SocketType.Reply */, options);
    }
}
exports.Reply = Reply;
(0, util_1.allowMethods)(Reply.prototype, ["send", "receive"]);
/**
 * A {@link Dealer} socket can be used to extend request/reply sockets. Each
 * message sent is round-robined among all connected peers, and each message
 * received is fair-queued from all connected peers.
 *
 * When a {@link Dealer} socket enters the mute state due to having reached the
 * high water mark for all peers, or if there are no peers at all, then any
 * {@link Writable.send}() operations on the socket shall block until the mute
 * state ends or at least one peer becomes available for sending; messages are
 * not discarded.
 *
 * When a {@link Dealer} is connected to a {@link Reply} socket, each message
 * sent must consist of an empty message part, the delimiter, followed by one or
 * more body parts.
 */
class Dealer extends native_2.Socket {
    constructor(options) {
        super(5 /* SocketType.Dealer */, options);
    }
}
exports.Dealer = Dealer;
(0, util_1.allowMethods)(Dealer.prototype, ["send", "receive"]);
/**
 * A {@link Router} can be used to extend request/reply sockets. When receiving
 * messages a {@link Router} shall prepend a message part containing the routing
 * id of the originating peer to the message. Messages received are fair-queued
 * from among all connected peers. When sending messages, the first part of the
 * message is removed and used to determine the routing id of the peer the
 * message should be routed to.
 *
 * If the peer does not exist anymore, or has never existed, the message shall
 * be silently discarded. However, if {@link Router.mandatory} is set to `true`,
 * the socket shall fail with a `EHOSTUNREACH` error in both cases.
 *
 * When a {@link Router} enters the mute state due to having reached the high
 * water mark for all peers, then any messages sent to the socket shall be
 * dropped until the mute state ends. Likewise, any messages routed to a peer
 * for which the individual high water mark has been reached shall also be
 * dropped. If {@link Router.mandatory} is set to `true` the socket shall block
 * or return an `EAGAIN` error in both cases.
 *
 * When a {@link Request} socket is connected to a {@link Router}, in addition
 * to the routing id of the originating peer each message received shall contain
 * an empty delimiter message part. Hence, the entire structure of each received
 * message as seen by the application becomes: one or more routing id parts,
 * delimiter part, one or more body parts. When sending replies to a
 * {@link Request} the delimiter part must be included.
 */
class Router extends native_2.Socket {
    constructor(options) {
        super(6 /* SocketType.Router */, options);
    }
    /**
     * Connects to the given remote address. To specificy a specific routing id,
     * provide a `routingId` option. The identity should be unique, from 1 to 255
     * bytes long and MAY NOT start with binary zero.
     *
     * @param address The `tcp://` address to connect to.
     * @param options Any connection options.
     */
    connect(address, options = {}) {
        if (options.routingId) {
            this.setStringOption(61, options.routingId);
        }
        super.connect(address);
    }
}
exports.Router = Router;
(0, util_1.allowMethods)(Router.prototype, ["send", "receive"]);
/**
 * A {@link Pull} socket is used by a pipeline node to receive messages from
 * upstream pipeline nodes. Messages are fair-queued from among all connected
 * upstream nodes. This socket cannot send messages.
 */
class Pull extends native_2.Socket {
    constructor(options) {
        super(7 /* SocketType.Pull */, options);
    }
}
exports.Pull = Pull;
(0, util_1.allowMethods)(Pull.prototype, ["receive"]);
/**
 * A {@link Push} socket is used by a pipeline node to send messages to
 * downstream pipeline nodes. Messages are round-robined to all connected
 * downstream nodes. This socket cannot receive messages.
 *
 * When a {@link Push} socket enters the mute state due to having reached the
 * high water mark for all downstream nodes, or if there are no downstream nodes
 * at all, then {@link Writable.send}() will block until the mute state ends or
 * at least one downstream node becomes available for sending; messages are not
 * discarded.
 */
class Push extends native_2.Socket {
    constructor(options) {
        super(8 /* SocketType.Push */, options);
    }
}
exports.Push = Push;
(0, util_1.allowMethods)(Push.prototype, ["send"]);
/**
 * Same as {@link Publisher}, except that you can receive subscriptions from the
 * peers in form of incoming messages. Subscription message is a byte 1 (for
 * subscriptions) or byte 0 (for unsubscriptions) followed by the subscription
 * body. Messages without a sub/unsub prefix are also received, but have no
 * effect on subscription status.
 */
class XPublisher extends native_2.Socket {
    /**
     * ZMQ_XPUB_VERBOSE / ZMQ_XPUB_VERBOSER
     *
     * Whether to pass any duplicate subscription/unsuscription messages.
     *  * `null` (default) - Only unique subscribe and unsubscribe messages are
     *    visible to the caller.
     *  * `"allSubs"` - All subscribe messages (including duplicates) are visible
     *    to the caller, but only unique unsubscribe messages are visible.
     *  * `"allSubsUnsubs"` - All subscribe and unsubscribe messages (including
     *    duplicates) are visible to the caller.
     */
    set verbosity(value) {
        /* ZMQ_XPUB_VERBOSE and ZMQ_XPUB_VERBOSER interact, so we normalize the
           situation by making it a single property. */
        switch (value) {
            case null:
                /* This disables ZMQ_XPUB_VERBOSE + ZMQ_XPUB_VERBOSER: */
                this.setBoolOption(40 /* ZMQ_XPUB_VERBOSE */, false);
                break;
            case "allSubs":
                this.setBoolOption(40 /* ZMQ_XPUB_VERBOSE */, true);
                break;
            case "allSubsUnsubs":
                this.setBoolOption(78 /* ZMQ_XPUB_VERBOSER */, true);
                break;
        }
    }
    constructor(options) {
        super(9 /* SocketType.XPublisher */, options);
    }
}
exports.XPublisher = XPublisher;
(0, util_1.allowMethods)(XPublisher.prototype, ["send", "receive"]);
/**
 * Same as {@link Subscriber}, except that you subscribe by sending subscription
 * messages to the socket. Subscription message is a byte 1 (for subscriptions)
 * or byte 0 (for unsubscriptions) followed by the subscription body. Messages
 * without a sub/unsub prefix may also be sent, but have no effect on
 * subscription status.
 */
class XSubscriber extends native_2.Socket {
    constructor(options) {
        super(10 /* SocketType.XSubscriber */, options);
    }
}
exports.XSubscriber = XSubscriber;
(0, util_1.allowMethods)(XSubscriber.prototype, ["send", "receive"]);
/**
 * A {@link Stream} is used to send and receive TCP data from a non-ØMQ peer
 * with the `tcp://` transport. A {@link Stream} can act as client and/or
 * server, sending and/or receiving TCP data asynchronously.
 *
 * When sending and receiving data with {@link Writable.send}() and
 * {@link Readable.receive}(), the first message part shall be the routing id of
 * the peer. Unroutable messages will cause an error.
 *
 * When a connection is made to a {@link Stream}, a zero-length message will be
 * received. Similarly, when the peer disconnects (or the connection is lost), a
 * zero-length message will be received.
 *
 * To close a specific connection, {@link Writable.send}() the routing id frame
 * followed by a zero-length message.
 *
 * To open a connection to a server, use {@link Stream.connect}().
 */
class Stream extends native_2.Socket {
    constructor(options) {
        super(11 /* SocketType.Stream */, options);
    }
    /**
     * Connects to the given remote address. To specificy a specific routing id,
     * provide a `routingId` option. The identity should be unique, from 1 to 255
     * bytes long and MAY NOT start with binary zero.
     *
     * @param address The `tcp://` address to connect to.
     * @param options Any connection options.
     */
    connect(address, options = {}) {
        if (options.routingId) {
            this.setStringOption(61, options.routingId);
        }
        super.connect(address);
    }
}
exports.Stream = Stream;
(0, util_1.allowMethods)(Stream.prototype, ["send", "receive"]);
/* The default is to use R/w. The overloads above ensure the correct flag is
   set if the property has been defined as readonly in the interface/class. */
function defineOpt(targets, name, id, type, acc = 3 /* Acc.ReadWrite */, values) {
    const desc = {};
    if (acc & 1 /* Acc.Read */) {
        const getter = `get${type}Option`;
        if (values) {
            desc.get = function get() {
                return values[this[getter](id)];
            };
        }
        else {
            desc.get = function get() {
                return this[getter](id);
            };
        }
    }
    if (acc & 2 /* Acc.Write */) {
        const setter = `set${type}Option`;
        if (values) {
            desc.set = function set(val) {
                this[setter](id, values.indexOf(val));
            };
        }
        else {
            desc.set = function set(val) {
                this[setter](id, val);
            };
        }
    }
    for (const target of targets) {
        if (target.prototype.hasOwnProperty(name)) {
            continue;
        }
        Object.defineProperty(target.prototype, name, desc);
    }
}
/* Context options. ALSO include any options in the Context interface above. */
defineOpt([native_2.Context], "ioThreads", 1, "Int32" /* Type.Int32 */);
defineOpt([native_2.Context], "maxSockets", 2, "Int32" /* Type.Int32 */);
defineOpt([native_2.Context], "maxSocketsLimit", 3, "Int32" /* Type.Int32 */, 1 /* Acc.Read */);
defineOpt([native_2.Context], "threadPriority", 3, "Int32" /* Type.Int32 */, 2 /* Acc.Write */);
defineOpt([native_2.Context], "threadSchedulingPolicy", 4, "Int32" /* Type.Int32 */, 2 /* Acc.Write */);
defineOpt([native_2.Context], "maxMessageSize", 5, "Int32" /* Type.Int32 */);
defineOpt([native_2.Context], "ipv6", 42, "Bool" /* Type.Bool */);
defineOpt([native_2.Context], "blocky", 70, "Bool" /* Type.Bool */);
/* Option 'msgTSize' is fairly useless in Node.js. */
/* These options should be methods. */
/* defineOpt([Context], "threadAffinityCpuAdd", 7, Type.Int32) */
/* defineOpt([Context], "threadAffinityCpuRemove", 8, Type.Int32) */
/* To be released in a new ZeroMQ version. */
/* if (Context.prototype.setStringOption) {
  defineOpt([Context], "threadNamePrefix", 9, Type.String)
} */
/* There should be no reason to change this in JS. */
/* defineOpt([Context], "zeroCopyRecv", 10, Type.Bool) */
/* Socket options. ALSO include any options in the Socket interface above. */
const writables = [
    Pair,
    Publisher,
    Request,
    Reply,
    Dealer,
    Router,
    Push,
    XPublisher,
    XSubscriber,
    Stream,
    draft.Server,
    draft.Client,
    draft.Radio,
    draft.Scatter,
    draft.Datagram,
];
defineOpt(writables, "sendBufferSize", 11, "Int32" /* Type.Int32 */);
defineOpt(writables, "sendHighWaterMark", 23, "Int32" /* Type.Int32 */);
defineOpt(writables, "sendTimeout", 28, "Int32" /* Type.Int32 */);
defineOpt(writables, "multicastHops", 25, "Int32" /* Type.Int32 */);
const readables = [
    Pair,
    Subscriber,
    Request,
    Reply,
    Dealer,
    Router,
    Pull,
    XPublisher,
    XSubscriber,
    Stream,
    draft.Server,
    draft.Client,
    draft.Dish,
    draft.Gather,
    draft.Datagram,
];
defineOpt(readables, "receiveBufferSize", 12, "Int32" /* Type.Int32 */);
defineOpt(readables, "receiveHighWaterMark", 24, "Int32" /* Type.Int32 */);
defineOpt(readables, "receiveTimeout", 27, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "affinity", 4, "Uint64" /* Type.Uint64 */);
defineOpt([Request, Reply, Router, Dealer], "routingId", 5, "String" /* Type.String */);
defineOpt([native_2.Socket], "rate", 8, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "recoveryInterval", 9, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "type", 16, "Int32" /* Type.Int32 */, 1 /* Acc.Read */);
defineOpt([native_2.Socket], "linger", 17, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "reconnectInterval", 18, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "backlog", 19, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "reconnectMaxInterval", 21, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "maxMessageSize", 22, "Int64" /* Type.Int64 */);
defineOpt([native_2.Socket], "lastEndpoint", 32, "String" /* Type.String */, 1 /* Acc.Read */);
defineOpt([Router], "mandatory", 33, "Bool" /* Type.Bool */);
defineOpt([native_2.Socket], "tcpKeepalive", 34, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "tcpKeepaliveCount", 35, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "tcpKeepaliveIdle", 36, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "tcpKeepaliveInterval", 37, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "tcpAcceptFilter", 38, "String" /* Type.String */);
defineOpt([native_2.Socket], "immediate", 39, "Bool" /* Type.Bool */);
/* Option 'verbose' is implemented as verbosity on XPublisher. */
defineOpt([native_2.Socket], "ipv6", 42, "Bool" /* Type.Bool */);
defineOpt([native_2.Socket], "securityMechanism", 43, "Int32" /* Type.Int32 */, 1 /* Acc.Read */, [
    null,
    "plain",
    "curve",
    "gssapi",
]);
defineOpt([native_2.Socket], "plainServer", 44, "Bool" /* Type.Bool */);
defineOpt([native_2.Socket], "plainUsername", 45, "String" /* Type.String */);
defineOpt([native_2.Socket], "plainPassword", 46, "String" /* Type.String */);
if (native_2.capability.curve) {
    defineOpt([native_2.Socket], "curveServer", 47, "Bool" /* Type.Bool */);
    defineOpt([native_2.Socket], "curvePublicKey", 48, "String" /* Type.String */);
    defineOpt([native_2.Socket], "curveSecretKey", 49, "String" /* Type.String */);
    defineOpt([native_2.Socket], "curveServerKey", 50, "String" /* Type.String */);
}
defineOpt([Router, Dealer, Request], "probeRouter", 51, "Bool" /* Type.Bool */, 2 /* Acc.Write */);
defineOpt([Request], "correlate", 52, "Bool" /* Type.Bool */, 2 /* Acc.Write */);
defineOpt([Request], "relaxed", 53, "Bool" /* Type.Bool */, 2 /* Acc.Write */);
const conflatables = [
    Pull,
    Push,
    Subscriber,
    Publisher,
    Dealer,
    draft.Scatter,
    draft.Gather,
];
defineOpt(conflatables, "conflate", 54, "Bool" /* Type.Bool */, 2 /* Acc.Write */);
defineOpt([native_2.Socket], "zapDomain", 55, "String" /* Type.String */);
defineOpt([Router], "handover", 56, "Bool" /* Type.Bool */, 2 /* Acc.Write */);
defineOpt([native_2.Socket], "typeOfService", 57, "Uint32" /* Type.Uint32 */);
if (native_2.capability.gssapi) {
    defineOpt([native_2.Socket], "gssapiServer", 62, "Bool" /* Type.Bool */);
    defineOpt([native_2.Socket], "gssapiPrincipal", 63, "String" /* Type.String */);
    defineOpt([native_2.Socket], "gssapiServicePrincipal", 64, "String" /* Type.String */);
    defineOpt([native_2.Socket], "gssapiPlainText", 65, "Bool" /* Type.Bool */);
    const principals = ["hostBased", "userName", "krb5Principal"];
    defineOpt([native_2.Socket], "gssapiPrincipalNameType", 90, "Int32" /* Type.Int32 */, 3 /* Acc.ReadWrite */, principals);
    defineOpt([native_2.Socket], "gssapiServicePrincipalNameType", 91, "Int32" /* Type.Int32 */, 3 /* Acc.ReadWrite */, principals);
}
defineOpt([native_2.Socket], "handshakeInterval", 66, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "socksProxy", 68, "String" /* Type.String */);
defineOpt([XPublisher, Publisher], "noDrop", 69, "Bool" /* Type.Bool */, 2 /* Acc.Write */);
defineOpt([XPublisher], "manual", 71, "Bool" /* Type.Bool */, 2 /* Acc.Write */);
defineOpt([XPublisher], "welcomeMessage", 72, "String" /* Type.String */, 2 /* Acc.Write */);
defineOpt([Stream], "notify", 73, "Bool" /* Type.Bool */, 2 /* Acc.Write */);
defineOpt([Publisher, Subscriber, XPublisher], "invertMatching", 74, "Bool" /* Type.Bool */);
defineOpt([native_2.Socket], "heartbeatInterval", 75, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "heartbeatTimeToLive", 76, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "heartbeatTimeout", 77, "Int32" /* Type.Int32 */);
/* Option 'verboser' is implemented as verbosity on XPublisher. */
defineOpt([native_2.Socket], "connectTimeout", 79, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "tcpMaxRetransmitTimeout", 80, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "threadSafe", 81, "Bool" /* Type.Bool */, 1 /* Acc.Read */);
defineOpt([native_2.Socket], "multicastMaxTransportDataUnit", 84, "Int32" /* Type.Int32 */);
defineOpt([native_2.Socket], "vmciBufferSize", 85, "Uint64" /* Type.Uint64 */);
defineOpt([native_2.Socket], "vmciBufferMinSize", 86, "Uint64" /* Type.Uint64 */);
defineOpt([native_2.Socket], "vmciBufferMaxSize", 87, "Uint64" /* Type.Uint64 */);
defineOpt([native_2.Socket], "vmciConnectTimeout", 88, "Int32" /* Type.Int32 */);
/* Option 'useFd' is fairly useless in Node.js. */
defineOpt([native_2.Socket], "interface", 92, "String" /* Type.String */);
defineOpt([native_2.Socket], "zapEnforceDomain", 93, "Bool" /* Type.Bool */);
defineOpt([native_2.Socket], "loopbackFastPath", 94, "Bool" /* Type.Bool */);
/* The following options are still in DRAFT. */
/* defineOpt([Socket], "metadata", 95, Type.String) */
/* defineOpt([Socket], "multicastLoop", 96, Type.String) */
/* defineOpt([Router], "notify", 97, Type.String) */
/* defineOpt([XPublisher], "manualLastValue", 98, Type.String) */
/* defineOpt([Socket], "socksUsername", 99, Type.String) */
/* defineOpt([Socket], "socksPassword", 100, Type.String) */
/* defineOpt([Socket], "inBatchSize", 101, Type.String) */
/* defineOpt([Socket], "outBatchSize", 102, Type.String) */
//# sourceMappingURL=index.js.map