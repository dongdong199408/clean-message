from word_clean import ac_automation
import pickle
import re
import os
import json
import random
from queue import Queue
import threading
import time
from flask import Flask, abort, request, jsonify, g, url_for,Response
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
#导入分类主函数
from run_classifier import BertClassifier
import tensorflow as tf
import watchgod
import pre_data as pre
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'miaoxudong'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config.update(
    DEBUG=True)
# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
# 进入api前端调试界面
class Predict:
    def __init__(self,path='./data/CensorWords.txt'):
        self.path=path
        self.model_path='./tmp'
        self.model_file=os.path.join(self.model_path,'^model.ckpt.*')
        self.ah=ac_automation()
        self.ah.parse(self.path)
        # 多线程释放
        self.lock = threading.RLock()
        # 导入训练的model，predict
        self.classifier = BertClassifier()
        #进入预测模式
        self.classifier.set_mode(tf.estimator.ModeKeys.PREDICT)

    #去除敏感性词汇
    def clean_data(self,sentence):
        sentence_cleaned=self.ah.words_replace(sentence)
        return sentence_cleaned

    def predict(self,sentence):
        with self.lock:
            return self.classifier.predict_one(sentence)

    def watch_updates(self):
        def worker():
            print("monitoring:", self.model_path)
            for changes in watchgod.watch(self.model_path):
                for _, file in changes:
                    print(file, "changed")
                    if re.compile(str(self.model_file),str(file)):
                        classifier = BertClassifier()
                        classifier.set_mode(tf.estimator.ModeKeys.PREDICT)
                        print("reload model")
                        with self.lock:
                            self.classifier = classifier
        thread = threading.Thread(target=worker,daemon=True)#主程序结束，不再继续
        thread.start()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


# 基于简单密码的认证
@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# 用户注册
@app.route('/clean_message/users', methods=['POST','GET'])
def new_user():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
    else:
        username = request.args.get('username')
        password = request.args.get('password')

    if username is None or password is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)  # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/clean_message/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/clean_message/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/clean_message/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/clean_message', methods=['POST', 'GET'])
#@auth.login_required
def clean_sentence():
    try:
        if request.method == 'POST':
            # sentence1 = request.form['message']
            g_data = request.get_data()
            question = json.loads(g_data).get('message')
        elif request.method == 'GET':
            question = request.args.get('message')
        else:
            question = ''
    except Exception as e:
        print(e)

    if question =='':
        abort(401) #超时，或者未获取到参数
    if question==None:
        abort(400) #参数错误

    #首先自定义无意义的数字
    if not re.compile(u'[\u4e00-\u9fa5]|[a-zA-Z0-9]+').search(question):
        print('无汉语或者无英语语言')
        probability=0.0
        is_effective = True if probability > 0.45 else False
        result = {'code': 1, 'result': {'probability': str(probability), 'is_effective': is_effective}}
        return jsonify(result)
    elif len(re.findall('\[', question)) > 4 and len(re.findall('\]', question)) > 4 or len(
            re.findall('[a-zA-Z]', question)) > 8:
        print('表情字符和英文过多！')
        probability = 0.0
        is_effective = True if probability > 0.45 else False
        result = {'code': 1, 'result': {'probability': str(probability), 'is_effective': is_effective}}
        return jsonify(result)
    #定义又意义的字段
    elif re.compile(pre.need_message).match(question):
        print('有效字段！')
        probability = 1.0
        is_effective = True if probability > 0.45 else False
        result = {'code': 1, 'result': {'probability': str(probability), 'is_effective': is_effective}}
        return jsonify(result)
    else:
        pass #转入下轮
    sentence = question.strip()
    clean = P.clean_data(sentence)
    if clean == sentence:
        probability=P.predict(clean)[0][1]
    else :
        probability = 0 #敏感词汇，筛除
    is_effective = True if probability > 0.45 else False

    result = {'code': 0, 'result': {'probability': str(probability), 'is_effective': is_effective}}
    return jsonify(result)

if __name__ == '__main__':
    if not os.path.exists('db.sqlite1'):
        db.create_all()
    P = Predict()
    P.watch_updates()
    app.run(host='0.0.0.0', port=5000, debug=True)

