// -- Variables and constants --

state.frame = 1;
state.timeframe = "{{ initial_tf.abbr }}";
state.symbol = "{{ initial_cp }}";
state.angles = [0, 0, 0];


let tab_visible         = true;
let window_is_resizing  = false;
let window_width        = window.innerWidth;
let touch_start         = null;
let touch_end           = null;
  
const arrows_left       = document.querySelectorAll(".arrow[data-dir='<']");
const arrows_right      = document.querySelectorAll(".arrow[data-dir='>']");
  
const frames_container  = document.querySelector("#frames");
const frames_list       = document.querySelectorAll(".frame");
const frames_min        = 0;
const frames_max        = frames_list.length - 1;
  
const header_symbols    = document.querySelectorAll(".header-symbol")

const curr_cp_container = document.querySelector(".curr-cp-container");
const curr_cp_first     = document.querySelector(".curr-cp-first");
const curr_cp_last      = document.querySelector(".curr-cp-last");
const curr_cp_firstname = document.querySelector(".curr-cp-firstname");
const curr_cp_lastname  = document.querySelector(".curr-cp-lastname");
const curr_cp_flags     = document.querySelectorAll(".curr-cp-container .cp-flag");

const angles            = [-70, -37, 0, 37, 70];
const rec_status_names  = ["активно продавать", "продавать", "нейтрально", "покупать", "активно покупать"];
 const colors = {
        0:'#E9761B',
        1:'#E9761B',
        2:'#FFFFFF',
        3:'#1CCAE8',
        4 :'#1CCAE8'
    };
const rec_arws          = document.querySelectorAll(".frame .rec-arw");
const rec_osc_arw       = document.querySelector(".frame[data-frame='0'] .rec-arw");
const rec_osc_status    = document.querySelector(".frame[data-frame='0'] .rec-status");
const rec_osc_sell_cnt  = document.querySelector(".frame[data-frame='0'] .rec-count .sell-count");
const rec_osc_hold_cnt  = document.querySelector(".frame[data-frame='0'] .rec-count .hold-count");
const rec_osc_buy_cnt   = document.querySelector(".frame[data-frame='0'] .rec-count .buy-count");

const rec_summ_arw      = document.querySelector(".frame[data-frame='1'] .rec-arw");
const rec_summ_status   = document.querySelector(".frame[data-frame='1'] .rec-status");
const rec_summ_sell_cnt = document.querySelector(".frame[data-frame='1'] .rec-count .sell-count");
const rec_summ_hold_cnt = document.querySelector(".frame[data-frame='1'] .rec-count .hold-count");
const rec_summ_buy_cnt  = document.querySelector(".frame[data-frame='1'] .rec-count .buy-count");

const rec_ma_arw        = document.querySelector(".frame[data-frame='2'] .rec-arw");
const rec_ma_status     = document.querySelector(".frame[data-frame='2'] .rec-status");
const rec_ma_sell_cnt   = document.querySelector(".frame[data-frame='2'] .rec-count .sell-count");
const rec_ma_hold_cnt   = document.querySelector(".frame[data-frame='2'] .rec-count .hold-count");
const rec_ma_buy_cnt    = document.querySelector(".frame[data-frame='2'] .rec-count .buy-count");

const btn_tf_list       = document.querySelectorAll("a.tf");
let btn_cp_list         = document.querySelectorAll(".cp-row:not(.disabled)");

const cp_row_list       = btn_cp_list; // 8==э - - -
const idc_row_list      = document.querySelectorAll(".idc-row");


// -- Handlers --
function getRandInt(min, max) {
    return Math.random() * (max - min) + min;
}

function tab_visibility_handler(event) {
    if (document.visibilityState == "visible") {
        console.log("tab is active")
        if (tab_visible === false) {
            tab_visible = true;
// todo
            websocket = ws_connect(wss_url);
        }
    } else {
        console.log("tab is inactive")
        tab_visible = false;
        if (websocket != null)
            websocket.close();
    }
}

