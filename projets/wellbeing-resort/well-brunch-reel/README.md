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
- **Typos** : Anton (titres, comme « BUFFET À VOLONTÉ » du flyer), Kaushan Script (touches manuscrites or, rappel du logo « Well Brunch »), Montserrat (infos).
- **Rythme** : une info par séquence, révélations en masque, éclats dorés aux coupes, fondu au noir final pour la boucle.

## Script parlé (voix off, ~17 s)

« Samedi, vous n'aurez qu'une seule question : par quoi commencer ? Buffet à volonté de 12h à 18h30, piscine, baby-foot, billard, karaoké et ambiance DJ. Le pass : 10.000 francs. Venez entre amis ou en famille. Écrivez “BRUNCH” pour réserver. »

## Son

- **Voix off** : ElevenLabs « Lola », décalée de 0,15 s, nettoyée (coupe-bas 90 Hz, présence +2 dB à 3,5 kHz, compression douce).
- **Musique** : composition originale, lounge / amapiano doux à **100 BPM**. Un temps dure 0,6 s, donc les coupes à **2,4 s · 6 s · 12 s · 15 s** tombent toutes sur un temps. L'accroche (0–2,4 s) n'a que la nappe et le shaker ; le rythme (kick doux, basse log drum, piano en contretemps) entre sur la coupe de 2,4 s. Souffle montant avant chaque coupe, impact doux et scintillement dessus. Fondu final à partir de 17 s.
- **Mixage** : la musique s'efface automatiquement quand la voix parle (ducking), environ 10 dB sous la voix. Niveau final -14 LUFS, crête -1,5 dBFS (norme Instagram / Facebook).

## Montage du rendu actuel

| Temps | Image | Texte à l'écran |
|---|---|---|
| 0–2,4 s | Table en plan large, zoom lent | SAMEDI, UNE SEULE QUESTION : PAR QUOI *commencer ?* |
| 2,4–4,3 s | Gros plan buffet | BUFFET À VOLONTÉ · SAMEDI · 12H–18H30 |
| 4,3–6 s | Verres qui trinquent | *on trinque, on partage* |
| 6–12 s | Liste animée sur fond flou | ET APRÈS LE BUFFET ? PISCINE · BABY-FOOT · BILLARD · KARAOKÉ · DJ MIXTE |
| 12–15 s | Groupe d'amis qui rit | ENTRE AMIS *ou en famille* · PASS : 10.000 FCFA |
| 15–18 s | Carte finale noir et or | Logo WBR · *Well Brunch* · ÉCRIVEZ « BRUNCH » AU 07 47 79 95 07 · 05 66 92 33 91 · Cocody Riviera 3 |

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
