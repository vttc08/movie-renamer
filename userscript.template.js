// ==UserScript==
// @name         OCR Auto Fill
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  Preprocess verifyimg and send to Cloudflare Worker OCR, auto-fill input
// @match        https://$SITE_ONE/*
// @match        https://$SITE_TWO/*
// @grant        none
// ==/UserScript==

(function () {
  "use strict";

  function preprocessImage(imgEl) {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    canvas.width = imgEl.naturalWidth;
    canvas.height = imgEl.naturalHeight;
    ctx.drawImage(imgEl, 0, 0);

    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imgData.data;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i],
        g = data[i + 1],
        b = data[i + 2];
      const gray = 0.299 * r + 0.587 * g + 0.114 * b;
      const val = gray < 128 ? 0 : 255;
      data[i] = data[i + 1] = data[i + 2] = val;
    }

    ctx.putImageData(imgData, 0, 0);
    return canvas.toDataURL("image/png");
  }

  async function runOCR() {
    const imgEl = document.querySelector(".$CSS_SELECTOR");
    if (!imgEl) return; // ✅ exit quietly if not found

    try {
      console.log("found");
      const processed = preprocessImage(imgEl);
      const res = await fetch("https://$WORKERS_URL", {
        method: "POST",
        headers: { "Content-Type": "application/json",
                 "x-api-key":"$WORKERS_API_KEY"},
        body: JSON.stringify({ image: processed })
      });
      const data = await res.json();
      const raw = (data.response || data.digits || "").toString();
      let value = raw.replace(/\D+/g, "");
      if (value.length > 5) value = value.slice(0, 5);
      followThrough(value);
    } catch (err) {
      console.error("OCR error:", err);
    }
  }

  function followThrough(value) {
    const intext = document.getElementById("intext");
    if (intext) {
      intext.value = value;
      if (typeof $JS_FUNCTION === "function") {
        $JS_FUNCTION();
      }
    }
  }

  // Run once when page finishes loading
  runOCR();
})();


