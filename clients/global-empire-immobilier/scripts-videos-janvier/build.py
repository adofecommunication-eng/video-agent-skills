"""Génère scripts.html (PDF des scripts de production des 4 vidéos de janvier) et les sous-titres .srt."""
import os

D = os.path.dirname(os.path.abspath(__file__))
IMG = "../presentation/img/"
WA = "(+225) 07 04 75 53 06"

# ------------------------------------------------------------------ données
# Chaque plan : (début, fin, cadrage/mouvement, image, voix off, texte écran, son/motion)
VIDEOS = [
 dict(
  num=1, slug="video1-jarrete-de-louer-30s", date="Vendredi 8 janvier", dur="30 s",
  titre="Cette année, j'arrête de louer",
  objectif="Transformer la bonne résolution de janvier en demande de visite pour la Cité Les Rives de l'Opulence. Vidéo principale de la campagne 1 en janvier.",
  cible="Locataires d'Abidjan, 27–45 ans, couples et jeunes familles (persona Awa).",
  formats="9:16 (Reels, TikTok, stories) + 4:5 (fil d'actualité, publicité)",
  voix="Féminine, voix intérieure du personnage : complice, un peu lasse au début, puis enthousiaste et décidée. Débit naturel.",
  musique="Début : nappe minimaliste et un peu terne (2 notes de piano). À 0:10, bascule vers une afro-pop lumineuse et positive. -18 dB sous la voix.",
  lieu="Séquence 1 : intérieur d'appartement loué, sobre et un peu exigu (à Abidjan). Séquence 2 : Cité Les Rives de l'Opulence, Adiaké, à l'heure dorée.",
  casting="Une actrice de 30–35 ans (le personnage d'Awa), naturelle et souriante. Tenue simple en séquence 1, plus colorée en séquence 2. Autorisation de droit à l'image signée.",
  materiel="Hybride + 24-70 mm, stabilisateur, lumière douce pour l'intérieur, drone pour le plan final.",
  plans=[
   ("0:00", "0:03", "Plan serré · caméra fixe", "Awa, assise, valide un paiement de loyer sur son téléphone (écran stylisé « Loyer de janvier · payé »). Elle soupire.", "Chaque mois, le même rituel : je paie mon loyer…", "LOYER DE JANVIER : PAYÉ", "Musique terne, son discret de notification."),
   ("0:03", "0:07", "Motion design sur plan fixe", "Un calendrier dont les 12 mois défilent et se barrent un par un.", "et à la fin de l'année, rien ne m'appartient.", "12 LOYERS. 0 MAISON.", "Effet de pages qui tournent, rythme accéléré."),
   ("0:07", "0:10", "Gros plan visage", "Awa relève la tête, regarde l'objectif, petit sourire décidé.", "Et si 2027 changeait tout ?", "ET SI 2027 CHANGEAIT TOUT ?", "Coupe nette : silence d'une demi-seconde puis bascule musicale."),
   ("0:10", "0:16", "Drone puis plan moyen stabilisé", "La villa des Rives de l'Opulence au soleil ; Awa franchit le portail, émerveillée.", "Avec Global Empire Immobilier, je deviens propriétaire de ma villa à Adiaké, avec un paiement progressif.", "✓ PAIEMENT PROGRESSIF", "Musique lumineuse, transition par balayage bleu."),
   ("0:16", "0:23", "Motion design sur façade floutée", "Bloc prix blanc : prix puis apport.", "Prix d'acquisition : quarante-cinq millions de francs CFA. Apport initial : quinze millions.", "45 M FCFA · APPORT 15 M", "Compteur animé, rebond."),
   ("0:23", "0:27", "Plan serré · ralenti léger", "Awa ouvre la porte d'entrée et se retourne vers la caméra, rayonnante.", "Cette année, c'est décidé : j'arrête de louer.", "CETTE ANNÉE, J'ARRÊTE DE LOUER", "Titre en masque, Montserrat Black."),
   ("0:27", "0:30", "Écran de fin", "Logo GEI, bandeau vert, WhatsApp.", "Réservez votre visite sur WhatsApp. Global Empire Immobilier.", "RÉSERVEZ VOTRE VISITE · (+225) 07 04 75 53 06", "Dernière note, fondu."),
  ],
  accroches=["« Chaque mois, le même rituel : je paie mon loyer… » (version principale)",
             "« 12 loyers par an. Et à la fin, rien ne vous appartient. »",
             "« Ma résolution 2027 ? Arrêter de louer. »"],
  legende="Cette année, c'est décidé : j'arrête de louer 🔑\nDevenez propriétaire de votre villa à Adiaké, avec un paiement progressif.\n✔ 45 M FCFA · Apport 15 M\n👉 Réservez votre visite : (+225) 07 04 75 53 06\n#GlobalEmpireImmobilier #ImmobilierCI #Adiaké #Résolution2027",
  notes=["Ne pas laisser entendre que les échéances équivalent à un loyer : le script compare des situations, pas des montants.",
         "L'écran de paiement du loyer est une maquette : ni vraie application, ni vraie donnée bancaire.",
         "Prévoir une version 15 s pour la publicité : plans 1, 3, 4 et 7."],
 ),
 dict(
  num=2, slug="video2-echeancier-45s", date="Vendredi 15 janvier", dur="45 s",
  titre="Comprendre l'échéancier",
  objectif="Lever le frein du financement en expliquant simplement le paiement progressif. Rubrique « GEI vous explique ».",
  cible="Prospects qui hésitent pour des raisons de budget, toutes cibles.",
  formats="9:16 (Reels, TikTok) + 4:5 (fil d'actualité, reciblage publicitaire)",
  voix="Le même conseiller GEI que dans la vidéo « L'ACD, c'est quoi ? », face caméra : la série devient reconnaissable. Ton pédagogique et rassurant.",
  musique="Nappe lo-fi discrète, -24 dB. Petits sons de validation sur les étapes.",
  lieu="Bureau GEI, Cocody, Cité des Arts, même cadre que la vidéo ACD.",
  casting="Le conseiller GEI de la série « GEI vous explique ».",
  materiel="Hybride sur trépied, 50 mm, 2 lumières douces, micro-cravate, prompteur.",
  plans=[
   ("0:00", "0:04", "Plan serré poitrine", "Le conseiller regarde l'objectif.", "Quarante-cinq millions pour une villa… vous vous dites que c'est impossible ? Attendez.", "45 MILLIONS, IMPOSSIBLE ?", "Titre géant, jaune sur bandeau bleu."),
   ("0:04", "0:09", "Plan moyen", "Il prend une feuille blanche et un feutre.", "Je vous explique comment fonctionne le paiement progressif, en trois étapes.", "LE PAIEMENT PROGRESSIF EN 3 ÉTAPES", ""),
   ("0:09", "0:16", "Motion design plein écran", "Étape 1 : une icône de dossier qui s'ouvre.", "Étape un : les frais de dossier, trois cent mille francs CFA, pour ouvrir votre dossier d'acquisition.", "① FRAIS DE DOSSIER · 300 000 FCFA", "Son de validation."),
   ("0:16", "0:23", "Motion design plein écran", "Étape 2 : une barre de progression qui se remplit au tiers.", "Étape deux : l'apport initial, quinze millions, votre premier versement sur le prix de la villa.", "② APPORT INITIAL · 15 M FCFA", "Barre remplie à 33 %."),
   ("0:23", "0:32", "Motion design plein écran", "Étape 3 : la barre se remplit par petits paliers jusqu'à 100 %.", "Étape trois : le solde, trente millions, réglé en plusieurs échéances, selon l'échéancier convenu avec votre conseiller.", "③ SOLDE · 30 M EN ÉCHÉANCES", "Paliers animés, la maison se dessine à côté de la barre."),
   ("0:32", "0:40", "Retour plan serré", "Le conseiller, sourire.", "Et la villa est déjà construite : l'habitation est immédiate. Chaque échéancier est personnalisé : on l'établit ensemble.", "✓ HABITATION IMMÉDIATE", ""),
   ("0:40", "0:45", "Écran de fin", "Logo GEI, bandeau vert, WhatsApp.", "Demandez votre échéancier personnalisé sur WhatsApp.", "DEMANDEZ VOTRE ÉCHÉANCIER · (+225) 07 04 75 53 06", "Fondu sur le logo."),
  ],
  accroches=["« 45 millions pour une villa… vous vous dites que c'est impossible ? Attendez. » (version principale)",
             "« Le paiement progressif, expliqué en 45 secondes. »",
             "« Comment devenir propriétaire sans tout payer d'un coup ? »"],
  legende="45 millions pour une villa… impossible ? Pas avec le paiement progressif 💡\n① Frais de dossier ② Apport initial ③ Solde en échéances\n👉 Demandez votre échéancier personnalisé : (+225) 07 04 75 53 06\n#GlobalEmpireImmobilier #ImmobilierCI #GEIvousExplique #Adiaké",
  notes=["GEI doit confirmer les conditions exactes du solde (nombre d'échéances, durée, éventuels frais) et le moment de l'entrée dans les lieux.",
         "Ne citer aucune durée ni montant d'échéance tant que GEI ne les a pas validés par écrit.",
         "À tourner le même jour que la vidéo n° 4 si le conseiller est disponible."],
 ),
 dict(
  num=3, slug="video3-temoignage-client-60s", date="Samedi 23 janvier", dur="45–60 s",
  titre="Témoignage client : « Je suis propriétaire »",
  objectif="Apporter la preuve sociale la plus forte : un vrai client qui raconte son expérience avec GEI.",
  cible="Toutes cibles, en particulier les prospects tièdes en reciblage publicitaire.",
  formats="9:16 (Reels, TikTok) + 4:5 (publicité de reciblage)",
  voix="Uniquement la voix réelle du client. Voix off courte en ouverture et en fermeture (féminine, la même que la vidéo 1).",
  musique="Acoustique douce et émotionnelle, -28 dB pendant la parole, remontée sur les plans d'illustration.",
  lieu="Chez le client, devant ou dans son bien GEI (idéalement à la Cité Les Rives de l'Opulence). Interview à l'ombre, lumière naturelle douce.",
  casting="Un client GEI réel, volontaire, ayant acheté ou en cours d'acquisition. Autorisation écrite de droit à l'image, avec validation du montage final par le client.",
  materiel="2 caméras (plan poitrine + plan serré de profil), micro-cravate sans fil, réflecteur, stabilisateur pour les plans d'illustration.",
  plans=[
   ("0:00", "0:05", "Plan serré · meilleure phrase du client", "Le client, ému ou souriant, dit sa phrase la plus forte (choisie au montage).", "(Son direct : la meilleure phrase de l'interview)", "Phrase du client en sous-titre", "Pas de musique les 2 premières secondes."),
   ("0:05", "0:09", "Plan large · le client devant sa maison", "Il pose devant la façade, les mains sur le portail.", "Voici [prénom]. Il y a quelques mois, il ou elle était encore locataire.", "[PRÉNOM], PROPRIÉTAIRE", "Titre en masque. Champs entre crochets à compléter après l'interview."),
   ("0:09", "0:25", "Interview · alternance des 2 caméras", "Le client raconte son projet, ses craintes, sa rencontre avec GEI.", "(Son direct : réponses aux questions 1 à 4)", "Sous-titres de la réponse exacte", "Plans d'illustration en surimpression : visite, documents, remise des clés."),
   ("0:25", "0:45", "Interview + plans d'illustration", "Le client parle de l'accompagnement et de sa vie aujourd'hui.", "(Son direct : réponses aux questions 5 à 7)", "Sous-titres de la réponse exacte", "Musique qui remonte doucement."),
   ("0:45", "0:52", "Plan serré · regard caméra", "Le conseil du client à ceux qui hésitent.", "(Son direct : réponse à la question 8)", "Sous-titres", ""),
   ("0:52", "0:60", "Écran de fin", "Logo GEI, bandeau vert, WhatsApp.", "Vous aussi, devenez propriétaire en toute sérénité. Écrivez-nous sur WhatsApp.", "À VOTRE TOUR · (+225) 07 04 75 53 06", "Fondu final."),
  ],
  accroches=["La meilleure phrase spontanée du client (version principale)",
             "« Il y a un an, j'étais locataire. »",
             "« Voici ce que nos clients disent de GEI. »"],
  legende="« [phrase du client] » 🗣️\nMerci [prénom] pour votre confiance et pour ce témoignage 🙏\nVous aussi, devenez propriétaire en toute sérénité.\n👉 (+225) 07 04 75 53 06\n#GlobalEmpireImmobilier #ImmobilierCI #Témoignage #Propriétaire",
  interview=["Pouvez-vous vous présenter en quelques mots ?",
             "Où en étiez-vous avant votre projet d'achat ?",
             "Qu'est-ce qui vous faisait peur dans l'achat d'un bien ?",
             "Comment avez-vous connu Global Empire Immobilier ?",
             "Comment s'est passée la visite et la présentation des documents ?",
             "Comment avez-vous vécu le paiement progressif ?",
             "Qu'est-ce qui a changé pour vous aujourd'hui ?",
             "Que diriez-vous à quelqu'un qui hésite encore ?"],
  notes=["Le témoignage n'est jamais écrit ni orienté : on garde les mots réels du client, même imparfaits.",
         "Aucun avantage (remise, cadeau) en échange du témoignage sans le mentionner dans la publication.",
         "Si aucun client n'est disponible avant le 20 janvier, inverser avec la vidéo de février et publier à la place un extrait de la journée de visite."],
 ),
 dict(
  num=4, slug="video4-deuxieme-programme-30s", date="Vendredi 29 janvier", dur="30 s",
  titre="Découvrez [nom du deuxième programme]",
  objectif="Lancer le deuxième programme de GEI et élargir l'offre au-delà des Rives de l'Opulence. Gabarit à compléter avec les informations de GEI.",
  cible="Investisseurs et primo-accédants (personas M. Traoré et Awa).",
  formats="9:16 (Reels, TikTok, stories) + 4:5 (publicité)",
  voix="Masculine, assurée et chaleureuse : la voix de l'investissement (la même que la vidéo diaspora).",
  musique="Afro-house élégante, 105–115 BPM, montée à 0:15. -18 dB sous la voix.",
  lieu="Site du deuxième programme. Repérage préalable obligatoire : accès, bornes, environnement, meilleure heure de lumière.",
  casting="Pas de comédien : plans du site, de l'environnement et éventuellement du conseiller GEI sur place.",
  materiel="Drone 4K, hybride + 16-35 mm et 24-70 mm, stabilisateur.",
  plans=[
   ("0:00", "0:03", "Drone · élévation verticale", "Le site se révèle depuis le sol jusqu'à la vue d'ensemble.", "Nouvelle année, nouvelle adresse.", "NOUVEAU PROGRAMME GEI", "Titre en masque, musique en fondu d'entrée."),
   ("0:03", "0:09", "Drone · travelling le long des voies", "Les lots, la voirie, les bornes.", "Global Empire Immobilier vous présente [nom du programme], à [zone].", "[NOM DU PROGRAMME] · [ZONE]", "Bandeau vert depuis la gauche."),
   ("0:09", "0:16", "Plans au sol · 3 × 2 s", "Route d'accès, environnement proche (écoles, commerces, axes), bornes.", "[Atout 1 : par exemple l'accès ou la proximité d'un axe]. [Atout 2 : environnement, équipements].", "✓ [ATOUT 1] · ✓ [ATOUT 2]", "Coupes sur le rythme."),
   ("0:16", "0:23", "Motion design sur vue drone floutée", "Bloc blanc : superficie et prix.", "Des [terrains / maisons] de [superficie], à partir de [prix] francs CFA, [modalités de paiement].", "[SUPERFICIE] · DÈS [PRIX] FCFA", "Compteur animé."),
   ("0:23", "0:27", "Plan au sol · conseiller GEI sur le site", "Le conseiller désigne le site d'un geste, sourire.", "La situation du programme vous est présentée avant toute signature.", "✓ [SITUATION JURIDIQUE VALIDÉE PAR GEI]", ""),
   ("0:27", "0:30", "Écran de fin", "Logo GEI, bandeau vert, WhatsApp.", "Réservez votre visite sur WhatsApp. Global Empire Immobilier.", "RÉSERVEZ VOTRE VISITE · (+225) 07 04 75 53 06", "Fondu."),
  ],
  accroches=["« Nouvelle année, nouvelle adresse. » (version principale)",
             "« [Zone] : la zone qui monte en 2027. » (seulement si GEI peut l'étayer)",
             "« Votre terrain à [zone], dès [prix] FCFA. »"],
  legende="Nouveau programme GEI 📍 [Nom du programme], à [zone]\n✔ [superficie] · ✔ dès [prix] FCFA · ✔ [modalités]\n👉 Réservez votre visite : (+225) 07 04 75 53 06\n#GlobalEmpireImmobilier #ImmobilierCI #[Zone]",
  notes=["Tous les champs entre crochets sont à remplir avec la fiche du programme fournie par GEI avant le 15 janvier.",
         "Aucune promesse de plus-value ni de « zone qui monte » sans élément vérifiable fourni par GEI.",
         "La mention sur la situation juridique n'est utilisée que si GEI la confirme par écrit."],
 ),
]

