function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    const mediaRecorder = new MediaRecorder(stream);
    const chunks = [];

    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: "audio/wav" });
      const formData = new FormData();
      formData.append("file", blob, "voice.wav");

      document.getElementById("subtitles").innerText = "Thinking...";

      fetch("/upload_audio", {
        method: "POST",
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById("subtitles").innerText =
          `You: ${data.user}\n${data.reply}`;
      });
    };

    mediaRecorder.start();

    setTimeout(() => mediaRecorder.stop(), 3000);  // Record 3 sec
  });
}

function saveCharacter() {
  const name = document.getElementById("user-name").value;
  const personality = document.getElementById("personality").value;

  fetch("/update_character", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, personality })
  })
  .then(res => res.json())
  .then(data => {
    alert("Saved: " + data.intro_text);
  });
}
