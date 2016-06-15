import sys
import datetime
import csv
import re
import requests
import tkinter as tk
from tkinter import filedialog
from pyzabbix import ZabbixAPI,ZabbixAPIException


def initializeapi():
    """Initializes the Zabbix API connection and logs the user in.

    Checks that username and password are strings. Login exceptions handled by pyzabbix.
    serverip must be the full url of the server (eg. http://192.168.0.7/zabbix)
    """
    tries = 4
    while tries >= 0:
        user = input("Zabbix username:")
        password = input("Zabbix password:")
        if isinstance(user, str) == True and isinstance(password, str) == True:
            try:
                z.login(user=user,password=password)
                print("Logged into ZabbixAPI version " + z.api_version() + ".")
                return True
            except ZabbixAPIException as e:
                print(e)
                tries -= 1
            except requests.Timeout as f:
                print(f, "\nProgram will now exit.")
                sys.exit(2)
        else:
            print("Username and password must be strings.")
    else:
        print("Too many failed login attempts.")
        return False


def getinventory(listname, hostid='',):
    """Get items from the inventory application from the given hosts.

    hostid is an optional property that can be used to pull data for only certain hosts. Default value ''
    pulls inventory from all hosts on the Zabbix server that have inventory data.
    """
    if isinstance(listname, list):
        if len(hostid) != 0:
            for i in z.item.get(output='extend', hostids=hostid, application='Inventory'):
                 j = [i['hostid'], i['itemid'], i['name'], i['lastvalue'], i['units'], i['description']]
                 listname.append(j)
        else:
            for i in z.item.get(output='extend', application='Inventory'):
                 j = [i['hostid'], i['itemid'], i['name'], i['lastvalue'], i['units'], i['description']]
                 listname.append(j)
    else:
        print("Must pass list variable.")
        return False
    return True


def validateserver(serverip):
    """Checks for 'http://' and 'zabbix' in the serverip to validate the URL.

    Alternatively checks for 'https://' and 'zabbix' for secured connections. This function does not verify the
    existence of the server, only that the correct convention was followed when typing in the address.
    """
    if re.search('http://', serverip) and re.search('zabbix', serverip):
        return True
    elif re.search('https://', serverip) and re.search('zabbix', serverip):
        return True
    else:
        return False


def gethostdict(dictname):
    """Pulls all hostids and names from the Zabbix server and creates a dictionary mapping ids to names."""
    if isinstance(dictname, dict):
        for h in z.host.get(output="extend"):
            dictname[h['hostid']] = h['name']
    else:
        print("Must pass dict variable.")
        return False
    return True

def hostchange(listname, dictname):
    """Replaces hostid in a nested list with a host name.

    A recursive function used to examine and change the base list in a nested-list structure.
    Replaces hostid with host name using a dictionary constructed by gethostdict().
    """
    for index, item in enumerate(listname):
        if isinstance(item, list):
            hostchange(item, dictname)
        elif item in dictname.keys():
            listname[index] = dictname[item]
    return


def writecsv(writelist):
    """Writes the data contained in the list of lists to a .csv file that can be opened in Excel with one click.

       Depends on getfilepath() to define the location and name of the created file.
       If the user "cancels" getfilepath(), the file will be created with the default name in the current
       working directory.
    """
    with open(getfilepath(), 'w', newline='') as result:
        writer = csv.writer(result, dialect='excel')
        header = ['Host', 'Item ID', 'Name', 'Value', 'Units', 'Description']
        writer.writerow(header)
        writer.writerows(writelist)


def getfilepath():
    """Calls tk to create a file dialog that asks the user where they want to place the file."""
    # If root.withdraw() is added, window is only accessible by alt-tab.
    root = tk.Tk()
    return filedialog.asksaveasfilename(initialdir='C:/', defaultextension='.csv',
                                             initialfile='Inventory ' + str(datetime.date.today()),
                                             filetypes=(("Comma Separated Values",'*.csv'),("All Files", '*.*')))


if __name__ == '__main__':
    retries = 4
    while retries >= 0:
        serverip = input("URL of zabbix server:")
        if validateserver(serverip):
            timeout = 3.5
            try:
                z = ZabbixAPI(str(serverip), timeout=timeout)
            except ZabbixAPIException as e:
                print(e)
            if initializeapi():
                break
        elif retries > 0:
            retries -= 1
        else:
            print("Too many failed attempts.")
            sys.exit(2)
    list1 = []
    dict1 = {}
    getinventory(list1)
    gethostdict(dict1)
    hostchange(list1, dict1)
    writecsv(list1)
    print("Complete.")