# ------------------------------------------------------------------ sous-titres SRT
def ts(t):
    m, s = t.split(":")
    return f"00:{int(m):02d}:{int(s):02d},000"

for v in VIDEOS:
    lines, k = [], 1
    for (a, b, _c, _i, vo, _t, _m) in v["plans"]:
        if vo and not vo.startswith("("):
            lines.append(f"{k}\n{ts(a)} --> {ts(b)}\n{vo}\n")
            k += 1
    open(os.path.join(D, f"{v['slug']}.srt"), "w", encoding="utf-8").write("\n".join(lines))

# ------------------------------------------------------------------ HTML
def foot(n):
    return f'<div class="foot"><span><img src="{IMG}logo-gei.png" alt="">GLOBAL EMPIRE IMMOBILIER SARL × 7CREATIVE</span><span>{n:02d}</span></div>'

def top():
    return f'<div class="bar"></div><img class="logo-top" src="{IMG}logo-gei.png" alt="">'

def words(v):
    txt = " ".join(p[4] for p in v["plans"] if p[4] and not p[4].startswith("("))
    return txt, len(txt.split())

pages = []
pages.append(f'''<section class="page cover">
  <div class="frame"></div>
  <div class="inner">
    <div class="logo-card"><img src="{IMG}logo-gei.png" alt="Logo Global Empire Immobilier Sarl"></div>
    <h1>Scripts vidéo<br><em>janvier 2027</em></h1>
    <p class="sub">Thème du mois : « Nouvelle année, nouveau chez-moi ». Scripts de production complets des 4 vidéos : découpage plan par plan, texte intégral des voix off, son, motion design, casting et légendes.</p>
  </div>
  <div class="photo"></div>
  <div class="meta">
    <div><b>RÉALISÉ PAR 7CREATIVE</b>Direction artistique et production</div>
    <div style="text-align:right"><b>À VALIDER PAR GEI</b>Version 1 · décembre 2026</div>
  </div>
</section>''')

