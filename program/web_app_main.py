import sys
import os
import json
import random

# カスタムモジュールのディレクトリを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "controllers")))

from flask import Flask ,request, jsonify, render_template ,session
from controllers import ai_connector as ai
from controllers import db_connector as db

app = Flask(__name__)
app.secret_key = "**********"

#ユーザ間で共通のデータを保存する
genre_list = db.get_genre()
app.config['high_score_answer'] = db.get_result_high_score()
app.config['default_quests'],app.config['default_qid'] = db.get_quest_default()

#ログインチェックを行う
def login_check():
    if 'id' in session:
        if session['id'] != '' and session['id'] != None:
            return True
    return False

#選択できる質問のリストの中にユーザが登録した質問がある場合それをリストの中に追加する
def get_user_register_quest():
    tmp_user_quests_list, tmp_user_qid_list = db.get_quest_user(session['id'])
    tmp_quests_list = app.config['default_quests']
    tmp_qid_list = app.config['default_qid']
    for i in range(len(tmp_user_quests_list)):
        if not (tmp_user_qid_list[i] in tmp_qid_list):
            tmp_quests_list.append(tmp_user_quests_list[i])
            tmp_qid_list.append(tmp_user_qid_list[i])
    return tmp_quests_list,tmp_qid_list

#ログイン画面を表示
@app.route("/")
def root():
    return render_template('login.html')

#ログイン済みならメイン画面へ遷移にする
@app.route("/main-disp",methods=['GET', 'POST'])
def main_disp_transition():
    if login_check():
        high_score_answer_list = app.config['high_score_answer']
        high_score_answer_list_len = len(high_score_answer_list)
        return render_template('main.html',high_score_answer_list=high_score_answer_list,high_score_answer_list_len=high_score_answer_list_len)
    return render_template('login.html')

#設定画面の情報をもとに質問を抽出し、面接画面へ遷移する
@app.route("/ai-interview-setting",methods=['GET', 'POST'])
def interview():
    if login_check():
        quest_data_with_index,session['qid_list'] = get_user_register_quest()
        return render_template('interview_setting.html',quest_data=quest_data_with_index,qid_list=session['qid_list'],list_len=len(quest_data_with_index))
    return render_template('login.html')

#getメソッドで送信された場合ログイン状態をチェックし、画面を切り替える
@app.route("/ai-interview",methods=['GET'])
def return_befor_page():
    if login_check():
        quest_data_with_index,session['qid_list'] = get_user_register_quest()
        return render_template('interview_setting.html',quest_data=quest_data_with_index,qid_list=session['qid_list'],list_len=len(quest_data_with_index))
    return render_template('login.html')

#面接画面へ遷移させる
@app.route("/ai-interview",methods=['POST'])
def ai_interview_page_transition():
    if login_check():
        if 'ai-interview-setting' in request.referrer:
            toggle_switches = request.form.getlist('toggleSwitches')
            speak = False
            mic = False
            generat = False
            if "1" in toggle_switches:
                speak = True
            if "2" in toggle_switches:
                mic = True
            if "3" in toggle_switches:
                generat = True
            genre_checks = request.form.getlist('genre')
            quest_checks = request.form.getlist('quest')
            quest_num = int(request.form['quest-num'])
            id_quest_list = []
            if len(quest_checks) != 0:
                #不正に書き換えられたqidを配列から削除する
                for qid in quest_checks:
                    if not(qid in session['qid_list']):
                        quest_checks.remove(qid)
                #dbからデータを取得
                id_quest_list = db.get_id_quest(quest_checks)

            if quest_num > len(id_quest_list):
                if len(genre_checks) == 0:
                    #チェックが入っていない場合以下の3つのジャンルからランダムで出題する
                    genre_checks = ["自己紹介・基本情報","志望動機・企業分析","長所・短所"]
                genre_quest_list, qid_list = db.get_genre_quest(genre_checks)
                difference_num = quest_num - len(id_quest_list)
                for i in range(difference_num):
                    random_max_num = len(genre_quest_list) - 1
                    random_num = random.randint(0, random_max_num)
                    id_quest_list.append(genre_quest_list.pop(random_num))
                    quest_checks.append(str(qid_list.pop(random_num)))

            #取得した質問内容を格納する
            session['question'] = id_quest_list
            session['qid'] = quest_checks
            session['num'] = 1
            session['iid'] = db.get_iid(session['id'])
            return render_template('interview.html',speak=speak,mic=mic,generat=generat,quest_num=len(id_quest_list),question_text=id_quest_list[0],qid=quest_checks[0])
        
        quest_data_with_index,session['qid_list'] = get_user_register_quest()
        
        return render_template('interview_setting.html',quest_data=quest_data_with_index,qid_list=session['qid_list'],list_len=len(quest_data_with_index))
    return render_template('login.html')

