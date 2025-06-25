<h1 data-loc-id="walkthrough.windows.install.compiler">Installer un compilateur C++ sur Windows</h1>
<p data-loc-id="walkthrough.windows.text1">Si vous effectuez un développement C++ pour Windows, nous vous recommandons d’installer le compilateur Microsoft Visual C++ (MSVC).</p>
<ol>
<li><p data-loc-id="walkthrough.windows.text2">Pour installer MSVC, ouvrez le terminal VS Code (CTRL + `) et collez-le dans la commande suivante :
</p><pre><code style="white-space: pre-wrap;">winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22000"</code></pre>
</li>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note1">Remarque</strong>: <span data-loc-id="walkthrough.windows.note1.text">Vous pouvez utiliser l’ensemble d’outils C++ à partir de Visual Studio Build Tools avec Visual Studio Code pour compiler, générer et vérifier n’importe quelle base de code C++, tant que vous disposez également d’une licence Visual Studio valide (Community, Pro ou Enterprise) que vous utilisez activement pour développer cette base de code C++.</span></p>
</blockquote>

</ol>
<h2 data-loc-id="walkthrough.windows.verify.compiler">Vérification de l’installation du compilateur</h2>
<ol>
<li><p data-loc-id="walkthrough.windows.open.command.prompt">Ouvrez le <strong data-loc-id="walkthrough.windows.command.prompt.name1">Invite de commandes développeur pour VS</strong> en tapant «&nbsp;développeur&nbsp;» dans le menu Démarrer de Windows.</p>
</li>
<li><p data-loc-id="walkthrough.windows.check.install">Vérifiez l’installation de votre MSVC en tapant <code>cl</code> dans la Invite de commandes développeur pour VS. Vous devez voir un message de Copyright avec la version et la description de l’utilisation de base.</p>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note2">Remarque</strong>: <span data-loc-id="walkthrough.windows.note2.text">Pour utiliser MSVC à partir de la ligne de commande ou VS Code, vous devez exécuter à partir d’un <strong data-loc-id="walkthrough.windows.command.prompt.name2">Invite de commandes développeur pour VS</strong>. Un interpréteur de commandes ordinaire, tel que <span>PowerShell</span>, <span>Bash</span> ou l’invite de commandes Windows, n’a pas les variables d’environnement de chemin d’accès nécessaires définies.</span></p>
</blockquote>
</li>
</ol>
<h2 data-loc-id="walkthrough.windows.other.compilers">Autres options du compilateur</h2>
<p data-loc-id="walkthrough.windows.text3">Si vous ciblez Linux à partir de Windows, consultez <a href="https://code.visualstudio.com/docs/cpp/config-wsl" data-loc-id="walkthrough.windows.link.title1">Utilisation de C++ et du Sous-système Windows pour Linux (WSL) dans VS Code</a>. Vous pouvez également <a href="https://code.visualstudio.com/docs/cpp/config-mingw" data-loc-id="walkthrough.windows.link.title2">installer GCC sur Windows avec MinGW</a>.</p>