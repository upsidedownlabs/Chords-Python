<h1 data-loc-id="walkthrough.windows.install.compiler">Installa un compilatore C++ in Windows</h1>
<p data-loc-id="walkthrough.windows.text1">Se si sviluppa in C++ per Windows, è consigliabile installare il compilatore Microsoft Visual C++ (MSVC).</p>
<ol>
<li><p data-loc-id="walkthrough.windows.text2">Per installare MSVC, aprire il terminale VS Code (CTRL+ `) e incollare il comando seguente:
</p><pre><code style="white-space: pre-wrap;">winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK"</code></pre>
</li>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note1">Nota</strong>: <span data-loc-id="walkthrough.windows.note1.text">È possibile usare il set di strumenti C++ di Visual Studio Build Tools insieme a Visual Studio Code per compilare, creare e verificare qualsiasi codebase C++, purché sia disponibile una licenza di Visual Studio valida (Community, Pro o Enterprise) usata attivamente per sviluppare la codebase C++.</span></p>
</blockquote>

</ol>
<h2 data-loc-id="walkthrough.windows.verify.compiler">Verifica dell'installazione del compilatore</h2>
<ol>
<li><p data-loc-id="walkthrough.windows.open.command.prompt">Per aprire <strong data-loc-id="walkthrough.windows.command.prompt.name1">Prompt dei comandi per gli sviluppatori per Visual Studio</strong>, digitare 'developer' nel menu Start di Windows.</p>
</li>
<li><p data-loc-id="walkthrough.windows.check.install">Verificare l'installazione di MSVC digitando <code>cl</code> al Prompt dei comandi per gli sviluppatori per Visual Studio. Verranno visualizzati un messaggio di copyright, la versione e la descrizione sulla sintassi di base.</p>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note2">Nota</strong>: <span data-loc-id="walkthrough.windows.note2.text">Per usare MSVC dalla riga di comando o da VS Code, è necessario eseguire l'applicazione da <strong data-loc-id="walkthrough.windows.command.prompt.name2">Prompt dei comandi per gli sviluppatori per Visual Studio</strong>. Con una shell normale, ad esempio <span>PowerShell</span>, <span>Bash</span> o il prompt dei comandi di Windows le variabili di ambiente del percorso necessarie non sono impostate.</span></p>
</blockquote>
</li>
</ol>
<h2 data-loc-id="walkthrough.windows.other.compilers">Altre opzioni del compilatore</h2>
<p data-loc-id="walkthrough.windows.text3">Se la destinazione è Linux da Windows, vedere <a href="https://code.visualstudio.com/docs/cpp/config-wsl" data-loc-id="walkthrough.windows.link.title1">Uso di C++ e del sottosistema Windows per Linux (WSL) in VS Code</a>. In alternativa, è possibile <a href="https://code.visualstudio.com/docs/cpp/config-mingw" data-loc-id="walkthrough.windows.link.title2">Installa GCC in Windows con MinGW</a>.</p>