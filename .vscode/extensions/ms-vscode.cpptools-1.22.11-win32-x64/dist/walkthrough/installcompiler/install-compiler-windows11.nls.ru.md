<h1 data-loc-id="walkthrough.windows.install.compiler">Установка компилятора C++ в Windows</h1>
<p data-loc-id="walkthrough.windows.text1">Если вы занимаетесь разработкой на C++ для Windows, рекомендуется установить компилятор Microsoft Visual C++ (MSVC).</p>
<ol>
<li><p data-loc-id="walkthrough.windows.text2">Чтобы установить MSVC, откройте терминал VS Code (CTRL + `) и вставьте следующую команду:
</p><pre><code style="white-space: pre-wrap;">winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22000"</code></pre>
</li>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note1">Примечание</strong>: <span data-loc-id="walkthrough.windows.note1.text">Вы можете использовать набор инструментов C++ из пакета Visual Studio Build Tools вместе с Visual Studio Code для компиляции, сборки и проверки любой базы кода C++, если у вас есть действующая лицензия Visual Studio (Community, Pro или Enterprise), которой вы активно пользуетесь для разработки этой базы кода C++.</span></p>
</blockquote>

</ol>
<h2 data-loc-id="walkthrough.windows.verify.compiler">Проверка установки компилятора</h2>
<ol>
<li><p data-loc-id="walkthrough.windows.open.command.prompt">Откройте <strong data-loc-id="walkthrough.windows.command.prompt.name1">Командная строка разработчика для VS</strong>, введя команду "developer" в меню "Пуск" в Windows.</p>
</li>
<li><p data-loc-id="walkthrough.windows.check.install">Проверьте установку MSVC, введя <code>cl</code> в командной строке разработчика для VS. Должно появиться сообщение об авторских правах с номером версии и кратким описанием использования.</p>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note2">Примечание</strong>: <span data-loc-id="walkthrough.windows.note2.text">Чтобы использовать MSVC из командной строки или VS Code, требуется запуск из <strong data-loc-id="walkthrough.windows.command.prompt.name2">Командная строка разработчика для VS</strong>. В обычной среде, например в <span>PowerShell</span>, в <span>Bash</span> или в командной строке Windows, не заданы необходимые переменные среды "path".</span></p>
</blockquote>
</li>
</ol>
<h2 data-loc-id="walkthrough.windows.other.compilers">Другие параметры компилятора</h2>
<p data-loc-id="walkthrough.windows.text3">Если вы нацеливаетесь на Linux из Windows, ознакомьтесь с <a href="https://code.visualstudio.com/docs/cpp/config-wsl" data-loc-id="walkthrough.windows.link.title1">Использование C++ и подсистемы Windows для Linux в VS Code</a>. Также вы можете <a href="https://code.visualstudio.com/docs/cpp/config-mingw" data-loc-id="walkthrough.windows.link.title2">Установка GCC в Windows с помощью MinGW</a>.</p>