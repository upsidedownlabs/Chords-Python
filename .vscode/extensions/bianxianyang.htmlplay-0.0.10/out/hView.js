"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.hView = void 0;
const vscode = require("vscode");
const jsdom_1 = require("jsdom");
function hView(webview, context) {
    this.webview = webview;
    webview.onDidReceiveMessage(msg => {
        switch (msg.command) {
            case "alert":
                if (!msg.text) {
                    return;
                }
                // vscode.window.showWarningMessage(msg.text, { modal: true });
                vscode.window.showWarningMessage(msg.text);
                break;
        }
    }, undefined, context.subscriptions);
    this.createHTML();
}
exports.hView = hView;
;
const resetStyle = `
/* reset browser styles */
html, body, div, span, object, iframe, h1, h2, h3, h4, h5, h6, p, blockquote, pre, a, abbr, acronym, address, big, cite, code, del, dfn, em, img, ins, kbd, q, s, samp,small, strike, strong, sub, sup, tt, var, b, u, i, center, dl, dt, dd, ol, ul, li, fieldset, form, label, legend,
table, caption, tbody, tfoot, thead, tr, th, td, article, aside, canvas, details, embed, 
figure, figcaption, footer, header, hgroup, menu, nav, output, ruby, section, summary,
time, mark, audio, video {
	margin: 0;
	padding: 0;
	border: 0;
	font-size: 100%;
	vertical-align: baseline;
}
article, aside, details, figcaption, figure, footer, header, hgroup, menu, nav, section {
	display: block;
}
body {
	line-height: 1.2;
}
ol { 
	padding-left: 1.4em;
	list-style: decimal;
}
ul {
	padding-left: 1.4em;
	list-style: square;
}
table {
	border-collapse: collapse;
	border-spacing: 0;
} 
/* end reset browser styles */

body {
    color: black;
    background: white;
}
`;
const innerScript = () => String.raw `
  const vscode = acquireVsCodeApi();

  window.alert = (message) => {
    vscode.postMessage({
      command: 'alert',
      text: JSON.stringify(message),
    })
  }
`;
hView.prototype.setCss = function (css) {
    this.css = css;
    // this.createHTML();
};
hView.prototype.setHtml = function (html) {
    this.html = html;
    // this.createHTML();
};
hView.prototype.setJs = function (js) {
    this.js = 'console.log("-------- START --------");\n' + js;
    // this.createHTML();
};
hView.prototype.createHTML = function () {
    const dom = new jsdom_1.JSDOM(this.html);
    const { document } = dom.window;
    // inner script
    let inner = document.createElement("script");
    inner.textContent = innerScript();
    document.head.prepend(inner);
    // css
    const style = document.createElement("style");
    style.textContent = resetStyle + this.css;
    document.head.prepend(style);
    // script
    const script = document.createElement("script");
    script.textContent = this.js;
    document.body.append(script);
    this.webview.html = dom.serialize();
};
//# sourceMappingURL=hView.js.map