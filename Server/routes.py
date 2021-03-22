import socket
from flask import Flask, jsonify, request
import threading
import time
from werkzeug.serving import make_server
import sqlite3, json
from datetime import date
import sys
import traceback
app = Flask(__name__)
IP = socket.gethostbyname(socket.gethostname())
print(IP)
app.host = IP
app.port = 5000

def printf(args):
    original_stdout = sys.stdout # Save a reference to the original standard output

    with open('LogFile.txt', 'w') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print(args)
    sys.stdout = original_stdout
@app.route('/', methods=['GET'])
def home():
    return 'Your flask app is working correctly'


@app.route('/check', methods=['GET'])
def check():
    re = {'Alive': True}
    return jsonify(re)


@app.route('/new_user', methods=['POST'])
def new_user():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = 'INSERT INTO users (id, name, password) VALUES (NULL,{},{})'.format(data['name'], data['password'])
    try:
        print(query)
        try:
            cursor.execute('select id from users where name="{}"')
            exist = cursor.fetchone()
        except Exception as e:
            exist = False
        if exist is None or exist == False:
            cursor.execute('INSERT INTO users VALUES (NULL,?,?,?,?,?)', (data['name'], data['password'], 1000, 0, 0))
            conn.commit()
            re = {'Success': True}
            return jsonify(re)
        else:
            print(exist)
            re = {'Success': False}
            conn.close()
            return jsonify(re)
    except Exception as e:
        print(e)
        printf(e)
        printf('Problem at server on line 32')
    conn.close()
    re = {'Success': False}
    return jsonify(re)


@app.route('/exact_user', methods=['POST'])
def api_user():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = 'SELECT * FROM users WHERE name="{}" and password="{}"'.format(data['username'], data['password'])
    try:
        print(query)
        cursor.execute(query)
        user = cursor.fetchone()
        print(user)
    except Exception as e:
        print(e)
        printf(e)
        user = False
        printf('Server issue at line 51')
    conn.close()
    if user:
        res = {'is_it_correct': True, 'data': user}
        return jsonify(res)
    else:
        res = {'is_it_correct': False}
    return jsonify(res)


@app.route('/get/user/num/company', methods=['POST'])
def get_user_comp():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = """select count(*) from companies join users on companies.company_owner_id = users.id where users.name='{}';""".format(
        data['username'])
    cursor.execute(query)
    grab = cursor.fetchone()
    re = {'number': grab[0]}
    print(re)
    conn.close()
    return jsonify(re)


@app.route('/get/user/num/investor', methods=['POST'])
def get_user_inves():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = """select count(*) from investors join users on investors.investor_id=users.id where users.name='{}';""".format(
        data['username'])
    cursor.execute(query)
    num = cursor.fetchone()
    re = {'number': num[0]}
    print(re)
    conn.close()
    return jsonify(re)


@app.route('/get/user/investor', methods=['POST'])
def get_user_investment():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = """select company_name from investors join users on investors.investor_id=users.id join companies on 
            investors.company_id = companies.id where name='{}';""".format(data['username'])
    cursor.execute(query)
    names = cursor.fetchall()
    re = {'companies_names': names}
    print(re)
    conn.close()
    return jsonify(re)


@app.route('/get/user/own_comp', methods=["POST"])
def user_owned_comp():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = """select company_name from companies join users on companies.company_owner_id=users.id where name='{}';""".format(
        data['username'])
    cursor.execute(query)
    comp_names = cursor.fetchall()
    conn.close()
    re = {'companies_name': comp_names}
    print(re)
    return jsonify(re)


@app.route('/get/all_comp', methods=['GET'])
def all_existing_comp():
    query = """select * from companies join users on companies.company_owner_id=users.id;"""
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    cursor.execute(query)
    companies = cursor.fetchall()
    re = {'Companies': companies}
    print(re)
    conn.close()
    return jsonify(re)


@app.route('/get/comp_detail', methods=['POST'])
def api_store():
    data = json.loads(request.data.decode())
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = 'select * from companies where id="{}";'.format(data['id'])
    try:
        print(query)
        cursor.execute(query)
        store = cursor.fetchone()
    except Exception as e:
        print(e)
        printf(e)
        printf('There was a issue with server line 173')
        store = False
    conn.close()
    if store:
        return jsonify(store)
    else:
        return jsonify(store)


