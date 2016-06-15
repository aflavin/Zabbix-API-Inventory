import sys
import getopt
import datetime
import csv
import re
import argparse
import requests
import tkinter as tk
from tkinter import filedialog
from pyzabbix import ZabbixAPI,ZabbixAPIException


def main():
    global z
    #try:
    #    opts, args = getopt.getopt(argv,"hp:s:u:",["password=", "server=", "user="])
    #except getopt.GetoptError:
    #    print("cli-inventory.py -s -server= <server> -u -username= <username> -p -password= <password>")
    #    sys.exit(2)
    #for opt, arg in opts:
    #    if opt == '-h':
    #        print("cli-inventory.py -s -server= <server> -u -username= <username> -p -password= <password>")
    #        sys.exit()
    #    elif opt in ("-s", "-server="):
    #        serverip = arg
    #    elif opt in ("-u", "-username="):
    #        user = arg
    #    elif opt in ("-p", "-password="):
    #        password = arg
    parser = argparse.ArgumentParser(description='This is an inventory export script for Zabbix by Alexander Flavin.')
    parser.add_argument('-s', '--server', help='URL of Zabbix Server', required=True)
    parser.add_argument('-u', '--username', help='Username used to log in to Zabbix Server', required=True)
    parser.add_argument('-p', '--password', help='Password used to log in to Zabbix Server', required=True)
    parser.add_argument('-f', '--filepath', help='Path to save the inventory file.', required=False)
    args = parser.parse_args()
    user = args.username
    password = args.password
    serverip = args.server
    filepath = args.filepath
    if len(serverip) > 0 and len(user) > 0 and len(password) > 0:
        if validateserver(serverip):
            z = ZabbixAPI(serverip)
            try:
                z.login(user=user, password=password)
                print("Now logged into ZabbixAPI version " + z.api_version())
            except ZabbixAPIException as e:
                print(e, "\nProgram will now close.")
                sys.exit(2)
            except requests.Timeout as f:
                print(f, "\nProgram will now close.")
                sys.exit(2)
        else:
            print("Must enter a correct URL for the Zabbix server (eg. http://192.168.0.4/zabbix).")
            sys.exit(2)
    else:
        print("Required parameter missing.")
        sys.exit(2)
    if filepath is not None:
        return filepath
    else:
        return 'arbitrary'


def getinventory(listname, hostid=''):
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


def writecsv(writelist, filepath):
    """Writes the data contained in the list of lists to a .csv file that can be opened in Excel with one click.

       Handles the file path passed from main(). Checks to see if the path is a directory or a .csv file. If .***
       is not found at the end of the file, it appends a default name and extension and saves in the current working
       directory.
    """
    if re.search('arbitrary', filepath):
        filepath = ''
        filename = 'Inventory_' + str(datetime.date.today()) + ".csv"
    else:
        if re.search('\.csv$', filepath):
            filename = ''
        elif re.search('\....$', filepath) or re.search('\.....$', filepath):
            filename = '.csv'
        else:
            filename = '\Inventory_' + str(datetime.date.today()) + ".csv"
    try:
        with open(filepath + filename, 'w', newline='') as result:
            writer = csv.writer(result, dialect='excel')
            header = ['Host', 'Item ID', 'Name', 'Value', 'Units', 'Description']
            writer.writerow(header)
            writer.writerows(writelist)
    except OSError as e:
        print(e)
        sys.exit(2)


def getfilepath():
    """Calls tk to create a file dialog that asks the user where they want to place the file."""
    # If root.withdraw() is added, window is only accessible by alt-tab.
    root = tk.Tk()
    return filedialog.asksaveasfilename(initialdir='C:/', defaultextension='.csv',
                                             initialfile='Inventory ' + str(datetime.date.today()),
                                             filetypes=(("Comma Separated Values",'*.csv'),("All Files", '*.*')))


if __name__ == '__main__':
    list1 = []
    dict1 = {}
    file_path = main()
    getinventory(list1)
    gethostdict(dict1)
    hostchange(list1, dict1)
    writecsv(list1, file_path)
    print("Complete.")