rows = "".join(f'<tr><td><b>Vidéo {v["num"]}</b></td><td>{v["titre"]}</td><td>{v["dur"]}</td><td>{v["date"]}</td></tr>' for v in VIDEOS)
pages.append(f'''<section class="page">{top()}
  <div class="kicker">Vue d'ensemble</div>
  <h2>4 vidéos,<br>un seul <span class="gold">fil rouge</span>.</h2>
  <table style="margin-bottom:6mm"><tr><th>N°</th><th>Titre</th><th>Durée</th><th>Publication</th></tr>{rows}</table>
  <h3>Calendrier de production</h3>
  <table class="sm" style="margin-bottom:6mm">
    <tr><td><b>Jusqu'au 20 déc.</b></td><td>Validation des scripts par GEI, casting de l'actrice (vidéo 1), choix du client témoin (vidéo 3)</td></tr>
    <tr><td><b>5 janv.</b></td><td>Tournage n° 2 : appartement + Rives de l'Opulence (vidéo 1), bureau de Cocody (vidéo 2)</td></tr>
    <tr><td><b>6 – 7 janv.</b></td><td>Montage, motion design, voix off, sous-titres ; envoi des vidéos 1 et 2 à GEI (validation sous 48 h)</td></tr>
    <tr><td><b>Avant le 15 janv.</b></td><td>GEI fournit la fiche du deuxième programme ; repérage du site (vidéo 4)</td></tr>
    <tr><td><b>16 janv.</b></td><td>Journée de visite et interview du client témoin (vidéo 3) ; tournage du deuxième programme (vidéo 4)</td></tr>
    <tr><td><b>18 – 21 janv.</b></td><td>Montage des vidéos 3 et 4, validation par GEI et par le client témoin</td></tr>
  </table>
  <div class="grid2 sm" style="gap:5mm">
    <div class="card"><h3>Règles communes</h3><ul class="check">
      <li>Accroche forte dans les 3 premières secondes, sans logo</li>
      <li>Sous-titres incrustés sur toute la durée (Montserrat Bold blanc sur fond bleu)</li>
      <li>Écran de fin identique : logo, bandeau vert, WhatsApp</li>
      <li>Rien d'important dans les 15 % du haut et les 20 % du bas (9:16)</li></ul></div>
    <div class="card"><h3>Livrables par vidéo</h3><ul class="check">
      <li>Export 9:16 et 4:5, 1080 px, H.264, 30 i/s</li>
      <li>Fichier de sous-titres .srt (fourni avec ce document)</li>
      <li>Image de couverture aux couleurs de GEI</li>
      <li>Musique sous licence commerciale, référence archivée</li></ul></div>
  </div>
{foot(2)}</section>''')

