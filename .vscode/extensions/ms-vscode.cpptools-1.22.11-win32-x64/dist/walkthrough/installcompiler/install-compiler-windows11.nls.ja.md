<h1 data-loc-id="walkthrough.windows.install.compiler">Windows で C++ コンパイラをインストールする</h1>
<p data-loc-id="walkthrough.windows.text1">Windows 向けの C++ 開発を行っている場合は、Microsoft Visual C++ (MSVC) コンパイラをインストールすることをお勧めします。</p>
<ol>
<li><p data-loc-id="walkthrough.windows.text2">MSVC をインストールするには、VS Code ターミナル (CTRL + `) を開き、次のコマンドで貼り付けます:
</p><pre><code style="white-space: pre-wrap;">winget install Microsoft.VisualStudio.2022.BuildTools --force --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.22000"</code></pre>
</li>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note1">メモ</strong>: <span data-loc-id="walkthrough.windows.note1.text">有効な Visual Studio ライセンス (Community、Pro、Enterprise のいずれか) があり、その C++ コードベースの開発に積極的に使用している場合は、Visual Studio Build Tools の C++ ツールセットを Visual Studio Code と合わせて使用して、C++ コードベースのコンパイル、ビルド、および検証を行うことができます。</span></p>
</blockquote>

</ol>
<h2 data-loc-id="walkthrough.windows.verify.compiler">コンパイラのインストールの確認中</h2>
<ol>
<li><p data-loc-id="walkthrough.windows.open.command.prompt">Windows スタート メニューに '開発者' と入力して、<strong data-loc-id="walkthrough.windows.command.prompt.name1">VS 向け開発者コマンド プロンプト</strong> を開きます。</p>
</li>
<li><p data-loc-id="walkthrough.windows.check.install">VS の開発者コマンド プロンプトに <code>cl</code> を入力して、MSVC インストールを確認します。バージョンと基本的な使用法の説明とともに、著作権に関するメッセージが表示されます。</p>
<blockquote>
<p><strong data-loc-id="walkthrough.windows.note2">メモ</strong>: <span data-loc-id="walkthrough.windows.note2.text">コマンド ラインまたは VS Code で MSVC を使用するには、<strong data-loc-id="walkthrough.windows.command.prompt.name2">VS 向け開発者コマンド プロンプト</strong> で実行する必要があります。<span>PowerShell</span>、<span>Bash</span>、Windows コマンド プロンプトなどの通常のシェルには、必要なパス環境変数が設定されていません。</span></p>
</blockquote>
</li>
</ol>
<h2 data-loc-id="walkthrough.windows.other.compilers">その他のコンパイラ オプション</h2>
<p data-loc-id="walkthrough.windows.text3">Windows から Linux に貼り付ける場合は、<a href="https://code.visualstudio.com/docs/cpp/config-wsl" data-loc-id="walkthrough.windows.link.title1">VS Code で C++ と Windows Subsystem for Linux (WSL) を使用する</a> をチェックしてください。あるいは、<a href="https://code.visualstudio.com/docs/cpp/config-mingw" data-loc-id="walkthrough.windows.link.title2">MinGW を使用して Windows で GCC をインストールする</a> も使用できます。</p>