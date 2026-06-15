# 💎 SuperSploit Pro: Administrative License Manager

The `manager.py` utility is the central nervous system for the SuperSploit Pro licensing ecosystem. It allows the administrator to manage the `manifest.json` database, handle HWID anchoring, and enforce global security policies.

## 📂 Location
- **Script**: `source/tools/licensing/manager.py`
*   **Database**: `source/tools/licensing/manifest.json` (Sync this to your GitHub repository)

---

## 🔄 Core Licensing Workflow

1.  **Generate a Key**: Use the manager to create a new "Pending" key.
2.  **User Activation**: Provide the key to the user. When they run `activate <KEY>`, you will receive an automated alert via your Discord/Slack webhook containing their **Hardware ID (HWID)**.
3.  **Anchoring**: Use the manager to "Anchor" that specific HWID to the key.
4.  **Remote Sync**: Commit and push the updated `manifest.json` to your GitHub repository. The user's framework will now recognize the activation.

---

## 🛠️ Command Reference

### 1. Adding a New Key
Create a new entry in the database. By default, the `hwid` is set to `null` and the status is `pending`.
```bash
python3 source/tools/licensing/manager.py --add "SUPERSPLOIT-PRO-2026-UNIQUE-ID" --tier "RedTeam"
```
*   **--tier**: (Optional) Specify the license level (`Individual`, `RedTeam`, `Enterprise`).

### 2. Anchoring a Hardware ID (HWID)
Bind a key to a specific machine. **Note: Once an HWID is anchored, it is immutable via the framework to prevent key sharing.**
```bash
python3 source/tools/licensing/manager.py --anchor "SUPERSPLOIT-PRO-2026-UNIQUE-ID" "BB5E4C61A070227D"
```

### 3. Revoking Access
Instantly invalidate a key. The next time the user's framework performs a remote check, access will be blocked.
```bash
python3 source/tools/licensing/manager.py --revoke "SUPERSPLOIT-PRO-2026-UNIQUE-ID"
```

### 4. Viewing the Database
Display the current state of all keys, including registration dates and active anchors.
```bash
python3 source/tools/licensing/manager.py --list
```

---

## 🌐 GitHub Integration

To make this "Remote," you must host the `manifest.json` on a public or private GitHub repository.

1.  Update the `manifest.json` locally using `manager.py`.
2.  Push to GitHub:
    ```bash
    git add manifest.json
    git commit -m "Update license manifest: Added HWID anchor for RedTeam-01"
    git push
    ```
3.  Ensure your SuperSploit framework is pointing to the **Raw URL** of this file:
    ```bash
    [SuperSploit]: set REMOTE_MANIFEST_URL https://raw.githubusercontent.com/user/repo/main/manifest.json
    ```

---

## 🛡️ Security Policies

The `policy` block in `manifest.json` allows for global framework control:

*   **`global_killswitch`**: Set to `true` to immediately disable all SuperSploit Pro installations globally (useful in case of a major leak).
*   **`maintenance_mode`**: Set to `true` to display a maintenance warning to users during activation.

---
*Generated June 2026 for SuperSploit Administrative Operations.*
