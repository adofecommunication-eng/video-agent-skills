# Notes pour Claude

## Clients ADOFE Communication

- **La Maison Élora** (résidences meublées haut standing, Cocody) : toute création pour ce client suit la fiche de marque `brand/maison-elora/README.md` (couleurs, typographies, ton, règles du logo). Lire ce fichier avant de produire un visuel, une vidéo ou un texte pour cette marque.

- **Wellbeing Resort (WBR)** (resort, Cocody Riviera 3, offre « Well Brunch ») : lire `brand/wellbeing-resort/README.md` avant toute création. Typos imposées : **Anton** en police principale, **Helvetica Neue** en police secondaire. Le Reel `projets/wellbeing-resort/well-brunch-reel/` a été validé par le client : c'est le modèle à suivre (style noir et or, structure, voix « Lola », animation et musique calées mot à mot sur la voix off, sous-titres).

## Méthode de travail

- **Projet validé = fusion** : dès que l'utilisateur valide un projet (ou une modification), ouvrir la pull request vers `main` puis la fusionner, sans attendre une nouvelle demande. Consigne donnée par l'utilisateur.
- **Vidéos en 4K** : tout rendu vidéo livré à l'utilisateur est en **4K** (9:16 = 2160x3840, 16:9 = 3840x2160), H.264 High, débit élevé (environ 12 Mb/s pour rester sous 100 Mo sur GitHub ; plus si le fichier n'est pas versionné). Consigne donnée par l'utilisateur après une perte de qualité à la publication. Les compositions peuvent être calculées en 1080x1920 puis exportées en 4K (Lanczos + léger renforcement), comme `export_4k()` dans `projets/wellbeing-resort/splash-party/spot/spot.py`.
