let intervalID;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'startSending') {
    // Start sending messages at the set interval
    intervalID = setInterval(() => {
      sendMessage(request.uid, request.message, request.senderName);
    }, request.delay * 1000); // Delay in seconds
  } else if (request.action === 'stopSending') {
    clearInterval(intervalID); // Stop sending messages
  }
});

function sendMessage(uid, message, senderName) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.executeScript(tabs[0].id, {
      code: `
        const messageInput = document.querySelector('div[aria-label="Type a message..."]');
        const sendButton = document.querySelector('div[aria-label="Press Enter to send"]');
        if (messageInput && sendButton) {
          messageInput.textContent = "${message}";
          sendButton.click();
        }
      `
    });
  });
}
