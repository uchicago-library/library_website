# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "torchbox/wagtail-stretch64"
  config.vm.box_version = "1.0.0"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8000" will access port 8000 on the guest machine.
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = false
    # Customize the amount of memory on the VM:
    vb.memory = "4096"
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL

    PROJECT_DIR=/vagrant
    VIRTUALENV_DIR=/home/vagrant/lw
    PYTHON=$VIRTUALENV_DIR/bin/python

    # Create the django error log
    echo "Creating /var/log/django-errors.log"
    touch /var/log/django-errors.log
    chown vagrant /var/log/django-errors.log
    chgrp vagrant /var/log/django-errors.log

    # Install dependencies
    echo "Installing dependencies" 
    apt-get update
    apt-get install -y libxml2-dev
    apt-get install -y libxslt-dev

    # Create a Postgres user and database
    echo "Creating Postgres user and database"
    sudo -u postgres createuser owning_user
    sudo -u postgres createdb -O vagrant lib_www_dev

    # Create a Python virtualenv
    echo "Creating a Python virtualenv"
    cd /home/vagrant && virtualenv lw 

    # Pip install project dependencies
    echo "Pip installing project dependencies"
    source lw/bin/activate && cd /vagrant/ && pip install -r requirements.txt
   
    # Start Elasticsearch
    systemctl enable elasticsearch
    systemctl start elasticsearch

    # Remove packages we don't need
    echo "Removing pacakages we don't need" 
    apt-get autoremove -y

    # Run migrations, load the dev db and build a search index
    echo "Running django migrations and loading the dev database"
    su - vagrant -c "$PYTHON $PROJECT_DIR/manage.py migrate --noinput && \
                     $PYTHON $PROJECT_DIR/manage.py loaddata /vagrant/base/fixtures/test.json && \
                     $PYTHON $PROJECT_DIR/manage.py update_index"

    # Create the static news feed JSON file
    echo "Installing the news feed test file"
    mkdir -p /vagrant/static/lib_news/files
    cp /vagrant/base/fixtures/news-feed-test.json /vagrant/static/lib_news/files/lib-news.json

    # Setup /etc/hosts
    echo "Setting up /etc/hosts"
    sudo su -
    echo "127.0.0.1 wwwdev" >> /etc/hosts
    echo "127.0.0.1 loopdev" >> /etc/hosts
  SHELL
end
