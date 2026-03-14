"""PyMon entry point."""

import sys


def main() -> None:
    """Launch the PyMon application."""
    from pymon.core.app import PyMonApp

    app = PyMonApp(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
