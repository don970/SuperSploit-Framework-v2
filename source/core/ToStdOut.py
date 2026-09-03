import sys


class ToStdout:
    @staticmethod
    def write(data):
        """we use this instead of print for errors with formating output"""
        if "str" not in str(type(data)):
            try:
                data = data.decode()
                pass
            except Exception:
                data = f"{str(data)}"
                pass
        if not data.endswith("\n"):
            data = f"{data}\n"
        sys.stdout.write(data)
        sys.stdout.flush()
