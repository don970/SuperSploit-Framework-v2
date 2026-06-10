import shlex
from .listener import Listener
from rich.console import Console
from rich.table import Table

from .ToStdOut import ToStdout

write = ToStdout.write
console = Console()

class Sessions:
    @staticmethod
    def manage(args):
        parts = shlex.split(args) if args else []
        
        # Handle 'sessions help' specifically
        if len(parts) >= 2 and parts[1] in ["help", "-h", "--help"]:
            from .help import Help
            Help.display("sessions")
            return

        # Show list of active sessions (e.g., "sessions" or "sessions -l")
        if not parts or len(parts) == 1 or (len(parts) == 2 and parts[1] == "-l"):
            sessions = Listener.active_sessions
            if not sessions:
                write("[-] No active sessions.\n")
                return
            
            table = Table(show_header=True, header_style="bold green", title="Active C2 Sessions")
            table.add_column("Session ID", style="dim", width=12)
            table.add_column("Target IP:Port", style="cyan")
            table.add_column("Status", style="green")

            for sid, info in sessions.items():
                addr = f"{info['addr'][0]}:{info['addr'][1]}"
                table.add_row(str(sid), addr, "Active")
                
            console.print(table)
            write("[*] Type 'sessions -i <ID>' to interact with a target.\n")
            return
            
        # Interact with a specific session (e.g., "sessions -i 1")
        if len(parts) >= 3 and parts[1] == "-i":
            try:
                sid = int(parts[2])
                Listener.interact(sid)
            except ValueError:
                write("[-] Invalid session ID. Usage: sessions -i <id>\n")
            return
            
        write("Usage: sessions [-l] | [-i <id>]\n")