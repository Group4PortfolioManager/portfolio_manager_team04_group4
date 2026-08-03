# Calculs de Performance du Portefeuille

Ce document explique comment le graphique de performance du portefeuille est calcule.

## Sources de Donnees

Le point d'acces de performance utilise :
- `portfolio.cash_balance` depuis la base de donnees
- les lignes `holdings` de la base de donnees (`ticker`, `shares`, `cost_basis`, `purchase_date`)
- les prix de cloture historiques de Yahoo Finance pour chaque ticker du portefeuille

Point d'acces API :
- `GET /portfolios/<portfolio_id>/performance?months=12`

Options de requete prises en charge :
- `GET /portfolios/<portfolio_id>/performance?window_type=months&window_size=12`
- `GET /portfolios/<portfolio_id>/performance?window_type=days&window_size=12`

Compatibilite ancienne version :
- `months=12` est toujours accepte et interprete comme `window_type=months&window_size=12`

## Fenetre de Calcul

Le point d'acces construit des points de fin de mois (12 points par defaut, incluant le mois en cours).

Comportement de la fenetre :
- `window_type=months` : 12 points de fin de mois (ou `window_size` points de fin de mois)
- `window_type=days` : 12 points journaliers incluant aujourd'hui (ou `window_size` points journaliers)

Pour chaque date de point `t`, la valeur du portefeuille est :

$$
V_t = C + \sum_{i=1}^{n} (S_i \times P_{i,t})
$$

Ou :
- $V_t$ = valeur du portefeuille a la date $t$
- $C$ = `cash_balance` actuel de la table portfolio
- $S_i$ = nombre d'actions (ou unites) de la position $i$
- $P_{i,t}$ = prix de cloture du ticker $i$ a la date $t$

## Regle de Date d'Achat

Une position contribue a la date `t` uniquement si :

$$
	ext{purchase\_date}_i \le t
$$

Si une position a ete achetee apres la date `t`, elle est exclue de ce point.

## Regle de Repli de Prix

Si les donnees Yahoo ne sont pas disponibles pour une date, le service utilise `cost_basis` comme valeur de repli :

$$
P_{i,t} = \text{cost\_basis}_i
$$

Cela evite les trous dans les donnees du graphique.

Pour les deux types de fenetre, le service utilise le dernier prix de cloture disponible a la date du point, ou avant.
Si aucun prix historique n'existe a cette date (ou avant), il revient a `cost_basis`.

## Bascule de Fenetre dans l'Interface

Le graphique de performance frontend inclut un groupe de boutons :
- `12M` envoie `window_type=months&window_size=12`
- `12D` envoie `window_type=days&window_size=12`

## Variation en Pourcentage dans l'Interface

Le badge et l'infobulle du graphique utilisent :

$$
	ext{Variation \%} = \frac{V_{last} - V_{first}}{V_{first}} \times 100
$$

Si $V_{first} = 0$, la variation est forcee a `0` pour eviter une division par zero.

## Hypotheses et Limites Importantes

Avec le schema actuel, les lignes holdings representent l'etat actuel et ne stockent pas un historique complet des transactions.

Implications :
- Le graphique est base de maniere logique sur les positions actuelles projetees en arriere avec les prix de marche.
- Les ventes partielles et les variations historiques de cash ne sont pas reconstruites mois par mois.
- Pour un NAV historique exact dans le temps, il faut ajouter une table de transactions (achats/ventes/flux de cash) et calculer des snapshots journaliers ou mensuels depuis ce journal.

## Format de Reponse

Exemple de reponse :

```json
{
  "portfolio_id": 1,
  "window_type": "months",
  "window_size": 12,
  "history": [
    { "date": "2026-02-28", "label": "Feb", "value": 10432.12 },
    { "date": "2026-03-31", "label": "Mar", "value": 10887.91 }
  ]
}
```
