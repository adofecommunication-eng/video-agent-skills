"""Génère visuels.html : les 16 publications de décembre 2026 pour GEI (format 1080x1350).
Chaque visuel est un <section class="s" data-name="..."> rendu en PNG par render.js."""

IMG = "../presentation/img/"
WA = "(+225) 07 10 29 67 20"
SITE = "geisarl.com"
ADDR = "Cocody, Cité des Arts"

CSS = """
:root{--navy:#0A1496;--blue:#1F5BE0;--green:#6B8E23;--lime:#D4E021;--ink:#141B3D;--cream:#F1F4FC}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Montserrat,sans-serif;background:#ddd}
.s{width:1080px;height:1350px;position:relative;overflow:hidden;background:#fff;margin:0 0 20px}
.blue{background:linear-gradient(180deg,var(--navy) 0%,#0B1FB0 60%,var(--blue) 100%);color:#fff}
.logo{position:absolute;top:44px;left:56px;background:#fff;border-radius:18px;padding:10px 14px;z-index:5}
.logo img{height:96px;display:block}
.brand{position:absolute;top:66px;right:56px;text-align:right;z-index:5}
.brand b{display:block;font-size:20px;letter-spacing:.24em;font-weight:800;color:var(--navy)}
.brand span{font-size:17px;font-weight:700;color:var(--green);letter-spacing:.06em}
.blue .brand b{color:#fff}.blue .brand span{color:var(--lime)}
.kick{font-size:24px;font-weight:800;letter-spacing:.22em;color:var(--green);text-transform:uppercase;margin-bottom:22px}
.blue .kick{color:var(--lime)}
h1{font-weight:900;text-transform:uppercase;line-height:1.02;letter-spacing:-.01em;color:var(--navy)}
.blue h1{color:#fff}
h1 em{font-style:normal;color:var(--green)}
.blue h1 em{color:var(--lime)}
p.t{font-size:32px;line-height:1.45;font-weight:500;color:var(--ink)}
.blue p.t{color:#E3E8F7}
.cta{position:absolute;left:0;right:0;bottom:0;height:140px;background:var(--green);display:flex;align-items:center;justify-content:space-between;padding:0 56px;color:#fff;z-index:6}
.cta .l b{display:block;font-size:28px;font-weight:900;text-transform:uppercase}
.cta .l span{font-size:19px;font-weight:600}
.cta .r{font-size:32px;font-weight:900;display:flex;align-items:center;gap:12px}
.cta .r svg{width:34px;height:34px}
.photo{position:absolute;left:0;right:0;background-size:cover;background-position:center}
.ov:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,20,150,0) 30%,rgba(10,20,150,.8) 75%,var(--navy) 100%)}
.tag{display:inline-block;background:var(--lime);color:var(--navy);font-weight:900;font-size:24px;letter-spacing:.14em;padding:12px 22px;border-radius:6px}
.check{list-style:none}
.check li{font-size:31px;font-weight:700;padding-left:58px;position:relative;margin-bottom:22px;line-height:1.3}
.check li:before{content:"✓";position:absolute;left:0;top:-2px;width:40px;height:40px;border-radius:50%;background:var(--lime);color:var(--navy);display:grid;place-items:center;font-size:22px;font-weight:900}
/* carrousel */
.dots{position:absolute;bottom:60px;left:56px;display:flex;gap:10px;z-index:6}
.dots i{width:14px;height:14px;border-radius:50%;background:rgba(10,20,150,.18)}
.dots i.on{background:var(--green);width:40px;border-radius:7px}
.blue .dots i{background:rgba(255,255,255,.3)}.blue .dots i.on{background:var(--lime)}
.swipe{position:absolute;bottom:46px;right:56px;font-size:22px;font-weight:800;letter-spacing:.14em;color:var(--green);z-index:6}
.blue .swipe{color:var(--lime)}
.big{font-size:230px;font-weight:900;line-height:.8;color:var(--lime);opacity:.95}
.card{background:var(--cream);border-radius:22px;padding:34px 38px;border-top:10px solid var(--green)}
.blue .card{background:rgba(255,255,255,.08);border-top-color:var(--lime)}
.ph{position:absolute;border:5px dashed rgba(10,20,150,.35);border-radius:22px;display:grid;place-items:center;text-align:center;color:rgba(10,20,150,.55);font-size:26px;font-weight:800;letter-spacing:.08em;background:repeating-linear-gradient(45deg,#F1F4FC 0 24px,#E7ECF9 24px 48px)}
.fill{background:#FFF7C2;color:#8A6D00;padding:0 10px;border-radius:6px}
.play{width:150px;height:150px;border-radius:50%;background:rgba(255,255,255,.92);display:grid;place-items:center;box-shadow:0 10px 40px rgba(0,0,0,.3)}
.play:after{content:"";border-left:52px solid var(--navy);border-top:32px solid transparent;border-bottom:32px solid transparent;margin-left:14px}
.dur{display:inline-block;background:var(--navy);color:#fff;font-weight:800;font-size:22px;padding:8px 16px;border-radius:30px;letter-spacing:.08em}
.price{background:#fff;border-radius:18px;padding:24px 30px;color:var(--navy)}
.price span{font-size:19px;font-weight:800;letter-spacing:.18em;color:var(--green)}
.price b{display:block;font-size:96px;font-weight:900;line-height:.95;margin-top:6px}
.fact{border:2px solid rgba(255,255,255,.35);border-radius:14px;padding:16px 22px;color:#fff}
.fact span{display:block;font-size:16px;letter-spacing:.16em;font-weight:700;color:#C9D3F5}
.fact b{font-size:31px;font-weight:900}
.wm{position:absolute;right:-120px;bottom:-110px;width:640px;opacity:.07;z-index:0}
.star{position:absolute;color:var(--lime);font-weight:900}
"""

