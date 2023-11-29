import ZODB, ZODB.FileStorage
import zc.lockfile
from BTrees._OOBTree import BTree
import transaction
import uuid
from models import User, Challenge, Post, Comment

import os
import json

class UserManager:
    def __init__(self, root):
        self.root = root
        self.users = root["users"]
    
    def create_user(self, email, name, password_hash):
        user_uuid = str(uuid.uuid3(uuid.NAMESPACE_URL, email.lower()))
        user = User(user_uuid, email=email.lower(), name=name, password_hash=password_hash)
        self.users[user_uuid] = user
    
    def get_user_from_email(self, email):
        return self.users.get(str(uuid.uuid3(uuid.NAMESPACE_URL, email)), None)
    
    def get_user_from_uuid(self, uuid):
        return self.users.get(uuid, None)
    
class ChallengeManager:
    def __init__(self, root):
        self.root = root
        self.challenges = root["challenges"]
        
    def get_challenges_with_difficulty(self, difficulty):
        result = []
        for challenge_id in self.challenges:
            challenge = self.challenges[challenge_id]
            if difficulty - 1 < challenge.difficulty < difficulty:
                result.append(challenge)
        return result

    def get_challenge_from_id(self, id, details=None):
        if id in self.challenges:
            return self.challenges[id].get_details(details)
        
    def get_score(self, difficulty: float):
        # score: 0 - 2000 based on difficulty (0-5)
        return round((difficulty/5)*(2000), -2)
        
class PostManager:
    POSTS_PER_PAGE = 10

    def __init__(self, root):
        self.root = root
        self.posts = root["posts"]

    def create_post(self, title, content, author_uuid):
        post_id = str(uuid.uuid4())
        post = Post(post_id, title=title, content=content, author_uuid=author_uuid)
        self.posts[post_id] = post
    
        return post
    
    def add_comment(self, post_id, author_uuid, comment_body):
        post = self.get_post(post_id)    

        comment_id = str(uuid.uuid4())
        comment = Comment(comment_id, post_id, author_uuid, comment_body)

        post.add_comment(comment)
        
        return comment
    
    def delete_comment(self, post_id, comment_id):
        self.get_post(post_id).delete_comment(comment_id)
        
    def get_post(self, post_id):
        return self.posts.get(post_id, None)

    def get_all_posts(self):
        return self.posts.values()

    def get_sorted_posts(self, sort_by, posts=None):
        if posts is None:
            posts = self.get_all_posts()
        if sort_by == "top":
            return sorted(posts, key=lambda post: len(post.comments), reverse=True)
        elif sort_by == "recent":
            return sorted(posts, key=lambda post: post.created_at, reverse=True)
        elif sort_by == "old":
            return sorted(posts, key=lambda post: post.created_at)
        else:
            return posts

    def get_searched_posts(self, search):
        result = []
        for post in self.posts.values():
            if search.lower() in post.title.lower():
                result.append(post)
        return result
    
    def get_page(self, page_num, sort_by, search):
        # https://pythonhosted.org/BTrees/
        start = (page_num-1) * PostManager.POSTS_PER_PAGE
        end = start + PostManager.POSTS_PER_PAGE
        
        posts = self.get_all_posts()
        
        if search is not None:
            posts = self.get_searched_posts(search)
        
        sorted_posts = self.get_sorted_posts(sort_by, posts)
        return sorted_posts[start:end]
    
    def get_comment_by_id(self, post_id, comment_id):
        return self.posts[post_id].get_comment(comment_id)
    
def save():
    print("SAVED")
    transaction.commit()

def load_challenges(root):
    filename = "challenges.json"
    
    with open(filename) as f:
        data = json.load(f)
    challenges = root["challenges"]

    for challenge in data:        
        challenges[challenge["_id"]] = Challenge(**challenge)
    
    save()
    
def initialize_database():
        
    # initialize database
    try:
        storage = ZODB.FileStorage.FileStorage("instances/database.fs")
        db = ZODB.DB(storage)
    except zc.lockfile.LockError:
        os.remove("instances/database.fs.lock")
        storage = ZODB.FileStorage.FileStorage("instances/database.fs")
        db = ZODB.DB(storage)
        
    connection = db.open()
    root = connection.root()

    # create users table if it doesn't exist
    if "users" not in root:
        root["users"] = BTree()
    if "challenges" not in root:
        root["challenges"] = BTree()
        load_challenges(root)
    if "posts" not in root:
        root["posts"] = BTree()

    save()
    
    return storage, db, connection, root
