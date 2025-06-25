<h1 data-loc-id="walkthrough.windows.install.compiler">C++-Compiler unter Windows installieren</h1>
<p data-loc-id="walkthrough.windows.text1">Wenn Sie mithilfe von C++ unter Windows entwickeln, empfehlen wir die Installation des Microsoft Visual C++-Compiler (MSVC).</p>
<ol>
<li><p data-loc-id="walkthrough.windows.text2">Öffnen Sie zum Installieren von MSVC das VS Code-Terminal (STRG + `), und fügen Sie den folgenden Befehl ein:
</p><pre><code style="white-space: pre-wrap;">winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22000"</code></pre>
</li>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note1">Hinweis</strong>: <span data-loc-id="walkthrough.windows.note1.text">Sie können das C++-Toolset aus Visual Studio Build Tools zusammen mit Visual Studio Code zum Kompilieren, Erstellen und Überprüfen von C++-Codebasis verwenden, sofern Sie auch über eine gültige Visual Studio-Lizenz (Community, Pro oder Enterprise) verfügen, die Sie aktiv zum Entwickeln dieser C++-Codebasis verwenden.</span></p>
</blockquote>

</ol>
<h2 data-loc-id="walkthrough.windows.verify.compiler">Überprüfen der Compilerinstallation</h2>
<ol>
<li><p data-loc-id="walkthrough.windows.open.command.prompt">Öffnen Sie die <strong data-loc-id="walkthrough.windows.command.prompt.name1">Developer-Eingabeaufforderung für VS</strong>, indem Sie im Windows-Startmenü "Developer" eingeben.</p>
</li>
<li><p data-loc-id="walkthrough.windows.check.install">Überprüfen Sie die MSVC-Installation, indem Sie <code>cl</code> in die Developer-Eingabeaufforderung für VS eingeben. Es sollten ein Copyrighthinweis mit der Version und der grundlegenden Nutzungsbeschreibung angezeigt werden.</p>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note2">Hinweis</strong>: <span data-loc-id="walkthrough.windows.note2.text">Um MSVC mithilfe der Befehlszeile oder mit VS Code zu verwenden, müssen Sie von einem <strong data-loc-id="walkthrough.windows.command.prompt.name2">Developer-Eingabeaufforderung für VS</strong> aus ausführen. Für eine normale Shell wie <span>PowerShell</span>, <span>Bash</span> oder die Windows-Eingabeaufforderung sind die erforderlichen PATH-Umgebungsvariablen nicht festgelegt.</span></p>
</blockquote>
</li>
</ol>
<h2 data-loc-id="walkthrough.windows.other.compilers">Andere Compileroptionen</h2>
<p data-loc-id="walkthrough.windows.text3">Wenn Sie Linux aus Windows verwenden, lesen Sie <a href="https://code.visualstudio.com/docs/cpp/config-wsl" data-loc-id="walkthrough.windows.link.title1">Verwenden von C++ und Windows-Subsystem für Linux (WSL) in VS Code</a>. Oder Sie können <a href="https://code.visualstudio.com/docs/cpp/config-mingw" data-loc-id="walkthrough.windows.link.title2">Installieren Sie GCC unter Windows mit MinGW.</a>.</p>