WA_SVG = '<svg viewBox="0 0 24 24" fill="#fff"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.5-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.9s.7-2.1 1-2.4c.3-.3.6-.3.8-.3h.6c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .6l-.4.6-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.5.3.1.5.1.6-.1l.9-1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.2.1.7-.1 1.4z"/></svg>'


def head(blue=False):
    return (f'<div class="logo"><img src="{IMG}logo-gei.png" alt=""></div>'
            '<div class="brand"><b>GLOBAL EMPIRE IMMOBILIER</b><span>Achetez en toute sécurité</span></div>')


def cta(title="Réservez votre visite", sub=f"{ADDR} · {SITE}"):
    return (f'<div class="cta"><div class="l"><b>{title}</b><span>{sub}</span></div>'
            f'<div class="r">{WA_SVG}{WA}</div></div>')


def dots(i, n):
    d = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(n))
    return f'<div class="dots">{d}</div>' + ('<div class="swipe">GLISSEZ →</div>' if i < n - 1 else "")


def sec(name, body, cls=""):
    wm = "" if "blue" in cls or "GABARIT" in name or "affiche" in name else f'<img class="wm" src="{IMG}logo-gei.png" alt="">'
    return f'<section class="s {cls}" data-name="{name}">{wm}{body}</section>'


out = []

