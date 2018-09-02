# input variables
variable "keyname" { }
variable "public_key_file" { }

# create resources
resource "digitalocean_ssh_key" "default" {
  name = "${var.keyname}-key"
  public_key = "${chomp(file(var.public_key_file))}"
}

# output variables
output "keypair_id" {
  value = "${digitalocean_ssh_key.default.id}"
}