def interview_block(v, on_text=False):
    if not v.get("interview") or (len(v["interview"]) > 5) != on_text:
        return ""
    return ('<div class="card" style="margin-top:5mm"><h3>Guide d\'interview</h3><ul class="check sm" style="columns:2;column-gap:6mm">'
            + "".join(f"<li>{q}</li>" for q in v["interview"]) + "</ul></div>")

def long_iv(v):
    return len(v.get("interview", [])) > 5

def notes_block(v):
    notes = "".join(f"<li>{x}</li>" for x in v["notes"])
    return f'<div class="card" style="margin-top:5mm;border-top-color:#C62828"><h3>Points de vigilance</h3><ul class="check sm">{notes}</ul></div>'

n = 3
for v in VIDEOS:
    txt, nb = words(v)
    plans = "".join(
        f'<tr><td>{i}</td><td>{a}–{b}</td><td><b>{c}</b><br>{im}</td><td class="vo">{vo or "—"}</td><td>{t or "—"}</td><td>{m or "—"}</td></tr>'
        for i, (a, b, c, im, vo, t, m) in enumerate(v["plans"], 1))
    pages.append(f'''<section class="page">{top()}
  <div class="kicker">Vidéo {v["num"]} · {v["dur"]} · {v["date"]}</div>
  <h2 style="font-size:21pt">{v["titre"]}</h2>
  <p class="sm" style="margin-bottom:4mm;font-size:9.5pt!important"><b>Objectif :</b> {v["objectif"]}</p>
  <h3>Découpage technique</h3>
  <table class="script dec"><tr><th>#</th><th>Temps</th><th>Cadrage et image</th><th>Voix</th><th>Texte écran</th><th>Son / motion</th></tr>{plans}</table>
  {interview_block(v)}
  {notes_block(v) if long_iv(v) else ""}
{foot(n)}</section>''')
    n += 1
    extra = interview_block(v, on_text=True)
    acc = "".join(f"<li>{a}</li>" for a in v["accroches"])
    notes = "".join(f"<li>{x}</li>" for x in v["notes"])
    pages.append(f'''<section class="page">{top()}
  <div class="kicker">Vidéo {v["num"]} · Texte intégral</div>
  <h2 style="font-size:19pt">Fiche technique et <span class="gold">texte</span>.</h2>
  <table class="fiche"><tr><td>Cible</td><td>{v["cible"]}</td></tr><tr><td>Formats</td><td>{v["formats"]}</td></tr><tr><td>Voix</td><td>{v["voix"]}</td></tr><tr><td>Musique</td><td>{v["musique"]}</td></tr><tr><td>Lieu</td><td>{v["lieu"]}</td></tr><tr><td>Casting</td><td>{v["casting"]}</td></tr><tr><td>Matériel</td><td>{v["materiel"]}</td></tr></table>
  <div class="card dark" style="padding:5mm 6mm;margin-top:4mm">
    <div class="kicker">Voix off · {nb} mots{" (ouverture et fin, le reste est en son direct)" if nb < 40 else " · environ " + v["dur"]}</div>
    <p style="color:#fff;font-size:10.5pt;line-height:1.6;font-style:italic">« {txt} »</p>
  </div>
  <p class="note">Respirations : une courte pause à chaque point, une pause plus longue avant l'appel à l'action. Les chiffres se prononcent en toutes lettres.</p>
  <div class="grid2 sm" style="gap:4mm;margin-top:3mm">
    <div class="card"><h3>Accroches à tester</h3><ul class="check">{acc}</ul></div>
    <div class="card"><h3>Légende de publication</h3><pre class="cap">{v["legende"]}</pre></div>
  </div>
  {extra}
  {"" if long_iv(v) else notes_block(v)}
{foot(n)}</section>''')
    n += 1

