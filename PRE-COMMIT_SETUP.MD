# Setting up pre-commits

This setup is required to configure pre-commit hooks.

1. Assuming that you have already set up a virtual environment and installed all the required dependencies. We now need to install the pre-commit hooks.

    ```bash
    pre-commit install
    ```

2. `pre-commit` hooks will run whenever we run `git commit -m` command.

    To skip particular pre-commit checks run:

    ```bash
    SKIP=flake8 git commit -m "foo"
    ```

    Skip all pre-commit checks.

    ```bash
    git commit -m "foo" --no-verify
    ```

3. To run pre-commit before commiting changes, run:

    ```bash
    pre-commit run --all-files
    ```

    To run individual pre-commit hooks, run the following commands for particular hook:

    Interrogate pre-commit hook:

    ```bash
    interrogate -c pyproject.toml -vv
    ```

    Flake8 pre-commit hook:

    ```bash
    flake8 .
    ```

    isort pre-commit hook:

    ```bash
    isort . --settings-path=pyproject.toml
    ```

    Black pre-commit hook:

    ```bash
    black . --config pyproject.toml --check
    ```

    pydocstyle pre-commit hook, list of [error codes](https://www.pydocstyle.org/en/stable/error_codes.html):

    ```bash
    pydocstyle .  -e --count --convention=google --add-ignore=D403
    ```

    darglint pre-commit hook, list of [error codes](https://github.com/terrencepreilly/darglint#error-codes):

    ```bash
    darglint -v 2 .
    ```
