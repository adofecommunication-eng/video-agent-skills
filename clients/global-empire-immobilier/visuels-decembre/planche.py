"""Génère planche.html : planche de validation des 16 publications de décembre, avec légendes."""
import glob, os

D = os.path.dirname(os.path.abspath(__file__))
WA = "(+225) 07 04 75 53 06"
TAGS = "#GlobalEmpireImmobilier #ImmobilierCI #Abidjan #Propriétaire"

posts = [
 ("01", "Lun 7 déc.", "Carrousel · 5 slides", "Qui est GEI ?",
  f"Faisons connaissance 👋\nChez Global Empire Immobilier, notre mission est simple : vous rendre propriétaire en toute sécurité.\n✔ Terrains et villas\n✔ Visite accompagnée\n✔ Paiement progressif\n📍 Cocody, Cité des Arts · 💬 WhatsApp {WA}\n{TAGS}"),
 ("02", "Mer 9 déc.", "Affiche", "Villa Rives de l'Opulence",
  f"🏡 Devenez propriétaire de votre villa à Adiaké !\nCité Les Rives de l'Opulence\n✔ Prix d'acquisition : 45 M FCFA\n✔ Apport initial : 15 M FCFA\n✔ Paiement progressif · Habitation immédiate\n👉 Réservez votre visite sur WhatsApp : {WA}\n{TAGS} #Adiaké"),
 ("03", "Ven 11 déc.", "Vidéo 1 · couverture", "Les Rives de l'Opulence en 30 s",
  f"30 secondes pour découvrir votre future villa à Adiaké 🌴\nHabitation immédiate, paiement progressif.\n👉 Visite sur rendez-vous : {WA}\n{TAGS} #Adiaké"),
 ("04", "Sam 12 déc.", "Carrousel · 7 slides", "5 vérifications avant d'acheter",
  f"Acheter un terrain ? Faites ces 5 vérifications avant de payer ⚠️\nEnregistrez ce post 📌 et partagez-le à un proche qui a un projet.\nUne question ? Écrivez-nous : {WA}\n{TAGS} #GEIvousExplique"),
 ("05", "Lun 14 déc.", "Photo · gabarit", "L'équipe GEI",
  f"Derrière chaque projet, une équipe à vos côtés 🤝\nDe la première visite à la remise des documents, nous vous accompagnons.\n📍 Cocody, Cité des Arts · 💬 {WA}\n{TAGS}"),
 ("06", "Mer 16 déc.", "Affiche · gabarit", "Deuxième programme GEI",
  f"[Nom du programme] à [zone] 📍\n✔ [superficie] · ✔ [prix / apport]\n👉 Informations et visite : {WA}\n{TAGS}"),
 ("07", "Ven 18 déc.", "Vidéo 2 · couverture", "L'ACD, c'est quoi ?",
  f"L'ACD, c'est quoi ? 🤔 Le document que vous devez connaître avant d'acheter un terrain.\nRegardez jusqu'au bout et posez vos questions en commentaire 👇\n{TAGS} #GEIvousExplique"),
 ("08", "Sam 19 déc.", "Photo · gabarit", "Nouveau propriétaire",
  f"Félicitations à [prénom], nouveau propriétaire ! 🎉🔑\nMerci pour votre confiance. À qui le tour ?\n💬 {WA}\n{TAGS}"),
 ("09", "Lun 21 déc.", "Carrousel · 6 slides", "Le paiement progressif",
  f"Le paiement progressif, comment ça marche ? 💡\nÀ la Cité Les Rives de l'Opulence : frais de dossier, apport initial, puis le solde selon votre échéancier.\n👉 Demandez votre échéancier personnalisé : {WA}\n{TAGS} #Adiaké"),
 ("10", "Mer 23 déc.", "Visuel", "Et si 2027… ?",
  f"Et si 2027 était l'année de votre maison ? ✨\nTerrains et villas, avec paiement progressif.\n👉 Parlons de votre projet : {WA}\n{TAGS}"),
 ("11", "Ven 25 déc.", "Visuel", "Joyeux Noël",
  "Joyeux Noël à toutes les familles ! 🎄\nQue la paix, la joie et l'amour remplissent chaque foyer.\n— Toute l'équipe Global Empire Immobilier\n#GlobalEmpireImmobilier #JoyeuxNoël"),
 ("12", "Sam 26 déc.", "Vidéo 3 · couverture", "Diaspora : on vous fait visiter",
  f"Vous êtes en France, en Belgique, au Canada… et vous rêvez d'investir au pays ? 🌍\nVisitez votre futur bien en vidéo, en direct, avec un conseiller GEI.\n👉 Rendez-vous en visio : {WA}\n{TAGS} #Diaspora"),
 ("13", "Lun 28 déc.", "Carrousel · 6 slides", "Le vrai coût d'un achat",
  f"Le prix du bien n'est pas la seule dépense 💰\nVoici ce qu'il faut prévoir pour acheter sereinement. Enregistrez ce post 📌\n👉 Demandez le détail des coûts : {WA}\n{TAGS} #GEIvousExplique"),
 ("14", "Mer 30 déc.", "Affiche", "Commencez 2027 propriétaire",
  f"Commencez 2027 propriétaire 🏡✨\nVilla à la Cité Les Rives de l'Opulence, Adiaké : 45 M FCFA, apport 15 M, paiement progressif.\n👉 Réservez votre visite : {WA}\n{TAGS} #Adiaké"),
 ("15", "Ven 1er janv.", "Visuel", "Bonne année 2027",
  "Bonne et heureuse année 2027 ! 🎉\nSanté, paix… et votre chez-vous.\n— Toute l'équipe Global Empire Immobilier\n#GlobalEmpireImmobilier #BonneAnnée2027"),
 ("16", "Sam 2 janv.", "Vidéo 4 · couverture", "Une journée de visite",
  f"Une journée de visite avec GEI 🚐🏡\nOn ne vous vend pas un bien sur photo : on vous emmène le voir.\n👉 Réservez votre place pour la prochaine visite : {WA}\n{TAGS}"),
]

