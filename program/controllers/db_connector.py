import MySQLdb

# DBに接続しカーソルを取得する
HOST = '**********'
PORT = 3306
USER = '**********'
PASSWD = '**********'
DB = '**********'

#DBのコネクションを生成し呼び出し元に返す
def create_connection():
    return MySQLdb.connect(host=HOST, port=PORT, user=USER, passwd=PASSWD, db=DB)

#コネクションを管理するクラス
class Database:
    def __init__(self):
        self.conn = create_connection()

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()

#引数のidが重複しているかを調べる
def id_duplication_check(id):
    query = "SELECT uid FROM users WHERE uid = %s;"
    with create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (id,))
            rows = cursor.fetchall()
    if rows:
        return True
    else:
        return False

#ユーザのデータを新規登録する
#第一引数：ユーザid,第二引数：ユーザ名,第三引数：パスワード,第四引数：ソルト,第五引数：回答を公開する場合True 戻り値なし
def userdata_insert(id, name, password, salt, agreement):
    flag = 1 if agreement == "True" else 0
    query = "INSERT INTO users VALUES (%s, %s, %s, %s, %s);"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (id, name, password, flag, salt))
        conn.commit()

#saltを取得する
#第一引数：ユーザid 戻り値は該当するユーザidのソルトを返す
def get_salt(id):
    query = "SELECT salt FROM users WHERE uid = %s;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (id,))
            row = cursor.fetchone()
    return row[0] if row else "False"

#idとパスワードが一致しているか確認
#第一引数：ユーザid,第二引数：パスワード 戻り値はidとパスワードが一致する場合ユーザ名を返し一致しない場Noneを返す
def check_user(id, password):
    query = "SELECT uname FROM users WHERE uid = %s AND pass = %s;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (id, password))
            row = cursor.fetchone()
    if row:
        return row[0]
    return None

#登録済みの質問を取得(ユーザが登録したものは除く) 引数：なし
def get_quest_default():
    query = "SELECT qtext,qid FROM quests WHERE uid is null and dqtext is null;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchall()
    id_list = []
    quest_list = []
    for data in row:
        quest_list.append(str(data[0]))
        id_list.append(str(data[1]))
    return quest_list,id_list

#該当ユーザが登録した質問をすべて取得 第一引数：ユーザid
def get_quest_user(id):
    query = "SELECT qtext,qid FROM quests WHERE uid = %s and dqtext is null;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (id,))
            row = cursor.fetchall()
    id_list = []
    quest_list = []
    for data in row:
        quest_list.append(str(data[0]))
        id_list.append(str(data[1]))
    return quest_list,id_list

#引数で渡されたlistに含まれるqidのqtextを取得
def get_id_quest(id_list):
    query = "SELECT qtext FROM quests WHERE qid IN %s and dqtext is null;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (tuple(id_list),))
            row = cursor.fetchall()
    quest_list = []
    for data in row:
        quest_list.append(data[0])
    return quest_list

#引数で渡されたlistに含まれるgenreのqtextを取得(qtextが入った配列とqidが入った配列を返す)
def get_genre_quest(genre_list):
    query = "SELECT qtext,qid FROM quests WHERE dqtext is null and genre IN %s;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (tuple(genre_list),))
            row = cursor.fetchall()
    quest_list = []
    qid_list = []
    for data in row:
        quest_list.append(data[0])
        qid_list.append(data[1])
    return quest_list,qid_list

#引数で受け取ったユーザidがもつiidの最大値プラス1を返す
def get_iid(id):
    query = "SELECT max(iid) FROM historys WHERE uid = %s;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (id,))
            row = cursor.fetchall()
    iid = row[0][0]
    if iid:
        return int(iid) + 1
    else:
        return 1

#面接の結果を受け取る 第一引数：ユーザid,第二引数：面接ごとのid
def get_result(uid,iid):
    query = "SELECT q.qtext,answer,conclusion,value1,wording,value2,logical,value3 FROM historys h inner join quests q on h.qid = q.qid WHERE h.uid = %s and iid = %s;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (uid,iid))
            row = cursor.fetchall()
    tmp_list = []
    result_list = []
    for data in row:
        for i in range(8):
            tmp_list.append(data[i])
        result_list.append(tmp_list)
        tmp_list = []
    return result_list

#引数で受け取ったユーザidの面接履歴を受け取る
def get_result_all(uid):
    query = "SELECT q.qtext,answer,conclusion,value1,wording,value2,logical,value3 FROM historys h inner join quests q on h.qid = q.qid WHERE h.uid = %s;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (uid,))
            row = cursor.fetchall()
    tmp_list = []
    result_list = []
    for data in row:
        for i in range(8):
            tmp_list.append(data[i])
        result_list.append(tmp_list)
        tmp_list = []
    return result_list

#平均評価点が85点を超えている回答を取得する(回答の公開に同意しているユーザの回答のみ) 引数なし
def get_result_high_score():
    query = "SELECT q.qtext,answer,value1,value2,value3 FROM historys h inner join quests q on h.qid = q.qid inner join users u on h.uid = u.uid WHERE u.agree;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchall()
    tmp_list = []
    result_list = []
    for data in row:
        for i in range(5):
            tmp_list.append(data[i])
        sum_point = tmp_list.pop(2) + tmp_list.pop(2) + tmp_list.pop(2)
        if sum_point / 3 >= 85:
            tmp_list.append(sum_point / 3)
            result_list.append(tmp_list)
        tmp_list = []
    return result_list

#ユーザが85点以上の回答の公開に同意している場合Trueを返す 第一引数：ユーザid
def get_agreement(uid):
    query = "SELECT agree FROM users where uid = %s;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (uid,))
            row = cursor.fetchall()
    if row[0][0] == 1:
        return True
    else:
        return False
    
#引数で受け取った結果をDBに保存する
#引数(質問id,ユーザid,面接id,結論第一,点数,正しい言葉遣いか,点数,論理的か,点数,ユーザの回答)
def result_insert(qid,uid,iid,conclusion_point,conclusion,wording_point,wording,logical_point,logical,answer):
    query = "INSERT INTO historys VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (qid,uid,iid,conclusion,conclusion_point,wording,wording_point,logical,logical_point,answer))
        conn.commit()

#AI生成された質問を登録し、登録したqidを返す
#引数(質問内容,ユーザid)
def dynamic_generat_qtext_insert(qtext,uid):
    query = "INSERT INTO quests (qtext, uid, dqtext) VALUES (%s, %s, 1);"
    query2 = "select max(qid) from quests where dqtext = 1 and uid = %s;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (qtext,uid))
        conn.commit()
        with conn.cursor() as cursor:
            cursor.execute(query2, (uid,))
            row = cursor.fetchall()
    return row[0][0]

#すべてのジャンルを取得する
def get_genre():
    query2 = "select distinct(genre) from quests where not genre is null;"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query2)
            row = cursor.fetchall()
    tmp_list = []
    for data in row:
        tmp_list.append(data[0])
    return tmp_list

#ユーザごとの質問を登録
#引数(質問内容,ユーザid,ジャンル)
def question_text_insert(qtext, uid, genre):
    query = "INSERT INTO quests (qtext, uid, genre) VALUES (%s, %s, %s);"
    with Database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (qtext,uid,genre))
        conn.commit()