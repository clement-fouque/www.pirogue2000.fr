# Pirogue 2000

Site de l’association Pirogue 2000, construit avec **Hugo 0.168.0** et destiné à GitHub Pages sur `www.pirogue2000.fr`. Les textes sont dans `content/`, les photos et documents dans `static/`. Aucun CMS, service de formulaire ou outil de suivi n’est nécessaire.

## Modifier une page dans GitHub

1. Ouvrir le fichier Markdown dans `content/` et cliquer sur le crayon. L’accueil est `content/_index.md`, la page Actions est `content/actions/_index.md`, les autres pages portent leur nom.
2. Modifier le texte sous le bloc initial délimité par `---`. Conserver le champ `url` : il maintient les adresses existantes, notamment leurs accents et leurs barres finales. Le champ `title` fournit le titre de la page.
3. Enregistrer la modification avec **Commit changes**, directement sur `main` si vous en avez le droit, ou dans une branche puis une pull request.

Une modification arrivée sur `main` déclenche la construction et, si tous les contrôles réussissent, la publication. Il n’y a pas de prévisualisation éditoriale dédiée. Un échec de construction empêche le déploiement : la dernière version publiée reste en ligne.

Le calendrier est simplement `content/calendrier.md` : modifier son titre, son année et ses dates à la main. Rien ne recalcule automatiquement les événements.

## Ajouter une photo ou un document

Dans GitHub, ouvrir `static/images/`, puis **Add file → Upload files**. Utiliser un nom simple, par exemple `jardin-2027.jpg`, et enregistrer le fichier avant de modifier la page.

Insérer une image avec du Markdown ordinaire :

```markdown
![Écoliers dans le jardin de l’école](/images/jardin-2027.jpg)
```

Le texte entre crochets décrit la photo pour les lecteurs d’écran. Une légende visible peut être ajoutée entre guillemets :

```markdown
![Écoliers récoltant des légumes](/images/jardin-2027.jpg "Le jardin de l’école")
```

Chaque image est automatiquement cliquable pour l’agrandir. Échap ferme la visionneuse. Sans JavaScript, le lien ouvre directement l’original. Si l’image est déjà un lien Markdown, sa destination est conservée :

```markdown
[![Nos actions au Niger](/images/jardin-2027.jpg)](/actions/)
```

Pour regrouper des photos, placer leurs lignes consécutivement, **sans ligne vide** entre elles. À partir de quatre images, le groupe devient une galerie avec boutons, défilement tactile et flèches du clavier. Sans JavaScript, toutes les photos restent visibles. Aucun shortcode ni HTML n’est nécessaire.

Sur la page Activités, les séparateurs Markdown `---` sous l’introduction délimitent les deux rangées photos/texte. Les conserver pour garder la mise en page alternée.

Les images locales reçoivent des versions WebP adaptées à l’écran pendant la construction ; les originaux restent accessibles pour l’agrandissement. Éviter les fichiers inutilement volumineux pour les nouveaux ajouts.

Les PDF s’ajoutent de la même manière dans `static/documents/`, puis s’insèrent comme liens :

```markdown
[Compte-rendu de l’assemblée générale (PDF)](/documents/compte-rendu-ag-2026-01-31.pdf)
```

Ne pas préfixer les liens publics par `static/`.

## Construire en local

Installer la version Hugo indiquée dans [`.hugo-version`](.hugo-version), depuis les [versions officielles Hugo](https://github.com/gohugoio/hugo/releases/tag/v0.168.0). Python 3.9 ou ultérieur suffit aux contrôles ; aucun paquet Python ni outil Node n’est requis.

Depuis la racine du dépôt :

```sh
hugo version
hugo --gc --minify --cleanDestinationDir --panicOnWarning
python3 -m unittest discover -s tests
python3 scripts/check_site.py
```

La sortie est dans `public/`, exclu du suivi Git. `--cleanDestinationDir` nettoie **ce répertoire de sortie** pour ne pas conserver d’anciennes pages. Ne pas choisir un répertoire contenant vos propres fichiers comme destination de build.

Pour consulter le site localement :

```sh
hugo server
```

Les templates sont dans `layouts/`, le CSS dans `static/css/site.css` et le JavaScript dans `static/js/site.js`. Les polices sont locales et leurs licences sont dans `static/fonts/`.

Le contrôle vérifie les routes migrées, les liens et ancres internes, les images, les PDF, l’absence de dépendances Jimdo et de ressources distantes chargées à l’exécution. Le manifeste `docs/source-inventory.json` est une référence de migration, **pas une base de contenu à mettre à jour à chaque ajout**. Conserver les médias historiques référencés ; si un retrait délibéré est nécessaire, adapter le manifeste dans la même modification, en expliquant pourquoi.

## Préparer GitHub Pages

Le workflow [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) installe Hugo à la version épinglée, vérifie son archive, construit le site, exécute les contrôles, puis téléverse uniquement `public/`. Le job `deploy`, dépendant du succès du job `build`, utilise l’environnement `github-pages`. Une exécution manuelle sur une branche autre que `main` ne publie pas.

Le propriétaire du dépôt doit configurer **Settings → Pages → Build and deployment → Source: GitHub Actions**, ainsi que les éventuelles autorisations de l’environnement `github-pages`. Le workflow doit pouvoir disposer de `contents: read`, `pages: write` et `id-token: write`.

Le domaine est préparé dans `hugo.toml` et `static/CNAME`. **La présence de ce fichier ne prouve ni l’activation du domaine dans GitHub Pages ni une bascule DNS.** Le propriétaire configure lui-même le domaine personnalisé, sa vérification, les DNS et HTTPS dans GitHub Pages. Attendre la validation de la publication et du domaine avant toute résiliation Jimdo.

Les mentions légales restent à compléter et valider par l’association. Les limites connues, l’inventaire et les différences avec Jimdo sont détaillés dans [`docs/migration.md`](docs/migration.md).
