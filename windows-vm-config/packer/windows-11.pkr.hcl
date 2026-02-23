packer {
  required_plugins {
    qemu = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/qemu"
    }
    vagrant = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/vagrant"
    }
  }
}

variable "iso_url" {
  type    = string
  default = "https://go.microsoft.com/fwlink/p/?LinkID=2195166&clcid=0x409&culture=en-us&country=US"
}

variable "virtio_iso_url" {
  type    = string
  default = "https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso"
}

source "qemu" "windows-11" {
  iso_url           = var.iso_url
  iso_checksum      = "none"
  shutdown_command  = "shutdown /s /t 10 /f /d p:4:1 /c "Packer Shutdown""
  communicator      = "winrm"
  winrm_username    = "matthias"
  winrm_password    = "correct-horse-battery-staple"
  winrm_timeout     = "1h"
  disk_size         = "60000"
  format            = "qcow2"
  accelerator       = "kvm"
  http_directory    = "."
  memory            = 8192
  cpus              = 4
  vm_name           = "windows-11"
  headless          = true
  
  # TPM Emulation for Windows 11
  qemuargs = [
    ["-tpmdev", "passthrough,id=tpm0,path=/dev/tpm0"],
    ["-device", "tpm-tis,tpmdev=tpm0"],
    ["-cpu", "host"]
  ]

  # Floppy for autounattend.xml
  floppy_files = [
    "./autounattend.xml"
  ]

  # Mount VirtIO ISO as secondary drive
  cd_files = [
    "./autounattend.xml" 
  ]
  cd_label = "cidata"
}

build {
  sources = ["source.qemu.windows-11"]

  provisioner "powershell" {
    inline = [
      "Set-ExecutionPolicy Bypass -Scope Process -Force",
      "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072",
      "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))",
      "choco install -y vscode git googlechrome icloud-for-windows"
    ]
  }

  post-processor "vagrant" {
    keep_input_artifact = false
    output              = "windows-11.box"
  }
}
