Pipeline: build.py → purgecss (build/tmp) → finish.py → flatten.py → ccsafe.py → extcss.py → push.
Il CSS va in un file esterno con hash nel nome (CC importa il CSS esterno senza toccarlo, ma non sovrascrive file con lo stesso nome).
Verifica finale: import da URL nel builder CC reale e controllo canvas desktop + mobile.
