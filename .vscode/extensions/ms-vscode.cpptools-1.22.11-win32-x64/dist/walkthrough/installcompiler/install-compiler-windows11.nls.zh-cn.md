<h1 data-loc-id="walkthrough.windows.install.compiler">在 Windows 上安装 C++ 编译器</h1>
<p data-loc-id="walkthrough.windows.text1">如果要对 Windows 进行 C++ 开发，建议安装 Microsoft Visual C++ (MSVC)编译器。</p>
<ol>
<li><p data-loc-id="walkthrough.windows.text2">若要安装 MSVC，请打开 VS Code 终端(CTRL + `)并在以下命令中粘贴:
</p><pre><code style="white-space: pre-wrap;">winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22000"</code></pre>
</li>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note1">注意</strong>: <span data-loc-id="walkthrough.windows.note1.text">可以使用 Visual Studio 生成工具中的 C++ 工具集以及 Visual Studio Code 以编译、生成并验证任何 C++ 代码库，前提是同时具有有效的 Visual Studio 许可证(社区版、专业版或企业版)，且正积极将其用于开发该 C++ 代码库。</span></p>
</blockquote>

</ol>
<h2 data-loc-id="walkthrough.windows.verify.compiler">正在验证编译器安装</h2>
<ol>
<li><p data-loc-id="walkthrough.windows.open.command.prompt">在 Windows“开始”菜单中键入‘开发人员’以打开 <strong data-loc-id="walkthrough.windows.command.prompt.name1">VS 的开发人员命令提示</strong>。</p>
</li>
<li><p data-loc-id="walkthrough.windows.check.install">在 VS 的开发人员命令提示中键入 <code>cl</code> 以检查 MSVC 安装。你应该会看到包含版本和基本使用情况说明的版权消息。</p>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note2">注意</strong>: <span data-loc-id="walkthrough.windows.note2.text">要从命令行或 VS Code 使用 MSVC，必须从 <strong data-loc-id="walkthrough.windows.command.prompt.name2">VS 的开发人员命令提示</strong> 运行。普通 shell (例如 <span>PowerShell</span>、 <span>Bash</span>)或 Windows 命令提示符未设置必要的路径环境变量。</span></p>
</blockquote>
</li>
</ol>
<h2 data-loc-id="walkthrough.windows.other.compilers">其他编译器选项</h2>
<p data-loc-id="walkthrough.windows.text3">如果面向的是 Windows 中的 Linux，请查看<a href="https://code.visualstudio.com/docs/cpp/config-wsl" data-loc-id="walkthrough.windows.link.title1">在 VS Code 中使用 C++ 和 适用于 Linux 的 Windows 子系统(WSL)</a>。或者，可<a href="https://code.visualstudio.com/docs/cpp/config-mingw" data-loc-id="walkthrough.windows.link.title2">在带 MinGW 的 Windows 上安装 GCC</a>。</p>