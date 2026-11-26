"""Génère scripts.html (PDF des scripts de production des 4 vidéos de décembre) et les sous-titres .srt."""
import os

D = os.path.dirname(os.path.abspath(__file__))
IMG = "../presentation/img/"
WA = "(+225) 07 10 29 67 20"

# ------------------------------------------------------------------ données
# Chaque plan : (début, fin, cadrage/mouvement, image, voix off, texte écran, son/motion)
VIDEOS = [
 dict(
  num=1, slug="video1-rives-opulence-30s", date="Vendredi 11 décembre", dur="30 s",
  titre="Les Rives de l'Opulence en 30 secondes",
  objectif="Générer des demandes de visite pour la Cité Les Rives de l'Opulence. Vidéo principale de la campagne 1 « Propriétaire à Abidjan ».",
  cible="Primo-accédants et familles d'Abidjan, 27–60 ans (persona Awa).",
  formats="9:16 (Reels, TikTok, stories) + 4:5 (fil d'actualité, publicité)",
  voix="Féminine, chaleureuse et posée, accent ivoirien léger. Débit calme : environ 2,4 mots par seconde.",
  musique="Afro-house douce ou acoustique lumineuse, 100–110 BPM, montée légère à 18 s, chute nette à 25 s pour l'appel à l'action. Niveau -18 dB sous la voix.",
  lieu="Cité Les Rives de l'Opulence, Adiaké. Tournage à l'heure dorée (6 h 30 – 8 h ou 17 h – 18 h 30).",
  casting="Une famille figurante (couple + 1 ou 2 enfants), tenue décontractée chic aux couleurs claires. Autorisations de droit à l'image signées.",
  materiel="Drone 4K, hybride plein format + 24-70 mm, stabilisateur, réflecteur.",
  plans=[
   ("0:00", "0:03", "Drone · travelling avant lent, en descente", "La villa apparaît au milieu des palmiers, soleil rasant derrière.", "Et si 2027 était l'année où vous rentrez enfin… chez vous ?", "VOTRE VILLA À ADIAKÉ", "Musique en fondu d'entrée. Titre en masque du bas vers le haut, 0,4 s."),
   ("0:03", "0:06", "Drone · orbite à 45°, hauteur 15 m", "Vue d'ensemble de la cité, voirie et verdure.", "Bienvenue à la Cité Les Rives de l'Opulence, à Adiaké.", "CITÉ LES RIVES DE L'OPULENCE", "Bandeau vert qui glisse depuis la gauche."),
   ("0:06", "0:10", "Plan large · glissement latéral au stabilisateur", "Façade 3/4 de la villa, lumières extérieures allumées.", "Des villas prêtes à habiter, dans un cadre calme et verdoyant.", "✓ HABITATION IMMÉDIATE", "Pastille jaune ✓ qui apparaît avec un léger rebond."),
   ("0:10", "0:13", "Plans serrés · 2 × 1,5 s", "Le portail s'ouvre / les palmiers du jardin au contre-jour.", "", "", "Coupe sur le temps fort de la musique."),
   ("0:13", "0:18", "Plan moyen · caméra qui suit la famille", "La famille franchit le portail, l'enfant court vers la maison, les parents sourient.", "Avec Global Empire Immobilier, vous payez progressivement, à votre rythme.", "✓ PAIEMENT PROGRESSIF", "Son d'ambiance léger (rires, pas) sous la musique."),
   ("0:18", "0:25", "Motion design sur façade floutée", "Bloc prix blanc qui monte du bas de l'écran.", "Prix d'acquisition : quarante-cinq millions de francs CFA, avec un apport initial de quinze millions.", "45 M FCFA · APPORT 15 M", "Compteur de 0 à 45 M en 0,8 s, puis rebond. Apport en second temps."),
   ("0:25", "0:30", "Écran de fin · fond Bleu Empire", "Logo GEI dans sa carte blanche, bandeau vert avec WhatsApp.", "Réservez votre visite dès aujourd'hui sur WhatsApp. Global Empire Immobilier : achetez en toute sécurité.", f"RÉSERVEZ VOTRE VISITE · {WA}", "Chute de la musique à 0:25, logo en fondu, dernière note tenue."),
  ],
  accroches=["« Et si 2027 était l'année où vous rentrez enfin… chez vous ? » (version principale)",
             "« Votre villa à Adiaké, prête à habiter. »",
             "« Propriétaire d'une villa avec un apport de 15 millions ? »"],
  legende=f"30 secondes pour découvrir votre future villa à Adiaké 🌴\nHabitation immédiate, paiement progressif.\n👉 Visite sur rendez-vous : {WA}\n#GlobalEmpireImmobilier #ImmobilierCI #Adiaké #Propriétaire",
  notes=["Si les intérieurs sont disponibles, remplacer le plan 4 par un plan du séjour (2 s).",
         "Prévoir une version 15 s pour la publicité (spot A) : plans 1, 3, 6 et 7."],
 ),
 dict(
  num=2, slug="video2-acd-45s", date="Vendredi 18 décembre", dur="45 s",
  titre="L'ACD, c'est quoi ?",
  objectif="Installer GEI comme l'expert de confiance et rassurer avant l'achat. Rubrique « GEI vous explique ».",
  cible="Tous les acheteurs de terrain, en particulier les primo-accédants et la diaspora.",
  formats="9:16 (Reels, TikTok) + 4:5 (fil d'actualité)",
  voix="Un conseiller GEI face caméra (voix réelle, pas de voix off). Ton pédagogique, souriant, phrases courtes. Lecture sur prompteur ou par blocs de 2 phrases.",
  musique="Nappe discrète, lo-fi ou piano léger, -24 dB : la voix doit rester très claire.",
  lieu="Bureau GEI, Cocody, Cité des Arts. Fond net et rangé, logo GEI visible en arrière-plan.",
  casting="Un conseiller ou une conseillère GEI à l'aise à l'oral, tenue professionnelle sobre (bleu, blanc). Micro-cravate.",
  materiel="Hybride sur trépied, 50 mm, 2 sources de lumière douce, micro-cravate, prompteur sur tablette.",
  plans=[
   ("0:00", "0:04", "Plan serré poitrine · caméra fixe", "Le conseiller regarde l'objectif, sourire.", "Avant d'acheter un terrain, il y a un document que vous devez absolument connaître : l'ACD.", "L'ACD, C'EST QUOI ?", "Titre géant en Montserrat Black, jaune sur bandeau bleu."),
   ("0:04", "0:12", "Motion design plein écran", "Document stylisé (sans reproduire un vrai document officiel) qui se remplit ligne par ligne.", "L'ACD, c'est l'Arrêté de Concession Définitive.", "ARRÊTÉ DE CONCESSION DÉFINITIVE", "Mots-clés qui apparaissent un par un."),
   ("0:12", "0:18", "Retour plan serré · léger zoom avant numérique", "Le conseiller, geste de la main ouverte.", "C'est le titre qui fait de vous le propriétaire définitif d'un terrain urbain en Côte d'Ivoire.", "PROPRIÉTAIRE DÉFINITIF", "Soulignement vert animé sous le texte."),
   ("0:18", "0:22", "Plan moyen", "Le conseiller compte sur ses doigts.", "Alors, avant de payer, posez toujours trois questions.", "3 QUESTIONS À POSER", ""),
   ("0:22", "0:34", "Motion : liste qui se coche", "Trois lignes avec cases à cocher sur fond Bleu Empire.", "Un : l'ACD est-il déjà obtenu ? Deux : s'il est en cours, à quelle étape en est le dossier ? Trois : quels documents puis-je consulter avant de signer ?", "✓ OBTENU ? ✓ EN COURS ? ✓ CONSULTABLE ?", "Son discret « clic » à chaque coche."),
   ("0:34", "0:41", "Retour plan serré", "Le conseiller, ton rassurant.", "Chez Global Empire Immobilier, nous vous présentons la situation de chaque bien avant toute signature.", "", ""),
   ("0:41", "0:45", "Écran de fin", "Logo GEI, bandeau vert, WhatsApp.", "Une question ? Écrivez-nous sur WhatsApp.", f"GEI VOUS EXPLIQUE · {WA}", "Fondu sur le logo."),
  ],
  accroches=["« Avant d'acheter un terrain, il y a un document que vous devez absolument connaître. » (version principale)",
             "« ACD, lettre d'attribution, attestation : vous savez faire la différence ? »",
             "« La question à poser avant de payer un terrain. »"],
  legende="L'ACD, c'est quoi ? 🤔 Le document que vous devez connaître avant d'acheter un terrain.\nRegardez jusqu'au bout et posez vos questions en commentaire 👇\n#GlobalEmpireImmobilier #ImmobilierCI #GEIvousExplique",
  notes=["Texte à faire relire et valider par GEI (et, si besoin, par son notaire) avant le tournage.",
         "La phrase « nous vous présentons la situation de chaque bien avant toute signature » est un engagement : GEI doit le confirmer.",
         "Ne pas filmer de vrais documents de clients (données personnelles)."],
 ),
 dict(
  num=3, slug="video3-diaspora-30s", date="Samedi 26 décembre", dur="30 s",
  titre="Vous êtes loin ? On vous fait visiter",
  objectif="Obtenir des rendez-vous en visio avec la diaspora. Vidéo principale de la campagne 2 « Diaspora ».",
  cible="Ivoiriens de la diaspora en France, Belgique, Suisse, Italie, Canada et États-Unis, 30–60 ans (persona Koffi).",
  formats="9:16 (Reels, TikTok, stories) + 4:5 (publicité)",
  voix="Masculine, grave et chaleureuse, accent ivoirien léger : la voix du pays. Débit posé.",
  musique="Afro-soul ou acoustique émotionnelle, montée progressive, -18 dB sous la voix. Une touche nostalgique au début, lumineuse à la fin.",
  lieu="Cité Les Rives de l'Opulence, Adiaké + bureau GEI. Plans de ville étrangère : banque d'images sous licence.",
  casting="Un conseiller GEI qui mène une visite en direct au téléphone. Un figurant « client » vu de dos devant un écran (peut être tourné à Abidjan dans un intérieur neutre, ambiance soir d'hiver).",
  materiel="Drone, hybride, smartphone sur stabilisateur pour le plan « visite en direct », écran ou tablette pour l'incrustation.",
  plans=[
   ("0:00", "0:03", "Écran partagé vertical", "En haut : rue d'une ville européenne en hiver (banque d'images). En bas : la villa au soleil à Adiaké.", "Vous vivez à Paris, Bruxelles ou Montréal… et vous rêvez d'investir au pays ?", "INVESTIR AU PAYS, MÊME DE LOIN", "Transition : la moitié froide glisse et laisse place au soleil."),
   ("0:03", "0:07", "Plan épaule · smartphone", "Le conseiller GEI marche vers la villa en filmant avec son téléphone, il parle à l'écran.", "Avec Global Empire Immobilier, vous visitez votre futur bien en vidéo,", "✓ VISITE VIDÉO EN DIRECT", "Interface d'appel vidéo stylisée (sans logo d'application)."),
   ("0:07", "0:12", "Plan de dos sur le figurant", "Le client, chez lui, regarde la visite sur sa tablette, sourire.", "en direct, avec un conseiller.", "", "Son direct léger de l'appel."),
   ("0:12", "0:20", "Gros plans d'écran", "Messages WhatsApp stylisés : photos du chantier, étapes du dossier.", "Vous suivez chaque étape de votre dossier sur WhatsApp, et vous payez progressivement.", "✓ SUIVI WHATSAPP · ✓ PAIEMENT PROGRESSIF", "Bulles de messages qui apparaissent une à une."),
   ("0:20", "0:26", "Drone · élévation au coucher du soleil", "La cité vue du ciel, lumière dorée.", "À Adiaké, votre villa vous attend, prête à habiter dès votre retour.", "CITÉ LES RIVES DE L'OPULENCE", "Montée musicale."),
   ("0:26", "0:30", "Écran de fin", "Logo GEI, bandeau vert, numéro avec indicatif +225.", "Prenez rendez-vous en visio sur WhatsApp. Global Empire Immobilier : achetez en toute sécurité.", f"RENDEZ-VOUS EN VISIO · {WA}", "Dernière note tenue, fondu."),
  ],
  accroches=["« Vous vivez à Paris, Bruxelles ou Montréal… et vous rêvez d'investir au pays ? » (version principale)",
             "« Construire au pays sans être trompé ? »",
             "« Préparez votre retour dès aujourd'hui. »"],
  legende=f"Vous êtes en France, en Belgique, au Canada… et vous rêvez d'investir au pays ? 🌍\nVisitez votre futur bien en vidéo, en direct, avec un conseiller GEI.\n👉 Rendez-vous en visio : {WA}\n#GlobalEmpireImmobilier #ImmobilierCI #Diaspora #Adiaké",
  notes=["Les services annoncés (visite vidéo en direct, suivi WhatsApp) doivent être confirmés par GEI avant diffusion.",
         "Les plans de villes étrangères proviennent d'une banque d'images sous licence commerciale.",
         "Prévoir une version 15 s pour la publicité (spot B) : plans 2, 4, 5 et 6."],
 ),
 dict(
  num=4, slug="video4-journee-visite-45s", date="Samedi 2 janvier", dur="45 s",
  titre="Une journée de visite avec GEI",
  objectif="Prouver le sérieux de GEI par l'image réelle et donner envie de réserver la prochaine visite.",
  cible="Prospects indécis qui ont déjà vu les offres, toutes cibles.",
  formats="9:16 (Reels, TikTok) + 4:5",
  voix="Féminine, souriante, style récit de journée. Voix off courte, le son direct des visites porte l'émotion.",
  musique="Afro-pop instrumentale entraînante, 110–120 BPM, baissée à -26 dB pendant l'interview.",
  lieu="Départ du bureau GEI (Cocody), trajet, visite de la Cité Les Rives de l'Opulence. À tourner lors d'une vraie journée de visite.",
  casting="L'équipe GEI et de vrais visiteurs volontaires. Autorisation écrite de chaque personne filmée, notamment pour l'interview.",
  materiel="Hybride + 24-70 mm, stabilisateur, micro-cravate sans fil pour l'interview, drone pour le plan d'arrivée.",
  plans=[
   ("0:00", "0:04", "Plan large · caméra épaule", "L'équipe GEI accueille les visiteurs devant le bureau, poignées de main.", "Samedi, huit heures. Aujourd'hui, nos clients découvrent leur futur chez-eux.", "UNE JOURNÉE DE VISITE", "Titre en masque, horloge animée « 8:00 »."),
   ("0:04", "0:10", "Plans courts · 3 × 2 s", "Départ en véhicule, route, panneau ou entrée de la cité.", "", "", "Montage rythmé sur la musique, son d'ambiance de route."),
   ("0:10", "0:15", "Drone · arrivée", "Le véhicule entre dans la cité, vue d'ensemble.", "Avec Global Empire Immobilier, on ne vous vend pas un bien sur photo : on vous emmène le voir.", "✓ VISITE ACCOMPAGNÉE", ""),
   ("0:15", "0:30", "Plans moyens et serrés", "Le conseiller fait visiter la villa, explique, montre ; les visiteurs posent des questions, touchent les finitions.", "Sur place, nos conseillers répondent à toutes vos questions : le prix, l'échéancier, les documents.", "VOS QUESTIONS, NOS RÉPONSES", "Son direct des échanges en alternance avec la voix off."),
   ("0:30", "0:40", "Interview · plan poitrine, regard à côté de l'objectif", "Un visiteur ou une visiteuse donne son impression spontanée.", "(Son direct : réponse réelle, non scénarisée)", "Prénom du visiteur", "Musique baissée, sous-titres de la réponse exacte."),
   ("0:40", "0:45", "Écran de fin", "Logo GEI, bandeau vert, WhatsApp.", "La prochaine visite, c'est peut-être la vôtre. Réservez votre place sur WhatsApp.", f"RÉSERVEZ VOTRE PLACE · {WA}", "Remontée de la musique, fondu final."),
  ],
  accroches=["« Samedi, 8 heures. Aujourd'hui, nos clients découvrent leur futur chez-eux. » (version principale)",
             "« On ne vous vend pas un bien sur photo : on vous emmène le voir. »",
             "« Voici comment se passe une visite chez GEI. »"],
  legende=f"Une journée de visite avec GEI 🚐🏡\nOn ne vous vend pas un bien sur photo : on vous emmène le voir.\n👉 Réservez votre place pour la prochaine visite : {WA}\n#GlobalEmpireImmobilier #ImmobilierCI #Propriétaire",
  interview=["Qu'est-ce qui vous a donné envie de venir visiter aujourd'hui ?",
             "Quelle a été votre première impression en arrivant ?",
             "Qu'est-ce qui compte le plus pour vous dans ce projet ?",
             "Que diriez-vous à quelqu'un qui hésite encore ?"],
  notes=["Ne jamais écrire ni souffler les réponses de l'interview : on garde les mots réels, même imparfaits (5 à 10 s).",
         "Si aucun visiteur ne souhaite témoigner, remplacer le plan 5 par le conseiller qui résume la journée.",
         "La date de publication (2 janvier) suppose une journée de visite filmée avant le 30 décembre."],
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
    <h1>Scripts vidéo<br><em>décembre 2026</em></h1>
    <p class="sub">Scripts de production complets des 4 vidéos du mois : découpage plan par plan, texte intégral des voix off, son, motion design, casting et légendes.</p>
  </div>
  <div class="photo"></div>
  <div class="meta">
    <div><b>RÉALISÉ PAR 7CREATIVE</b>Direction artistique et production</div>
    <div style="text-align:right"><b>À VALIDER PAR GEI</b>Version 1 · novembre 2026</div>
  </div>
</section>''')

rows = "".join(f'<tr><td><b>Vidéo {v["num"]}</b></td><td>{v["titre"]}</td><td>{v["dur"]}</td><td>{v["date"]}</td></tr>' for v in VIDEOS)
pages.append(f'''<section class="page">{top()}
  <div class="kicker">Vue d'ensemble</div>
  <h2>4 vidéos,<br>un seul <span class="gold">fil rouge</span>.</h2>
  <table style="margin-bottom:6mm"><tr><th>N°</th><th>Titre</th><th>Durée</th><th>Publication</th></tr>{rows}</table>
  <h3>Calendrier de production</h3>
  <table class="sm" style="margin-bottom:6mm">
    <tr><td><b>Jusqu'au 3 déc.</b></td><td>Validation des scripts par GEI, casting de la famille figurante, choix du conseiller face caméra</td></tr>
    <tr><td><b>5 déc.</b></td><td>Tournage n° 1 : Rives de l'Opulence (vidéos 1 et 3) et bureau de Cocody (vidéo 2)</td></tr>
    <tr><td><b>6 – 9 déc.</b></td><td>Montage, motion design, enregistrement des voix off, sous-titres</td></tr>
    <tr><td><b>9 déc.</b></td><td>Envoi des vidéos 1 à 3 à GEI pour validation sous 48 h</td></tr>
    <tr><td><b>Avant le 30 déc.</b></td><td>Tournage d'une journée de visite réelle (vidéo 4), montage et validation</td></tr>
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
      <li>Image de couverture (déjà créée dans les visuels de décembre)</li>
      <li>Musique sous licence commerciale, référence archivée</li></ul></div>
  </div>
{foot(2)}</section>''')

def interview_block(v):
    if not v.get("interview"):
        return ""
    return ('<div class="card" style="margin-top:5mm"><h3>Guide d\'interview (plan 5)</h3><ul class="check sm">'
            + "".join(f"<li>{q}</li>" for q in v["interview"]) + "</ul></div>")

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
{foot(n)}</section>''')
    n += 1
    extra = ""
    acc = "".join(f"<li>{a}</li>" for a in v["accroches"])
    notes = "".join(f"<li>{x}</li>" for x in v["notes"])
    pages.append(f'''<section class="page">{top()}
  <div class="kicker">Vidéo {v["num"]} · Texte intégral</div>
  <h2 style="font-size:19pt">Fiche technique et <span class="gold">texte</span>.</h2>
  <table class="fiche"><tr><td>Cible</td><td>{v["cible"]}</td></tr><tr><td>Formats</td><td>{v["formats"]}</td></tr><tr><td>Voix</td><td>{v["voix"]}</td></tr><tr><td>Musique</td><td>{v["musique"]}</td></tr><tr><td>Lieu</td><td>{v["lieu"]}</td></tr><tr><td>Casting</td><td>{v["casting"]}</td></tr><tr><td>Matériel</td><td>{v["materiel"]}</td></tr></table>
  <div class="card dark" style="padding:5mm 6mm;margin-top:4mm">
    <div class="kicker">Voix off · {nb} mots · environ {v["dur"]}</div>
    <p style="color:#fff;font-size:10.5pt;line-height:1.6;font-style:italic">« {txt} »</p>
  </div>
  <p class="note">Respirations : une courte pause à chaque point, une pause plus longue avant l'appel à l'action. Les chiffres se prononcent en toutes lettres.</p>
  <div class="grid2 sm" style="gap:4mm;margin-top:3mm">
    <div class="card"><h3>Accroches à tester</h3><ul class="check">{acc}</ul></div>
    <div class="card"><h3>Légende de publication</h3><pre class="cap">{v["legende"]}</pre></div>
  </div>
  {extra}
  <div class="card" style="margin-top:4mm;border-top-color:#C62828"><h3>Points de vigilance</h3><ul class="check sm">{notes}</ul></div>
{foot(n)}</section>''')
    n += 1

pages.append(f'''<section class="page cta">
  <div class="logo-card" style="position:absolute;top:12mm;right:16mm"><img src="{IMG}logo-gei.png" alt="" style="height:20mm"></div>
  <div class="kicker" style="margin-top:6mm">Avant le tournage du 5 décembre</div>
  <h2>La check-list<br>de <span class="gold">validation</span>.</h2>
  <ul class="check" style="margin-top:6mm">
    <li>GEI valide les 4 scripts, en particulier les textes juridiques (vidéo 2) et les services annoncés (vidéo 3)</li>
    <li>GEI désigne le conseiller qui parlera face caméra et lui transmet le texte</li>
    <li>La famille figurante est choisie et les autorisations de droit à l'image sont prêtes</li>
    <li>L'accès à la Cité Les Rives de l'Opulence est confirmé, avec une villa présentable (et ses intérieurs si possible)</li>
    <li>L'autorisation de vol du drone est vérifiée pour le site</li>
    <li>La date de la journée de visite filmée (vidéo 4) est fixée avant le 30 décembre</li>
    <li>Le numéro WhatsApp affiché à la fin des vidéos est confirmé</li>
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
