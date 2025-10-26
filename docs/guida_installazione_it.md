# Guida rapida all'uso del repository

Questa guida riassume i passaggi essenziali per iniziare a utilizzare il progetto **whisper.cpp** partendo da un ambiente vuoto.

## 1. Clonare il repository

Assicurati di avere installato `git`, quindi esegui:

```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
```

## 2. Scaricare un modello

I modelli convertiti nel formato `ggml` si trovano nella cartella [`models`](../models). Per scaricarne uno pronto all'uso puoi utilizzare lo script incluso:

```bash
bash ./models/download-ggml-model.sh base.en
```

## 3. Compilare l'esempio principale

Per generare il binario di esempio `main`, esegui `make` dalla radice del progetto:

```bash
make
```

## 4. Trascrivere un file audio di esempio

Dopo la compilazione puoi provare la trascrizione utilizzando uno dei file audio di prova inclusi:

```bash
./main -f samples/jfk.wav
```

## 5. Ulteriori risorse

- Consulta il [README principale](../README.md) per approfondimenti e opzioni avanzate.
- Esplora la cartella [`examples`](../examples) per altri casi d'uso, come lo streaming da microfono o l'esecuzione sul web.

Questi passaggi forniscono un percorso rapido per "caricare" e utilizzare il repository con impostazioni standard.
