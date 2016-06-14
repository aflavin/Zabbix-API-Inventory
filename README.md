# Zabbix-API-Inventory
Python script to pull inventory data from Zabbix.
Written in pycharm edu 2.0.4 for Python 3.5.1
The script must be run at the python interpreter.
The script asks for the URL of a Zabbix server and uses regex to check that it is a valid URL (eg. http://192.168.2.7/zabbix, https://zabbixcom/zabbix)
The script then attempts to authenticate to the zabbix server using user-supplied credentials, trying up to five times, at which the Zabbix server will lock out the user that is attempting to log on.
After successful authentication, the script requests all items for all hosts on the server that belong to the application "Inventory".
The script stores hostid, itemid, item name, the last value, units, and the description, then writes them into a csv file formatted to be compatible with excel. 
