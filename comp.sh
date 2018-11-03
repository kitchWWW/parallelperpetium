rm out.*
python compile.py
/Applications/LilyPond.app/Contents/Resources/bin/lilypond out.ly
open out.pdf