pages.append(f'''<section class="page cta">
  <div class="logo-card" style="position:absolute;top:12mm;right:16mm"><img src="{IMG}logo-gei.png" alt="" style="height:20mm"></div>
  <div class="kicker" style="margin-top:6mm">Avant le tournage du 5 janvier</div>
  <h2>La check-list<br>de <span class="gold">validation</span>.</h2>
  <ul class="check" style="margin-top:6mm">
    <li>GEI valide les 4 scripts, en particulier les conditions du paiement progressif (vidéo 2)</li>
    <li>L'actrice de la vidéo 1 est choisie et un appartement de tournage est trouvé</li>
    <li>Le même conseiller GEI que pour la vidéo ACD est disponible le 5 janvier</li>
    <li>Un client volontaire accepte de témoigner (vidéo 3) et signe son autorisation</li>
    <li>GEI fournit la fiche complète du deuxième programme : nom, zone, superficies, prix, modalités, situation juridique</li>
    <li>Le site du deuxième programme est repéré et l'autorisation de vol du drone vérifiée</li>
    <li>La journée de visite du samedi 16 janvier est annoncée dès le 6 janvier</li>
  </ul>
  <div style="margin-top:12mm;border-top:1px solid rgba(212,224,33,.5);padding-top:7mm">
    <h3 style="color:#fff;font-size:17pt">Votre équipe 7CREATIVE</h3>
    <p style="margin-top:2mm">WhatsApp : <b style="color:#fff">(+225) 07 08 49 69 01</b> · contact.sevencreative@gmail.com</p>
  </div>
  <div class="foot"><span>7CREATIVE — AGENCE 360°</span><span>{n:02d}</span></div>
</section>''')

