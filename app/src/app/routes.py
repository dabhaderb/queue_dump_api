import os
from flask import Flask, request, jsonify
import logging
from ..utils.utils import *
from ..properties.properties import UPLOAD_FOLDER
from ..utils.rmq_utils import RMQ

app = Flask(__name__)

# Logging
root_dir = os.getcwd()
log_dir = os.path.join(root_dir, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'routes.log')
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s - Line %(lineno)d')


# API
@app.route("/add_urls", methods=['POST'])
def dump_to_queue():
    try:
        try:
            rmq = RMQ("amqp://app:llmdev@103.93.20.138:5000/llm_dev?heartbeat=3600")
            logging.info("successfully connected to RMQ")
        except Exception as e:
            return jsonify({"ERROR: connecting to RMQ": str(e)})

        if 'file' not in request.files:
            logging.error("ERROR: file is not attached ")
            return jsonify("ERROR: file is not attached")
        file = request.files['file']

        if file.filename == "":
            logging.error("ERROR: file is not attached ")
            return jsonify("ERROR: file is not attached ")
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            logging.info(f"file saved to path {str(file_path)}")

        files = os.listdir(UPLOAD_FOLDER)
        logging.info(f"found total no of files in the upload folder {files}")

        if files:
            file_name = os.path.join(UPLOAD_FOLDER, files[0])
            logging.info(f"{file_name} reading from folder")
            file_type = check_file_type(file_name)
            logging.info(f"{str(file_type)} found reading file")

            if file_type == 'csv':
                web_links = read_csv(file_name)
                logging.info(f"web links extracted from {file_name}")

            elif file_type == 'json':
                web_links = read_json(file_name)
                logging.info(f"web links extracted from {file_name}")

            else:
                logging.error("ERROR: file format is not supported")
                return jsonify("ERROR: file format is not supported")

            if web_links:
                queue_dump(rmq, web_links)
                logging.info(f"web links dumped to queue")

            os.remove(file_name)
            logging.info(f"{str(file_name)} removed from folder")
            return jsonify('successfully dumped total links to queue'), 200

    except Exception as e:
        logging.error(f"ERROR in main function {str(e)}")
        return jsonify({"ERROR in main function": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
