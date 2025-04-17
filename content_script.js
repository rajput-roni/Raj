chrome.storage.local.get(["autoMessage"], (result) => {
  if (result.autoMessage) {
    const interval = setInterval(() => {
      const activeElement = document.activeElement;
      if (activeElement && activeElement.tagName === "INPUT") {
        activeElement.value = result.autoMessage;
        activeElement.dispatchEvent(new Event("input", { bubbles: true }));
        clearInterval(interval);
      }
    }, 1000);
  }
});