# ---------- 01 · Lun 7 déc · Carrousel « Qui est GEI ? » (5 slides)
n = 5
out.append(sec("01_07dec_carrousel-qui-est-gei_1", head() + f'''
<div class="photo ov" style="top:0;height:1350px;background-image:url({IMG}villa-adiake.jpg)"></div>
<div style="position:absolute;left:56px;right:56px;bottom:200px;z-index:4">
  <div class="kick" style="color:var(--lime)">Faisons connaissance</div>
  <h1 style="font-size:96px;color:#fff">Qui est<br>Global Empire<br><em style="color:var(--lime)">Immobilier ?</em></h1>
</div>{dots(0,n)}''', "blue"))
out.append(sec("01_07dec_carrousel-qui-est-gei_2", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:300px">
  <div class="kick">Notre mission</div>
  <h1 style="font-size:84px">Vous rendre<br><em>propriétaire</em><br>en toute sécurité.</h1>
  <p class="t" style="margin-top:44px;max-width:900px">Acheter un terrain ou une maison est l'un des plus grands projets d'une vie. Notre rôle : vous accompagner à chaque étape, avec clarté et honnêteté.</p>
</div>{dots(1,n)}'''))
out.append(sec("01_07dec_carrousel-qui-est-gei_3", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:280px">
  <div class="kick">Ce que nous proposons</div>
  <h1 style="font-size:80px;margin-bottom:56px">Du terrain<br>à la <em>villa</em>.</h1>
  <div style="display:grid;gap:26px">
    <div class="card"><b style="font-size:38px;font-weight:900;color:#fff">Terrains</b><p class="t" style="font-size:27px;margin-top:8px">Des lots dans des zones d'avenir pour bâtir ou investir.</p></div>
    <div class="card"><b style="font-size:38px;font-weight:900;color:#fff">Villas</b><p class="t" style="font-size:27px;margin-top:8px">Des maisons prêtes à habiter, comme à la Cité Les Rives de l'Opulence, à Adiaké.</p></div>
  </div>
</div>{dots(2,n)}''', "blue"))
out.append(sec("01_07dec_carrousel-qui-est-gei_4", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:300px">
  <div class="kick">Nos engagements</div>
  <h1 style="font-size:80px;margin-bottom:60px">Avec GEI,<br>vous <em>savez</em><br>où vous allez.</h1>
  <ul class="check" style="color:var(--navy)">
    <li>Une visite accompagnée du bien</li>
    <li>Un paiement progressif, à votre rythme</li>
    <li>Une situation du bien présentée avant signature</li>
    <li>Un conseiller joignable sur WhatsApp</li>
  </ul>
</div>{dots(3,n)}'''))
out.append(sec("01_07dec_carrousel-qui-est-gei_5", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:330px">
  <div class="kick">Venez nous rencontrer</div>
  <h1 style="font-size:92px">Parlons de<br>votre <em>projet</em>.</h1>
  <p class="t" style="margin-top:48px;font-size:36px;line-height:1.6">📍 {ADDR}, Abidjan<br>🌐 {SITE}<br>💬 {WA}</p>
</div>{cta("Écrivez-nous sur WhatsApp")}''', "blue"))

# ---------- 02 · Mer 9 déc · Affiche Rives de l'Opulence
def affiche(name, tag, small, title, cta_t="Réservez votre visite"):
    return sec(name, head() + f'''
<div class="photo ov" style="top:0;height:820px;background-image:url({IMG}villa-adiake.jpg);background-position:center 40%"></div>
<div style="position:absolute;top:190px;left:56px;z-index:4"><span class="tag">{tag}</span></div>
<div style="position:absolute;left:56px;right:56px;top:560px;z-index:4">
  <div class="kick" style="color:var(--lime);margin-bottom:10px">{small}</div>
  <h1 style="font-size:68px;color:#fff">{title}</h1>
</div>
<div style="position:absolute;top:820px;left:0;right:0;bottom:140px;padding:30px 56px 0" class="blue">
  <div style="font-size:28px;font-weight:800;letter-spacing:.06em;margin-bottom:24px">📍 ADIAKÉ · CÔTE D'IVOIRE</div>
  <div style="display:grid;grid-template-columns:1.05fr 1fr;gap:26px">
    <div class="price"><span>PRIX D'ACQUISITION</span><b>45 M</b><span style="letter-spacing:.06em;font-size:24px">FCFA</span></div>
    <div style="display:flex;flex-direction:column;gap:14px">
      <div class="fact"><span>APPORT INITIAL</span><b>15 000 000 FCFA</b></div>
      <div class="fact"><span>FRAIS DE DOSSIER</span><b>300 000 FCFA</b></div>
    </div>
  </div>
  <div style="margin-top:22px;font-size:25px;font-weight:700">✓ Paiement progressif &nbsp;&nbsp; ✓ Habitation immédiate</div>
</div>{cta(cta_t)}''')

