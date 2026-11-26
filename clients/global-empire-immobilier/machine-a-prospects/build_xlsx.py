"""Tableau de suivi des prospects GEI (Excel) : Mode d'emploi, Prospects, Tableau de bord, Listes."""
import os, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter as L
from openpyxl.comments import Comment

D = os.path.dirname(os.path.abspath(__file__))
NAVY, BLUE, GREEN, LIME = "0A1496", "1F5BE0", "6B8E23", "D4E021"
F = "Arial"
thin = Side(style="thin", color="D9E0F2")
B = Border(left=thin, right=thin, top=thin, bottom=thin)
AUTO = PatternFill("solid", fgColor="EEF1F8")      # colonnes automatiques
HEAD = PatternFill("solid", fgColor=NAVY)
HEAD2 = PatternFill("solid", fgColor=GREEN)
N_ROWS = 500
FIRST = 5
LAST = FIRST + N_ROWS - 1

wb = Workbook()

# ------------------------------------------------------------ Listes
ls = wb.active; ls.title = "Listes"
LISTS = {
 "Source": ["Formulaire Meta", "WhatsApp", "Messenger", "Instagram", "TikTok", "Appel direct", "Visite au bureau", "Site web", "Recommandation"],
 "Campagne": ["Campagne 1 - Abidjan", "Campagne 2 - Diaspora", "Reciblage", "Organique (sans pub)"],
 "Residence": ["Abidjan", "Ailleurs en Côte d'Ivoire", "À l'étranger"],
 "TypeBien": ["Terrain", "Villa", "Ne sait pas encore"],
 "Programme": ["Rives de l'Opulence (Adiaké)", "Deuxième programme", "Autre / à préciser"],
 "Budget": ["Moins de 15 M", "15 à 30 M", "30 à 50 M", "Plus de 50 M"],
 "Delai": ["Dans le mois", "Dans 3 mois", "Dans 6 mois ou plus", "Je me renseigne"],
 "Paiement": ["Comptant", "Progressif", "À définir"],
 "Statut": ["Nouveau", "Contacté", "Injoignable", "Visite programmée", "Visite effectuée", "Négociation", "Vendu", "Perdu"],
 "Motif": ["Budget insuffisant", "Zone ne convient pas", "Achat ailleurs", "Projet reporté", "Ne répond plus", "Autre"],
}
for c, (name, vals) in enumerate(LISTS.items(), start=1):
    ls.cell(1, c, name).font = Font(name=F, bold=True, color="FFFFFF")
    ls.cell(1, c).fill = HEAD
    for r, v in enumerate(vals, start=2):
        ls.cell(r, c, v).font = Font(name=F)
    ls.column_dimensions[L(c)].width = 28
LREF = {name: f"Listes!${L(c)}$2:${L(c)}${len(vals)+1}" for c, (name, vals) in enumerate(LISTS.items(), start=1)}

# ------------------------------------------------------------ Prospects
ws = wb.create_sheet("Prospects", 0)
COLS = [  # (titre, largeur, liste ou None, auto?)
 ("N°", 6, None, True),
 ("Date et heure de réception", 18, None, False),
 ("Source", 17, "Source", False),
 ("Campagne", 21, "Campagne", False),
 ("Nom et prénom", 22, None, False),
 ("WhatsApp / téléphone", 18, None, False),
 ("Lieu de résidence", 18, "Residence", False),
 ("Type de bien", 15, "TypeBien", False),
 ("Programme d'intérêt", 24, "Programme", False),
 ("Budget (FCFA)", 15, "Budget", False),
 ("Délai du projet", 18, "Delai", False),
 ("Mode de paiement", 14, "Paiement", False),
 ("Score", 9, None, True),
 ("Conseiller GEI", 16, None, False),
 ("Date et heure du 1er appel", 18, None, False),
 ("Délai de rappel (h)", 11, None, True),
 ("Rappel < 2 h ?", 10, None, True),
 ("Statut", 17, "Statut", False),
 ("Date de visite", 13, None, False),
 ("Relance J+3", 12, None, True),
 ("Relance J+7", 12, None, True),
 ("Relance J+15", 12, None, True),
 ("Prochaine action", 26, None, False),
 ("Montant de la vente (FCFA)", 17, None, False),
 ("Motif de perte", 18, "Motif", False),
 ("Commentaires", 34, None, False),
]
C = {t: i for i, (t, *_r) in enumerate(COLS, start=1)}
col = lambda t: L(C[t])

