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
  config.vm.box_version = "20221219.0.0"

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

    up_message = <<-MSG

    WRITE SOME CODE!!!
         ___________________________            ____
    ...  \____DLDC_220_________|_// __=*=__.--"----"--._________
                        \  |        /-------.__________.--------'
                   /=====\ |======/      '     "----"
                      \________          }]
                               `--------'
    MAKE IT SO!!!
    MSG

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

  # Some provisioning as the Vagrant user
  config.vm.provision "shell", inline: <<-SHELL, privileged: false
    # NVM and Node JS
    echo ""
    echo "============== Installing NVM and NodeJS =============="
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.36.0/install.sh | bash
    source $HOME/.nvm/nvm.sh
    nvm install --lts
    npm install --save-dev eslint
    npm i -D prettier eslint-plugin-prettier eslint-config-prettier
    npm install eslint-config-airbnb --save-dev
    npx install-peerdeps -y --dev eslint-config-airbnb
  SHELL

  # Normal provisioning
  config.vm.provision "shell", inline: <<-SHELL

    PROJECT_DIR=/vagrant
    VIRTUALENV_DIR=/home/vagrant/lw
    PYTHON=$VIRTUALENV_DIR/bin/python
    VAGRANT_HOME=/home/vagrant

    # Silence "dpkg-preconfigure: unable to re-open stdin" warnings
    export DEBIAN_FRONTEND=noninteractive

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
    #apt-get update -y

    # Jammy ships wih Python 10. We need Python 9.
    # Remove this to go to Python 10 in the future.
    echo ""
    echo "============== Downgrading to Python 3.9 =============="
    apt-get install -y software-properties-common
    add-apt-repository ppa:deadsnakes/ppa
    apt-get install -y python3.9
    apt-get -y install python3.9-distutils
    apt-get install -y python3-pip python3.9-dev python3.9-venv

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
    echo "let g:ale_python_flake8_options = '--ignore=D100,D101,D202,D204,D205,D400,D401,E303,E501,W503,N805,N806'" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_fixers = { 'python': ['isort', 'autopep8', 'black'], 'javascript': ['eslint'] }" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_python_black_options = '--skip-string-normalization'" >> $VAGRANT_HOME/.vimrc
    echo "let g:ale_python_isort_options = '--profile black'" >> $VAGRANT_HOME/.vimrc

    # Install UChicago dependencies
    echo ""
    echo "============== Installing UChicago dependencies =============="
    apt-get update -y
    apt-get install -y libxml2-dev
    apt-get install -y libxslt-dev

    # Java for Elasticsearch
    echo ""
    echo "============== Installing Java for Elsasticsearch =============="
    apt-get update -y
    apt-get install -y openjdk-11-jre-headless ca-certificates-java

    # Install poetry and Fabric
    # We need virtualenv >13.0.0 in order to get pip 7 to automatically install
    echo ""
    echo "============== Pip installing poetry, Fabric, and virtualenv =============="
    pip3 install poetry Fabric
    pip3 install virtualenv

    # Create a Postgres user and database
    echo ""
    echo "============== Creating Postgres user and database =============="
    echo "..."
    su - postgres -c "createuser -s vagrant"
    sudo -u postgres createdb -O vagrant lib_www_dev

    # Elasticsearch
    echo ""
    echo "============== Downloading Elasticsearch =============="
    wget -q https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.8.23.deb
    dpkg -i elasticsearch-6.8.23.deb
    # reduce JVM heap size from 2g to 512m
    sed -i 's/^\(-Xm[sx]\)2g$/\1512m/g' /etc/elasticsearch/jvm.options
    rm elasticsearch-6.8.23.deb

    # Create a Python virtualenv
    echo ""
    echo "============== Creating a Python virtualenv =============="
    echo "..."
    cd /home/vagrant && python3.9 -m venv lw

    # Pip install project dependencies
    echo ""
    echo "============== Pip installing project dependencies =============="
    source lw/bin/activate
    pip install --upgrade pip
    cd /vagrant/
    pip install -r requirements.txt && pip install -r requirements-dev.txt
   
    # Start Elasticsearch
    echo ""
    echo "============== Starting Elasticsearch =============="
    systemctl enable elasticsearch
    systemctl start elasticsearch

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
    echo "./manage.py runserver 0.0.0.0:8000" >> /home/vagrant/.bashrc
  SHELL
end
