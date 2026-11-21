# Bigger logo pill for the viral4 cut (Alan 11-20: "You think YardSwaps should be bigger?"): the same top-left lockup,
# about 1.4x in 4:5, 1.27x in 9:16 (clears the band caption), 1.2x in 1:1 (where the bigger pill would hit the photo band). Writes vr-<ratio>/brand-big.png.
import os, runpy, sys
D = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(D, "layout-viral.py")).read().split("LINES = [")[0]   # imports, W, WM, SIZES and badge() only
g = {"__file__": os.path.join(D, "layout-viral.py")}; exec(src, g)
for key, glyph in (("9x16-paid", 66), ("4x5", 74), ("1x1", 62)):
    z = g["SIZES"][key]; k = glyph / 52
    g["badge"](z["H"], z["badgeY"], glyph_h=glyph, pad_x=round(34 * k), pad_y=round(22 * k)).save(os.path.join(D, "vr-" + key, "brand-big.png"))
    print(key, glyph)
