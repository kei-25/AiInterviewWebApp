//webサーバのIPアドレス
const host = '127.0.0.1';

async function get_sha256(salt){
    text = document.getElementById('password1').value;
    text += salt
    const uint8  = new TextEncoder().encode(text)
    const digest = await crypto.subtle.digest('SHA-256', uint8)
    var sha_text = Array.from(new Uint8Array(digest)).map(v => v.toString(16).padStart(2,'0')).join('')
    return sha_text;
}

//16桁のソルトを生成し返す
function random_cahar_create(){
    // 使用する英数字を変数charに指定
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let random_str = '';
    // 用意した空文字列にランダムな英数字を格納
    for(let i = 0; i < 16; i++) {
        random_str += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return random_str
}

//入力したデータが条件を満たすと登録ボタンが有効になる
function input_data_check(){
    const id = document.getElementById('id').value;
    const name = document.getElementById('name').value;
    const password1 = document.getElementById('password1').value;
    const password2 = document.getElementById('password2').value;
    const register_btn = document.getElementById('register-btn-id');
    if (id.length >= 6 && id.length <= 20 && name.length >= 1 && name.length <= 20 && password1.length >= 8 && password1.length <= 20 && password2.length >= 8 && password2.length <= 20) {
        register_btn.style.backgroundColor = "rgb(67, 67, 255)";
        register_btn.disabled = false;
    }else{
        register_btn.style.backgroundColor = "rgb(100, 100, 100)";
        register_btn.disabled = true;
    }
}

//入力されたユーザデータをサーバに送信しする
async function send_data() {
    const password1 = document.getElementById('password1').value;
    const password2 = document.getElementById('password2').value;
    if(password1 != password2){
        document.getElementById('error-message').innerText = '入力されたパスワードが一致しません';
    }else{
        const input_id = document.getElementById('id').value;
        const input_name = document.getElementById('name').value;
        let check = "False";
        const flag = document.getElementById('agreement').checked;
        if(flag){
            check = "True"
        }
        let salt = random_cahar_create();
        let sha_text = await get_sha256(salt);
        const dir = 'user-data-upload';
        const url = 'http://'+host+':8080/'+dir;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({id:input_id,name:input_name,shaText:sha_text,agreement:check,salt:salt}),
        });
        if (response.ok) {
            const result = await response.json();
            if(result.judge == "True"){
                document.forms['tmp-form'].submit();
            }else{
                document.getElementById('error-message').innerText = result.message;
            }
        } else {
            document.getElementById('error-message').innerText = 'エラーが発生しました';
        }
    }
}