function window_resize_handler(event) {
    if (window_is_resizing === true)
        return;

    window_is_resizing = true;

    setTimeout(function () {
        if (window.innerWidth < 201) {
            window_is_resizing = false;
            return;
        }

        frames_list.forEach(frame => {
            frame.classList.add("d-none");
        });
        
        window_width = document.body.offsetWidth;

        frames_container.style.width = frames_list.length * window_width + "px";
        frames_container.style.left  = -state.frame * window_width + "px";
        frames_list.forEach((frame, i) => {
            frame.style.width = window_width + "px";
        });

        while (curr_cp_container.offsetWidth > window.innerWidth - 200) {
            const font_size = parseInt(getComputedStyle(curr_cp_first).fontSize.replace("px", ''));
            curr_cp_first.style.fontSize = (font_size - 10) + "px";
            curr_cp_last.style.fontSize = (font_size - 10) + "px";
            curr_cp_flags[0].style.height = (font_size - 10) + "px";
            curr_cp_flags[1].style.height = (font_size - 10) + "px";
        }
        
        window_scroll_handler();

        frames_list.forEach(frame => {
            frame.classList.remove("d-none");
        });

        window_is_resizing = false;
    }, 250);
}

function window_scroll_handler(event) {
    return;
}
    
function checkDirection() {
    const delta_x = touch_end[0] - touch_start[0];
    const delta_y = touch_end[1] - touch_start[1];

    if (Math.abs(delta_y) > Math.abs(delta_x)) {
        // Do nothing. Let browser take control.
    }
    else {
        if (Math.abs(delta_x) < 50)
            return;

        if (delta_x < 0) {
            right_arrow_clickhandler();
        }
        else {
            left_arrow_clickhandler();
        }
    }

    touch_start = null; 
    touch_end = null;
}

function touch_start_handler(event) {
    touch_start = []
    touch_start.push(event.changedTouches[0].screenX);
    touch_start.push(event.changedTouches[0].screenY);
}

function touch_end_handler(event) {
    touch_end = [];
    touch_end.push(event.changedTouches[0].screenX);
    touch_end.push(event.changedTouches[0].screenY);
    checkDirection()
}


function btn_tf_clickhandler(event) {

    if (event.target.dataset.active === '1')
        return;
    
    btn_tf_list.forEach(btn => {
        if (btn.dataset.abbr === event.target.dataset.abbr){
            btn.dataset.active = "1";
            btn.classList.add("active");
        }
    });

    state.timeframe = event.target.dataset.abbr;

    btn_tf_list.forEach(btn => {
        if (btn.dataset.abbr === state.timeframe || btn.dataset.active === '0')
            return;

        btn.dataset.active = "0";
        btn.classList.remove("active");
    });

    // Resetting "recommendation arc view"
    reset_rcm_view();

    // Resetting indicators recommendations
    reset_idcs();

    // Websocket
    let message = JSON.stringify({ 
        a: "clear_subs", 
        t: hello,
    });
    if (websocket != null)
        websocket.send(message);

    message = JSON.stringify({ 
        a: "add_sub:all", 
        p: [state.symbol, state.timeframe], 
        t: hello,
    });
    if (websocket != null)
        websocket.send(message);

    // Other symbols + current timeframe
    const data_items = get_data_items();

    data_items.forEach(([symbol, tf]) => {
        const message = JSON.stringify({ 
            a: "add_sub2:summ", 
            p: [symbol, tf], 
            t: hello,
        });
        websocket.send(message);
    }); 
}


function btn_cp_clickhandler(event) {
    const ect_btn = event.currentTarget.querySelector(".btn-cp");

    if (ect_btn.dataset.active === "1" || ect_btn.classList.contains("disabled"))
        return;
    
    state.symbol = ect_btn.dataset.abbr;
    curr_cp_first.innerText = ect_btn.dataset.first;
    curr_cp_last.innerText = ect_btn.dataset.last;
    curr_cp_firstname.innerText = ect_btn.dataset.firstname;
    curr_cp_lastname.innerText = ect_btn.dataset.lastname;
    
    // Replacing flags in "current currency pair view"
    let flag1_src = curr_cp_flags[0].src;
    flag1_src = flag1_src.replace(/([A-Z]+)/, ect_btn.dataset.first);
    curr_cp_flags[0].setAttribute("src", flag1_src);

    let flag2_src = curr_cp_flags[1].src;
    flag2_src = flag2_src.replace(/([A-Z]+)/, ect_btn.dataset.last);
    curr_cp_flags[1].setAttribute("src", flag2_src);
    
    ect_btn.dataset.active = "1";
    ect_btn.classList.add("active");

    header_symbols.forEach(element => {
        element.innerText = ect_btn.dataset.abbr;
    })

    btn_cp_list.forEach(item => {
        const btn = item.querySelector(".btn-cp")
        if (btn.dataset.abbr === state.symbol || btn.dataset.active === '0')
            return;

        btn.dataset.active = '0';
        btn.classList.remove("active");
    });

    // Resetting "recommendation arc view"
    reset_rcm_view();

    // Websocket
    let message = JSON.stringify({ 
        a: "clear_subs", 
        t: hello,
    });
    if (websocket != null)
        websocket.send(message);

    message = JSON.stringify({ 
        a: "add_sub:all", 
        p: [state.symbol, state.timeframe], 
        t: hello,
    });
    if (websocket != null)
        websocket.send(message);
}


