# Windows 11 VM & iCloud Migration Handoff

This project contains the configuration for a clean, custom-built Windows 11 Virtual Machine using Vagrant and Libvirt (KVM/QEMU). It also documents the iCloud to Google Drive migration process.

## 1. Windows 11 VM

### Status
- **Builder:** `packer` using `rgl/windows-vagrant` templates.
- **Box Type:** Windows 11 Enterprise Evaluation (24H2).
- **Provider:** Libvirt (KVM).

### Starting the VM
Once the Packer build completes (check `~/github/rgl-windows-vagrant/make-build.log`), the box file `windows-11-24h2-amd64-libvirt.box` will be created.

1.  **Register the Box:**
    ```bash
    vagrant box add windows-11-24h2 ~/github/rgl-windows-vagrant/windows-11-24h2-amd64-libvirt.box
    ```

2.  **Start the VM:**
    ```bash
    cd ~/github/windows-vm-config
    vagrant up
    ```

### Connection Info
- **RDP Address:** `localhost:3389` (Check `vagrant port` if that fails).
- **Default User:** `vagrant`
- **Default Password:** `vagrant`
- **Admin User (Provisioned):** `matthias`
- **Admin Password:** `correct-horse-battery-staple`

### Installed Tools (Provisioned)
- VS Code
- Git
- Google Chrome
- Chocolatey

---

## 2. iCloud Migration

### Strategy
Since Linux support for iCloud Drive is limited (no official client, Rclone issues with ADP), the most robust path is:
1.  Boot this Windows 11 VM.
2.  Install **iCloud for Windows** inside the VM.
3.  Install **Google Drive for Desktop** inside the VM.
4.  Sync files down from iCloud and drag them over to Google Drive.

### Steps inside VM
1.  Open PowerShell (Admin).
2.  Install iCloud: `choco install -y icloud` (or download from Microsoft Store).
3.  Log in to iCloud and enable **iCloud Drive**.
4.  Wait for files to sync.
5.  Install Google Drive: `choco install -y googledrive`.
6.  Move files from `C:\Users\vagrant\iCloudDrive` to `G:\My Drive`.

---

## 3. Repository Structure

```
~/github/windows-vm-config/
├── Vagrantfile          # VM definition and provisioning script
├── packer/              # Bespoke Packer config (if needed)
├── scripts/             # Helper scripts
└── handoff.md           # This file
```
