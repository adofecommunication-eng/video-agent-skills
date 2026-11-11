# Wellbeing Resort (WBR) : fiche client

Client d'ADOFE Communication. Lire ce fichier avant toute création pour Wellbeing Resort (visuels, vidéos, Reels, textes).

## Identité

- **Nom** : Wellbeing Resort, sigle **WBR** (logo : « WBR » dans une couronne de laurier, or, mention WELLBEING RESORT)
- **Localisation** : Cocody Riviera 3, route M'Badon (Abidjan)
- **Réservations** : 07 47 79 95 07 / 05 66 92 33 91
- **Offre phare** : **Well Brunch**, buffet à volonté tous les samedis de 12h à 18h30, pass 10.000 FCFA. Activités : causerie, chill, karaoké, jeux, baby-foot, billard, piscine, ambiance DJ mixte.
- **Cibles** : groupes d'amis, couples, familles.
- **Appel à l'action validé** : « Écrivez “BRUNCH” pour réserver. »

## Style visuel (validé par le client, novembre 2026)

- **Couleurs** : noir chaud `#0B0906` + or en dégradé (`#FCE8A0` → `#E2B54A` → `#B08024` → `#F0CF7A`), blanc pour les titres. Or uni de référence `#D6A83E`.
- **Typos (règle du client)** :
  - **Police principale : Anton** (titres, accroches, prix, numéros, en capitales).
  - **Police secondaire : Helvetica Neue** (infos pratiques, horaires, adresse, sous-titres, textes courants).
  - Accent manuscrit or (ex. Kaushan Script pour « Well Brunch ») : seulement en touche ponctuelle, jamais à la place d'Anton ou d'Helvetica Neue.
  - Helvetica Neue est une police payante : pour les rendus automatisés, utiliser le fichier fourni par l'agence (`.otf`/`.ttf`) ; à défaut, remplaçant le plus proche : Arimo ou Liberation Sans, en le signalant.
  - Le Reel Well Brunch de novembre 2026 utilisait encore Montserrat en secondaire : à remplacer par Helvetica Neue dans les prochaines versions.
- **Habillage** : photos au format cinéma 2.35:1 cerclées d'un filet or sur fond flou assombri, filets or, motif art déco en éventails en bas (repris du flyer), éclats dorés aux coupes, grain léger et vignettage.
- **Ton** : chaleureux, convivial, haut de gamme sans être guindé.

## Recette Reel validée : « Well Brunch » 18 s

Projet de référence : `projets/wellbeing-resort/well-brunch-reel/` (le client a dit « c'est très bien fait »). Réutiliser cette structure pour les prochains Reels WBR.

- Format 9:16, 1080x1920, 30 i/s, textes entre 250 px et 1 560 px du haut ; sous-titres à 1 610 px.
- Structure : accroche question (0–2,4 s) · buffet + trinquer (2,4–6 s) · liste d'activités animée (6–12 s) · groupe + pass (12–15 s) · carte finale logo or + CTA + numéros (15–18 s).
- Son : voix off ElevenLabs « Lola » (féminine, posée, assurée) ; musique légère lounge/amapiano à 100 BPM pour que les coupes (2,4 · 6 · 12 · 15 s) tombent sur les temps ; ducking ~10 dB sous la voix ; -14 LUFS, crête -1,5 dBFS.
- Livrer 2 versions : avec sous-titres incrustés (version principale) et sans, + le `.srt`.
- Typos : Anton + Helvetica Neue (voir ci-dessus).
- Outils : `render.py` (image + mixage, `--subs`), `music.py` (musique), `remix.py` (remixer l'audio seul).