function reset_rcm_view() {
    // OSC
    state.angles[0]                 = 0;
    rec_osc_arw.style.transform     = `rotate(0deg)`;
    rec_osc_status.innerText        = rec_status_names[2];
    rec_osc_sell_cnt.innerText      = "0";
    rec_osc_hold_cnt.innerText      = "0";
    rec_osc_buy_cnt.innerText       = "0";

    // SUMM
    state.angles[1]                 = 0;
    rec_summ_arw.style.transform    = `rotate(0deg)`;
    rec_summ_status.innerText       = rec_status_names[2];
    rec_summ_sell_cnt.innerText     = "0";
    rec_summ_hold_cnt.innerText     = "0";
    rec_summ_buy_cnt.innerText      = "0";

    // MA
    state.angles[2] = 0;
    rec_ma_arw.style.transform      = `rotate(0deg)`;
    rec_ma_status.innerText         = rec_status_names[2];
    rec_ma_sell_cnt.innerText       = "0";
    rec_ma_hold_cnt.innerText       = "0";
    rec_ma_buy_cnt.innerText        = "0";
}


function reset_idcs() {
    // OSC + MA
    idc_row_list.forEach(idc_row => {
        const idc_summ = idc_row.querySelector(".idc-summ");
        idc_summ.innerText = "нейтрально";
        idc_summ.style.color = colors[2];  
  });

    // SUMM
    btn_cp_list.forEach(btn => {
        const cp_summ = btn.querySelector(".cp-summ");
        cp_summ.innerText = "нейтрально";
        cp_summ.style.color = colors[2];
    });
}


function init_frames(){
    window_resize_handler();
    frames_container.style.width = frames_list.length * window_width + "px";
    frames_container.style.left  = -state.frame * window_width + "px";
}

function frame_change_handler() {
    return;
}


function left_arrow_clickhandler(event) {
    if (state.frame > frames_min) {

        state.frame -= 1;
        if (state.frame === frames_min)
            arrows_left.forEach(arrow => arrow.classList.add("hidden"));
        
        arrows_right.forEach(arrow => arrow.classList.remove("hidden"));
        
        frames_container.style.left = -state.frame * window_width + "px";

        frame_change_handler();
    }
}

function right_arrow_clickhandler(event) {
    if (state.frame < frames_max) {

        state.frame += 1;
        if (state.frame === frames_max)
            arrows_right.forEach(arrow => arrow.classList.add("hidden"));
        
        arrows_left.forEach(arrow => arrow.classList.remove("hidden"));

        frames_container.style.left = -state.frame * window_width + "px";
        
        frame_change_handler();
    }
}

function get_data_items() {
    const data_items = [];

    cp_row_list.forEach(cp_row => {
        const symbol = cp_row.querySelector(".btn-cp").dataset.abbr;
        data_items.push([symbol, state.timeframe]);
    });

    return data_items;
}

