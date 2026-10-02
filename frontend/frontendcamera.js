/* Camera lifecycle */
window.AidCamera = (function () {
  const { $, toast } = window.AidUtils;
  let stream = null;

  async function start() {
    const video = $('#camVideo');
    const empty = $('#camEmpty');
    const overlay = $('#camOverlay');

    // Early HTTPS check (mobile browsers require secure context for camera)
    if (location.protocol !== 'https:' && !location.hostname.match(/^(localhost|127\.0\.0\.1)$/)) {
      toast('Camera may be blocked: open over HTTPS or use localhost, or upload an image.', 'warn', 6000);
    }

    // Ensure video will play inline on mobile (iOS)
    if (video) {
      try { video.setAttribute('playsinline', ''); video.playsInline = true; video.muted = true; } catch (e) {}
    }

    const tryConstraints = [
      { video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false },
      { video: { facingMode: { exact: 'environment' }, width: { ideal: 1280 } }, audio: false },
      { video: { width: { ideal: 1280 } }, audio: false },
      { video: true, audio: false }
    ];

    // Try constraints progressively
    for (const c of tryConstraints) {
      try {
        stream = await navigator.mediaDevices.getUserMedia(c);
        break;
      } catch (err) {
        console.warn('getUserMedia failed for constraints', c, err && err.name);
        // Continue to next constraint
      }
    }

    // If still no stream, try enumerateDevices to pick a back camera deviceId (best-effort)
    if (!stream && navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoInputs = devices.filter(d => d.kind === 'videoinput');
        let chosen = null;
        // Prefer device labels that suggest back/rear camera
        for (const d of videoInputs) {
          const label = (d.label || '').toLowerCase();
          if (label.includes('back') || label.includes('rear') || label.includes('environment')) { chosen = d; break; }
        }
        if (!chosen && videoInputs.length) chosen = videoInputs[videoInputs.length - 1];
        if (chosen) {
          try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: chosen.deviceId }, width: { ideal: 1280 } }, audio: false });
          } catch (err) {
            console.warn('getUserMedia by deviceId failed', err);
          }
        }
      } catch (err) {
        console.warn('enumerateDevices failed', err);
      }
    }

    if (!stream) {
      // Final graceful failure
      console.warn('Camera start failed: no stream available');
      toast('Camera unavailable — try uploading an image or use the demo', 'error', 5000);
      return false;
    }

    // Bind stream to video element
    try {
      video.srcObject = stream;
      video.autoplay = true;
      try { await video.play(); } catch (e) { /* autoplay may be blocked until user interacts */ }
      empty.hidden = true;
      overlay.hidden = false;
      $('#btnCapture').disabled = false;
      $('#camStatus').textContent = 'Camera active — frame the affected area';
      toast('Camera started', 'success');
      return true;
    } catch (err) {
      console.warn('Error attaching stream to video', err);
      toast('Camera started but could not display preview. Capture may still work.', 'warn');
      return true;
    }
  }

  function stop() {
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
    const video = $('#camVideo');
    if (video) video.srcObject = null;
    $('#camEmpty').hidden = false;
    $('#camOverlay').hidden = true;
    $('#btnCapture').disabled = true;
  }

  function captureFrame() {
    const video = $('#camVideo');
    const canvas = $('#camCanvas');
    if (!video || !video.videoWidth) return null;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    return canvas.toDataURL('image/jpeg', 0.85);
  }

  return { start, stop, captureFrame, isActive: () => !!stream };
})();