css_extra = """
.sm,.sm p,.sm td,.sm li{font-size:8.6pt!important;line-height:1.45}
.note{font-size:8pt!important;color:var(--muted);margin-top:2mm;line-height:1.4}
table.script th{background:var(--navy);color:#fff;font-size:7pt;padding:1.6mm 2mm}
table.script td{font-size:7.7pt;line-height:1.38;padding:1.6mm 2mm;vertical-align:top}
table.script td:first-child{font-weight:900;color:var(--navy)}
table.script td:nth-child(2){white-space:nowrap;font-weight:800;color:var(--green)}
table.script td.vo{font-style:italic;color:var(--ink);width:30%}
table.script td:nth-child(3){width:30%}
table.script td{font-size:8.2pt!important}
table.fiche td{font-size:8pt;padding:1.3mm 2.5mm;line-height:1.35;vertical-align:top}
table.fiche td:first-child{width:22mm;font-weight:800;color:var(--navy)}
.card{padding:4.5mm 5mm}
pre.cap{white-space:pre-wrap;font-family:Montserrat,sans-serif;font-size:8.3pt;line-height:1.5;color:var(--ink)}
"""
html = ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Scripts vidéo GEI</title>'
        '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">'
        '<link rel="stylesheet" href="../plan-communication/gei.css">'
        f'<style>{css_extra}</style></head><body>' + "\n".join(pages) + "</body></html>")
open(os.path.join(D, "scripts.html"), "w", encoding="utf-8").write(html)
print(len(pages), "pages", [words(v)[1] for v in VIDEOS], "mots")
