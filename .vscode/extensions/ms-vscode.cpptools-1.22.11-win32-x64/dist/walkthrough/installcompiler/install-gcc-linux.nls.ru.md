<h1 data-loc-id="walkthrough.linux.install.compiler">Установка компилятора C++ в Linux</h1>
<p data-loc-id="walkthrough.linux.text1">Если вы занимаетесь разработкой на C++ для Linux, рекомендуем установить компилятор GCC. Это очень просто, достаточно выполнить следующие действия:</p>
<ol>
<li><p data-loc-id="walkthrough.linux.text2">Выполните следующую команду в окне терминала, чтобы обновить списки пакетов Ubuntu. Устаревший дистрибутив Linux в определенных случаях может помешать установке новых пакетов.</p>
<pre><code class="lang-bash">sudo apt update</code></pre>
</li>
<li><p data-loc-id="walkthrough.linux.text3">Установите инструменты компилятора GNU и отладчик GDB с помощью следующей команды:</p>
<pre><code class="lang-bash">sudo apt install build-essential gdb
</code></pre>
</li>
<li><p data-loc-id="walkthrough.linux.text4">Убедитесь, что система GCC установлена, выполнив следующую команду. На экране должно появиться сообщение об авторских правах и об используемой версии GCC.</p>
<pre><code class="lang-bash">gcc --version</code></pre>
</li>
</ol>
