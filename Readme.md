# Quietnet

Simple chat program using near ultrasonic frequencies. Works without Wifi or Bluetooth and won't show up in a pcap.

Note: If you can clearly hear the send script working then your speakers may not be high quality enough to produce sounds in the near ultrasonic range.

## Usage

run `python send.py` in one terminal window and `python listen.py` in another. Text you input into the send.py window should appear (after a delay) in the listen.py window.

**Warning:** May annoy some animals and humans.

![Screenshot](https://raw.github.com/Katee/quietnet/master/screenshot.png)

## Installation

Quietnet is dependant on [pyaudio](http://people.csail.mit.edu/hubert/pyaudio/) and [Numpy](http://www.numpy.org/).

## Better Projects

Quietnet is just a toy! Here are some more robust and polished projects to look at:
* [quiet-js](https://quiet.github.io/quiet-js/) (works in the browser!)
* [minimodem](http://www.whence.com/minimodem/)
* [gnuradio](http://gnuradio.org/)
