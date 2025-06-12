#!/usr/bin/env python3
"""
Simple FreeRADIUS Accounting Test for bob
"""

from pyrad.client import Client
from pyrad.dictionary import Dictionary
import pyrad.packet
import time
import uuid

def main():
    # Setup
    username = "bob"
    password = "bob123"
    session_id = str(uuid.uuid4())[:8]
    
    print("FreeRADIUS initialized")
    
    # Connect to RADIUS for authentication
    auth_client = Client(
        server="127.0.0.1",
        authport=1812,
        secret=b"testing123",
        dict=Dictionary("dictionary")
    )
    
    # Connect to RADIUS for accounting
    acct_client = Client(
        server="127.0.0.1",
        acctport=1813,
        secret=b"testing123",
        dict=Dictionary("dictionary")
    )
    
    # Authenticate user
    req = auth_client.CreateAuthPacket(
        code=pyrad.packet.AccessRequest,
        User_Name=username
    )
    req["User-Password"] = req.PwCrypt(password)
    
    reply = auth_client.SendPacket(req)
    
    if reply.code == pyrad.packet.AccessAccept:
        print("Auth is completed")
    else:
        print("Auth failed")
        return
    
    print("Accounting started")
    
    # Start accounting
    req = acct_client.CreateAcctPacket(
        User_Name=username,
        Acct_Status_Type="Start"
    )
    req["Acct-Session-Id"] = session_id
    req["NAS-IP-Address"] = "192.168.1.1"
    req["NAS-Port"] = 1
    
    acct_client.SendPacket(req)
    
    # Wait
    time.sleep(2)
    
    print("Accounting interim update")
    
    # Interim update
    req = acct_client.CreateAcctPacket(
        User_Name=username,
        Acct_Status_Type="Interim-Update"
    )
    req["Acct-Session-Id"] = session_id
    req["Acct-Input-Octets"] = 1000000
    req["Acct-Output-Octets"] = 500000
    req["Acct-Session-Time"] = 120
    
    acct_client.SendPacket(req)
    
    # Wait
    time.sleep(2)
    
    print("Accounting stopped")
    
    # Stop accounting
    req = acct_client.CreateAcctPacket(
        User_Name=username,
        Acct_Status_Type="Stop"
    )
    req["Acct-Session-Id"] = session_id
    req["Acct-Input-Octets"] = 5000000
    req["Acct-Output-Octets"] = 2000000
    req["Acct-Session-Time"] = 300
    req["Acct-Terminate-Cause"] = "User-Request"
    
    acct_client.SendPacket(req)

if __name__ == "__main__":
    main()