ws["A1"] = "SUIVI DES PROSPECTS — GLOBAL EMPIRE IMMOBILIER"
ws["A1"].font = Font(name=F, bold=True, size=15, color=NAVY)
ws["A2"] = "Colonnes blanches : à remplir par l'équipe (listes déroulantes). Colonnes grises : calculées automatiquement, ne pas modifier. La ligne 5 est un exemple à remplacer."
ws["A2"].font = Font(name=F, italic=True, size=9, color="55607A")
ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=12); ws["A3"] = "PROSPECT ET QUALIFICATION"
ws.merge_cells(start_row=3, start_column=13, end_row=3, end_column=22); ws.cell(3, 13, "SUIVI COMMERCIAL")
ws.merge_cells(start_row=3, start_column=23, end_row=3, end_column=26); ws.cell(3, 23, "ISSUE")
for c in (1, 13, 23):
    cell = ws.cell(3, c); cell.font = Font(name=F, bold=True, color="FFFFFF", size=9); cell.fill = HEAD2
    cell.alignment = Alignment(horizontal="center")
for t, (title, w, lst, auto) in zip(C, COLS):
    c = C[t]
    h = ws.cell(4, c, title)
    h.font = Font(name=F, bold=True, color="FFFFFF", size=9)
    h.fill = HEAD if not auto else PatternFill("solid", fgColor=BLUE)
    h.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    h.border = B
    ws.column_dimensions[L(c)].width = w
ws.row_dimensions[4].height = 34
ws.freeze_panes = "F5"

for r in range(FIRST, LAST + 1):
    rec, call, sc = f"{col('Date et heure de réception')}{r}", f"{col('Date et heure du 1er appel')}{r}", f"{col('Score')}{r}"
    nom = f"{col('Nom et prénom')}{r}"
    ws.cell(r, C["N°"], f'=IF({nom}="","",ROW()-{FIRST-1})')
    dl, bu = f"{col('Délai du projet')}{r}", f"{col('Budget (FCFA)')}{r}"
    ws.cell(r, C["Score"], f'=IF({dl}="","",IF({dl}="Je me renseigne","Froid",IF(AND(OR({dl}="Dans le mois",{dl}="Dans 3 mois"),{bu}<>"Moins de 15 M"),"Chaud","Tiède")))')
    ws.cell(r, C["Délai de rappel (h)"], f'=IF(OR({rec}="",{call}=""),"",({call}-{rec})*24)')
    dr = f"{col('Délai de rappel (h)')}{r}"
    ws.cell(r, C["Rappel < 2 h ?"], f'=IF({dr}="","",IF({dr}<=2,"Oui","Non"))')
    for k, d in (("Relance J+3", 3), ("Relance J+7", 7), ("Relance J+15", 15)):
        ws.cell(r, C[k], f'=IF({rec}="","",INT({rec})+{d})')
    for t, (title, w, lst, auto) in zip(C, COLS):
        cell = ws.cell(r, C[t]); cell.border = B; cell.font = Font(name=F, size=9)
        if auto:
            cell.fill = AUTO; cell.alignment = Alignment(horizontal="center")
    ws.cell(r, C["Date et heure de réception"]).number_format = "dd/mm/yyyy hh:mm"
    ws.cell(r, C["Date et heure du 1er appel"]).number_format = "dd/mm/yyyy hh:mm"
    ws.cell(r, C["Délai de rappel (h)"]).number_format = "0.0"
    for k in ("Date de visite", "Relance J+3", "Relance J+7", "Relance J+15"):
        ws.cell(r, C[k]).number_format = "dd/mm/yyyy"
    ws.cell(r, C["Montant de la vente (FCFA)"]).number_format = '#,##0'