function update_curr_rec(rcms) {
    const conv = {
        STRONG_SELL : 0,
        SELL        : 1,
        HOLD        : 2,
        BUY         : 3,
        STRONG_BUY  : 4
    };

    if (tab_visible === false)
        return;

    // OSC
    idx = conv[rcms.OSC.RCM];
    state.angles[0] = angles[idx];
    rec_osc_arw.style.transform = `rotate(${angles[idx]}deg)`;
    rec_osc_status.innerText = rec_status_names[idx];
    rec_osc_sell_cnt.innerText = rcms.OSC.SELL;
    rec_osc_hold_cnt.innerText = rcms.OSC.HOLD;
    rec_osc_buy_cnt.innerText = rcms.OSC.BUY;

    // SUMM
    idx = conv[rcms.SUMM.RCM];
    state.angles[1] = angles[idx];
    rec_summ_arw.style.transform = `rotate(${angles[idx]}deg)`;
    rec_summ_status.innerText = rec_status_names[idx];
    rec_summ_sell_cnt.innerText = rcms.SUMM.SELL;
    rec_summ_hold_cnt.innerText = rcms.SUMM.HOLD;
    rec_summ_buy_cnt.innerText = rcms.SUMM.BUY;

    // MA
    idx = conv[rcms.MA.RCM];
    state.angles[2] = angles[idx];
    rec_ma_arw.style.transform = `rotate(${angles[idx]}deg)`;
    rec_ma_status.innerText = rec_status_names[idx];
    rec_ma_sell_cnt.innerText = rcms.MA.SELL;
    rec_ma_hold_cnt.innerText = rcms.MA.HOLD;
    rec_ma_buy_cnt.innerText = rcms.MA.BUY;

    // OSC frame
    Object.entries(rcms.OSC.CMP).forEach(([key, value]) => {
        // TODO Optimize this
        let i = 0;
        while (i < idc_row_list.length) {
            const idc_row = idc_row_list[i];
            
            if (idc_row.dataset.name === key) {
                idc_summ = idc_row.querySelector(".idc-summ");
                idc_summ.innerText = rec_status_names[conv[value]];
                idc_summ.style.color = colors[conv[value]];
                break;
            }
            i += 1;
        }
    });

    // MA frame
    Object.entries(rcms.MA.CMP).forEach(([key, value]) => {
        // TODO Optimize this
        let i = 0;
        while (i < idc_row_list.length) {
            const idc_row = idc_row_list[i];
            
            if (idc_row.dataset.name === key) {
                idc_summ = idc_row.querySelector(".idc-summ");
                idc_summ.innerText = rec_status_names[conv[value]];
                idc_summ.style.color = colors[conv[value]];
                break;
            }
            i += 1;
        }
    });
}

function update_curr_rec2(items) {
    
    const conv = {
        STRONG_SELL : 0,
        SELL        : 1,
        HOLD        : 2,
        BUY         : 3,
        STRONG_BUY  : 4
    };
    
    if (tab_visible === false)
        return;

    items.forEach(item => {
        const rcms2 = item.rcms2;

        console.log('item:');
        console.log(item)
    
        btn_cp_list.forEach(btn => {
            const a = btn.querySelector("a.btn-cp");
            
            if (a.dataset.abbr !== item.symbol || item.tf !== state.timeframe)
                return;
    
            const cp_summ = btn.querySelector(".col-auto.cp-summ.align-items-center");
            cp_summ.style.display = 'block';
            let percents = btn.querySelector('div.col-auto.d-flex > div.align-items-center.d-flex').innerHTML.replace(" %", "");
            percents = parseFloat(percents);
            console.log(percents)
            if (percents < 0) {
                cp_summ.innerHTML = `<img src="../../static/images/orange.png" style="width: 1.3rem;">`;
            } else if (percents > 0) {
                cp_summ.innerHTML = `<img src="../../static/images/blue.png" style="width: 1.3rem;">`;
            } else {
                cp_summ.innerHTML = `<div style="width: 1.3rem"> </div>`;
            }
            cp_summ.style.color = colors[conv[rcms2.SUMM.RCM]];
        });
    });
}

// -- Binding handlers to event listeners --
window.addEventListener("resize", window_resize_handler);

document.addEventListener("visibilitychange", tab_visibility_handler);

document.addEventListener('touchstart', touch_start_handler);
  
document.addEventListener('touchend', touch_end_handler);

btn_tf_list.forEach(btn => {
    btn.addEventListener("click", btn_tf_clickhandler);
});


btn_cp_list.forEach(btn => {
    btn.addEventListener("click", btn_cp_clickhandler);
});

arrows_left.forEach(arrow => {
    arrow.addEventListener("click", left_arrow_clickhandler);
});
arrows_right.forEach(arrow => {
    arrow.addEventListener("click", right_arrow_clickhandler);
});


// -- Execution -- 
init_frames();

const rec_ntr_short = setInterval(function(){
    if (tab_visible === false)
        return;

    const randint = getRandInt(-5, 5);
    rec_arws.forEach((arw, i) => {
        arw.style.transform = `rotate(${state.angles[i] + randint}deg)`;
    });
}, 1000);

