from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

def validate_post_data_content_and_title(data):
    if not data.get("content") and not data.get("title"):
        return False
    return True

def validate_post_data_content(data):
    """
    Checks that all fields on the form have been filled in.
    If any of the fields are empty, ‘False’ is returned.
    """

    if not data.get("content"):
        return False
    return True

def validate_post_data_title(data):
    if not data.get("title"):
        return False
    return True

@app.route('/api/posts', methods=['GET'])
def get_posts():

    sort_query = request.args.get('sort')
    direction_query = request.args.get('direction')

    results = list(POSTS)

    if sort_query:
        if sort_query.lower() not in ("title", "content"):
            return jsonify({"error": "sort must be 'title' or 'content'"}), 400

        reverse = direction_query and direction_query.lower() == "desc" # is desc --> reverse is True; is not desc --> asc or what ever --> reverse is False(default)
                # <- sort blog by key ->         <- explained by blog sort.query(title or content) ->
        results.sort(key=lambda blog: blog[sort_query.lower()].lower(), reverse=reverse)

    return jsonify(results)


@app.route('/api/posts', methods=['POST'])
def add_posts():

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

    if not validate_post_data_content_and_title(new_blog_post):
        return jsonify({"error": "missing title and content data"}), 400

    if not validate_post_data_content(new_blog_post):
        return jsonify({"error": "missing content data"}), 400

    if not validate_post_data_title(new_blog_post):
        return jsonify({"error": "missing title data"}), 400

    POSTS.append(new_blog_post)
    return jsonify(new_blog_post), 201


@app.route('/api/posts/<int:postID>', methods=['DELETE'])
def delete_post(postID):

    global POSTS

    post_exists = any(blog["id"] == postID for blog in POSTS)

    if not post_exists:
        return jsonify({"message": f"Post with id {postID} not found."}), 404

    POSTS = [blog for blog in POSTS if blog["id"] != postID]
    return jsonify({"message": f"Post with id {postID} has been deleted successfully."}), 200


@app.route('/api/posts/<int:postID>', methods=['PUT'])
def update(postID):
    
    for blog in POSTS:
        if blog["id"] == postID:
            data = request.get_json()

            blog["title"] = data.get('title', blog['title'])
            blog["content"] = data.get('content', blog['content'])

            return jsonify(blog), 200

    return jsonify({"message": f"Post with id {postID} not found."}), 404

@app.route('/api/posts/search', methods=['GET'])
def search():

    title_query = request.args.get('title', '')
    content_query = request.args.get('content', '')

    results = []
    for blog in POSTS:
        title_match = title_query.lower() in blog['title'].lower() if title_query else False
        content_match = content_query.lower() in blog['content'].lower() if content_query else False

        if title_match or content_match:
            results.append(blog)

    return jsonify(results)




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
