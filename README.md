# Live-Chord,Note-Recognition

<h2>Mentions</h2>

This project draws inspiration and uses parts of code from the following projects.

<ol>
<li>
  <a href = https://github.com/orchidas/Chord-Recognition>Chord-Recognition by Orchidas.</a>
</li>
<li>
  <a href = https://github.com/mzucker/python-tuner>python-tuner by mzucker.</a>
</li>
</ol>

<h2>About</h2>
The script extracts musical information from live auido (chords or up to two notes) and displays it at the end.

<h2>How to use</h2>

First you need to run the setup.py file and install the C python extension as well as installing all other dependencies.

After that you need to run one of the following commands depending on the type of analysis you want.

```
python ChordDetector.py -m 'chords'
```

```
python ChordDetector.py -m 'notes'
```
