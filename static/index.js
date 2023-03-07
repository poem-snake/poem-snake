var game, round;
var urd=0;
var socket = io();
socket.on('connect', function () {
    console.log('connected to server');
});

socket.on('disconnect', function () {
    console.log('Disconnected');
    socket.connect();
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

socket.on('skip_check',function (data){
    let mes = data.message;
    swal({
        title: data.status == "success" ? "请稍候下一题开始" : "跳过失败",
        text: mes,
        icon: data.status,
    });
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
    $('#submit').removeClass('ui loading disabled primary button').addClass('ui primary button');
    if (mes != "提交成功") {
        $("#answer").parent().removeClass("ui input").addClass("ui error disabled input");
        $("#answer").val(mes);
        setTimeout(function () {
            $("#answer").parent().removeClass("ui error disabled input").addClass("ui input");
            $("#answer").val("");
        }, 2000);
    }
    else {
        $("#answer").parent().removeClass("ui input").addClass("uidisabled input");
        console.log("test success");
        update_coin();
        $("#answer").val(mes);
        setTimeout(function () {
            $("#answer").parent().removeClass("ui disabled input").addClass("ui input");
            $("#answer").val("");
        }, 3000);
    }
});

socket.on('record_add', function (data) {
    data = JSON.parse(data.data);
    title = data.title;
    author = data.author;
    text = data.line;
    username = data.username;
    let record = data;
    $("#history").prepend(`<div class="event">
            <div class="label">
                <img src="${record.gravatar}">
            </div>
            <div class="content">
                <div class="summary">
                    <a class="user">${record.username}</a> 进行了回答
                    <div class="date" data="${record.time}">${moment.utc(record.time).fromNow()} </div>
                </div>
                <div class="extra text">
                    <p>
                       <span class="poem" style="font-size: 24px;"> ${record.line}</span>
                       ——<span style="font-size: 18px; font-family: Kaiti;">${record.author}《${record.title}》</span>
                    </p>
                </div>
            </div>
        </div>`)
    origin = $("#problem_segment").html();
    $('#problem_head').text(`已被${username}答出`);
    $('#problem').text(text);
    $('#title').text(`《${title}》`);
    $('#author').text(author);
    setTimeout(function () {
        $('#problem_segment').html(origin);
    }, 3000);
});

socket.on('talk',function(data){
    // console.log(data);
    // 检测 talk 选项卡是否激活
    if ($('[data-tab="talk"].item.active').attr("data-tab")!='talk')
        urd++;
    if (urd!=0)
    {
        $('[data-tab="talk"].item').html(
            `聊天<span style="color:red;" id="urdlb">（${urd}）</span>`
        );
    }
    message=data.message.data
    udata=JSON.parse(data.user)
    $("#talk").prepend(`<div class="event">
    <div class="label">
        <img src="${udata.gravatar}">
    </div>
    <div class="content">
        <div class="summary">
            <a class="user">${udata.username}</a> 在聊天中说
            <div class="date" data="${moment.utc()}">${moment.utc().fromNow()} </div>
        </div>
        <div class="extra text">
            <p>
               ${filterXSS(message,options)}
            </p>
        </div>
    </div>
    `)
})

var last = 10000000000;

function load_more() {
    $.get(`/api/history?last=${last}`, function (data) {
        console.log(data);
        for (let i = 0; i < data.length; i++) {
            let record = data[i];
            $("#history").append(`<div class="event">
            <div class="label">
                <img src="${record.gravatar}">
            </div>
            <div class="content">
                <div class="summary">
                    <a class="user">${record.username}</a> 进行了回答
                    <div class="date" data="${record.time}">${moment.utc(record.time).fromNow()} </div>
                </div>
                <div class="extra text">
                    <p>
                       <span class="poem" style="font-size: 24px;"> ${record.line}</span>
                       ——<span style="font-size: 18px; font-family: Kaiti;">${record.author}《${record.title}》</span>
                    </p>
                </div>
            </div>
        </div>`)
            last = data[data.length - 1].id;
        }
    });
}

var options = {
    whiteList: {
        a: ['href', 'title', 'target']
    }
};

function update_coin (){
    $.get("/api/coin",function(data){
        $("#coin_num").text(data.coin);
    })
}
$(document).ready(function () {
    load_more();
    update_coin();
    setInterval(function () {
        $("#history .date").each(function () {
            let time = $(this).attr('data');
            $(this).text(moment.utc(time).fromNow());
        });
        $("#talk .date").each(function () {
            let time = $(this).attr('data');
            $(this).text(moment.utc(time).fromNow());
        });
    }, 10000);
    $('#submit').click(function () {
        $('#submit').removeClass("ui primary button").addClass("ui loading disabled primary button");
        let answer = $('#answer').val();
        console.log(answer);
        socket.emit('answer', { data: answer });
    });
    $('#answer').keydown(function (e) {
        if (e.keyCode == 13 && e.ctrlKey) {
            $('#submit').click();
        }
    });
    $('#talk_input').keydown(function (e) {
        if (e.keyCode == 13 && e.ctrlKey) {
            $('#talk_submit').click();
        }
    });
    $('#load_more').click(load_more);
    $('#skip').click(function () {
        socket.emit('skip');
    });
    $('#hint').click(function () {
        $('.ui.modal').modal('show');
    });
    $('.tabular.menu .item').tab();
    $('.tabular.menu .item').tab('change tab', 'history');
    $("#talk_submit").click(function () {
        socket.emit("talk_message", { data: $("#talk_input").val() })
        $("#talk_input").val("")
    })
    $('[data-tab="online"].item').click(function () {
        $.get("/api/users", function (data) {
            $("#online").html("");
            for (let i = 0; i < data.length; i++) {
                let user = data[i];
                $("#online").append(`<div class="item">
                <img class="ui avatar image" src="${user.gravatar}">
                <div class="content">
                    <a class="header">${user.username}</a>
                    <div class="description">在线！</div>
                </div>
            </div>`)
            }
        });
    });
    $('[data-tab="rank"].item').click(function () {
       $.get('/api/ranklist',function (data){
           $('#rank').html("");
           data=data.data
           $.each(data,function (index,item){
               $("#rank").append(`<div class="item">
                <img class="ui avatar image" src="${item.gravatar}">
                <div class="content">
                    <a class="header">${item.username}</a>
                    <div class="description">#${item.num}，${item.count} 条</div>
                </div>
            </div>
               `)
           })
       })
    });
    $('[data-tab="talk"].item').click(function () {
        urd=0;
        console.log(urd);
        $("#urdlb").remove();
    });
});