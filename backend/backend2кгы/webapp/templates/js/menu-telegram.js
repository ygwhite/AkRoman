// -- Telegram part --
const tg = window.Telegram.WebApp;

tg.MainButton.textColor = "#FFFFFF";
tg.MainButton.color = "#2cab37";
tg.MainButton.setText("Подтвердить выбор")

tg.onEvent("mainButtonClicked", function(event) {
    const data = [];
    
    state.data.forEach(item => {
        data.push(JSON.parse(item));
    });
    
    const json = JSON.stringify(data);
    tg.sendData(json);
});

tg.ready()
tg.expand()