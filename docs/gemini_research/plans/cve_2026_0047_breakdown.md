# CVE-2026-0047: ActivityManagerService UI Bitmap Exfiltration

## Overview
CVE-2026-0047 is a high-severity local privilege escalation and information disclosure vulnerability in the Android Framework, specifically within the `ActivityManagerService` (AMS). The flaw allows a malicious application with no special permissions to exfiltrate rendered UI surfaces (bitmaps/screenshots) of all running applications.

## Technical Details
The vulnerability stems from a missing permission check in the `dumpBitmapsProto` method. This method was designed to provide diagnostic information about the system's memory usage related to bitmaps, but it also includes the actual pixel data of rendered surfaces.

### The Bug
In `ActivityManagerService.java`, the `dumpBitmapsProto` method is exposed over the Binder IPC interface. Prior to the fix, the method did not verify if the caller held the `android.permission.DUMP` permission.

**Vulnerable Code (Conceptual):**
```java
// frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java

public void dumpBitmapsProto(ParcelFileDescriptor fd, String[] args, int userId, 
                             boolean dumpAll, String format) {
    // BUG: Missing enforceCallingPermission(android.Manifest.permission.DUMP, "dumpBitmapsProto");
    
    // Logic to traverse processes and write bitmap data to 'fd' as a Protobuf stream
    protoLog.dumpBitmaps(fd, args, userId, dumpAll, format);
}
```

### Exploitation Path
An attacker can invoke this method directly by crafting a raw Binder transaction to the `activity` service.

1. **Transaction ID:** 117 (Android 16 QPR2)
2. **Descriptor:** `android.app.IActivityManager`
3. **Parameters:**
   - `fd`: A file descriptor to receive the Proto stream.
   - `args`: Arguments for the dump operation (can be empty).
   - `userId`: Target user ID (-2 for current user).
   - `dumpAll`: Boolean flag to dump all bitmaps.
   - `format`: Desired output format (e.g., "png").

The system then writes a Protobuf stream containing the UI bitmaps of every visible application into the provided file descriptor.

## Impact
A background app can silently monitor the user's screen, capturing sensitive information such as:
- Authentication tokens/QR codes.
- Banking details.
- Private messages.
- Passwords displayed during entry.

## Remediation
Google addressed this issue in the March 2026 Android Security Bulletin by adding a mandatory permission check:

```java
public void dumpBitmapsProto(...) {
    if (checkCallingPermission(android.Manifest.permission.DUMP) 
            != PackageManager.PERMISSION_GRANTED) {
        throw new SecurityException("Requires DUMP permission");
    }
    // ...
}
```

## References
- Android Security Bulletin - March 2026
- CVE-2026-0047
- [PoC] mobilehackinglab/CVE-2026-0047-poc
