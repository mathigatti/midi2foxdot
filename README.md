# midi2code: Coding Billie Eilish - Bad Guy

Small script to convert midi files into FoxDot code (A python live coding framework) to generate covers through python commands.

You can see an example here.

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/fCMHcZfPvDA/0.jpg)](https://www.youtube.com/watch?v=fCMHcZfPvDA)

## Requirements

- python
- music21 python library (Try something like: `pip install music21`)

## Usage
It is used running the main script `midi2code.py` it takes an input midi file and converts that into a text file that can be used inside FoxDot the python live coding framework.

Usage example

```
python midi2code.py INPUT_MIDI

python midi2code.py midis/bad_guy.mid
```

Possible problems
Sometimes different instruments might not be synched, usually changing the 4 in `start = Clock.mod(4)` with some other multiple of 4 like 8, 12 or 16 fixes the problem. I'm not sure why it happens, It's something I still need to fix.