out.append(affiche("02_09dec_affiche-rives-opulence", "VILLA EN VENTE", "Cité Les Rives de l'Opulence", "Devenez propriétaire<br>de votre villa"))

# ---------- 03 · Ven 11 déc · Couverture vidéo 1
def cover(name, dur, kick, title, sub, photo=True):
    bg = (f'<div class="photo" style="top:0;height:1350px;background-image:url({IMG}villa-adiake.jpg)"></div>'
          '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,20,150,.25),rgba(10,20,150,.55) 45%,var(--navy) 88%)"></div>') if photo else ""
    return sec(name, bg + head() + f'''
<div style="position:absolute;top:430px;left:0;right:0;display:grid;place-items:center;z-index:4"><div class="play"></div></div>
<div style="position:absolute;left:56px;right:56px;bottom:200px;z-index:4">
  <span class="dur" style="background:var(--lime);color:var(--navy)">▶ VIDÉO · {dur}</span>
  <div class="kick" style="color:var(--lime);margin:26px 0 12px">{kick}</div>
  <h1 style="font-size:78px;color:#fff">{title}</h1>
  <p class="t" style="color:#E3E8F7;margin-top:18px">{sub}</p>
</div>''', "blue")

out.append(cover("03_11dec_video1-couverture-rives-30s", "30 S", "Cité Les Rives de l'Opulence",
                 "Votre villa<br>à <em>Adiaké</em>", "Visitez-la en 30 secondes."))