css = """
@page{size:A4;margin:0}*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Montserrat,sans-serif;color:#141B3D;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.pg{width:210mm;height:297mm;padding:14mm 14mm 12mm;page-break-after:always;position:relative}
.bar{position:absolute;top:0;left:0;right:0;height:3mm;background:linear-gradient(90deg,#0A1496 0 62%,#1F5BE0 62% 80%,#6B8E23 80%)}
h1{font-size:20pt;font-weight:900;color:#0A1496;text-transform:uppercase;margin:3mm 0 1mm}
.sub{font-size:9pt;color:#55607A;margin-bottom:6mm}
.post{display:grid;grid-template-columns:62mm 1fr;gap:7mm;margin-bottom:9mm;align-items:start}
.thumbs{display:flex;flex-wrap:wrap;gap:1.5mm}
.thumbs img{width:62mm;border-radius:1.5mm;box-shadow:0 .5mm 2mm rgba(10,20,150,.2)}
.thumbs.multi img{width:19.6mm}.thumbs.multi img:first-child{width:62mm}
.meta{font-size:8pt;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#6B8E23}
h2{font-size:13pt;font-weight:800;color:#0A1496;margin:1mm 0 3mm}
pre{white-space:pre-wrap;font-family:Montserrat,sans-serif;font-size:8.6pt;line-height:1.5;background:#F1F4FC;border-left:1mm solid #6B8E23;padding:3mm 4mm;border-radius:1mm}
.gab{display:inline-block;background:#FFF7C2;color:#8A6D00;font-size:7.5pt;font-weight:800;padding:.6mm 2mm;border-radius:3mm;margin-left:2mm}
.foot{position:absolute;left:14mm;right:14mm;bottom:7mm;font-size:7pt;color:#55607A;display:flex;justify-content:space-between}
"""

from PIL import Image
os.makedirs(os.path.join(D, "thumbs"), exist_ok=True)
def thumb(f):
    t = os.path.join("thumbs", os.path.basename(f).replace(".png", ".jpg"))
    Image.open(f).convert("RGB").resize((540, 675)).save(os.path.join(D, t), quality=85)
    return t

pages, cur = [], []
for i, (num, date, fmt, title, cap) in enumerate(posts):
    files = sorted(glob.glob(os.path.join(D, "png", f"{num}_*.png")))
    imgs = "".join(f'<img src="{thumb(f)}">' for f in files)
    gab = '<span class="gab">GABARIT À COMPLÉTER</span>' if "GABARIT" in files[0] else ""
    cur.append(f'<div class="post"><div class="thumbs {"multi" if len(files) > 1 else ""}">{imgs}</div>'
               f'<div><div class="meta">{num} · {date} · {fmt}</div><h2>{title}{gab}</h2><pre>{cap}</pre></div></div>')
    if len(cur) == 2 or i == len(posts) - 1:
        pages.append(cur); cur = []

body = ""
for k, p in enumerate(pages):
    head = ('<h1>Publications de décembre 2026</h1><div class="sub">Global Empire Immobilier · 16 publications · visuels 1080×1350 · légendes prêtes à publier · à valider par GEI</div>' if k == 0 else "")
    body += f'<section class="pg"><div class="bar"></div>{head}{"".join(p)}<div class="foot"><span>GLOBAL EMPIRE IMMOBILIER SARL × 7CREATIVE</span><span>{k+1}/{len(pages)}</span></div></section>'

open(os.path.join(D, "planche.html"), "w", encoding="utf-8").write(
    '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Planche décembre GEI</title>'
    '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&display=swap" rel="stylesheet">'
    f'<style>{css}</style></head><body>{body}</body></html>')
print(len(pages), "pages")
