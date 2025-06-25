# Python Type Hint

Provides type hint auto-completion for Python, with completion items for built-in types, classes and the typing module.


![](https://github.com/njqdev/vscode-python-typehint/raw/HEAD/images/demo.gif)


## Features

* Provides type hint completion items for built-in types, estimated types and the typing module.

* Estimates the correct type to provide as a completion item.

* Can search Python files in the workspace for type estimation purposes.

## Settings

| Name | Description | Default
|---|---|---|
| workspace.searchEnabled | _(boolean)_ If enabled, other files in the workspace are searched when estimating types for a parameter. Disabling this will increase performance, but may reduce estimation accuracy. | true
| workspace.searchLimit | _(number)_ The maximum number of files searched in a workspace search. Has no effect if workspace searching is disabled. | 10

## Known Issues

* If workspace searching is enabled, a VSCode event (onDidOpen) is triggered when a file is searched. This causes other extensions that are listening to the event to analyse the same files, which can add the problems of those files to the Problems window. The only way to prevent this, for now, is by disabling the workspace search setting.

* The difference between function and class constructor calls when detecting types is determined by the first letter being upper case (unless the class or function is defined in the currently edited document).

## Installation

The extension can found on the [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=njqdev.vscode-python-typehint).

-------------------------------------------------------------------------------------------


<p>
  <a href="https://img.shields.io/visual-studio-marketplace/i/njqdev.vscode-python-typehint">
    <img src="https://img.shields.io/visual-studio-marketplace/i/njqdev.vscode-python-typehint" alt="Installs"></img>
  </a>
  <a href="https://www.codefactor.io/repository/github/njqdev/vscode-python-typehint/badge">
    <img src="https://www.codefactor.io/repository/github/njqdev/vscode-python-typehint/badge" alt="CodeFactor"></img>
  </a>
</p>