# ---------- 04 · Sam 12 déc · Carrousel « 5 vérifications » (7 slides)
n = 7
out.append(sec("04_12dec_carrousel-5-verifications_1", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:300px">
  <span class="tag">GEI VOUS EXPLIQUE</span>
  <div class="big" style="margin-top:40px">5</div>
  <h1 style="font-size:84px;margin-top:10px">vérifications<br>avant d'acheter<br>un <em>terrain</em>.</h1>
</div>{dots(0,n)}''', "blue"))
steps = [
    ("Le vendeur", "Qui vend ? Demandez l'identité du vendeur ou les documents de la société (registre du commerce, agrément pour un promoteur)."),
    ("Le document", "Quel est le statut du terrain : ACD, lettre d'attribution, attestation villageoise ? Demandez à consulter les originaux."),
    ("Le terrain lui-même", "Visitez sur place. Vérifiez les bornes, les limites et l'accès. Un géomètre peut confirmer la superficie."),
    ("Le lotissement", "Le lotissement est-il approuvé ? Le terrain n'est-il pas sur une réserve, une voie ou une zone non constructible ?"),
    ("Le paiement", "Payez de façon traçable, avec reçu et contrat écrit. Faites-vous accompagner par un notaire."),
]
for i, (t, d) in enumerate(steps, start=1):
    out.append(sec(f"04_12dec_carrousel-5-verifications_{i+1}", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:300px">
  <div class="big" style="color:var(--green);font-size:200px">{i}</div>
  <div class="kick" style="margin-top:20px">Vérification {i} sur 5</div>
  <h1 style="font-size:86px">{t}</h1>
  <p class="t" style="margin-top:40px;font-size:36px;max-width:920px">{d}</p>
</div>{dots(i,n)}'''))
out.append(sec("04_12dec_carrousel-5-verifications_7", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:320px">
  <div class="kick">Une question ?</div>
  <h1 style="font-size:84px">Chez GEI,<br>on vous <em>explique</em><br>tout avant<br>de signer.</h1>
  <p class="t" style="margin-top:40px">Enregistrez ce post et partagez-le à un proche qui veut acheter.</p>
</div>{cta("Posez votre question")}''', "blue"))

# ---------- 05 · Lun 14 déc · Photo équipe (gabarit)
out.append(sec("05_14dec_photo-equipe_GABARIT", head() + f'''
<div class="ph" style="left:56px;right:56px;top:190px;height:700px">PHOTO DE L'ÉQUIPE GEI<br>(tournage du 5 décembre)</div>
<div style="position:absolute;left:56px;right:56px;top:930px">
  <div class="kick">Ceux qui vous accompagnent</div>
  <h1 style="font-size:66px">Une équipe <em>à vos côtés</em>,<br>de la visite aux documents.</h1>
</div>{cta("Rencontrez-nous", f"{ADDR} · {SITE}")}'''))

# ---------- 06 · Mer 16 déc · Deuxième programme (gabarit)
out.append(sec("06_16dec_affiche-programme-2_GABARIT", head() + f'''
<div class="ph" style="left:0;right:0;top:170px;height:640px;border-radius:0;border-left:0;border-right:0">PHOTO DU PROGRAMME</div>
<div style="position:absolute;top:210px;left:56px"><span class="tag">TERRAINS / MAISONS EN VENTE</span></div>
<div style="position:absolute;top:810px;left:0;right:0;bottom:140px;padding:40px 56px 0" class="blue">
  <div class="kick" style="margin-bottom:10px"><span class="fill">[NOM DU PROGRAMME]</span></div>
  <h1 style="font-size:64px;color:#fff">Votre <em>terrain</em><br>à <span class="fill">[ZONE]</span></h1>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:30px">
    <div class="fact"><span>SUPERFICIE</span><b><span class="fill">[ ] m²</span></b></div>
    <div class="fact"><span>PRIX / APPORT</span><b><span class="fill">[ ] FCFA</span></b></div>
  </div>
</div>{cta()}'''))

# ---------- 07 · Ven 18 déc · Couverture vidéo 2 (ACD)
out.append(sec("07_18dec_video2-couverture-acd-45s", head() + f'''
<div style="position:absolute;top:250px;left:56px;right:56px">
  <span class="tag">GEI VOUS EXPLIQUE</span>
  <h1 style="font-size:150px;margin-top:50px;color:#fff">L'ACD,</h1>
  <h1 style="font-size:92px;color:var(--lime)">c'est quoi ?</h1>
  <p class="t" style="margin-top:40px;max-width:860px">Le document que vous devez connaître avant d'acheter un terrain.</p>
</div>
<div style="position:absolute;right:70px;bottom:150px"><div class="play"></div></div>
<div style="position:absolute;left:56px;bottom:180px"><span class="dur" style="background:var(--lime);color:var(--navy)">▶ VIDÉO · 45 S</span></div>''', "blue"))

# ---------- 08 · Sam 19 déc · Remise de documents (gabarit)
out.append(sec("08_19dec_photo-remise-documents_GABARIT", head() + f'''
<div class="ph" style="left:56px;right:56px;top:190px;height:720px">PHOTO : REMISE DE DOCUMENTS<br>OU DE CLÉS À UN CLIENT<br>(avec son autorisation écrite)</div>
<div style="position:absolute;left:56px;right:56px;top:950px">
  <div class="kick">Un moment qui compte</div>
  <h1 style="font-size:60px">Félicitations à <span class="fill">[prénom]</span>,<br><em>nouveau propriétaire</em> !</h1>
</div>{cta("À qui le tour ?")}'''))

# ---------- 09 · Lun 21 déc · Carrousel paiement progressif (6 slides)
n = 6
out.append(sec("09_21dec_carrousel-paiement-progressif_1", f'''
<div class="photo ov" style="top:0;height:1350px;background-image:url({IMG}villa-adiake.jpg)"></div>''' + head() + f'''
<div style="position:absolute;left:56px;right:56px;bottom:200px;z-index:4">
  <span class="tag">CITÉ LES RIVES DE L'OPULENCE</span>
  <h1 style="font-size:88px;color:#fff;margin-top:30px">Le paiement<br><em>progressif</em>,<br>comment ça marche ?</h1>
</div>{dots(0,n)}''', "blue"))
pay = [
    ("Étape 1", "Les frais de dossier", "300 000 FCFA", "Pour ouvrir votre dossier d'acquisition."),
    ("Étape 2", "L'apport initial", "15 000 000 FCFA", "Votre premier versement sur le prix de la villa."),
    ("Étape 3", "Le solde", "30 000 000 FCFA", "Réglé progressivement, selon l'échéancier convenu avec votre conseiller GEI."),
    ("Le +", "Habitation immédiate", "Prête à habiter", "La villa est déjà construite. Votre conseiller vous détaille toutes les conditions."),
]
for i, (k, t, v, d) in enumerate(pay, start=1):
    out.append(sec(f"09_21dec_carrousel-paiement-progressif_{i+1}", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:320px">
  <div class="kick">{k}</div>
  <h1 style="font-size:82px">{t}</h1>
  <div class="price" style="background:var(--navy);color:#fff;margin-top:50px;padding:40px 44px"><b style="font-size:84px;color:var(--lime)">{v}</b></div>
  <p class="t" style="margin-top:40px;font-size:36px">{d}</p>
</div>{dots(i,n)}'''))
out.append(sec("09_21dec_carrousel-paiement-progressif_6", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:330px">
  <div class="kick">Prix d'acquisition : 45 M FCFA</div>
  <h1 style="font-size:88px">Recevez<br>votre <em>échéancier</em><br>personnalisé.</h1>
  <p class="t" style="margin-top:40px">Un conseiller GEI vous répond sur WhatsApp et vous propose une visite de la cité.</p>
</div>{cta("Demandez votre échéancier")}''', "blue"))

# ---------- 10 · Mer 23 déc · « Et si 2027… »
out.append(sec("10_23dec_visuel-2027-annee-maison", head() + f'''
<div class="star" style="top:250px;right:120px;font-size:90px">✦</div>
<div class="star" style="top:420px;right:260px;font-size:44px">✦</div>
<div style="position:absolute;left:56px;right:56px;top:330px">
  <div class="kick">Votre résolution 2027</div>
  <h1 style="font-size:104px">Et si<br><em>2027</em><br>était l'année<br>de votre<br>maison ?</h1>
</div>{cta("Commencez votre projet", f"Terrains et villas · {SITE}")}''', "blue"))

# ---------- 11 · Ven 25 déc · Joyeux Noël
out.append(sec("11_25dec_visuel-joyeux-noel", head() + f'''
<div class="star" style="top:240px;left:50%;transform:translateX(-50%);font-size:120px">✦</div>
<div style="position:absolute;left:56px;right:56px;top:420px;text-align:center">
  <h1 style="font-size:130px">Joyeux<br><em>Noël</em></h1>
  <p class="t" style="margin-top:50px;font-size:36px">Que la paix, la joie et l'amour remplissent<br>chaque foyer en ce jour de fête.</p>
  <p class="t" style="margin-top:30px;font-size:28px;font-weight:700;color:var(--lime)">— Toute l'équipe Global Empire Immobilier</p>
</div>''', "blue"))

# ---------- 12 · Sam 26 déc · Couverture vidéo 3 (diaspora)
out.append(cover("12_26dec_video3-couverture-diaspora-30s", "30 S", "Diaspora",
                 "Vous êtes loin ?<br>On vous fait <em>visiter</em>.", "Investir au pays, même depuis l'étranger."))

# ---------- 13 · Lun 28 déc · Carrousel le vrai coût (6 slides)
n = 6
out.append(sec("13_28dec_carrousel-vrai-cout_1", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:320px">
  <span class="tag">GEI VOUS EXPLIQUE</span>
  <h1 style="font-size:96px;margin-top:44px">Le <em>vrai coût</em><br>d'un achat<br>immobilier.</h1>
  <p class="t" style="margin-top:36px">Le prix du bien n'est pas la seule dépense. Voici ce qu'il faut prévoir.</p>
</div>{dots(0,n)}''', "blue"))
cost = [
    ("Le prix du bien", "C'est le montant principal. Avec un paiement progressif, il se règle en plusieurs fois : un apport, puis des échéances."),
    ("Les frais de dossier", "Ils ouvrent votre dossier d'acquisition. Exemple : 300 000 FCFA à la Cité Les Rives de l'Opulence."),
    ("Les frais de notaire et d'enregistrement", "Ils sécurisent la vente. Leur montant varie selon le bien : demandez toujours un devis au notaire."),
    ("Les frais liés aux documents", "Selon la situation du terrain, l'obtention ou la mutation du titre peut entraîner des frais. Renseignez-vous avant de signer."),
]
for i, (t, d) in enumerate(cost, start=1):
    out.append(sec(f"13_28dec_carrousel-vrai-cout_{i+1}", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:320px">
  <div class="big" style="color:var(--green);font-size:180px">{i}</div>
  <h1 style="font-size:74px;margin-top:20px">{t}</h1>
  <p class="t" style="margin-top:40px;font-size:36px;max-width:930px">{d}</p>
</div>{dots(i,n)}'''))
out.append(sec("13_28dec_carrousel-vrai-cout_6", head() + f'''
<div style="position:absolute;left:56px;right:56px;top:330px">
  <div class="kick">Zéro surprise</div>
  <h1 style="font-size:86px">On vous<br>détaille <em>tout</em><br>avant de<br>signer.</h1>
  <p class="t" style="margin-top:40px">Demandez le récapitulatif complet des coûts à un conseiller GEI.</p>
</div>{cta("Demandez le détail")}''', "blue"))

# ---------- 14 · Mer 30 déc · Affiche fin d'année
out.append(affiche("14_30dec_affiche-commencez-2027-proprietaire", "VILLA EN VENTE", "Cité Les Rives de l'Opulence",
                   "Commencez 2027<br><em>propriétaire</em>", "Réservez votre visite"))

# ---------- 15 · Ven 1er janv · Bonne année
out.append(sec("15_01jan_visuel-bonne-annee-2027", head() + f'''
<div class="star" style="top:250px;left:120px;font-size:70px">✦</div>
<div class="star" style="top:300px;right:140px;font-size:46px">✦</div>
<div style="position:absolute;left:56px;right:56px;top:380px;text-align:center">
  <div class="kick">Bonne et heureuse année</div>
  <div style="font-size:300px;font-weight:900;line-height:.9;color:var(--lime)">2027</div>
  <p class="t" style="margin-top:50px;font-size:36px">Que cette nouvelle année vous apporte<br>la santé, la paix… et votre chez-vous.</p>
  <p class="t" style="margin-top:30px;font-size:28px;font-weight:700;color:var(--lime)">— Toute l'équipe Global Empire Immobilier</p>
</div>''', "blue"))

# ---------- 16 · Sam 2 janv · Couverture vidéo 4
out.append(cover("16_02jan_video4-couverture-journee-visite-45s", "45 S", "Dans les coulisses",
                 "Une journée<br>de <em>visite</em><br>avec GEI", "Suivez nos clients jusqu'à leur futur chez-eux."))

html = ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Visuels GEI décembre</title>'
        '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&display=swap" rel="stylesheet">'
        f'<style>{CSS}</style></head><body>' + "\n".join(out) + '</body></html>')
open(__file__.replace("build.py", "visuels.html"), "w", encoding="utf-8").write(html)
print(len(out), "slides")
