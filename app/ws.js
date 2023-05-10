var server = 'wss://localhost:8008/';
var channelError = "Not in channel"
function zPad(n) {
    if (n < 10) return '0' + n;
    else return n;
}

function timestamp() {
    var d = new Date();
    return zPad(d.getHours()) + ':' + zPad(d.getMinutes()) + ':' + zPad(d.getSeconds());
}

var channelMessage = {};
function write_to_connection(message) {
    var line = '[' + timestamp() + '] ' + message + '<br>';
    $('#messages').append(line);
}
function write_to_mbox(message) {
    // if(["send", "message"].indexOf(message.kind) !== -1){
    //     let author = message.data.author;
    //     if(author === undefined){
    //         author = "me";
    //     }
    // var line = '[' + timestamp() + '] ' +author+": "+ message.data.content + '<br>';
    // $('#messages').append(line);
    const select = document.querySelector('#channel');
    let optionValue = select.options.item(select.options.selectedIndex).value;
    let channel = message.data.where;
    console.log(channel);
    if(optionValue === "manual"){
        optionValue = $("#type_manual").val();
    }
    if (channelMessage[channel] === undefined){
        channelMessage[channel] = [message];
    } else if(channelMessage[channel] !== undefined) {
        channelMessage[channel].push(message);
    }
    console.log(channelMessage);
    if(channel === optionValue){
        write_message_from_cache(optionValue);
    }
}
var socket;
function write_message_from_cache(optionValue){

    $("#messages").empty();
    let listOfMessages = channelMessage[optionValue];
    if(listOfMessages === undefined) return;
    for(let i = 0 ; i <listOfMessages.length; i = i+1){
        let author = listOfMessages.at(i).data.author;
        if(author === undefined || author === name){
            author = "me";
        }
        var line = '[' + timestamp() + '] ' +author+": "+ listOfMessages.at(i).data.content + '<br>';
        $('#messages').append(line);
    }
}
function on_select_channel(){
    const select = document.querySelector('#channel');
    const optionValue = select.options.item(select.options.selectedIndex).value;
    if(optionValue === "manual"){
        $("#type_manual").show();

        $("#messages").empty();
    } else{
        $("#type_manual").hide();
        $("#leave_btn").show();
        write_message_from_cache(optionValue);
}}
function on_click_channel() {
    const select = document.querySelector('#channel');
    socket.send(JSON.stringify({ "kind": "list_channels", "data": {}}));
    socket.onmessage = function (event){
        let message = JSON.parse(event.data);
        console.log(message)
        if(message.kind === "leave" || message.error !== undefined){console.log(message); return;}
        if(message.kind === "message") {defaultOnMessage(event); return;}
        const channels = message.data.channels;
        if(channels.length === 0) return;
        const value = select.options.item(select.options.selectedIndex).value;
        select.options.length = 0;
        for (let i = 0 ; i < channels.length; i++){
            const channel = channels.at(i);
            let newOption = new Option("#"+channel,channel);
            if(channel === value){
                newOption = new Option("#"+channel, channel, false, true);
            }
            select.add(
                newOption, undefined
            )
        }
        let manualOption = new Option("Type Manually", "manual");

        if("manual" === value){
            manualOption = new Option("Type Manually","manual", false, true);
        }
        select.add(
            manualOption,undefined
        );

    };
   // const optionText = document.createTextNode('Option Text');
    // select.add(newOption,undefined);
    // console.log(select.options.item(select.options.selectedIndex).value);

    // socket.onmessage = function (event){
    //     console.log(event);
    //     write_to_mbox(event.data);
    // }

    return false;
}
function leave_channel(){
    const select = document.querySelector('#channel');

    const value = select.options.item(select.options.selectedIndex).value;
    socket.send(JSON.stringify({ "kind": "leave", "data": { "where": value } }));

}
function defaultOnMessage (event) {
    let message = JSON.parse(event.data);
    if(message.code == "4") {
        location.reload();
        alert("Password is wrong! Please, try again.")
        return;

    }
    if(message.kind === "identified") return;
    console.log(event);
    write_to_mbox(JSON.parse(event.data));
}

var name;
$(document).ready(function() {

    $('#name').focus();
    $('#connect-form').submit(function() {

        socket = new WebSocket(server);
        name = $('#name').val();
        passwd = $('#password').val();
        socket.onerror = function(error) {
            console.log('WebSocket Error: ' + error);
        };

        socket.onopen = function(event) {
            $('#jumbotron').hide();
            write_to_connection('Connected to: ' + server);
            socket.send(JSON.stringify({"kind": "identify", "data": { "name": name}}));
            socket.send(JSON.stringify({"kind": "register_name", "data":{"passwd": passwd}}));
            $('#message_wrapper').show();
            $('#channel_loop').show();
            $('#channel').show();
            $('#message').focus();
            $("#type_manual").show();
        };

        socket.onmessage = defaultOnMessage;
        socket.onclose = function(event) {
            write_to_connection('Disconnected from ' + server);
        };

        $('#message-form').submit(function() {
            socket.onmessage = defaultOnMessage;
            let channel = $('#channel').val();
            if(channel === "manual"){
                channel = $('#type_manual').val();
                console.log(channel);
                if(channel === ""){

                    alert("You need to type a channel you want!")
                    return false;
                }
            }
            socket.send(JSON.stringify({"kind": "join", "data":{ "where": channel }}));
            let message = JSON.stringify({ "kind": "send", "data": { "where": channel, "content": $("#message").val() } });
            socket.send(message);
            write_to_mbox(JSON.parse(message));
            return false;
        });

        return false;
    });
});