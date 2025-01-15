//webサーバのIPアドレス
let host = '127.0.0.1';

//引数のパスワードとソルトを結合し、そのハッシュ値を返す
async function get_sha256(pass,salt){
    const text = pass + salt
    const uint8  = new TextEncoder().encode(text)
    const digest = await crypto.subtle.digest('SHA-256', uint8)
    var sha_text = Array.from(new Uint8Array(digest)).map(v => v.toString(16).padStart(2,'0')).join('')
    return sha_text;
}

//引数のユーザIDに該当するソルトを返す
async function get_salt(id) {
    let dir = 'get-salt';
    let url = 'http://'+host+':8080/'+dir;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({id:id}),
    });
    if (response.ok) {
        const result = await response.json();
        return result.salt;
    }else{
        return "False";
    }
}

//入力されたidとパスワードが一致した場合formを送信する
async function data_check() {
    const ERROR_MESSAGE = "ユーザIDまたはパスワードが間違っています"
    const id = document.getElementById('id').value;
    const salt = await get_salt(id);
    if(salt == "False"){
        document.getElementById('error-message').innerText = ERROR_MESSAGE;
    }else{
        const password = document.getElementById('password').value;
        let hash_password = await get_sha256(password,salt);
        let dir = 'check-user';
        let url = 'http://'+host+':8080/'+dir;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({id:id,password:hash_password}),
        });
        if (response.ok) {
            const result = await response.json();
            if(result.flag == "True"){
                document.forms['tmp-form'].submit();
            }else{
                document.getElementById('error-message').innerText = ERROR_MESSAGE;
            }
        } else {
            document.getElementById('error-message').innerText = 'エラーが発生しました';
        }
    }
}