//todo
const wss_url = "{{ wss_url }}";
let websocket = null;

// -- Handlers --
function ws_open_handler(event) {
    console.log("[open] Соединение установлено");
    console.log("Отправляем данные на сервер");
    
    const ws = event.currentTarget;
    const data = {
        a: "hello",
        f: "webapp",
        t: hello,
    };
    
    ws.send(JSON.stringify(data));
};

function ws_message_handler(event) {
    const ws = event.currentTarget;
    const data = JSON.parse(event.data);

    if (data.a === "hello" && data.s === "ok") {

        if (state.symbol && state.timeframe) {
            const message = JSON.stringify({ 
                a: "add_sub:all", 
                p: [state.symbol, state.timeframe], 
                t: hello,
            });
            ws.send(message);
        }

        // Other symbols + current timeframe
        const data_items = get_data_items();

        data_items.forEach(([symbol, tf]) => {
            const message = JSON.stringify({ 
                a: "add_sub2:summ", 
                p: [symbol, tf], 
                t: hello,
            });
            ws.send(message);
        });        
    }
    if (data.a === "add_sub:all" && data.s === "ok") {
        console.log(`[ws][info] Подписка "add_sub:all" добавлена`);
    }
    if (data.a === "add_sub2:summ" && data.s === "ok") {
        console.log(`[ws][info] Подписка "add_sub2:summ" добавлена`);
    }
    if (data.a === "clear_subs" && data.s === "ok") {
        console.log(`[ws][info] Подписки очищены`)
    }
    if (data.a === "rcms" && data.s === "ok") {
        data.p.forEach(item => {
            console.log(item);
            if (item.symbol === state.symbol 
                && item.tf === state.timeframe) {
                update_curr_rec(item.rcms);
            }
        });
    }
    if (data.a === "rcms2" && data.s === "ok") {
        update_curr_rec2(data.p);
    }
};

function ws_close_handler(event) {
    if (event.wasClean) {
        console.log(`[ws][info] Соединение закрыто чисто, код=${event.code} причина=${event.reason}`);
    } else {
        console.log('[ws][info] Соединение прервано');
    }
};

function ws_error_handler(error) {
    console.error(`[ws][error] ${error.message}`);
};

function ws_connect(url) {
    const ws = new WebSocket(url);
    // Listeners
    ws.onopen    = ws_open_handler;
    ws.onmessage = ws_message_handler;
    ws.onclose   = ws_close_handler;
    ws.onerror   = ws_error_handler;

    return ws;
}

// -- Execution --
//todo
//websocket = ws_connect("ws://127.0.0.1:7890/home");
websocket = ws_connect(wss_url + '/home');