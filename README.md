# Setup

Das setup.ipynb erstellt alle simulierte Datenbanktabellen (siehe PDF Beschreibung) und speichert sie in ein ddi.db File

# Docker Container

Danach wird ein Docker Container erstellt (dieses übernimmt dann eine passende Python Umgebung und installiert die Packages aus dem requirements.txt):

```
docker build -t meu_ddi_interaction .   
```

Diese wird danach gestartet:

```
docker run -p 5001:5000 meu_ddi_interaction
```

Danach läuft das Tool grundsätzlich unter localhost:5001/