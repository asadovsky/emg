# emg

## Environment setup

### Requirements

- Python version 3.11 or above
- Node.js version 16 or above (for Pyright)

### pyenv

- https://github.com/pyenv/pyenv
- https://github.com/pyenv/pyenv-virtualenv

### venv

See [here](https://docs.python.org/3/library/venv.html) for background on venv.

We recommend adding this to your `~/.bashrc` file:

    export PIP_REQUIRE_VIRTUALENV=1
    alias vn='python3 -m venv .venv'
    alias va='source .venv/bin/activate'
    alias vd='deactivate'

### pip

Install required packages:

    $ pip install -r requirements.in

Add a new package (using `numpy` as an example):

    $ echo numpy >> requirements.in && sort -u -o requirements.in requirements.in
    $ pip install -r requirements.in
    $ pip freeze > requirements.txt

## Resources

- https://en.wikipedia.org/wiki/Dynamic_time_warping
