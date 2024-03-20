#!/bin/ash

# Überprüfen, ob ein Dateiname als Argument übergeben wurde
if [ $# -ne 1 ]; then
    echo "Usage: $0 filename"
    exit 1
fi

filename=$1

# Überprüfen, ob die Datei existiert
if [ ! -f "$filename" ]; then
    echo "File does not exist: $filename"
    exit 2
fi

tempfile=$(mktemp) # Erstellt eine temporäre Datei

# Sicherstellen, dass die letzte Zeile verarbeitet wird, auch wenn kein abschließender Zeilenumbruch existiert
while IFS= read -r line || [[ -n "$line" ]]; do
    # Nutzt eval und echo, um die Variablen in jeder Zeile zu expandieren
    eval echo \""$line"\"
done < "$filename" > "$tempfile"

# Ersetze die Originaldatei durch die modifizierte Datei
mv "$tempfile" "$filename"
