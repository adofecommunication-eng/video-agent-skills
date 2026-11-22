# Spot « WELL CHRISTMAS » : Wellbeing Resort

Spot motion design de 30 s (9:16, 1080x1920, 30 i/s) pour la fête de Noël du 24 décembre 2026, validé par le client.

| Fichier | Contenu |
|---|---|
| `rendu/well-christmas-30s-sous-titres.mp4` | Version principale, sous-titres incrustés |
| `rendu/well-christmas-30s.mp4` | Sans sous-titres (charger `rendu/well-christmas-30s.srt` sur Facebook) |
| `rendu/planche-apercu.jpg` | Une image par séquence |
| `script-spot-30s.md` | Script validé (voix off ElevenLabs, découpage minuté) |
| `spot.py` | Animation et mixage (`python3 spot.py`, `--subs`, `--stills`) |
| `musique.py` | Musique originale et bruitages de Noël (`sources/musique-et-bruitages.wav`) |
| `decoupe.py` | Détourage des éléments (animateur HD, boule dorée) vers `elements/` |
| `sources/` | Flyer, photo HD de l'animateur, voix off « Lola » |

## Direction artistique

- **Palette de Noël** demandée par le client : rouge velours, blanc neige, or (le noir de la charte WBR ne sert que d'ombre). Polices de la charte : Anton (titres, chiffres) et Helvetica (infos, sous-titres ; TeX Gyre Heros tant que le fichier Helvetica Neue n'est pas fourni).
- **Idées signature** : cadeau qui s'ouvre sur « NOËL », bonnet de Père Noël sur « PISCINE », animateur détouré avec contour blanc, calendrier de l'Avent pour la date, étiquettes cadeau suspendues pour le programme, ticket de tombola qui défile jusqu'à 2.000 F, rideau de velours pour Miss Wellbeing, cadeau qui explose sur « GRATUITE !!! ».
- **Décor permanent** : guirlande lumineuse, flocons en trois profondeurs, titres en or en relief avec reflet, transitions en ruban d'or, légère poussée de caméra.
- **Inspiration** : deux spots de référence du client (rythme, personnage détouré, objets flottants, typographie cinétique, transitions liquides). Leur musique et leurs sons n'ont **pas** été repris (droits d'auteur).

## Son

- Voix off ElevenLabs « Lola », décalée de 0,25 s ; texte calé mot à mot (table `CUE` dans `spot.py`).
- Musique originale house festive 128 BPM (grelots, cloches, basse), silences avant « PISCINE » et « GRATUITE ».
- Bruitages de Noël synthétisés : grelots de traîneau, carillons, cloche d'église, boîte à musique, papier cadeau, poussière d'étoiles.
- Ducking de la musique sous la voix ; -14 LUFS, crête -1,5 dBFS.
