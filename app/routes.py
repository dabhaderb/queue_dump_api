import os
from flask import Flask, request, jsonify
from .utils import *
from .properties import UPLOAD_FOLDER

app = Flask(__name__)


# API
@app.route("/rmq_dump", methods=['POST'])
def dump_to_queue():
    try:
        form = request.form
        if 'file' not in request.files:
            return jsonify("ERROR: file is not attached")
        file = request.files['file']

        if file.filename == "":
            return jsonify("ERROR: file is not attached ")
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

        files = os.listdir(UPLOAD_FOLDER)
        if files:
            file_name = files[0]
            file_type = check_file_type(file_name)
            if file_type == 'csv':
                web_links = read_csv(file_name)
            elif file_type == 'json':
                web_links = read_json(file_name)
            else:
                return jsonify("ERROR: file format is not supported")

            queue_dump(web_links)
            os.remove(os.path.join(UPLOAD_FOLDER, file_name))
            return jsonify('successfully dumped total links to queue'), 200

    except Exception as e:
        return jsonify({"ERROR in main function": str(e)}), 400


if __name__=="__main__":
    app.run(debug=True)