@app.route('/get/comp/investors', methods=['POST'])
def comp_ivestors():
    data = json.loads(request.data.decode())
    query = """select company_name from companies where id='{}'""".format(data['id'])
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    cursor.execute(query)
    name = cursor.fetchone()[0]
    query = """select name from investors 
        join users on investors.investor_id = users.id
        join companies on investors.company_id = companies.id where company_name='{}';""".format(name)
    cursor.execute(query)
    investors = cursor.fetchall()
    conn.close()
    re = {'IN': investors}
    return jsonify(re)


@app.route('/get/comp/investors/percents', methods=['POST'])
def comp_investors_percents():
    data = json.loads(request.data.decode())
    query = """select company_name from companies where id='{}'""".format(data['id'])
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    cursor.execute(query)
    name = cursor.fetchone()[0]
    query = """select percent from investors 
        join users on investors.investor_id = users.id
        join companies on investors.company_id = companies.id where company_name='{}'
        and company_owner_id != users.id;""".format(name)
    cursor.execute(query)
    percent = 0
    p = cursor.fetchall()
    print(p)
    for pe in p:
        print(pe)
        percent += pe[0]
        if percent >= 100:
            re = {'Can_You_invest': False}
            return jsonify(re)
    re = {'Can_You_invest': True, 'Percent_left_to_invest_in': 100 - percent}
    return jsonify(re)


@app.route('/get/comp/investnow', methods=["POST"])
def invest_in_comp_now():
    try:
        data = json.loads(request.data.decode())
        query = """select user_money from users where id={};""".format(data['user_id'])
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        user_money = cursor.fetchone()[0]
        conn.close()
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        if user_money >= data['money']:
            try:
                conn= sqlite3.connect('server.db')
                cursor = conn.cursor()
                print(data['comp_id'])
                query = """select company_owner_id from companies where id={};""".format(data['comp_id'])
                cursor.execute(query)
                owner_id = cursor.fetchone()[0]
                # User 2 is the owner id, or in other words the id of the person he/she is tryin to send the request to.
                query = """insert into comp_transactions (user1_id, user2_id, money, comp, percent) values
                ({},{},{}, {},{});""".format(data['user_id'], owner_id, data['money'], data['comp_id'], data['percent'])
                cursor.execute(query)
                conn.commit()
                conn.close()
                re = {'Success': True}
                return jsonify(re)
            except Exception as e:
                print(e)
                print('error with server line 257 file routes')
        else:
            re = {'Success': False, 'issue': 'not enough money'}
            return jsonify(re)
    except Exception as e:
        print(e)
        printf(e)
        printf('There was a issue with server line 269')
    re = {'Success': False, 'issue': 'error'}
    return jsonify(re)

@app.route('/createusercomp', methods=['POST'])
def user_Comp_create():
    try:
        data = json.loads(request.data.decode())
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        today = date.today()
        # dd/mm/YY
        d1 = today.strftime("%d/%m/%Y")
        print("Data company was created", d1)
        query = """
            insert into companies ( company_name, company_owner_id,
            company_cost, company_gain, date_company_created,
            company_money, company_worth) values ("{}",
            {}, {}, {}, "{}", {}, {})
        """.format(data['comp_name'], data['owner_id'], 0, 0, d1, data['amount'],
        0)
        print(query) 
        cursor.execute(query)
        query = """select id from companies where date_company_created ="{}" 
        and company_owner_id={};""".format(d1, data['owner_id'])
        print(query)
        cursor.execute(query)
        ids = cursor.fetchone()[0]    
        query = """
            insert into investors (investor_id, company_id, percent, intial_payed) 
            values ({}, {}, 100, {})
        """.format(data['owner_id'], ids, data['amount'])
        print(query)
        cursor.execute(query)
        query= """
            update users set user_money= user_money-{} where id ={};
        """.format(data['amount'], data['owner_id'])
        print(query) 
        cursor.execute(query)
        conn.commit()
        re = {'Success': True}
        return jsonify(re)
    except Exception as e:
        print(e, repr(e))
        printf(e.__str__())
        printf("Problem with server line 318 file routes")
        re = {"Success": False}
        return jsonify(re)
