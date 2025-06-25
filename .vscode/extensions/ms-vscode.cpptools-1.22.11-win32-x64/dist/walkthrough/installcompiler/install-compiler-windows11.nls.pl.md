<h1 data-loc-id="walkthrough.windows.install.compiler">Zainstaluj kompilator języka C++ w systemie Windows</h1>
<p data-loc-id="walkthrough.windows.text1">W przypadku programowania w języku C++ dla systemu Windows zalecamy zainstalowanie kompilatora Microsoft Visual C++ (MSVC).</p>
<ol>
<li><p data-loc-id="walkthrough.windows.text2">Aby zainstalować program MSVC, otwórz terminal VS Code (CTRL + `) i wklej następujące polecenie:
</p><pre><code style="white-space: pre-wrap;">winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22000"</code></pre>
</li>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note1">Notatka</strong>: <span data-loc-id="walkthrough.windows.note1.text">Zestawu narzędzi języka C++ z narzędzi Visual Studio Build Tools wraz z programem Visual Studio Code można używać do kompilowania, tworzenia i weryfikowania dowolnej bazy kodu języka C++, o ile masz również ważną licencję programu Visual Studio (Community, Pro lub Enterprise), której aktywnie używasz do opracowywania tej bazy kodu języka C++.</span></p>
</blockquote>

</ol>
<h2 data-loc-id="walkthrough.windows.verify.compiler">Weryfikowanie instalacji kompilatora</h2>
<ol>
<li><p data-loc-id="walkthrough.windows.open.command.prompt">Otwórz pozycję <strong data-loc-id="walkthrough.windows.command.prompt.name1">Wiersz polecenia dla deweloperów dla programu VS</strong>, wpisując „deweloper” w menu Start systemu Windows.</p>
</li>
<li><p data-loc-id="walkthrough.windows.check.install">Sprawdź instalację programu MSVC, wpisując <code>cl</code> w wierszu polecenia dewelopera dla programu VS. Powinien zostać wyświetlony komunikat o prawach autorskich z wersją i opisem użycia podstawowego.</p>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note2">Notatka</strong>: <span data-loc-id="walkthrough.windows.note2.text">Aby użyć programu MSVC z wiersza polecenia lub programu VS Code, należy uruchomić z <strong data-loc-id="walkthrough.windows.command.prompt.name2">Wiersz polecenia dla deweloperów dla programu VS</strong>. Zwykła powłoka, taka jak <span>PowerShell</span>, <span>Bash</span> lub wiersz polecenia systemu Windows, nie ma ustawionych wymaganych zmiennych środowiskowych ścieżki.</span></p>
</blockquote>
</li>
</ol>
<h2 data-loc-id="walkthrough.windows.other.compilers">Inne opcje kompilatora</h2>
<p data-loc-id="walkthrough.windows.text3">Jeśli zamierzasz korzystać z systemu Linux z poziomu systemu Windows, sprawdź <a href="https://code.visualstudio.com/docs/cpp/config-wsl" data-loc-id="walkthrough.windows.link.title1">Używanie języka C++ i podsystemu Windows dla systemu Linux (WSL) w programie VS Code</a>. Możesz też <a href="https://code.visualstudio.com/docs/cpp/config-mingw" data-loc-id="walkthrough.windows.link.title2">Zainstaluj zestaw kompilatorów GCC w systemie Windows z funkcją MinGW</a>.</p>