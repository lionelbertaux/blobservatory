
UUID=AD69-1F4B		/mnt/key	vfat auto,owner,rw,uid=1000,gid=1000 0 0 
*/10 * * * * pi cd /home/pi/scripts/blobservatory && python3 blobservatory.py --mode cron --directory /mnt/key/captures/ --awb-mode cloudy --preview 5
1-59/10 * * * * pi  rclone sync /mnt/key/captures/ gdrive:captures/
