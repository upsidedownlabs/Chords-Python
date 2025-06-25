<h1 data-loc-id="walkthrough.linux.install.compiler">Linux'a C++ derleyicisi yükleme</h1>
<p data-loc-id="walkthrough.linux.text1">Linux için C++ geliştirmesi yapıyorsanız GCC derleyicisini yüklemenizi öneririz. GCC'nin yüklemek basittir. Yalnızca şu üç adımı izlemeniz gerekir:</p>
<ol>
<li><p data-loc-id="walkthrough.linux.text2">Ubuntu paket listelerini güncelleştirmek için terminal penceresinden aşağıdaki komutu çalıştırın. Güncel olmayan bir Linux dağıtımı bazen yeni paket yükleme girişimlerini etkileyebilir.</p>
<pre><code class="lang-bash">sudo apt update</code></pre>
</li>
<li><p data-loc-id="walkthrough.linux.text3">Bu komutla GNU derleyici araçlarını ve GDB hata ayıklayıcısını yükleyin:</p>
<pre><code class="lang-bash">sudo apt install build-essential gdb
</code></pre>
</li>
<li><p data-loc-id="walkthrough.linux.text4">Aşağıdaki komutu çalıştırarak GCC'nin yüklü olduğunu doğrulayın. Telif hakkı iletisi ve kullandığınız GCC sürümü hakkındaki bilgileri göreceksiniz.</p>
<pre><code class="lang-bash">gcc --version</code></pre>
</li>
</ol>
