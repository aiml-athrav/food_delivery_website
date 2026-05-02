from app import app

# This runs the app when python run.py is executed
if __name__ == '__main__':
    # debug=True automatically restarts the server when we save code changes!
    app.run(debug=True, host='127.0.0.1', port=5000)
