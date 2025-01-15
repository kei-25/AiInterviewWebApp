//webサーバのIPアドレス
let host = '127.0.0.1';

//1文字以上入力されたら登録ボタンを有効化する
function question_register(){
    const quest_text = document.getElementById('quest-text').value;
    const register_btn = document.getElementById('register');
    if (quest_text.length >= 1) {
        register_btn.style.backgroundColor = "rgb(67, 67, 255)";
        register_btn.disabled = false;
    }else{
        register_btn.style.backgroundColor = "rgb(100, 100, 100)";
        register_btn.disabled = true;
    }
}

//登録ボタンを押すと登録確認を表示し、質問の登録処理を行う
async function register_question_text(){
    const quest_text = document.getElementById('quest-text').value;
    const genre = document.getElementById('genre').value;
    const result = window.confirm("以下の内容で登録します。よろしいですか？\nジャンル : "+genre+"\n質問内容 : "+quest_text);
    if(result){
        const dir = 'question-text-upload';
        const url = 'http://'+host+':8080/'+dir;
        const response = await fetch(ulr, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({qtext:quest_text,genre:genre}),
        });
        if (response.ok) {
            const result = await response.json();
            if(result.flag == "True"){
                document.getElementById('message').innerText = "質問の登録に成功しました";
                document.getElementById('quest-text').value = "";
            }else{
                document.getElementById('message').innerText = "エラーが発生しました";
            }
        } else {
            document.getElementById('message').innerText = "エラーが発生しました";
        }
    }
}