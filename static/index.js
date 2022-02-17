var game,round;
var socket=io();
socket.on('connect',function(){
    console.log('connected to server');
});

socket.on('disconnect',function(){
    console.log('Disconnected');
});

socket.on('game_start',function(data){
    data=JSON.parse(data.data);
    text=data.text;
    title=data.title;
    author=data.author;
    console.log(text,title,author);
    $('#problem').html(`<span class="now_char" style="font-size:42px;">${text[0]}</span>${text.slice(1)}`);
    $('#title').html(`《${title}》`);
    $('#author').html(author);
});

socket.on('game_end',function(){
    $('#problem').text('等待下一题');
    $('#title').html('');
    $('#author').html('');
})