import flask
from flask import jsonify, make_response
import random
import os
import socket
import json
import sys
import mariadb

quotes = []
quoteCount = 0

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return prepareResponse(jsonify("qotd"))

@app.route('/version', methods=['GET'])
def version():
    response = make_response("v2")
    response.mimetype = "text/plain"
    return prepareResponse(response)
@app.route('/writtenin', methods=['GET'])
def writtenin():
    response = make_response("Python 3.8")
    response.mimetype = "text/plain"
    return prepareResponse(response)

@app.route('/health', methods=['GET'])
def health():
    return 'foo'

@app.route('/quotes', methods=['GET'])
def getQuotes():
    global quotes
    return prepareResponse(jsonify(quotes))
  
@app.route('/quotes/<int:id>', methods=['GET'])
def getQuoteById(id):
    return prepareResponse(jsonify(replaceHostname(quotes[id])))

@app.route('/quotes/random', methods=['GET'])
def getRandom():
    try:
        conn = mariadb.connect(
            user=os.environ['USER_DB'],
            password=os.environ['PASSWORD_DB'],
            host=os.environ['HOST_DB'],
            database="citas",
            port=3306)
        
        mycursor = conn.cursor(dictionary=True)
        mycursor.execute("SELECT '-hostname-' as hostname, id, quotation, author FROM quotes ORDER BY author, id")
        rows = mycursor.fetchall()
        n = random.randint(0,(mycursor.rowcount)-1)
        conn.close()
        quotes = rows
        return prepareResponse(jsonify(replaceHostname(quotes[n])))
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

def prepareResponse(response):
    # Enable Access-Control-Allow-Origin
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def replaceHostname(jsondoc):
    q = json.dumps(jsondoc)
    q = q.replace('-hostname-', socket.gethostname())
    return json.loads(q)

def main():
    global quotes
    try:
        conn = mariadb.connect(
            user=os.environ['USER_DB'],
            password=os.environ['PASSWORD_DB'],
            host=os.environ['HOST_DB'],
            database="citas",
            port=3306)
        mycursor = conn.cursor(dictionary=True)
        mycursor.execute("SELECT '-hostname-' as hostname, id, quotation, author FROM quotes ORDER BY author, id")
        quotes = mycursor.fetchall()
        conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)