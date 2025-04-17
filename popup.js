document.getElementById("save").addEventListener("click", () => {
  const message = document.getElementById("message").value;
  chrome.storage.local.set({ autoMessage: message }, () => {
    alert("Message saved!");
  });
});
