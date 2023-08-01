// -- Consts and variables --
state.data = new Set();

let tab_visible    = true;


const menuFrame = document.getElementById("menu-frame");
const topWinnersLosersFrame = document.getElementById("top-winnerslosers");
const fearAndGreedFrame = document.getElementById("fear-greed-frame");
const btn_main     = document.querySelector(".btn-main");
const button1 = document.getElementById("menu-frame").querySelector(".my-button1");
const button2 = document.getElementById("fear-greed-frame").querySelector(".my-button2");
const button3 = document.getElementById("menu-frame").querySelector(".my-button3");
const button4 = document.getElementById("top-winnerslosers").querySelector(".my-button4");
const backButton2 = document.getElementById("top-winnerslosers").querySelector(".back-to-menu2");
const backButton3 = document.getElementById("fear-greed-frame").querySelector(".back-to-menu3");
const cp_row_list  = document.querySelectorAll(".cp-row:not(.disabled)");
const cp_row_items = document.querySelectorAll(".cp-row-item");
const btn_tf_list  = document.querySelectorAll(".btn-tf");

const rec_status_names = ["sell", "hold", "buy"];

// -- Handlers --
function cp_row_item_click_handler(event) {
    const cp_row_item = event.currentTarget;
    const cp_row = cp_row_item.closest(".cp-row");

    if (cp_row.classList.contains("disabled"))
        return;
    
    const btn_tf_list = cp_row.querySelectorAll(".btn-tf");
    const btn_tf_active_list = cp_row.querySelectorAll(".btn-tf.active");
    const btn_cp = cp_row_item.querySelector(".btn-cp");
    
    if (btn_tf_active_list.length === 1) {
        btn_tf_active_list[0].classList.remove("active");
        btn_tf_active_list[0].dataset.active = "0";

        btn_cp.classList.remove("active");
        btn_cp.dataset.active = "0";
        return;
    }
        
    btn_tf_list[0].classList.add("active");
    btn_tf_list[0].dataset.active = "1";   
    
    if (btn_cp.classList.contains("active") === false) {
        btn_cp.classList.add("active");
        btn_cp.dataset.active = "1";
    }

    update_state_data();
}

function btn_tf_click_handler(event) {
    const btn = event.currentTarget;    
    const cp_row = btn.closest(".cp-row");

    if (cp_row.classList.contains("disabled"))
        return;

    if (btn.classList.contains("active") === true) {
        btn.classList.remove("active");
        btn.dataset.active = "0";
    }
    else {
        btn.classList.add("active");
        btn.dataset.active = "1";
    }
    
    const btn_tf_list = cp_row.querySelectorAll(".btn-tf");
    const btn_tf_active_list = cp_row.querySelectorAll(".btn-tf.active");
    const btn_cp = cp_row.querySelector(".btn-cp");
    
    if (btn_tf_active_list.length > 0) {
        if (btn_cp.classList.contains("active") === false) {
            btn_cp.classList.add("active");
            btn_cp.dataset.active = "1";
        }
    }
    else {
        if (btn_cp.classList.contains("active") === true) {
            btn_cp.classList.remove("active");
            btn_cp.dataset.active = "0";
        }
    }

    update_state_data();
}

function update_state_data() {
    cp_row_list.forEach(item => {

        const btn_cp = item.querySelector(".btn-cp");

        const btn_tf_list = item.querySelectorAll(".btn-tf");

        btn_tf_list.forEach(btn_tf => {
            const item = JSON.stringify([
                btn_cp.dataset.abbr, 
                btn_tf.dataset.abbr
            ]);

            if (btn_tf.dataset.active === "1") 
                state.data.add(item);
            else
                state.data.delete(item);
        });
    });
}


function update_curr_rec2(items) {
    // TODO Optimize
    const conv = {
        STRONG_SELL : 0,
        SELL        : 0,
        HOLD        : 1,
        BUY         : 2,
        STRONG_BUY  : 2
    };

    const colors = {
        STRONG_SELL : '#E9761B',
        SELL        : '#E9761B',
        HOLD        : '#FFFFFF',
        BUY         : '#1CCAE8',
        STRONG_BUY  : '#1CCAE8'
    }
    
    if (tab_visible === false)
        return;

    items.forEach(item => {
        const rcms2 = item.rcms2;

        console.log(item);

        cp_row_list.forEach(cp_row => {
            if (cp_row.dataset.abbr != item.symbol)
                return;

            const tf_cols = cp_row.querySelectorAll(".tf-col")

            tf_cols.forEach(tf_col => {
                const a = tf_col.querySelector(".btn-tf");
                if (a.dataset.abbr != item.tf)
                    return;
                
                const span = tf_col.querySelector("span");
                span.innerText = rec_status_names[conv[rcms2.SUMM.RCM]];
                span.style.color = colors[rcms2.SUMM.RCM];
            })
        });
    });
}

function get_data_items() {
    const data_items = [];

    cp_row_list.forEach(cp_row => {
        const symbol = cp_row.querySelector(".btn-cp").dataset.abbr;
        
        const tf_cols = cp_row.querySelectorAll(".tf-col");
        tf_cols.forEach(tf_col => {
            const tf = tf_col.querySelector(".btn-tf").dataset.abbr;
            data_items.push([symbol, tf]);
        });
    });

    return data_items;
}

function btn_main_show() {
    btn_main.classList.remove("d-none");
}

function btn_main_hide() {
    btn_main.classList.add("d-none");
}

function btn_main_click_handler(event) {
    const data = [];
    
    state.data.forEach(item => {
        data.push(JSON.parse(item));
    });
    
    const json = JSON.stringify(data);

    window.Telegram.WebApp.sendData(json);
    window.Telegram.WebApp.close();
}

function window_resize_handler() {
    const width = window.innerWidth;
    const height = window.innerHeight;
  
    if (width < 768) {
      switchFrames(topWinnersLosersFrame, menuFrame); // заменить menu_frame на menuFrame
    } else {
      switchFrames(fearAndGreedFrame, menuFrame); // заменить menu_frame на menuFrame
    }
  }

// -- Event listeners --
cp_row_items.forEach(item => {
    item.addEventListener("click", cp_row_item_click_handler);
});

btn_tf_list.forEach(btn => {
    btn.addEventListener("click", btn_tf_click_handler);
});

btn_main.addEventListener("click", btn_main_click_handler);

window.addEventListener("resize", window_resize_handler);

// -- Execution --
window_resize_handler();
update_state_data();
