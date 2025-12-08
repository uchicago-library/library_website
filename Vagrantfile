# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  # https://app.vagrantup.com/ubuntu/boxes/jammy64
  config.vm.box = "ubuntu/jammy64"
  config.vm.box_version = "20240720.0.1"

  es = "true"
  if ENV['ELASTICSEARCH']
    es = ENV['ELASTICSEARCH']
  end

  njs = "true"
  if ENV['NODEJS']
    njs = ENV['NODEJS']
  end

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
    vb.memory = "10240"
    vb.cpus = 8

    # Read shared developer documentation
    up_message = File.read('dev-docs.txt')

    config.vm.post_up_message = up_message
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

  # Normal provisioning
  config.vm.provision "shell", inline: <<-SHELL, args: [es, njs]

    # Force the build to fail if a command fails
    set -e

    PROJECT_DIR=/vagrant
    VIRTUALENV_DIR=/home/vagrant/lw
    PYTHON=$VIRTUALENV_DIR/bin/python
    VAGRANT_HOME=/home/vagrant

    # Silence "dpkg-preconfigure: unable to re-open stdin" warnings
    export DEBIAN_FRONTEND=noninteractive

    if [ "$1" == "false" ]; then
        echo "============== Building without Elasticsearch and Java =============="
        echo "..."
    fi

    if [ "$2" == "false" ]; then
        echo "============== Building without NVM and NodeJS =============="
        echo "..."
    fi

    if [ "$2" != "false" ]; then
        echo "============== Installing NVM and NodeJS =============="
        curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
        NODE_MAJOR=18
        echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
        apt-get update
        apt-get install nodejs -y
        su - vagrant -c "cd $PROJECT_DIR && npm install --no-save"
        npm install eslint@8.57.0
        npm i prettier eslint-plugin-prettier eslint-config-prettier
        npm install eslint-config-airbnb
        npm install -g install-peerdeps -y
        cd /vagrant/
        npm install
    fi

    # Create the django error log
    echo "============== Creating /var/log/django-errors.log =============="
    echo "..."
    touch /var/log/django-errors.log
    chown vagrant /var/log/django-errors.log
    chgrp vagrant /var/log/django-errors.log

    # Update repos
    echo ""
    echo "============== Updating repos =============="
    rm -rf /var/lib/apt/lists/partial
    apt-get update -y -o Acquire::CompressionTypes::Order::=gz

    # Jammy ships wih Python 10. We need Python 11.
    # Remove this to go to Python 10 in the future.
    echo ""
    echo "============== Upgrading to Python 3.11 =============="
    apt-get install -y software-properties-common
    add-apt-repository ppa:deadsnakes/ppa
    apt-get install -y python3.11
    apt-get -y install python3.11-distutils
    apt-get install -y python3-pip python3.11-dev python3.11-venv

    # Install Wagtail dependencies and useful dev tools
    echo -e ""
    echo "============== Installing Wagtail dependencies and setting up useful dev tools =============="
    apt-get install -y vim git curl gettext build-essential
    mkdir -p $VAGRANT_HOME/.vim/pack/git-plugins/start
    git clone --depth 1 https://github.com/dense-analysis/ale.git $VAGRANT_HOME/.vim/pack/git-plugins/start/ale
    apt-get install -y libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev libllvm11
    apt-get install -y redis-server postgresql libpq-dev
    touch $VAGRANT_HOME/.vimrc
    echo "let g:ale_linters_explicit = 1" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_linters = { 'python': ['flake8'], 'javascript': ['eslint'] }" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_fixers = { 'python': ['isort', 'autopep8', 'black'], 'javascript': ['eslint'] }" >> $VAGRANT_HOME/.vimrc
    # Note: flake8 options are read from .flake8
    # Note: black and isort options are read from pyproject.toml

    # Install UChicago dependencies
    echo ""
    echo "============== Installing UChicago dependencies =============="
    apt-get update -y
    apt-get install -y libxml2-dev
    apt-get install -y libxslt-dev

    # Java for Elasticsearch
    if [ "$1" != "false" ]; then
        echo ""
        echo "============== Installing Java for Elsasticsearch =============="
        apt-get update -y
        apt-get install -y openjdk-11-jre-headless ca-certificates-java
    fi

    # We need virtualenv >13.0.0 in order to get pip 7 to automatically install
    echo ""
    echo "============== Virtualenv =============="
    pip3 install virtualenv

    # Create a Postgres user and database
    echo ""
    echo "============== Creating Postgres user and database =============="
    echo "..."
    su - postgres -c "createuser -s vagrant"
    sudo -u postgres createdb -O vagrant lib_www_dev

    # Elasticsearch
    if [ "$1" != "false" ]; then
        echo ""
        echo "============== Downloading Elasticsearch =============="
        wget -q https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.13-amd64.deb
        dpkg -i elasticsearch-7.17.13-amd64.deb
        # reduce JVM heap size from 2g to 512m
        sed -i 's/^\(-Xm[sx]\)2g$/\1512m/g' /etc/elasticsearch/jvm.options
        rm elasticsearch-7.17.13-amd64.deb
        echo "xpack.security.enabled: false" | sudo tee -a /etc/elasticsearch/elasticsearch.yml > /dev/null
    fi

    # Create a Python virtualenv
    echo ""
    echo "============== Creating a Python virtualenv =============="
    echo "..."
    cd /home/vagrant && python3.11 -m venv lw

    # Pip install project dependencies
    echo ""
    echo "============== Pip installing project dependencies =============="
    source lw/bin/activate
    pip install --upgrade pip
    cd /vagrant/
    pip install -r requirements.txt && pip install -r requirements-dev.txt
   
    # Start Elasticsearch
    if [ "$1" != "false" ]; then
        echo ""
        echo "============== Starting Elasticsearch =============="
        systemctl enable elasticsearch
        systemctl start elasticsearch
    fi

    # Make a static directory if one does not exist
    echo ""
    echo "============== Make static directories if needed =============="
    echo "..."
    mkdir -p static
    mkdir -p library_website/static # I have no idea why this is needed. It shouldn't be.

    # Remove packages we don't need
    echo ""
    echo "============== Cleaning up =============="
    apt-get autoremove -y
    # Remove Python tests pycache (only used for testing Python itself. Saves 29.5MB)
    rm -rf /usr/local/lib/python3.7/test/__pycache__
    apt-get clean

    # Run migrations, load the dev db and build a search index
    echo ""
    echo "============== Running django migrations and loading the dev database =============="
    su - vagrant -c "$PYTHON $PROJECT_DIR/manage.py migrate --noinput && \
                     $PYTHON $PROJECT_DIR/manage.py loaddata /vagrant/base/fixtures/test.json && \
                     $PYTHON $PROJECT_DIR/manage.py shell -c \"from wagtail.models import Site; Site.objects.filter(hostname='localhost').delete()\" && \
                     $PYTHON $PROJECT_DIR/manage.py update_index"

    # Create the static news feed JSON file
    echo ""
    echo "============== Creating the news feed test file =============="
    echo "..."
    mkdir -p /vagrant/static/lib_news/files
    cp /vagrant/base/fixtures/news-feed-test.json /vagrant/static/lib_news/files/lib-news.json

    # Setup /etc/hosts
    echo ""
    echo "============== Setting up /etc/hosts =============="
    echo "..."
    sudo su -
    echo "127.0.0.1 wwwdev" >> /etc/hosts
    echo "127.0.0.1 loopdev" >> /etc/hosts

    # Fix git permissions
    echo ""
    echo "============== Fixing git permissions =============="
    echo "..."
    sudo chown -R vagrant /home/vagrant

    # Add some dev sweetness
    echo ""
    echo "============== Simplicity for developers =============="
    echo "..."
    echo "source lw/bin/activate" >> /home/vagrant/.bashrc
    echo "cd /vagrant/" >> /home/vagrant/.bashrc
    echo "export PATH=\"/vagrant/node_modules/.bin:$PATH\"" >> /home/vagrant/.bashrc
    echo "export TURNSTILE_ENABLED=\"False\"" >> /home/vagrant/.bashrc
  SHELL
end
