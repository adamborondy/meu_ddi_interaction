# Setup

Das setup.ipynb erstellt alle Simulierte Datenbanktabellen (siehe PDF Beschreiung) und speichert sie in ein ddi.db File.

# Docker Container

Danach wird ein Docker Container erstellt (dieses übernimmt dann ein passende Python Umgebung und instelliert die Packages aus dem requirements.txt):

```
docker build -t meu_ddi_interaction .   
```

Und danach gestartet

```
docker run -p 5001:5000 meu_ddi_interaction
```

Danach läuft das Tool grundsätzlich unter localhost:5001/