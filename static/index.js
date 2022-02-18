var game, round;
var socket = io();
socket.on('connect', function () {
    console.log('connected to server');
});

socket.on('disconnect', function () {
    console.log('Disconnected');
});

socket.on('game_start', function (data) {
    data = JSON.parse(data.data);
    text = data.text;
    title = data.title;
    author = data.author;
    console.log(text, title, author);
    $('#problem').html(`<span class="now_char" style="font-size:42px;" id="problem_now">${text[0]}</span>${text.slice(1)}`);
    $('#title').html(`《${title}》`);
    $('#author').html(author);
});

socket.on('game_end', function () {
    $('#problem').text('等待下一题');
    $('#title').html('');
    $('#author').html('');
})

socket.on('round_start', function (data) {
    data = JSON.parse(data.data);
    let char = $("#problem_now").text();
    $("#problem_now").html(char);
    let origin = $("#problem").text();
    console.log(data, char, origin);
    $("#problem").html(origin.slice(0, data.real_number) + `<span class="now_char" style="font-size:42px;" id="problem_now">` + data.text + `</span>` + origin.slice(data.real_number + 1));
});

socket.on("connect_message", function (data) {
    game = JSON.parse(data.current_game_content);
    round = JSON.parse(data.current_round);
    console.log(game, round);
    text = game.text;
    title = game.title;
    author = game.author;
    console.log(text, title, author);
    $('#problem').html(text);
    $('#title').html(`《${title}》`);
    $('#author').html(author);
    let origin = $("#problem").text();
    $("#problem").html(origin.slice(0, round.real_number) + `<span class="now_char" style="font-size:42px;" id="problem_now">` + round.text + `</span>` + origin.slice(round.real_number + 1));

});

socket.on('answer_check', function (data) {
    mes = data.message;
    console.log(mes);
});

$(document).ready(function () {
    $('#submit').click(function () {
        let answer = $('#answer').val();
        console.log(answer);
        socket.emit('answer', { data: answer });
    });
});