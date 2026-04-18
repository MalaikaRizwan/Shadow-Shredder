# USER GUIDE

## 1. Introduction
ForensiWipe is an academic secure deletion workstation designed for digital forensics learning.  
It supports controlled data destruction while teaching artifact-awareness and forensic limitations.

## 2. Legal and Ethical Considerations
- Use only with explicit authorization.
- Do not use on evidence systems without legal protocol.
- Do not use for unauthorized concealment or destruction.

## 3. System Requirements
- Windows 10/11 recommended.
- Python 3.10+ and dependencies from `requirements.txt`.

## 4. Installation
See `docs/INSTALLATION.md`.

## 5. Interface Walkthrough
### Dashboard
- View detected drives, privilege level, and recent operations.

### File / Folder Shredder
1. Select file or folder.
2. Click Analyze Target for preview.
3. Select wipe method, passes, chunk size, and options.
4. Keep Dry Run ON for demo.
5. Click Start Shred.

### Partition / Free-space Wipe
1. Select a drive.
2. Choose mode:
   - Full partition wipe (safety-constrained in academic build)
   - Free-space wipe only
   - Quick forensic wipe mode
3. Type `WIPE` to confirm.
4. Start operation.

### Reports & Logs
- Refresh list, filter reports, open generated JSON/CSV/HTML/TXT reports.

### Forensic Notes
- Review NTFS/FAT behavior and deletion limitations.

## 6. Example Use Cases
- Secure deletion of assignment answer sheet before sharing system image.
- Folder sanitization before disk handover.
- Free-space wipe demo after deleting sample artifacts.

## 7. Output Interpretation
- `success` + `verification=deleted` means target path no longer exists.
- Warnings may still mention residual forensic risk.
- HTML reports are presentation-ready for viva and coursework submission.

## 8. Suggested Screenshot Placeholders
- [Screenshot Placeholder] Dashboard drive list
- [Screenshot Placeholder] Shredder settings panel
- [Screenshot Placeholder] Free-space wipe typed confirmation
- [Screenshot Placeholder] HTML report view

## 9. Team Work Division (Template)
- Member A: Core wipe engine
- Member B: GUI and UX
- Member C: Reporting and documentation
- Member D: Testing and demo validation
