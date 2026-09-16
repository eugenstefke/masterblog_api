from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

def get_json():
    """
    Read the json file
    return: all blogs as a dict in list [{},{}] structure
    """

    with open("posts.json", "r", encoding="utf-8") as data:
        return json.load(data)

def write_json(post):
    """
    write the python blog posts to json structure
    """

    with open("posts.json", "w", encoding="utf-8") as data:
        json.dump(post, data, indent=4, ensure_ascii=False)

def validate_post_data_content_and_title(data):
    """
    Checks that all fields on the form have been filled in.
    If any of the fields are empty, ‘False’ is returned.
    """
    if not data.get("content") and not data.get("title"):
        return False
    return True

def validate_post_data_content(data):
    """
    Checks whether the ‘content’ field in the form has been filled in.
    If this field is empty, ‘False’ is returned.
    """
    if not data.get("content"):
        return False
    return True

def validate_post_data_title(data):
    """
    Checks whether the ‘title’ field in the form has been filled in.
    If this field is empty, ‘False’ is returned.
    """
    if not data.get("title"):
        return False
    return True

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieves all posts
    provides the sort and direction parameters for the query

    A copy of the posts is created and stored in ‘results’

    If sort_query == True
    it checks whether ‘title’ or ‘content’ has been selected for sorting.
    If neither has been selected, a 400 error message is returned.

    If the query is based on ‘title’ or ‘content’, the results are sorted according to the selected direction and returned.
    ‘asc’ means descending, ‘desc’ means ascending

    The sorted list is returned in JSON format
    """
    all_blogs = get_json()
    sort_query = request.args.get('sort')
    direction_query = request.args.get('direction')

    results = list(all_blogs)

    if sort_query:
        if sort_query.lower() not in ("title", "content"):
            return jsonify({"error": "sort must be 'title' or 'content'"}), 400

        reverse = direction_query and direction_query.lower() == "desc" # is desc --> reverse is True; is not desc --> asc or what ever --> reverse is False(default)
                # <- sort blog by key ->         <- explained by blog sort.query(title or content) ->
        results.sort(key=lambda blog: blog[sort_query.lower()].lower(), reverse=reverse)

    return jsonify(results)


@app.route('/api/posts', methods=['POST'])
def add_posts():
    """
    Converts the body content from the front end into Python.

    Creates a new ID

    Creates a new post based on the input from the front end and the newly created ID

    Checks the content of the post. If the title and/or post content is empty, an error is displayed

    If the check is successful, the new post is created and added to the JSON list
    """
    data = request.get_json() # userinput from frontend like that: {"title": "My titel", "content": "My content"}. request.get_json() converts it in Python
    all_blogs = get_json()

    if len(all_blogs) == 0:
        new_id = 1
    else:
        new_id = max(blog_post['id'] for blog_post in all_blogs) + 1

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

    all_blogs.append(new_blog_post)
    write_json(all_blogs)
    return jsonify(new_blog_post), 201


@app.route('/api/posts/<int:postID>', methods=['DELETE'])
def delete_post(postID):
    """
    It goes through all the posts, searching for the ID to be deleted.

    If the ID is not found, an error is displayed.

    If the ID is found, the post with that ID is deleted.
    """

    all_blogs = get_json()

    post_exists = any(blog["id"] == postID for blog in all_blogs)

    if not post_exists:
        return jsonify({"message": f"Post with id {postID} not found."}), 404

    all_blogs = [blog for blog in all_blogs if blog["id"] != postID]
    write_json(all_blogs)
    return jsonify({"message": f"Post with id {postID} has been deleted successfully."}), 200


@app.route('/api/posts/<int:postID>', methods=['PUT'])
def update(postID):
    """
    It goes through all the posts, searching for the ID to be updated.

    If the ID is not found, an error is displayed.

    If the ID is found, the post is updated in the title and/or post content.
    """
    all_blogs = get_json()
    for blog in all_blogs:
        if blog["id"] == postID:
            data = request.get_json() # liest den Body der eingehenden HTTP-Anfrage (also die Daten, die der Client beim PUT-Request mitgeschickt hat), interpretiert ihn als JSON-Text und wandelt ihn in ein Python-Dict um.

            blog["title"] = data.get('title', blog['title'])
            blog["content"] = data.get('content', blog['content'])

            write_json(all_blogs)
            return jsonify(blog), 200

    return jsonify({"message": f"Post with id {postID} not found."}), 404

@app.route('/api/posts/search', methods=['GET'])
def search():
    """
    Search function based on key/value parameters

    The title and post content are provided as key parameters.

    The values are compared with existing posts; if a match is found, the post is added to the results list.

    Returns the new list 
    """
    title_query = request.args.get('title', '')
    content_query = request.args.get('content', '')

    all_blogs = get_json()

    results = []
    for blog in all_blogs:
        title_match = title_query.lower() in blog['title'].lower() if title_query else False
        content_match = content_query.lower() in blog['content'].lower() if content_query else False

        if title_match or content_match:
            results.append(blog)

    return jsonify(results)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
