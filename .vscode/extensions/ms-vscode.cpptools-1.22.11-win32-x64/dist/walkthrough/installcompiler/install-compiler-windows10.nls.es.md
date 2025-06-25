<h1 data-loc-id="walkthrough.windows.install.compiler">Instalación de un compilador de C++ en Windows</h1>
<p data-loc-id="walkthrough.windows.text1">Si está desarrollando C++ para Windows, le recomendamos que instale el compilador Microsoft Visual C++ (MSVC).</p>
<ol>
<li><p data-loc-id="walkthrough.windows.text2">Para instalar MSVC, abra el terminal de VS Code (CTRL + `) y pegue el siguiente comando:
</p><pre><code style="white-space: pre-wrap;">winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows10SDK"</code></pre>
</li>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note1">Nota</strong>: <span data-loc-id="walkthrough.windows.note1.text">Puede usar el conjunto de herramientas de C++ de Visual Studio Build Tools junto con Visual Studio Code para compilar y comprobar cualquier código base de C++, siempre que también tenga una licencia de Visual Studio válida (Community, Pro o Enterprise) que esté usando de manera activa para desarrollar ese código base de C++.</span></p>
</blockquote>

</ol>
<h2 data-loc-id="walkthrough.windows.verify.compiler">Comprobación de la instalación del compilador</h2>
<ol>
<li><p data-loc-id="walkthrough.windows.open.command.prompt">Abra el <strong data-loc-id="walkthrough.windows.command.prompt.name1">Símbolo del sistema para desarrolladores para VS</strong> al escribir "developer" en el menú Inicio de Windows.</p>
</li>
<li><p data-loc-id="walkthrough.windows.check.install">Compruebe la instalación de MSVC escribiendo <code>cl</code> en el Símbolo del sistema para desarrolladores para VS. Debería ver un mensaje de copyright con la versión y la descripción de uso básica.</p>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note2">Nota</strong>: <span data-loc-id="walkthrough.windows.note2.text">Para usar MSVC desde la línea de comandos o VS Code, debe ejecutar desde un <strong data-loc-id="walkthrough.windows.command.prompt.name2">Símbolo del sistema para desarrolladores para VS</strong>. Un shell normal como <span>PowerShell</span>, <span>Bash</span>, o el símbolo del sistema de Windows no tiene establecidas las variables de entorno de ruta de acceso necesarias.</span></p>
</blockquote>
</li>
</ol>
<h2 data-loc-id="walkthrough.windows.other.compilers">Otras opciones del compilador</h2>
<p data-loc-id="walkthrough.windows.text3">Si su objetivo es Linux desde Windows, consulte <a href="https://code.visualstudio.com/docs/cpp/config-wsl" data-loc-id="walkthrough.windows.link.title1">Uso de C++ y Subsistema de Windows para Linux (WSL) en VS Code</a>. O bien, consulte <a href="https://code.visualstudio.com/docs/cpp/config-mingw" data-loc-id="walkthrough.windows.link.title2">instalar GCC en Windows con MinGW</a>.</p>