# Ligne exemple
ex = {
 "Date et heure de réception": datetime.datetime(2026, 12, 9, 10, 15),
 "Source": "Formulaire Meta", "Campagne": "Campagne 1 - Abidjan", "Nom et prénom": "EXEMPLE — Awa K.",
 "WhatsApp / téléphone": "+225 07 00 00 00 00", "Lieu de résidence": "Abidjan", "Type de bien": "Villa",
 "Programme d'intérêt": "Rives de l'Opulence (Adiaké)", "Budget (FCFA)": "30 à 50 M", "Délai du projet": "Dans 3 mois",
 "Mode de paiement": "Progressif", "Conseiller GEI": "Nom du conseiller",
 "Date et heure du 1er appel": datetime.datetime(2026, 12, 9, 11, 20), "Statut": "Visite programmée",
 "Date de visite": datetime.date(2026, 12, 12), "Prochaine action": "Confirmer la visite la veille (vendredi)",
 "Commentaires": "Ligne d'exemple : à supprimer ou remplacer.",
}
for k, v in ex.items():
    c = ws.cell(FIRST, C[k], v); c.font = Font(name=F, size=9, italic=True, color="55607A")

# Listes déroulantes
for t, (title, w, lst, auto) in zip(C, COLS):
    if lst:
        dv = DataValidation(type="list", formula1=f"={LREF[lst]}", allow_blank=True)
        dv.error = "Choisissez une valeur dans la liste."; dv.showErrorMessage = True
        ws.add_data_validation(dv); dv.add(f"{col(t)}{FIRST}:{col(t)}{LAST}")

# Mises en forme conditionnelles
rng = lambda t: f"{col(t)}{FIRST}:{col(t)}{LAST}"
ws.conditional_formatting.add(rng("Score"), CellIsRule(operator="equal", formula=['"Chaud"'], fill=PatternFill("solid", fgColor="F8D2D2"), font=Font(name=F, bold=True, color="B71C1C")))
ws.conditional_formatting.add(rng("Score"), CellIsRule(operator="equal", formula=['"Tiède"'], fill=PatternFill("solid", fgColor="FDE9C8"), font=Font(name=F, bold=True, color="A15C00")))
ws.conditional_formatting.add(rng("Score"), CellIsRule(operator="equal", formula=['"Froid"'], fill=PatternFill("solid", fgColor="D8E2FA"), font=Font(name=F, bold=True, color=BLUE)))
ws.conditional_formatting.add(rng("Rappel < 2 h ?"), CellIsRule(operator="equal", formula=['"Non"'], font=Font(name=F, bold=True, color="B71C1C")))
ws.conditional_formatting.add(rng("Statut"), CellIsRule(operator="equal", formula=['"Vendu"'], fill=PatternFill("solid", fgColor="DCEBC5"), font=Font(name=F, bold=True, color="3E5A10")))
ws.conditional_formatting.add(rng("Statut"), CellIsRule(operator="equal", formula=['"Perdu"'], font=Font(name=F, color="9AA3B5")))
# relance du jour en jaune (si le prospect n'est ni vendu ni perdu ni visité)
st = f"${col('Statut')}{FIRST}"
for k in ("Relance J+3", "Relance J+7", "Relance J+15"):
    c0 = f"{col(k)}{FIRST}"
    ws.conditional_formatting.add(rng(k), FormulaRule(
        formula=[f'AND({c0}<>"",{c0}=TODAY(),OR({st}="Nouveau",{st}="Contacté",{st}="Injoignable"))'],
        fill=PatternFill("solid", fgColor=LIME), font=Font(name=F, bold=True, color=NAVY)))
ws.cell(4, C["Score"]).comment = Comment("Chaud : projet dans le mois ou dans 3 mois et budget de 15 M ou plus.\nTiède : projet sous 3 mois avec budget de moins de 15 M, ou projet dans 6 mois ou plus.\nFroid : « Je me renseigne ».\nRègle définie par 7CREATIVE, à ajuster avec GEI.", "7CREATIVE")
ws.cell(4, C["Relance J+3"]).comment = Comment("Surlignées en jaune le jour où la relance est à faire, tant que le prospect est Nouveau, Contacté ou Injoignable.", "7CREATIVE")
ws.auto_filter.ref = f"A4:{L(len(COLS))}{LAST}"

# ------------------------------------------------------------ Tableau de bord
db = wb.create_sheet("Tableau de bord", 1)
db.column_dimensions["A"].width = 38
for c in "BCDE":
    db.column_dimensions[c].width = 16
