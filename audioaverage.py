import sys
from pydub import AudioSegment
from tempfile import TemporaryFile, NamedTemporaryFile
import wave
import audioop
import glob
import os

if __name__ == '__main__': 
    filepaths = glob.glob(os.getcwd()+"/*.mp3")
    files = [AudioSegment.from_file(path) for path in filepaths]
    bigass = files[0]
    for sound in files[1:]:
        bigass = bigass.overlay(sound)

    bigass.export("combined.wav", format='wav')

"""def muloverlay(self, segs, position=0, loop=False):
    output = TemporaryFile()

    mulsegs = syncem(segs)
    sample_width = mulsegs[0].sample_width
    spawn = mulsegs[0]._spawn

    output.write(mulsegs[0][:position]._data)

    # drop down to the raw data
    seg1 = seg1[position:]._data
    seg2 = seg2._data
    pos = 0
    seg1_len = len(seg1)
    seg2_len = len(seg2)
    while True:
        remaining = max(0, seg1_len - pos)
        if seg2_len >= remaining:
            seg2 = seg2[:remaining]
            seg2_len = remaining
            loop = False

        output.write(audioop.add(seg1[pos:pos + seg2_len], seg2,
                                 sample_width))
        pos += seg2_len

        if not loop:
            break

    output.write(seg1[pos:])

    return spawn(data=output)

def syncem(segs):
    seg_len = [len(seg) for seg in segs]

    channels = max([seg.channels for seg in segs])
    frame_rate = max([seg.frame_rate for seg in segs])
    sample_width = max ([seg.sample_width for seg in segs])
    for seg in segs:
        seg.channels = channels
        seg.frame_rate = frame_rate
        seg.sample_width = sample_width

    seg_len2 = [len(seg) for seg in segs]
    assert(seg_len == seg_len2)

    return segs"""