# 🛠️ Guide de contribution – Backend GLOBAL IT NET

Bienvenue ! Voici les étapes à suivre pour collaborer proprement sur ce projet backend Django.

## 📦 Branche principale

- `main` : contient uniquement le code **stabilisé et testé**.
- `develop` : branche d'intégration, toutes les nouvelles fonctionnalités y sont fusionnées.

---

## 🧑‍💻 Étapes pour contribuer

### 🔁 1. Cloner le dépôt

```bash
git clone https://github.com/<utilisateur>/global-it-net-backend.git
cd global-it-net-backend

🌱 2. Bascule vers develop

git checkout develop

🌿 3. Créer une branche de fonctionnalité

Crée une branche nommée selon la fonctionnalité :

git checkout -b feature/nom-fonctionnalite

Exemples :

    feature/authentication

    feature/gestion-utilisateurs

    feature/api-contact

💻 4. Coder ta fonctionnalité

Travaille sur tes fichiers normalement.
✅ 5. Enregistrer les modifications

git add .
git commit -m "Ajout de la fonctionnalité : [nom clair]"

🚀 6. Pousser ta branche sur GitHub

git push origin feature/nom-fonctionnalite

🔀 7. Créer une Pull Request

    Va sur GitHub.

    Clique sur "Compare & pull request".

    Choisis la branche de base : develop.

    Vérifie que ta branche est celle de la fonctionnalité.

    Décris clairement ce que tu as ajouté/modifié.

    Clique sur "Create pull request".

🔎 8. Revue de code & fusion

    Un administrateur du projet (souvent @Toi) vérifiera la PR.

    Si tout est OK, elle sera fusionnée dans develop.

⚠️ Règles importantes

    Ne jamais coder directement sur main !

    Utiliser des noms de branche clairs et cohérents.

    Écrire des messages de commit explicites.

    Tester ton code avant d’envoyer une PR.

    Fusion dans main uniquement quand le code est stable.
