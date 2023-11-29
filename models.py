import persistent
from datetime import datetime

class User(persistent.Persistent):
    DEFAULT_PROFILE_COLOR = "#000000"
    def __init__(self, uuid, email, name, password_hash):
        self.uuid = uuid
        self.email = email
        self.name = name
        self.password_hash = password_hash
        self.completed_challenges = {}
        self.score = 0
        self.posts = []
        self.comments = []
        
        self.profile_pic_path = ""
        self.profile_color = User.DEFAULT_PROFILE_COLOR

    def get_password_hash(self):
        return self.password_hash
    
    def get_challenge_completed(self, challenge_id):
        if challenge_id in self.completed_challenges:
            return self.completed_challenges[challenge_id]
        return False
    
    def get_score(self):
        return int(sum(self.completed_challenges.values()))
    
    def add_post(self, post):
        self.posts.append(post)
        self._p_changed = True
    
    def add_comment(self, comment):
        self.comments.append(comment)
        self._p_changed = True
    
    def add_completed_challenge(self, challenge_id, score):
        self.completed_challenges[challenge_id] = score
        self._p_changed = True
        
    def set_profile_pic_path(self, path):
        self.profile_pic_path = path
    
    def get_profile_pic_path(self):
        return self.profile_pic_path
    
    def set_profile_color(self, color):
        self.profile_color = color
        
    def get_profile_color(self):
        try:
            if self.profile_color == "":
                self.profile_color = User.DEFAULT_PROFILE_COLOR
            return self.profile_color
        except AttributeError:
            self.profile_color = User.DEFAULT_PROFILE_COLOR
            return self.profile_color
    
class Challenge(persistent.Persistent):
    def __init__(self, _id, code, title, instructions, difficulty, lab):
        self._id: str = _id
        self.code: str = code
        self.title: str = title
        self.instructions: str = instructions
        self.difficulty: float = difficulty
        self.lab: str = lab

    def get_details(self, details=None):
        if details == None:
            return self.__dict__
        
        try:
            return {key: self.__dict__[key] for key in details}
        except KeyError:
            return self.__dict__
    
class Post(persistent.Persistent):
    def __init__(self, post_id, title, content, author_uuid):
        self.post_id = post_id
        self.title = title
        self.content = content
        self.author_uuid = author_uuid
        self.created_at = datetime.now()
        self.comments = {}

    def add_comment(self, comment):
        self.comments[comment.comment_id] = comment
        self._p_changed = True
    
    def delete_comment(self, comment_id):
        self.comments.pop(comment_id)
        self._p_changed = True

    def get_comment(self, comment_id):
        return self.comments[comment_id]

    def get_comments(self):
        return self.comments
    
    def get_dict(self):
        result = dict(self.__dict__)
        result["created_at"] = str(self.created_at)
        result["created_at_formatted"] = self.created_at.strftime("%d/%m/%Y %H:%M:%S")
        result["comments"] = [c.get_dict() for c in self.comments.values()]

        return result

class Comment(persistent.Persistent):
    def __init__(self, comment_id, parent_post_id, author_uuid, content):
        self.comment_id = comment_id
        self.parent_post_id = parent_post_id
        self.author_uuid = author_uuid
        self.content = content
        self.created_at = datetime.now()
        self.edited = False
        
    def edit_comment(self, new_content):
        self.content = new_content
        self.edited = True
        
    def get_dict(self):
        result = dict(self.__dict__)
        result["created_at"] = self.created_at.strftime("%d/%m/%Y %H:%M:%S")
    
        return result
    