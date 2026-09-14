from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts(postID):

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

        POSTS.append(new_blog_post)

    return jsonify(POSTS)

@app.route('/delete/<int:postID>', methods=['POST'])
def delete_post(postID):

    data = request.get_json()


    for blog in data:
        print(blog)
        if blog["ID"] == postID:
            data.remove(blog)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
