# pixel-store

[![roundtrip-test](https://github.com/Kushalr3ddy/pixel-store/actions/workflows/roundtrip.yml/badge.svg)](https://github.com/Kushalr3ddy/pixel-store/actions/workflows/roundtrip.yml)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/kushalr3ddy/pixel-store)

Store any file inside a **video** of black-and-white squares. Upload that video
to any video host (YouTube, etc.) and you get free, effectively unlimited
storage — then download it later and decode it back to the exact original file.

```
file ──▶ bits ──▶ black/white squares ──▶ frames ──▶ video  ──▶ upload
file ◀── bits ◀── black/white squares ◀── frames ◀── video  ◀── download
```

## How it works

- **Bits to pixels.** Every file is just bytes, every byte is 8 bits. Each bit
  becomes a small square on a video frame — `1` = black, `0` = white. Frames are
  stitched into one video.
- **Frame 0 is metadata.** The first frame stores a small JSON note (filename,
  exact bit count, cell size, parity, and an md5 checksum) so the decoder knows
  how to rebuild the file and can verify it came out perfect.
- **Big cells beat compression.** Each bit is a `4x4` pixel cell by default.
  Tiny cells get smeared into grey by lossy video compression; `4x4` cells stay
  cleanly black or white so the data survives a real YouTube re-encode.
- **Reed–Solomon self-repair.** The bytes are wrapped in error-correcting parity
  before encoding, so a handful of pixels mangled by compression get *repaired*
  on decode instead of corrupting the whole file.

For the full, plain-English walkthrough see **[HOW_THIS_WORKS.txt](HOW_THIS_WORKS.txt)**.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```python
from pixelstore.encoder import Encoder
from pixelstore.decodr import Decoder

# file  ->  video   (writes output/dummy.avi)
Encoder("dummy.pdf").encode()

# video ->  file     (writes decoded_files/dummy.pdf)
Decoder("output/dummy.avi").decode_data()
```

The decoder verifies the md5 against the checksum baked into the metadata frame,
so it tells you whether the result is byte-for-byte identical.

### Options

```python
Encoder("dummy.pdf", pix_size=64)  # 8x8 cells: tougher against compression, bigger video
Encoder("dummy.pdf", parity=0)     # no error correction: smallest output
Encoder("dummy.pdf", parity=64)    # double the Reed-Solomon repair budget
```

| option     | default | what it does                                                        |
|------------|---------|---------------------------------------------------------------------|
| `pix_size` | `16`    | pixels per bit-cell (perfect square: 4, 16, 64 → 2x2, 4x4, 8x8)     |
| `parity`   | `32`    | Reed–Solomon parity bytes per block (0 disables error correction)   |

## Project layout

```
pixelstore/
  encoder.py       file  -> video
  decodr.py        video -> file   (the current decoder)
  ecc.py           Reed-Solomon error-correction helpers
  color.py         which colors mean 0 and 1
  resolutions.py   frame sizes (480p, 720p, ...)
  hash_gen.py      md5 / sha1 checksums
tools/             misc byte/bit inspection scripts
test.py            example encode/decode driver
```

## Tests

A round-trip check lives in [`.github/workflows/roundtrip.yml`](.github/workflows/roundtrip.yml):
it md5s `dummy.pdf`, encodes it to video, decodes it back, and fails if the
result isn't byte-identical. Run it from the **Actions** tab via *Run workflow*
(manual dispatch).

## License

See [LICENSE](LICENSE).
