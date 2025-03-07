# Majestic FPV



On Device

Just first update the firmware via sysupgrade (so that the current one is installed 2025.03.05), and then execute majestic_webui to get acquainted with the default WEB interface of OpenIPC IP cameras. Perhaps there will be interesting thoughts in the future.


Then make a backup of current folders on device (optional, recommended)
```
cd /var
cp -r www www.bak
```

Then you need to scp the www folder to the device
```
cd ...
scp -Or www 192.168.1.18:/var
```

Navigate to http://localhost:8080