db["A1"] = "TABLEAU DE BORD — MACHINE À PROSPECTS GEI"; db["A1"].font = Font(name=F, bold=True, size=15, color=NAVY)
db["A3"] = "Mois analysé (saisir le 1er jour du mois)"; db["A3"].font = Font(name=F, bold=True)
db["B3"] = datetime.date(2026, 12, 1); db["B3"].number_format = "mmmm yyyy"
db["B3"].fill = PatternFill("solid", fgColor="FFFF00"); db["B3"].font = Font(name=F, bold=True, color="0000FF")
db["B3"].comment = Comment("Cellule à modifier : saisissez le 1er jour du mois à analyser (ex. 01/01/2027).", "7CREATIVE")
db["A4"] = "Fin du mois"; db["B4"] = "=EOMONTH(B3,0)+0.99999"; db["B4"].number_format = "dd/mm/yyyy"
for c in ("A4", "B4"):
    db[c].font = Font(name=F, size=9, color="55607A")

P = "Prospects!"
R = lambda t: f"{P}${col(t)}${FIRST}:${col(t)}${LAST}"
inmonth = f'{R("Date et heure de réception")},">="&$B$3,{R("Date et heure de réception")},"<="&$B$4'

def header(row, title):
    db.cell(row, 1, title).font = Font(name=F, bold=True, color="FFFFFF")
    for c in range(1, 4):
        db.cell(row, c).fill = HEAD
    db.cell(row, 2, "Nombre").font = Font(name=F, bold=True, color="FFFFFF")
    db.cell(row, 3, "Part").font = Font(name=F, bold=True, color="FFFFFF")

row = 6
db.cell(row, 1, "INDICATEURS CLÉS DU MOIS").font = Font(name=F, bold=True, color="FFFFFF")
for c in range(1, 4):
    db.cell(row, c).fill = HEAD2
kpis = [
 ("Prospects reçus", f"=COUNTIFS({inmonth})", "0"),
 ("Prospects chauds", f'=COUNTIFS({inmonth},{R("Score")},"Chaud")', "0"),
 ("Rappelés en moins de 2 h", f'=COUNTIFS({inmonth},{R("Rappel < 2 h ?")},"Oui")', "0"),
 ("Taux de rappel en moins de 2 h", "=IF(B7=0,0,B9/B7)", "0.0%"),
 ("Visites effectuées (y compris ventes et négociations)", f'=COUNTIFS({inmonth},{R("Statut")},"Visite effectuée")+COUNTIFS({inmonth},{R("Statut")},"Négociation")+COUNTIFS({inmonth},{R("Statut")},"Vendu")', "0"),
 ("Ventes", f'=COUNTIFS({inmonth},{R("Statut")},"Vendu")', "0"),
 ("Taux de transformation prospect → vente", "=IF(B7=0,0,B12/B7)", "0.0%"),
 ("Chiffre d'affaires des ventes (FCFA)", f'=SUMIFS({R("Montant de la vente (FCFA)")},{inmonth},{R("Statut")},"Vendu")', '#,##0'),
 ("Budget publicitaire du mois (FCFA)", 300000, '#,##0'),
 ("Coût par prospect (FCFA)", "=IF(B7=0,0,B15/B7)", '#,##0'),
]
for i, (lab, f, fmt) in enumerate(kpis, start=7):
    db.cell(i, 1, lab).font = Font(name=F)
    c = db.cell(i, 2, f); c.number_format = fmt; c.font = Font(name=F, bold=True)
    for cc in range(1, 4):
        db.cell(i, cc).border = B
db["B15"].font = Font(name=F, bold=True, color="0000FF"); db["B15"].fill = PatternFill("solid", fgColor="FFFF00")
db["B15"].comment = Comment("Hypothèse : budget recommandé de 300 000 FCFA/mois (plan de communication 7CREATIVE). À remplacer par le montant réellement dépensé (Gestionnaire de publicités Meta).", "7CREATIVE")
db["C15"] = "← à mettre à jour"; db["C15"].font = Font(name=F, size=9, italic=True, color="55607A")

def breakdown(start, title, field, values):
    header(start, title)
    for j, v in enumerate(values, start=start + 1):
        db.cell(j, 1, v).font = Font(name=F)
        c = db.cell(j, 2, f'=COUNTIFS({inmonth},{R(field)},A{j})'); c.font = Font(name=F)
        p = db.cell(j, 3, f"=IF($B$7=0,0,B{j}/$B$7)"); p.number_format = "0.0%"; p.font = Font(name=F)
        for cc in range(1, 4):
            db.cell(j, cc).border = B
    return start + len(values) + 2

