let tg = window.Telegram.WebApp;
tg.expand();

async function sendForTranslate() {
    let text = document.getElementById("text").value;

    let response = await fetch(`/api/translate/?text=${encodeURIComponent(text)}&src=uz&dest=en`);
    let data = await response.json();

    document.getElementById("result").innerText = "Tarjima: " + data.translated;

    // Botga qaytarish
    tg.sendData(data.translated);
}
