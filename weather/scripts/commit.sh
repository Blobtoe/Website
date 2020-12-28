git -C /home/pi/website/ pull origin master
git -C /home/pi/website/ add --all
git -C /home/pi/website/ commit -m "'$1'"
git -C /home/pi/website/ push origin master