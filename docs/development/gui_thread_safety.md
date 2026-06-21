# Tkinter GUI Thread Safety Standard

## The Problem
The SuperSploit-Framework makes extensive use of Tkinter for its Professional-tier graphical interfaces (SMTP Suite, Evil Twin, Web Stager, etc.). 

Because network operations (HTTP requests, SMTP connections, socket binding) are blocking, they must be executed in background threads (`threading.Thread`) to prevent the UI from freezing. 

However, **Tkinter is fundamentally not thread-safe**. If a background thread directly attempts to modify a Tkinter widget (e.g., inserting text into a console, enabling a button, or showing a message box), it can cause race conditions, rendering glitches, or hard `SIGSEGV` segmentation faults that crash the entire framework.

## The SuperSploit Standard Solution
To bridge background network threads with the main UI thread, all SuperSploit modules must use the `self.root.after(0, callback)` method. This safely pushes the UI update into Tkinter's main event queue to be executed on the next render cycle.

### Example 1: Updating the Telemetry Console
**INCORRECT (Crash Prone):**
```python
def log(self, msg):
    self.console.insert(tk.END, f"{msg}\n") # Called directly from background thread
```

**CORRECT (Thread-Safe):**
```python
def log(self, msg):
    def _update():
        self.console.insert(tk.END, f"{msg}\n")
        self.console.see(tk.END)
    self.root.after(0, _update) # Queued to main UI thread
```

### Example 2: Re-enabling Buttons after Execution
**INCORRECT:**
```python
def _delivery_logic(self):
    # ... network stuff ...
    self.send_btn.config(state=tk.NORMAL)
```

**CORRECT:**
```python
def _delivery_logic(self):
    # ... network stuff ...
    self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
```