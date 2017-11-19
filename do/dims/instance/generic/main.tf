variable "name" { default = "dims" }
variable "domain" { default = "dims" }
variable "datacenter" { default = "dims" }
variable "image_name" { default = "debian-8-x64" }
variable "region" { default = "sfo1" } # Must have metadata support
# Hosts
variable "count" { default = "1" }
variable "count_format" { default = "%03d" }
variable "size" { default = "512mb" }
#variable "role" {}
variable "keypair_id" { }
variable "private_key_filename" { default = "~/.ssh/do" }
variable "ssh_fingerprint" { }

resource "digitalocean_droplet" "instance" {
    image = "${var.image_name}"
    #name = "${var.name}-${var.role}-${format(var.count_format, count.index+1)}"
    name = "${var.name}.${var.domain}"
    region = "${var.region}"
    size = "${var.size}"
    private_networking = true
    #ssh_keys = ["${var.keypair_id}"]
    ssh_keys = [
      "${var.ssh_fingerprint}"
    ]
    #user_data = "{\"role\":\"${var.role}\",\"dc\":\"${var.datacenter}\"}"
    user_data = "{\"dc\":\"${var.datacenter}\"}"

  connection {
      user = "root"
      type = "ssh"
      private_key = "${file(var.private_key_filename)}"
      host = "${self.ipv4_address}"
      timeout = "2m"
  }

  provisioner "remote-exec" {
    inline = [
      "export PATH=$PATH:/usr/bin",
      "if which apt-get 2>&1 >/dev/null; then sudo apt-get update && sudo apt-get upgrade -y; fi",
      "if which yum 2>&1 >/dev/null; then sudo yum update -y && sudo yum install python epel-release -y; fi",
    ]
  }

  provisioner "file" {
    source      = "../../files/common-scripts/keys.host.fingerprints.sh"
    destination = "/tmp/keys.hosts.fingerprints.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/keys.hosts.fingerprints.sh",
      "/tmp/keys.hosts.fingerprints.sh",
    ]
  }
}

output "droplet_ids" {
  value = "${join(",", digitalocean_droplet.instance.*.id)}"
}

output "droplet_ips" {
  value = "${join(",", digitalocean_droplet.instance.*.ipv4_address)}"
}
