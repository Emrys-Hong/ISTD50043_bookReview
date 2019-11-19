# One-tme set up for mysql
sudo apt update
sudo apt install mysql-server

# Add right for root user
sudo mysql -e 'update mysql.user set plugin = "mysql_native_password" where User="root"'
sudo mysql -e 'create user "root"@"%" identified by ""'
sudo mysql -e 'grant all privileges on *.* to "root"@"%" with grant option'
sudo mysql -e 'flush privileges'
sudo service mysql restart

# open connection for all IP address
sudo systemctl stop mysql
sudo sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/mysql.conf.d/mysqld.cnf

# add files for mysqld running
sudo mkdir -p /var/run/mysqld 
sudo chown mysql:mysql /var/run/mysqld 
nohup sudo mysqld_safe --skip-grant-tables &

# download bash cript for SQL set up
wget https://database-project-50043.s3-us-west-2.amazonaws.com/load_sql_db.sh





