from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

def validate_post_data(data):
    """
    Checks that all fields on the form have been filled in.
    If any of the fields are empty, ‘False’ is returned.
    """

    if not data.get("title") or not data.get("content"):
        return False
    return True

@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():

    if request.method == 'POST':
        data = request.get_json()

        if len(POSTS) == 0:
            new_id = 1
        else:
            new_id = max(blog_post['id'] for blog_post in POSTS) + 1

        new_blog_post = {
                        "id": new_id,
                        "title": data.get('title'),
                        "content": data.get('content')
                        }

        if not validate_post_data(new_blog_post):
            return jsonify({"error": "Invalid post data"}), 400

        POSTS.append(new_blog_post)

    return jsonify(POSTS)

@app.route('/api/posts/<int:postID>', methods=['DELETE'])
def delete_post(postID):

    global POSTS

    POSTS = [blog for blog in POSTS if blog["id"] != postID]

    return jsonify(POSTS)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
