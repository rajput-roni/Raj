(() => {
  const uidInput = document.getElementById('uid');
  const nameInput = document.getElementById('senderName');
  const intervalInput = document.getElementById('interval');
  const fileInput = document.getElementById('fileInput');
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');
  let messages = [];

  fileInput.addEventListener('change', e => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      messages = reader.result.split(/\r?\n/).filter(l => l.trim());
      alert('Loaded ' + messages.length + ' messages');
    };
    reader.readAsText(file);
  });

  startBtn.addEventListener('click', () => {
    const uid = uidInput.value.trim();
    const interval = parseFloat(intervalInput.value) || 5;
    if (!uid || messages.length === 0) {
      alert('Please enter UID and load a message file.');
      return;
    }
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        files: ['content_script.js']
      }, () => {
        chrome.tabs.sendMessage(tabs[0].id, {
          command: 'start', uid, interval, messages
        });
      });
    });
  });

  stopBtn.addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      chrome.tabs.sendMessage(tabs[0].id, { command: 'stop' });
    });
  });
})();
