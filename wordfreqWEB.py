#! /usr/bin/python3
# -*- coding: utf-8 -*-

from WordFreq import WordFreq
from wordfreqCMD import youdao_link, sort_in_descending_order
from UseSqlite import InsertQuery, RecordQuery
import pickle_idea
import os
import random, glob
from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for, session, abort, flash


app = Flask(__name__)

#path_prefix = '/var/www/wordfreq/wordfreq/'
path_prefix = './' # for deployment

def get_random_image(path):
    img_path = random.choice(glob.glob(os.path.join(path, '*.jpg')))
    return img_path[img_path.rfind('/static'):]
    
def load_freq_history(path):
    d = {}
    if os.path.exists(path):
        d = pickle_idea.load_record(path)
    return d

def verify_user(username, password):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT * FROM user WHERE name='%s' AND password='%s'" % (username, password))
    rq.do()
    result = rq.format_results()
    return result.strip() != ''

def add_user(username, password):
    start_date = datetime.now().strftime('%Y%m%d')
    expiry_date = start_date
    rq = InsertQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("INSERT INTO user Values ('%s', '%s', '%s', '%s')" % (username, password, start_date, expiry_date))
    rq.do()

    
def check_username_availability(username):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT * FROM user WHERE name='%s'" % (username))
    rq.do()
    result = rq.format_results()
    return  result.strip() == ''

def get_expiry_date(username):
    rq = RecordQuery(path_prefix + 'static/wordfreqapp.db')
    rq.instructions("SELECT expiry_date FROM user WHERE name='%s'" % (username))
    rq.do()
    result = rq.format_results()
    return  result.strip()

def get_today_article():
    f = open(path_prefix + 'static/today.txt')
    s = f.read()
    f.close()
    s = s.replace('\n', '<br/>')
    return s

@app.route("/mark", methods=['GET', 'POST'])
def mark_word():
    if request.method == 'POST':
        d = load_freq_history(path_prefix + 'static/frequency.p')
        lst_history = pickle_idea.dict2lst(d)
        lst = []
        for word in request.form.getlist('marked'):
            lst.append((word, 1))
        d = pickle_idea.merge_frequency(lst, lst_history)
        pickle_idea.save_frequency_to_pickle(d, path_prefix + 'static/frequency.p')
        return redirect(url_for('mainpage'))
    else:
        return 'Under construction'



@app.route("/", methods=['GET', 'POST'])
def mainpage():
    if request.method == 'POST':  # when we submit a form
        content = request.form['content']
        f = WordFreq(content)
        lst = f.get_freq()
        page = '<form method="post" action="/mark">\n'
        count = 1
        for x in lst:
            page += '<p><font color="grey">%d</font>: <a href="%s">%s</a> (%d)  <input type="checkbox" name="marked" value="%s"></p>\n' % (count, youdao_link(x[0]), x[0], x[1], x[0])
            count += 1
        page += ' <input type="submit" value="确定并返回"/>\n'
        page += '</form>\n'
        # save history 
        d = load_freq_history(path_prefix + 'static/frequency.p')
        lst_history = pickle_idea.dict2lst(d)
        d = pickle_idea.merge_frequency(lst, lst_history)
        pickle_idea.save_frequency_to_pickle(d, path_prefix + 'static/frequency.p')
        
        return page
    elif request.method == 'GET': # when we load a html page
        page = '<p><b><font color="red">English Pal - Make you better</font></b>'
        if session.get('logged_in'):
            page += ' <a href="%s">%s</a></p>\n' % (session['username'], session['username'])
        else:
            page += ' <a href="/login">我有账号</a>  <a href="/signup">我没有账号</a></p>\n'
        page += '<p><img src="%s" width="400px" alt="advertisement"/></p>' % (get_random_image(path_prefix + 'static/img/'))
        page += '<form method="post" action="/">'
        page += ' <textarea name="content" rows="20" cols="80"></textarea><br/>'
        page += ' <input type="submit" value="统计"/>'
        page += ' <input type="reset" value="清除"/>'
        page += '</form>'
        d = load_freq_history(path_prefix + 'static/frequency.p')
        if len(d) > 0:
            page += '<p><b>常见词</b></p>'
            for x in sort_in_descending_order(pickle_idea.dict2lst(d)):
                if x[1] <= 99:
                    break
                page += '<a href="%s">%s</a> %d\n' % (youdao_link(x[0]), x[0], x[1])
                
        return page


