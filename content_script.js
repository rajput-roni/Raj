let sendIntervalId = null;
let msgQueue = [];

chrome.runtime.onMessage.addListener((req) => {
  if (req.command === 'start') {
    msgQueue = [...req.messages];
    navigateAndStart(req.uid, req.interval);
  } else if (req.command === 'stop') {
    clearInterval(sendIntervalId);
  }
});

function navigateAndStart(uid, interval) {
  const url = 'https://www.facebook.com/messages/t/' + uid;
  if (!window.location.href.startsWith(url)) {
    window.location.href = url;
    window.onload = () => setTimeout(() => startSending(interval), 3000);
  } else {
    startSending(interval);
  }
}

function startSending(interval) {
  clearInterval(sendIntervalId);
  sendIntervalId = setInterval(() => {
    if (msgQueue.length === 0) return clearInterval(sendIntervalId);
    const text = msgQueue.shift();
    const inputDiv = document.querySelector('div[contenteditable="true"]');
    if (!inputDiv) return;
    inputDiv.focus();
    document.execCommand('insertText', false, text);
    inputDiv.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, cancelable: true, key: 'Enter' }));
  }, interval * 1000);
}
