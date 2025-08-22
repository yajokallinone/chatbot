(function(){
  const chatEl = document.getElementById('chat');
  const inputEl = document.getElementById('input');
  const sendBtn = document.getElementById('send');
  const spinner = document.getElementById('spinner');
  const sendLabel = document.getElementById('sendLabel');

  function addMsg(role, content){
    const wrap = document.createElement('div');
    wrap.className = 'd-flex mb-2 ' + (role === 'user' ? 'justify-content-end' : 'justify-content-start');

    const bubble = document.createElement('div');
    bubble.className = 'msg ' + (role === 'user' ? 'msg-user' : 'msg-bot');
    bubble.textContent = content;

    wrap.appendChild(bubble);
    chatEl.appendChild(wrap);
    chatEl.scrollTop = chatEl.scrollHeight;
  }

  function setLoading(v){
    sendBtn.disabled = v;
    if(spinner){ spinner.classList.toggle('d-none', !v); }
    if(sendLabel){ sendLabel.textContent = v ? 'กำลังส่ง...' : 'ส่ง'; }
  }

  async function send(){
    const text = (inputEl.value || '').trim();
    if(!text) return;
    addMsg('user', text);
    inputEl.value = '';
    inputEl.focus();

    setLoading(true);
    try {
      const res = await fetch(window.CHAT_CONFIG.apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      if(!res.ok){ throw new Error(data.error || 'Request failed'); }
      addMsg('bot', data.reply || '(no reply)');
    } catch (err){
      addMsg('bot', '❌ Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  }

  sendBtn.addEventListener('click', send);
  inputEl.addEventListener('keydown', (e)=>{ if(e.key==='Enter') send(); });
})();
