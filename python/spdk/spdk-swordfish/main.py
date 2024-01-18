from flask import Flask

if __name__ == "__main__":
    app = Flask("spdk-swordfish")
    app.run(debug=True)
