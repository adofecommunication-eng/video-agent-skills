# Reel « Well Brunch » — Wellbeing Resort (WBR)

Reel vertical 9:16, 18 secondes, 1080x1920, 30 i/s. Client : Wellbeing Resort, Cocody Riviera 3, route M'Badon.

## Livrables

| Fichier | Contenu |
|---|---|
| `rendu/well-brunch-reel-18s-sous-titres.mp4` | **Version finale** : voix off Lola + musique légère + sous-titres incrustés |
| `rendu/well-brunch-reel-18s.mp4` | Même version sans sous-titres incrustés (pour charger le `.srt` sur Facebook) |
| `rendu/planche-apercu.jpg` | Une image par séquence |
| `rendu/voix-off.srt` | Sous-titres calés sur la voix réelle (8 répliques) |
| `render.py` | Rendu image + mixage (`python3 render.py`, `--subs` pour incruster les sous-titres, `--stills` pour les aperçus) |
| `music.py` | Compose la musique légère (`sources/musique-legere.wav`) |
| `remix.py` | Refait seulement le mixage audio d'une vidéo déjà rendue |
| `sources/voix-off-lola.mp3` | Voix off ElevenLabs (Lola), 17,4 s |
| `sources/flyer-well-brunch.png` | Flyer officiel, seule source image |

## Direction artistique

- **Univers** : noir chaud + or, comme le flyer. Plans au format cinéma 2.35:1 cerclés d'un filet or, fond flou de la scène.
- **Typos (règle du client)** : **Anton** en principale (titres, accroches, prix, numéros) ; **Helvetica Neue** en secondaire (horaires, adresse, infos pratiques, sous-titres). En l'absence du fichier Helvetica Neue, le rendu utilise **TeX Gyre Heros**, clone libre d'Helvetica ; déposer `HelveticaNeue-Bold.otf` dans `fonts/` suffit pour qu'il soit pris automatiquement.
- **Synchronisation voix / image** : chaque mot clé apparaît sur la syllabe où Lola le prononce (instants mesurés sur la voix, table `CUE` dans `render.py`). Les mots « claquent » (arrivée en grand + secousse brève), les coupes tombent sur la voix.

## Script parlé (voix off, ~17 s)

« Samedi, vous n'aurez qu'une seule question : par quoi commencer ? Buffet à volonté de 12h à 18h30, piscine, baby-foot, billard, karaoké et ambiance DJ. Le pass : 10.000 francs. Venez entre amis ou en famille. Écrivez “BRUNCH” pour réserver. »

## Son

- **Voix off** : ElevenLabs « Lola », décalée de 0,15 s, nettoyée (coupe-bas 90 Hz, présence +2 dB à 3,5 kHz, compression douce).
- **Musique** : composition originale lounge / amapiano doux à 100 BPM, dont la grille démarre sur le mot « PAR ». Silence de suspense entre « …une seule question : » et « par quoi commencer ? », souffle aspiré, puis trois impacts sur PAR / QUOI / COMMENCER où le groove entre. Souffle + impact doux à chaque coupe, scintillement sur chaque activité prononcée, compteur qui tique pendant que le prix défile, impact sur « BRUNCH ».
- **Mixage** : la musique s'efface sous la voix (ducking), environ 10 dB sous la voix. -14 LUFS, crête -1,5 dBFS.

## Montage du rendu actuel (calé sur la voix)

| Temps | Voix | Image et texte |
|---|---|---|
| 0–2,35 s | « Samedi, vous n'aurez qu'une seule question : » | Table en plan large · SAMEDI, (0,15 s) · UNE SEULE QUESTION : (1,5 s) |
| 2,35–2,75 s | silence | Tout s'efface : suspense |
| 2,75–4,1 s | « par quoi commencer ? » | PAR (2,75) · QUOI (2,99) · COMMENCER ? en or (3,21), impacts + éclat |
| 4,1–7,05 s | « Buffet à volonté de 12h à 18h30 » | BUFFET À VOLONTÉ (4,15) · SAMEDI · 12H – 18H30 (4,97) · buffet puis verres |
| 7,05–11,6 s | « piscine, baby-foot, billard, karaoké et ambiance DJ » | Chaque activité tombe sur son mot (7,17 · 7,85 · 8,57 · 9,45 · 10,21) |
| 11,6–15,4 s | « Le pass : 10.000 francs. Venez entre amis ou en famille. » | Badge sur « pass » · prix qui défile jusqu'à 10.000 FCFA · ENTRE AMIS (13,6) · OU EN FAMILLE (14,5) |
| 15,4–18 s | « Écrivez “BRUNCH” pour réserver. » | Logo · WELL BRUNCH · ÉCRIVEZ (15,47) · « BRUNCH » (15,83) · POUR RÉSERVER + numéros (16,1) · adresse |

## Tournage réel (version 2, à filmer sur place un samedi)

Le flyer ne contient ni piscine, ni baby-foot, ni billard : la séquence 6–12 s est donc typographique. Pour la version tournée, garder la même structure et le même habillage, en remplaçant les plans :

| Temps | Plan à filmer (vertical 9:16, 4K 50 i/s pour ralentir) |
|---|---|
| 0–3 s | Plongée sur le buffet, mains qui se servent, vapeur en contre-jour (filmer face au soleil, 12h–13h) |
| 3–6 s | Gros plan d'une assiette garnie, puis verres qui trinquent (ralenti 50 %) |
| 6–9 s | Baby-foot et billard : mains, balle, rires (caméra à hauteur de table) |
| 9–12 s | Plongeon dans la piscine, caméra à ras de l'eau (pochette étanche) |
| 12–15 s | Groupe d'amis qui rit à table, léger travelling latéral |
| 15–18 s | Carte finale (reprendre celle du rendu) |

Astuces : lumière de fin de matinée, tenues claires (blanc, beige, or), autorisation écrite des personnes filmées, zones de texte entre 250 px et 1 560 px du haut (hors interface Instagram/Facebook).

## Légende de publication

Samedi, on se retrouve au Well Brunch 🥂 Buffet à volonté de 12h à 18h30, piscine, baby-foot, billard, karaoké et ambiance DJ. Pass : 10.000 FCFA. Réservez au 07 47 79 95 07 / 05 66 92 33 91 ou écrivez « BRUNCH » en commentaire. 📍 Cocody Riviera 3, route M'Badon.

#WellBrunch #WellbeingResort #BrunchAbidjan #Abidjan #Cocody #SortieAbidjan #Samedi #BuffetAVolonte
