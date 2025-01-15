// 音声合成APIを取得
const synth = window.speechSynthesis;
var speak;
var generat;
var visibility_original_load;
var visibility_original_recode;
let qid;
let recognition; // SpeechRecognitionオブジェクト
let is_recognizing = false; // 音声認識の状態を管理

//webサーバのIPアドレス
const host = '127.0.0.1';

//ページが読み込まれた際に初期設定を行う
document.addEventListener("DOMContentLoaded", function() {
    //モーションの初期状態を保存
    visibility_original_load = document.getElementById('pulse-container').style.visibility;
    visibility_original_recode = document.getElementById('loader').style.visibility;
    //ロード中のモーションを非表示
    document.getElementById('pulse-container').style.visibility = "hidden";
    document.getElementById('loader').style.visibility = "hidden";
    //htmlに記述したdivタグから設定情報を取得する
    var setting_data_element = document.getElementById("setting-data");
    speak = setting_data_element.getAttribute("speak");
    var mic = setting_data_element.getAttribute("mic");
    generat = setting_data_element.getAttribute("generat");
    if(mic == "True"){
        input_text_field = document.getElementById('input-text');
        send_btn = document.getElementById('send-btn');
        input_text_field.remove();
        send_btn.remove();
    }else{
        mic_btn = document.getElementById('mic-btn');
        mic_btn.remove();
    }
    //htmlに記述したdivタグからを取得すセッション情報を取得する
    let quest_num = parseInt(setting_data_element.getAttribute("quest_num"));
    let question = setting_data_element.getAttribute("question_text");
    qid = setting_data_element.getAttribute("qid");

    //画面上部のテキストの初期化
    if(generat == "True"){
        document.getElementById('leftover_num').innerText = "残り"+(quest_num*2)+"問"
    }else{
        document.getElementById('leftover_num').innerText = "残り"+(quest_num)+"問"
    }
    //面接官側のテキストの初期化
    document.getElementById('question').innerText = "今から面接を始めます";
    speak_text();
    //3秒待ってから質問を表示する
    sleep(3, function() {
        document.getElementById('question').innerText = question;
        speak_text();
    });
    start_speech_recognition();
});

//タイマー
function sleep(waitSec, callbackFunc) {
    var spanedSec = 0;
    var waitFunc = function () {
        spanedSec++;
        if (spanedSec >= waitSec) {
            if (callbackFunc) callbackFunc();
            return;
        }
        clearTimeout(id);
        id = setTimeout(waitFunc, 1000);
    };
    var id = setTimeout(waitFunc, 1000);
}

// 読み上げを開始する関数
function speak_text() {
    if(speak == "True"){
        const textArea = document.getElementById('question');//読み上げさせたいテキストが格納された要素
        const text = textArea.textContent;
        if (text !== '') {
            const utterance = new SpeechSynthesisUtterance(text); // 読み上げるテキストを設定
            utterance.lang = 'ja-JP'; // 言語を日本語に設定
            utterance.rate = 1.2;      // 読み上げ速度（0.1 ～ 10、1が標準）
            utterance.pitch = 1;     // 音の高さ（0 ～ 2、1が標準）
            utterance.volume = 0.5;  //音の大きさ
            synth.speak(utterance);  // 読み上げを実行
        }
    }
}

//マイクをオンにする
function start_speech_recognition() {
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'ja-JP'; // 言語設定
    recognition.onstart = () => console.log('音声認識を開始しました');
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('認識結果:', transcript);
        //テキストを画面に表示
        document.getElementById('user-speak-text').innerText += transcript;
    };
    recognition.onerror = (event) => console.error('エラー:', event.error);

    // 音声認識が終了したときのイベント
    recognition.onend = () => {

        if (is_recognizing) {
            console.log('音声認識を再開します...');
            recognition.start(); // 音声認識を再開（継続的な認識が必要な場合）
        }
    };
}

// 音声認識の開始・停止をトグルする関数
function toggle_recognition() {
    if (!is_recognizing) {
        //現在入力されているテキストを初期化
        document.getElementById('user-speak-text').innerText = "";
        //マイクオンのモーションを表示
        document.getElementById('loader').style.visibility = visibility_original_load;
        // 音声認識を開始
        is_recognizing = true;
        recognition.start();
    } else {
        //マイクオンのモーションを非表示
        document.getElementById('loader').style.visibility = "hidden";
        // 音声認識を停止
        is_recognizing = false;
        recognition.stop();
        // テキストをバックエンドに送信
        var input_text = document.getElementById('user-speak-text').textContent;
        answer_send_text(input_text);
    }
}

//引数のテキストをサーバに送信
async function answer_send_text(input_text) {
    question_text = document.getElementById('question').textContent;
    //面接官側のテキストをリセット
    answer_text = document.getElementById('question').innerText = "";
    //ロード中のモーションを表示
    document.getElementById('pulse-container').style.visibility = visibility_original_load;
    const dir = 'text-upload';
    const url = 'http://'+host+':8080/'+dir;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answer : input_text ,question : question_text ,generat : generat ,qid : qid}),
    });
    //ロード中のモーションを非表示
    document.getElementById('pulse-container').style.visibility = "hidden";
    if (response.ok) {
        //responsから次の質問を取り出す
        const result = await response.json();
        if(result.transition_flag){
            document.forms['transition-form'].submit();
        }else{
            num_update();
            document.getElementById('question').innerText = result.question;
            speak_text();
            qid = result.qid;
            document.getElementById('user-speak-text').innerText = "";
            document.getElementById('input-text').value = "";
        }
    } else {
        document.getElementById('result').innerText = 'エラーが発生しました';
    }
}

//画面上に入力された取得し、テキストをサーバに送信する
async function send_text() {
    answer_text = document.getElementById('input-text').value;
    answer_send_text(answer_text);
}

//残りの問題の数を更新する
function num_update(){
    var leftover_num_str = question_text = document.getElementById('leftover_num').textContent;
    leftover_num_str = leftover_num_str.replace('残り', '').replace('問','');
    var leftover_num = Number(leftover_num_str);
    leftover_num = leftover_num - 1;
    document.getElementById('leftover_num').innerText = "残り"+(leftover_num)+"問"
}
