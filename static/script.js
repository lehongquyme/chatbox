document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const promptInput = document.getElementById("prompt");
  const messages = document.getElementById("messages");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const prompt = promptInput.value;
    messages.innerHTML += `<div class="message user">🧑: ${prompt}</div>`;
    promptInput.value = "";

    const formData = new FormData();
    formData.append("prompt", prompt);

    const res = await fetch("/chat", { method: "POST", body: formData });
    const data = await res.json();
    messages.innerHTML += `<div class="message bot">🤖: ${data.response}</div>`;
  });
});