r0 = 19
r0 = breakdown(r0, "PROSPECTS PAR STATUT", "Statut", LISTS["Statut"])
r0 = breakdown(r0, "PROSPECTS PAR SCORE", "Score", ["Chaud", "Tiède", "Froid"])
r0 = breakdown(r0, "PROSPECTS PAR CAMPAGNE", "Campagne", LISTS["Campagne"])
r0 = breakdown(r0, "PROSPECTS PAR SOURCE", "Source", LISTS["Source"])
r0 = breakdown(r0, "PROSPECTS PAR LIEU DE RÉSIDENCE", "Lieu de résidence", LISTS["Residence"])
r0 = breakdown(r0, "MOTIFS DE PERTE", "Motif de perte", LISTS["Motif"])

# ------------------------------------------------------------ Mode d'emploi
me = wb.create_sheet("Mode d'emploi", 0)
me.column_dimensions["A"].width = 4; me.column_dimensions["B"].width = 120
lines = [
 ("MODE D'EMPLOI — SUIVI DES PROSPECTS GEI", "t"),
 ("Fichier préparé par 7CREATIVE pour l'équipe commerciale de Global Empire Immobilier.", "i"),
 ("", ""),
 ("1. Onglet « Prospects »", "h"),
 ("Une ligne = un prospect. 7CREATIVE saisit chaque nouveau contact (formulaire Meta, WhatsApp, Messenger) dès sa réception.", ""),
 ("Colonnes blanches (en-tête bleu foncé) : à remplir, avec les listes déroulantes quand elles existent.", ""),
 ("Colonnes grises (en-tête bleu vif) : calculées automatiquement (n°, score, délai de rappel, dates de relance). Ne pas les modifier.", ""),
 ("Le conseiller GEI renseigne : son nom, la date et l'heure du 1er appel, le statut, la date de visite, la prochaine action et, à la fin, le montant ou le motif de perte.", ""),
 ("La ligne 5 est un exemple : remplacez-la par le premier vrai prospect.", ""),
 ("", ""),
 ("2. Le score (automatique)", "h"),
 ("Chaud : projet dans le mois ou dans 3 mois, budget de 15 M ou plus → appel sous 2 h et proposition de visite.", ""),
 ("Tiède : projet sous 3 mois avec un budget de moins de 15 M, ou projet dans 6 mois ou plus → appel sous 24 h et envoi du catalogue.", ""),
 ("Froid : « Je me renseigne » → message WhatsApp et reciblage publicitaire.", ""),
 ("", ""),
 ("3. Les relances", "h"),
 ("Les dates J+3, J+7 et J+15 se calculent depuis la date de réception. Le jour J, la case passe en jaune si le prospect est encore Nouveau, Contacté ou Injoignable.", ""),
 ("Chaque matin, filtrez les colonnes de relance sur la date du jour et envoyez les messages types du guide (réponses rapides WhatsApp).", ""),
 ("", ""),
 ("4. Les statuts", "h"),
 ("Nouveau → Contacté (ou Injoignable) → Visite programmée → Visite effectuée → Négociation → Vendu ou Perdu.", ""),
 ("", ""),
 ("5. Onglet « Tableau de bord »", "h"),
 ("Saisissez le 1er jour du mois dans la case jaune : tous les indicateurs du mois se mettent à jour (prospects, rappels < 2 h, visites, ventes, coût par prospect).", ""),
 ("Mettez à jour le budget publicitaire réellement dépensé (case jaune) pour un coût par prospect exact.", ""),
 ("", ""),
 ("6. Confidentialité", "h"),
 ("Ce fichier contient des données personnelles : partagez-le uniquement avec l'équipe commerciale GEI et 7CREATIVE, n'utilisez les contacts que pour répondre à la demande du prospect et supprimez ceux qui le demandent.", ""),
]
for i, (t, kind) in enumerate(lines, start=1):
    c = me.cell(i, 2, t)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    c.font = {"t": Font(name=F, bold=True, size=15, color=NAVY), "h": Font(name=F, bold=True, size=11, color=GREEN),
              "i": Font(name=F, italic=True, size=9, color="55607A")}.get(kind, Font(name=F, size=10))

wb.active = 0
out = os.path.join(D, "Suivi-Prospects-GEI.xlsx")
wb.save(out)
print(out)
