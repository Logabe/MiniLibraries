# ![Mini Libraries Icon](/static/LibrariesIcon.svg) Mini Libraries
Mini Libraries (better title WIP) is a web app for sharing books on a small scale (think friends, family). It acts as a way to keep track of who is borrowing what, and as a way to check out other member's personal book collections.

This was originally my Final Project for [CS50x 2023](https://cs50.harvard.edu/x/2023/), but I thought it was a neat concept and have decided to keep working on it. The project is in a very unstable state at present, and I'm currently working on improving organisation and making sure everything is stable before I will make any updates.

## How to run Mini Libraries
1. Install [Python3](https://wiki.python.org/moin/BeginnersGuide/Download) and [Pip](https://pip.pypa.io/en/stable/installation/)
2. Download the source code for this project.
3. Run `pip install -r requirements.txt` to install dependencies
4. Run the following commands
    1. **For testing:** Run `flask run` to start the app.
    2. **For production:** Run `waitress-serve --listen=*:8000 app:app` to listen on port 8000. See the [Waitress Docs](https://docs.pylonsproject.org/projects/waitress/en/stable/runner.html) for more info.