@app.route("/<username>/mark", methods=['GET', 'POST'])
def user_mark_word(username):
    username = session[username]
    user_freq_record = path_prefix + 'static/' +  'frequency_%s.pickle' % (username)
    if request.method == 'POST':
        d = load_freq_history(user_freq_record)
        lst_history = pickle_idea.dict2lst(d)
        lst = []
        for word in request.form.getlist('marked'):
            lst.append((word, 1))
        d = pickle_idea.merge_frequency(lst, lst_history)
        pickle_idea.save_frequency_to_pickle(d, user_freq_record)
        return redirect(url_for('userpage', username=username))
    else:
        return 'Under construction'



@app.route("/<username>", methods=['GET', 'POST'])
def userpage(username):
    user_expiry_date = get_expiry_date(username)
    print(user_expiry_date)
    
    if not session.get('logged_in'):
        return '<p>请先<a href="/login">登录</a>。</p>'
    
    if datetime.now().strftime('%Y%m%d') > user_expiry_date:
        return '<p>账号 %s 过期。</p><p>扫描下面支付宝二维码支付。每年36元。我们会于12小时内激活账号。</p><p><img src="static/donate-the-author.jpg" width="120px" alt="支付宝二维码" /></p><p>开发者微信 torontohui</p>' % (username)

    username = session[username]
    user_freq_record = path_prefix + 'static/' +  'frequency_%s.pickle' % (username)
    
    if request.method == 'POST':  # when we submit a form
        content = request.form['content']
        f = WordFreq(content)
        lst = f.get_freq()
        page = '<form method="post" action="/%s/mark">\n' % (username)
        count = 1
        for x in lst:
            page += '<p><font color="grey">%d</font>: <a href="%s">%s</a> (%d)  <input type="checkbox" name="marked" value="%s"></p>\n' % (count, youdao_link(x[0]), x[0], x[1], x[0])
            count += 1
        page += ' <input type="submit" value="确定并返回"/>\n'
        page += '</form>\n'
        # save history 
        # d = load_freq_history(user_freq_record)
        # lst_history = pickle_idea.dict2lst(d)
        # d = pickle_idea.merge_frequency(lst, lst_history)
        # pickle_idea.save_frequency_to_pickle(d, user_freq_record)
        return page
    
    elif request.method == 'GET': # when we load a html page
        page = '<meta charset="UTF8">'
        page += '<p><b>English Pal for <font color="red">%s</font></b> <a href="/logout">登出</a></p>' % (username)
        page += '<form method="post" action="/%s">' % (username)
        page += ' <textarea name="content" rows="20" cols="80"></textarea><br/>'
        page += ' <input type="submit" value="统计"/>'
        page += ' <input type="reset" value="清除"/>'
        page += '</form>\n'
        page += '<p><b>阅读以下文章并回答问题</b></p>\n'
        page += '%s'  % (get_today_article())
        d = load_freq_history(user_freq_record)
        if len(d) > 0:
            page += '<p><b>加强词</b></p>'
            for x in sort_in_descending_order(pickle_idea.dict2lst(d)):
                page += '<a href="%s">%s</a> %d\n' % (youdao_link(x[0]), x[0], x[1])
                
        return page

### Sign-up, login, logout ###
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        available = check_username_availability(username)
        if not available:
            flash('用户名 %s 已经被注册。' % (username))
            return render_template('signup.html')
        elif len(password.strip()) < 4:
            return '密码过于简单。'
        else:
            add_user(username, password)
            verified = verify_user(username, password)
            if verified:
                session['logged_in'] = True
                session[username] = username
                session['username'] = username
                return '<p>恭喜，你已成功注册， 你的用户名是 %s。</p><p>请扫描下面支付宝二维码支付。每年36元。未及时支付的账号，12小时后停用。</p> \
        <p><img src="static/donate-the-author.jpg" width="120px" alt="支付宝二维码" /></p> \
        <p><a href="/%s">开始使用</a> <a href="/">返回首页</a><p/>' % (username, username)
            else:
                return '用户名密码验证失败。'


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if not session.get('logged_in'):
            return render_template('login.html')
        else:
            return '你已登录 <a href="/%s">%s</a>。 登出点击<a href="/logout">这里</a>。' % (session['username'], session['username'])
    elif request.method == 'POST':
        # check database and verify user
        username = request.form['username']
        password = request.form['password']
        verified = verify_user(username, password)
        if verified:
            session['logged_in'] = True
            session[username] = username
            session['username'] = username
            return redirect(url_for('userpage', username=username))
        else:
            return '无法通过验证。'


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('mainpage'))


if __name__ == '__main__':
    app.secret_key = os.urandom(16)
    #app.run(debug=False, port='6000')
    app.run(debug=True)
