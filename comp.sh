rm out.*
python create.py
/Applications/LilyPond.app/Contents/Resources/bin/lilypond out.ly
open out.pdf