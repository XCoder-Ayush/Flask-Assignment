from flask import Flask, Response, jsonify, request, send_from_directory
import os

class OutlineItem:
    def __init__(self, url, text, children=None):
        self.url = url
        self.text = text
        self.children = children if children else []

    def add_child(self, child_url):
        self.children.append(child_url)

    def remove_child(self, child_url):
        if child_url in self.children:
            self.children.remove(child_url)

    def update_text(self, new_text):
        self.text = new_text

    def __repr__(self):
        return f"OutlineItem(url='{self.url}', text='{self.text}', children={self.children})"

app = Flask(__name__)

outlines = []

@app.route('/')
def index():
    return send_from_directory('static', 'ui.html')

@app.route('/style.css')
def style():
    with open(os.path.join('static', 'style.css'), 'rb') as f:
        css_content = f.read()
    return Response(css_content, mimetype='text/css')

@app.route('/main.js')
def javascript():
    with open(os.path.join('static', 'main.js'), 'rb') as f:
        js_content = f.read()
    return Response(js_content, mimetype='application/javascript')

@app.route('/favicon.ico')
def favicon():
    with open(os.path.join('static', 'favicon.ico'), 'rb') as f:
        icon_bytes = f.read()
    return Response(icon_bytes, mimetype='image/x-icon')

root_item = OutlineItem(url="/outline", text="Root")
outlines.append(root_item)

# /outline/0/3
# Node->url,text,children

@app.route('/<path:url>', methods=['GET'])
def get_outline(url):
    target_url = '/' + url
    for item in outlines:
        if item.url == target_url:
            return jsonify(item.__dict__)

    return jsonify({"error": "Outline Not Found!!"}), 404

@app.route('/<path:url>', methods=['POST'])
def add_child(url):
    target_url = '/' + url
    new_text = request.json.get('text', '')
    
    parent_item = None
    for item in outlines:
        if item.url == target_url:
            parent_item = item
            break
    
    if parent_item:
        new_child_url = f"{target_url}/{len(parent_item.children)}"
        new_child_item = OutlineItem(url=new_child_url, text=new_text)
        parent_item.add_child(new_child_url)
        outlines.append(new_child_item)
        
        return jsonify(new_child_item.__dict__), 201
    else:
        return jsonify({"error": "Parent Item Not Found!!"}), 404


@app.route('/<path:url>', methods=['PUT'])
def update_text(url):
    target_url = '/' + url
    new_text = request.json.get('text', '')
    
    for item in outlines:
        if item.url == target_url:
            item.update_text(new_text)
            return jsonify(item.__dict__)
    
    return jsonify({"error": "Outline Not Found!!"}), 404

@app.route('/<path:url>', methods=['DELETE'])
def delete_outline_item(url):
    target_url = '/' + url
    # url=outline/0/0
    parent_url=target_url[:-2]

    # Del,Put OR Get
    # /outline/0
    # Parent 
    isDeleted=False
    for item in outlines:
        if item.url == target_url:
            outlines.remove(item)
            isDeleted=True

    # Remove This Node From Children Array
    if isDeleted==False:
        return jsonify({"error": "Outline Not Found!!"}), 404

    if isDeleted==True:
        for item in outlines:
            if item.url == parent_url:
                item.remove_child(target_url)

    return '', 204

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
