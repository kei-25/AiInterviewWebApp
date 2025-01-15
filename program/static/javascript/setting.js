var max_quest_num = 10;

//数値をプラス1させる
function num_plus(){
    var num = parseInt(document.getElementById("quest-num").value);
    if(num < max_quest_num){
        document.getElementById("quest-num").value = num + 1;
    }
}

//数値をマイナス1させる
function num_minus(){
    var num = parseInt(document.getElementById("quest-num").value);
    if(num > 1){
        document.getElementById("quest-num").value = num - 1;
    }
}

//想定されていない値が入力された場合1を代入する
function num_check(){
    var num = parseInt(document.getElementById("quest-num").value);
    if(!(num <= max_quest_num && num > 0)){
        document.getElementById("quest-num").value = 1;
    }
}

//質問の選択した数が指定した質問数以上選択されている場合エラーを出力する
function quest_num_check(){
    var num = parseInt(document.getElementById("quest-num").value);
    const checkboxes = document.querySelectorAll(
        'input[name="quest"]:checked'
    );  
    if(checkboxes.length > num){
        const MESSAGE = "指定した質問数以上のチェックボックスが選択されています";
        document.getElementById("error-message").textContent = MESSAGE;
    }else{
        document.forms['setting-data-send'].submit();
    }
}

//回答から質問を生成するにチェックを入れている場合、質問数設定の数値の上限値を変更する
function quest_num_check_generat(){
    let generat_flag = document.getElementById("toggle-generat").checked;
    if(generat_flag){
        max_quest_num = 5;
        var num = parseInt(document.getElementById("quest-num").value);
        if(num >= 6){
            document.getElementById("quest-num").value = 5;
        }
    }else{
        max_quest_num = 10;
    }
}