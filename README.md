# Camp2Code_Project_1

## GIT-Wiki:
#### Klonen eines vorhandenen Repositorys
* git clone git@github.com:a3k2011/Camp2Code-Gruppe-4-Phase-1.git

#### Prüfung auf geänderte Dateien im eigenen Arbeitsverzeichnis
* git status

#### Auflistung aller durchgeführten push-Vorgänge
* git log

#### Arbeitsverzeichnis auf den aktuellen Status bringen
* git pull

#### Arbeitsverzeichnis zu GIT-Hub hochladen
1. git add --all oder (git add beispiel.txt)
2. git commit -m "Hier steht das Kommentar"
3. git push

## GIT-Einrichtung
* ssh-keygen -o (Beide Abfragen leer bestätigen.)
* cat /home/pi/.ssh/id_rsa.pub
* SSH-Key in GitHub einfügen

#### GIT-Config prüfen
* git config --list

## .gitignore
Ignoriert im Arbeitsverzeichnis die folgenden Dateien bzw. Ordner:
* \*.json
* /Logger
* /\__pycache__

## SD-Karte klonen / Backup
Tool: Win32 Disk Imager
1. Backup erstellen, indem *.img-Datei von altem Datenträger erstellt wird.
2. Backup lesen, indem *.img-Datei auf neuen Datenträger geschrieben wird
3. Partition auf Raspberry Pi erweitern, mit folgendem Befehl:
* sudo raspi-config --expand-rootfs
