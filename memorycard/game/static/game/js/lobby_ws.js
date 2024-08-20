const lobby_name = document.getElementById("lobby_name").textContent;
const ws = new WebSocket("ws://127.0.0.1:8000/" + lobby_name + '/');

let messageHistory = "";

ws.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.action === 'chat_update'){
        messageHistory = data.text;
        localStorage.setItem("messageHistory", messageHistory);
        document.getElementById("joins").innerHTML = messageHistory;
    } 
    else if (data.action === 'start'){
        setTimeout(function() {
            window.location.href = "http://127.0.0.1:8000/play/"+data.user1+"/"+data.user2+"/start/"; 
        }, 1000);
    }
};