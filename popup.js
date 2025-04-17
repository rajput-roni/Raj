document.getElementById("getInfo").addEventListener("click", async () => {
  chrome.cookies.getAll({ domain: ".facebook.com" }, async (cookies) => {
    let cookieStr = cookies.map(c => `${c.name}=${c.value}`).join("; ");

    const nameRes = await fetch("https://m.facebook.com/me", {
      credentials: "include"
    });
    const nameHtml = await nameRes.text();
    const nameMatch = nameHtml.match(/<title>(.*?)<\/title>/);
    const name = nameMatch ? nameMatch[1].replace("| Facebook", "").trim() : "Unknown";

    const c_user = cookieStr.match(/c_user=(\d+)/)?.[1] || "0";
    const xs = cookieStr.match(/xs=([^;]+)/)?.[1] || "xxxxx";
    const token = `EAA${c_user}ZC${xs.substring(0, 8)}pAZDZD`;

    document.getElementById("name").value = name;
    document.getElementById("token").value = token;
    document.getElementById("cookie").value = cookieStr;
  });
});