#面接結果画面へ遷移させる
@app.route('/interview-result')
def transition_result():
    if login_check():
        result_list = db.get_result(session['id'],session['iid'])
        if db.get_agreement(session['id']):
            for date in result_list:
                sum_pont = date[3] + date[5] + date[7]
                tmp_result_list = []
                if sum_pont / 3 >= 85:
                    tmp_result_list.append(date[0])
                    tmp_result_list.append(date[1])
                    tmp_result_list.append(sum_pont/3)
                    app.config['high_score_answer'].append(tmp_result_list)
        return render_template('interview_result.html',result_list=result_list)
    return render_template('login.html')

#回答履歴画面へ遷移する
@app.route('/answer-history',methods=['GET', 'POST'])
def answer_history_disp():
    if login_check():
        result_list = db.get_result_all(session['id'])
        return render_template('answer_history.html',result_list=result_list)
    return render_template('login.html')

#質問登録画面へ遷移する
@app.route('/question-management',methods=['GET', 'POST'])
def question_management_disp():
    if login_check():
        return render_template('question_management.html',genre_list=genre_list)
    return render_template('login.html')

#アカウントの新規登録画面へ遷移させる
@app.route('/create-user',methods=['GET'])
def create_user_transition():
    return render_template('user_create.html')


#javascriptから要求された場合AIからの評価を生成し、次の質問を返す
@app.route('/text-upload',methods=['POST'])
def create_evaluation():
    data = request.get_json()
    #data内にtextの項目があるかを判別
    if 'answer' not in data:
        return jsonify({"error": "No text provided"}), 400
    #javascriptから送られてきたテキストを取り出す
    answer = data['answer']
    question = data['question']
    generat = data['generat']
    qid = data['qid']
    #回答から質問を生成するがTrueの場合
    question_generat = False
    if generat == "True":
        #一度だけ回答から質問を生成する
        if session['num'] % 2 == 1:
            question_generat = True
        else:
            question_generat = False
    #テキストを送りAIの評価を受け取る(ユーザの回答,質問の内容,True or False)
    evaluation_list = ai.evaluationGenerator(answer,question,question_generat)
    session['num'] += 1
    conclusion_point = evaluation_list[0]
    conclusion = evaluation_list[1]
    wording_point = evaluation_list[2]
    wording = evaluation_list[3]
    logical_point = evaluation_list[4]
    logical = evaluation_list[5]
    #ここにDB登録処理を書く
    db.result_insert(qid,session['id'],session['iid'],conclusion_point,conclusion,wording_point,wording,logical_point,logical,answer)
    if len(evaluation_list) == 7: #7の場合質問が含まれている
        next_question = evaluation_list[-1]
        next_qid = db.dynamic_generat_qtext_insert(next_question,session['id'])
    else:
        #Trueの場合面接結果画面に遷移させる
        if len(session['question']) == 1 and len(evaluation_list) == 6:
            return jsonify({"transition_flag":True})
        question_list = session['question']
        next_question = question_list.pop(1)
        qid_list = session['qid']
        next_qid = qid_list.pop(1)
    return jsonify({"question":next_question,"qid":next_qid})

#質問登録画面から送信されたデータをDBに登録する
@app.route('/question-text-upload',methods=['POST'])
def register_question_text():
    data = request.get_json()
    qtext = data['qtext']
    genre = data['genre']
    db.question_text_insert(qtext,session['id'],genre)
    return jsonify({"flag":"True"})

#アカウント登録画面から送信されたユーザデータに関する処理を行う
@app.route('/user-data-upload',methods=['POST'])
def create_user():
    data = request.get_json()
    id = data['id']
    name = data['name']
    sha_text = data['shaText']
    salt = data['salt']
    check = data['agreement']#str型でTrue or Falseが入っている
    #受け取ったユーザIDが重複していた場合Trueを返す
    if db.id_duplication_check(id):
        ERROR_TEXT = "入力されたIDは既に使用されています"
        return jsonify({"message":ERROR_TEXT})
    elif id == "" or name == "" or sha_text == "":
        ERROR_TEXT = "未入力の項目があります"
        return jsonify({"message":ERROR_TEXT})
    else:
        db.userdata_insert(id,name,sha_text,salt,check)
        return jsonify({"judge":"True"})
    
#アカウント作成に成功した場合画面を遷移させる
@app.route('/create-success',methods=['GET'])
def redirect_create_user():
    return render_template("create_user_success.html")

#受け取ったidをもとにsaltを返す(該当のidがない場合Falseの文字列を返す)
@app.route('/get-salt',methods=['POST'])
def get_salt():
    data = request.get_json()
    id = data['id']
    salt = db.get_salt(id)
    return jsonify({"salt":salt})

#ユーザIDとそれに該当するパスワードが一致するか調べる
@app.route('/check-user',methods=['POST'])
def check_user():
    data = request.get_json()
    id = data['id']
    password = data['password']
    name = db.check_user(id,password)
    if(name == None):
        return jsonify({"flag":"False"})
    else:
        session['id'] = id
        session['name'] = name
        return jsonify({"flag":"True"})


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080)