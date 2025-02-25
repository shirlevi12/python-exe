from flask import Flask
import s3

app = Flask(__name__)

@app.route('/s3/', methods=['GET'])
def list_s3_buckets():
    return s3.list_s3_buckets()
    
