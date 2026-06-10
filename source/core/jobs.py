import time
import threading
from .ToStdOut import ToStdout

write = ToStdout.write

class JobManager:
    _jobs = {}
    _job_counter = 1
    _lock = threading.Lock()

    @classmethod
    def register(cls, name, terminate_func, thread_obj=None):
        """Registers a background task with a termination callback."""
        with cls._lock:
            job_id = cls._job_counter
            cls._job_counter += 1
            
            cls._jobs[job_id] = {
                "name": name,
                "terminate_func": terminate_func,
                "thread": thread_obj,
                "start_time": time.time()
            }
            return job_id

    @classmethod
    def unregister(cls, job_id):
        """Silently removes a job from the registry if it completes naturally."""
        with cls._lock:
            if job_id in cls._jobs:
                del cls._jobs[job_id]

    @classmethod
    def list_jobs(cls):
        """Displays all active background jobs."""
        with cls._lock:
            # Clean up dead threads automatically before listing
            dead_jobs = []
            for jid, details in cls._jobs.items():
                t = details.get("thread")
                if t and not t.is_alive():
                    dead_jobs.append(jid)
            
            for jid in dead_jobs:
                del cls._jobs[jid]

            if not cls._jobs:
                write("[*] No active background jobs.\n")
                return

            write("\n========== Active Background Jobs ==========\n")
            write(f"  {'ID':<5} | {'Job Name':<30} | {'Uptime (s)':<10}\n")
            write("-" * 52 + "\n")
            
            for jid, details in cls._jobs.items():
                uptime = int(time.time() - details['start_time'])
                write(f"  {jid:<5} | {details['name']:<30} | {uptime:<10}\n")
                
            write("============================================\n")

    @classmethod
    def kill_job(cls, job_id):
        """Executes the termination callback for a specific job."""
        with cls._lock:
            if job_id not in cls._jobs:
                write(f"[-] Error: Job ID {job_id} not found.\n")
                return

            job = cls._jobs[job_id]
            name = job['name']
            func = job['terminate_func']
            
            write(f"[*] Terminating Job {job_id} ({name})...\n")
            try:
                if func:
                    func()
                write(f"[+] Job {job_id} terminated successfully.\n")
                del cls._jobs[job_id]
            except Exception as e:
                write(f"[-] Error terminating Job {job_id}: {e}\n")

    @classmethod
    def handle_command(cls, data):
        """Parses CLI input for the 'jobs' command."""
        import shlex
        parts = shlex.split(data)
        
        if len(parts) == 1 or parts[1].lower() in ["list", "ls"]:
            cls.list_jobs()
            return
            
        action = parts[1].lower()
        
        if action == "kill":
            if len(parts) < 3:
                write("[-] Usage: jobs kill <id>\n")
                return
            try:
                job_id = int(parts[2])
                cls.kill_job(job_id)
            except ValueError:
                write("[-] Error: Job ID must be an integer.\n")
        else:
            write(f"[-] Unknown jobs action: {action}. Use 'list' or 'kill <id>'.\n")
