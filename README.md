# Gestion des Étudiants

Ce projet propose deux applications pour la gestion des étudiants et enseignants, avec une version console et une version graphique (Tkinter), toutes deux connectées à une base de données MySQL.

## Fonctionnalités

- Ajout, modification, suppression et recherche d'utilisateurs (stagiaires ou enseignants)
- Saisie et affichage des notes (3 notes par utilisateur)
- Calcul automatique de la moyenne
- Interface graphique moderne avec Tkinter (version graphique)
- Validation des entrées et gestion des erreurs
- Persistance des données via MySQL

## Structure du projet

- [`Gestion_Etudiant_V5.py`](Gestion_Etudiant_V5.py) : Version graphique (Tkinter)
- [`Getion_etudiant_console.py`](Getion_etudiant_console.py) : Version console
- `bk.png`, `D7GT.png` : Images utilisées dans l'interface graphique

## Prérequis

- Python 3.x
- MySQL Server
- Bibliothèques Python :
  - `mysql-connector-python`
  - `tkinter` (inclus avec Python standard)

## Installation des dépendances

```sh
pip install mysql-connector-python
```

## Préparation de la base de données

Créez une base de données MySQL avec les tables suivantes :

```sql
CREATE DATABASE YOUR_DB_NAME;
USE YOUR_DB_NAME;

CREATE TABLE etudiant (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    ed_group VARCHAR(50),
    type VARCHAR(20)
);

CREATE TABLE notes (
    id_note INT AUTO_INCREMENT PRIMARY KEY,
    id_ed INT,
    note1 FLOAT,
    note2 FLOAT,
    note3 FLOAT,
    FOREIGN KEY (id_ed) REFERENCES etudiant(id) ON DELETE CASCADE
);
```

Remplacez `YOUR_DB_NAME` et `YOUR_DB_PASSWORD` dans les scripts par vos informations MySQL.

## Utilisation

### Version Console

```sh
python Getion_etudiant_console.py
```

### Version Graphique

```sh
python Gestion_Etudiant_V5.py
```

## Auteurs

- Projet réalisé par Med El Anani

## Remarques

- Les images `bk.png` et `D7GT.png` doivent être présentes dans le même dossier que les scripts pour l'affichage correct dans l'interface graphique.
- Le projet utilise la programmation orientée objet (POO) avec abstraction, encapsulation, héritage et polymorphisme.
