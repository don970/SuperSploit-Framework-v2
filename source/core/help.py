import os
from .ToStdOut import ToStdout
from .errors import Error

install_location = f'{os.getenv("HOME")}/.SuperSploit'
help_dir = f"{install_location}/.data/.help/"
write = ToStdout.write

class Help:
    @staticmethod
    def display(topic=None):
        """
        Dynamically fetches and displays modular help text files.
        If no topic is specified, loads the main overview (all).
        """
        # If topic is None or just "help", default to "all"
        if not topic or topic.strip().lower() == "help":
            safe_topic = "all"
        else:
            try:
                # If input is "help topic", extract "topic"
                if " " in topic:
                    safe_topic = topic.split()[1].lower().strip()
                else:
                    # If input is already just the topic (unlikely from input_handling_engine but safe)
                    safe_topic = topic.lower().strip()
            except IndexError:
                safe_topic = "all"

        # Sanitize input to prevent directory traversal
        safe_topic = os.path.basename(safe_topic)
        help_file = os.path.join(help_dir, safe_topic)

        if os.path.exists(help_file):
            try:
                with open(help_file, "r") as file:
                    write(f"\n{file.read()}\n")
            except Exception as e:
                Error.silent(f"Failed to read help file {safe_topic}: {e}")
                write(f"[-] Could not load help for '{safe_topic}'. Check error logs.")
        else:
            write(f"[-] No specific help documentation found for '{safe_topic}'.")
            write("[*] Type 'help' to see the main command menu.\n")
