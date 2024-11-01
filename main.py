# SNSでの投稿にAIによるポジティブ判定とポイントシェア機能を実装するコードの一部

from datetime import datetime, timedelta
import random
import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

class User:
    def __init__(self, username):
        self.username = username
        self.points = 100  # アカウント作成時の初期ポイント
        self.posts = []
        self.likes = []

    def create_post(self, content):
        post = Post(self, content)
        self.posts.append(post)
        return post

    def like_post(self, post):
        post.add_like(self)
        self.points += 0.1  # "いいね"によるユーザーへの少量ポイント

class Post:
    def __init__(self, author, content):
        self.author = author
        self.content = content
        self.likes = []
        self.timestamp = datetime.now()
        self.ai_positive_score = self.evaluate_content()

    def evaluate_content(self):
        # AIによるポジティブな投稿の判定（シンプルなランダム値を使用した例）
        return random.uniform(0, 1)  # 0から1の間のスコアを生成し、ポジティブ度を表す

    def is_positive(self):
        return self.ai_positive_score > 0.5  # 0.5以上ならポジティブと判断

    def add_like(self, user):
        self.likes.append(user)
        self.author.points += 0.5  # 投稿者に"いいね"ポイントが加算される

# ユーザー管理
users = {}
posts = []

@app.route('/create_user', methods=['POST'])
def create_user():
    username = request.json.get('username')
    if username in users:
        return jsonify({"error": "User already exists"}), 400
    users[username] = User(username)
    return jsonify({"message": f"User {username} created successfully"}), 201

@app.route('/create_post', methods=['POST'])
def create_post():
    username = request.json.get('username')
    content = request.json.get('content')
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    user = users[username]
    post = user.create_post(content)
    posts.append(post)
    if post.is_positive():
        user.points += 10  # ポジティブな投稿に対するボーナスポイント
    return jsonify({"message": f"Post created by {username}", "points": user.points}), 201

@app.route('/like_post', methods=['POST'])
def like_post():
    username = request.json.get('username')
    post_index = request.json.get('post_index')
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    if post_index < 0 or post_index >= len(posts):
        return jsonify({"error": "Post not found"}), 404
    user = users[username]
    post = posts[post_index]
    user.like_post(post)
    return jsonify({"message": f"{username} liked a post by {post.author.username}", "user_points": user.points, "author_points": post.author.points}), 200

@app.route('/get_user_points', methods=['GET'])
def get_user_points():
    username = request.args.get('username')
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    user = users[username]
    return jsonify({"username": user.username, "points": user.points}), 200

if __name__ == '__main__':
    app.run()
