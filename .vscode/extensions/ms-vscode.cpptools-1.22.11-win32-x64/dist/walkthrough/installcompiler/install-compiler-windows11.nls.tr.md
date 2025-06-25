<h1 data-loc-id="walkthrough.windows.install.compiler">Windows'a C++ derleyicisi yükleme</h1>
<p data-loc-id="walkthrough.windows.text1">Windows için C++ geliştirme yapıyorsanız Microsoft Visual C++ (MSVC) derleyicisini yüklemenizi öneririz.</p>
<ol>
<li><p data-loc-id="walkthrough.windows.text2">MSVC'yi yüklemek için VS Code terminalini (CTRL + `) açın ve aşağıdaki komutu yapıştırın:
</p><pre><code style="white-space: pre-wrap;">winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22000"</code></pre>
</li>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note1">Not</strong>: <span data-loc-id="walkthrough.windows.note1.text">Herhangi bir C++ kod temelini derlemek, oluşturmak ve doğrulamak için Visual Studio Code ile birlikte Visual Studio Derleme Araçları’nda bulunan C++ araç takımını kullanabilirsiniz. Bunun yanı sıra, bu C++ kod temelini geliştirmek için etkin olarak kullandığınız geçerli bir Visual Studio lisansına (Community, Pro veya Enterprise) sahip olursunuz.</span></p>
</blockquote>

</ol>
<h2 data-loc-id="walkthrough.windows.verify.compiler">Derleyici yüklemesi doğrulanıyor</h2>
<ol>
<li><p data-loc-id="walkthrough.windows.open.command.prompt">Windows Başlat menüsüne 'geliştirici' yazarak <strong data-loc-id="walkthrough.windows.command.prompt.name1">VS için Geliştirici Komut İstemi</strong> açın.</p>
</li>
<li><p data-loc-id="walkthrough.windows.check.install">VS için Geliştirici Komut İstemi’ne <code>cl</code> yazarak MSVC yüklemenizi denetleyin. Sürüm ve temel kullanım açıklamasını içeren bir telif hakkı iletisi göreceksiniz.</p>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note2">Not</strong>: <span data-loc-id="walkthrough.windows.note2.text">Komut satırından veya VS Code’dan MSVC’yi kullanmak için şuradan çalıştırmanız gerek: <strong data-loc-id="walkthrough.windows.command.prompt.name2">VS için Geliştirici Komut İstemi</strong>. <span>PowerShell</span>, <span>Bash</span> veya Windows komut istemi gibi sıradan bir kabuk gerekli yol ortam değişkenleri kümesi içermez.</span></p>
</blockquote>
</li>
</ol>
<h2 data-loc-id="walkthrough.windows.other.compilers">Diğer derleme seçenekleri</h2>
<p data-loc-id="walkthrough.windows.text3">Windows'tan Linux'u hedefliyorsanız <a href="https://code.visualstudio.com/docs/cpp/config-wsl" data-loc-id="walkthrough.windows.link.title1">VS Code'da Linux için C++’yı ve Windows Alt Sistemi’ni (WSL) kullanma</a>‘a bakın. Veya, <a href="https://code.visualstudio.com/docs/cpp/config-mingw" data-loc-id="walkthrough.windows.link.title2">MinGW ile Windows’a GCC'yi yükleme</a>.</p>