@app.route('/UserRanksArrange', methods=['POST'])
def user_rank_arrange():
    data = json.loads(request.data.decode())
    conn =  sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = """select user_money, id, name from users order by user_money desc;"""
    cursor.execute(query)
    order = cursor.fetchall()  
    print("Go through for loop after line 329")
    user_rank = 0
    money = 0
    for i in order:
        print('User id', i[1])
        if data['id'] == i[1]:
            money = i[0]
            break
        print(order)
        user_rank += 1
    rank_system = {'User_INFOR': {'Rank': user_rank, 'Money': money}, 'Rank_': order}
    print("Rank System", rank_system)
    return jsonify(rank_system)
@app.route('/get/all/users', methods=['GET']) 
def get_all_users():
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    query = """select id, name from users;"""
    cursor.execute(query)
    all_users = cursor.fetchall()
    print(all_users)
    return jsonify(all_users)
@app.route('/get/certain/user/chat', methods=['POST']) 
def get_certain_user_chat():
    data = json.loads(request.data.decode())
    query="""select from_user, to_user, message, date_sent from chat where from_user={} and to_user={} or from_user={} and to_user={};
    """.format(data['chat_id'], data['user_id'], data['user_id'], data['chat_id'])
    print(query)  
    conn= sqlite3.connect('server.db')
    cursor = conn.cursor()
    cursor.execute(query)
    chats = cursor.fetchall()
    print(chats) 
    return jsonify(chats)
@app.route('/send/message/to/user', methods=['POST'])
def send_message_to_user():
    try:
        data = json.loads(request.data.decode())
        today = date.today()
            # dd/mm/YY
        d1 = today.strftime("%d/%m/%Y")
        query="""insert into chat (from_user, to_user, message, date_sent) VALUES ({}, {}, "{}", "{}");""".format(
            data['from_user'], data['to_user'], data['message'], d1
        )
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor() 
        cursor.execute(query)
        conn.commit()
        re = {'Success': True}
    except Exception as e:
        print(e) 
        print('Problem with server line 381 file routes')
        re = {'Success': False}
    return jsonify(re)
@app.route('/send/user/transaction', methods=['POST'])
# Sends transcation
def send_transaction_to_user():
    try:
        data = json.loads(request.data.decode())
        print('User id', data['user_id'])
        query = """select name, money, percent, company_name, comp_transactions.id from comp_transactions join companies on
        comp=companies.id join users on user1_id = users.id where user2_id={};""".format(data['user_id'])
        print(query)
        conn= sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        tran = cursor.fetchall()
        print('transcations', tran)
        re = {'Success': True, 'Transcations': tran}
        return jsonify(re)
    except Exception as e:
        print(e)
        print('Error at server line 392')
        re = {'Success': False}
        return jsonify(re)
@app.route('/denied/user/transaction', methods=['POST'])
def deny_trans():
    try:
        data = json.loads(request.data.decode())
        query = """delete from comp_transactions where id={};""".format(data['row'])
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return jsonify({'Complete': True})
    except Exception as e:
        print(e)
        print("Error at server line 403")
        return jsonify({'Complete': False})
@app.route('/accept/user/transaction', methods=['POST'])
def accept_trans():
    try:
        data = json.loads(request.data.decode())
        query="""select * from comp_transactions where id={};""".format(data['row'])
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchone()
        print('rows', rows)
        query = """update users set user_money = user_money-{} where id={}""".format(rows[3],rows[1])
        print(query)
        cursor.execute(query)
        conn.commit()
        conn = sqlite3.connect('server.db')
        cursor=  conn.cursor()
        query = """update investors set percent = percent- {} where investor_id={} and company_id={}""".format(rows[5], rows[2], rows[4])
        cursor.execute(query)
        conn.commit()
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        query="""insert into investors (investor_id, company_id, percent, intial_payed) 
            values ({}, {}, {}, {})""".format(rows[1], rows[4], rows[5], rows[3])
        cursor.execute(query)
        conn.commit()
        conn = sqlite3.connect('server.db')
        cursor = conn.cursor()
        query = """delete from comp_transactions where id={};""".format(data['row'])
        cursor.execute(query)
        conn.commit()
        return jsonify({'Complete': True})
    except Exception as e:
        print(e)
        print("Error at server line 415")
        return jsonify({'Complete': False})
class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.srv = make_server(IP, 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        print('starting server')
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def start_server():
    global servers
    servers = ServerThread(app)
    servers.start()
    print('server started')


def stop_server():
    global servers
    servers.shutdown()
