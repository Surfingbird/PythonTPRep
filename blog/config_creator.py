import configparser

config = configparser.ConfigParser()
config.add_section("Settings")
config.set("Settings", "host", "localhost")
config.set("Settings", "user", "root")
config.set("Settings", "password", "2206")
config.set("Settings", "database", "BlogDB")
config.set("Settings", "port", "3306")

with open('settings.config', "w") as config_file:
    config.write(config_file)

config.read('settings.config')
host = config.get('Settings', 'host')
user = config.get('Settings', 'user')
password = config.get('Settings', 'password')
database = config.get('Settings', 'database')
port = config.get('Settings', 'port')
print(host, user, password, database, port)
