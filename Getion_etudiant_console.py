# Gestion_Etudiant_Console.py

import mysql.connector
from mysql.connector import Error
from abc import ABC, abstractmethod

class Person(ABC):
    def __init__(self, id_person, nom, age, group, notes=None):
        self.id_person = id_person
        self.nom = nom
        self.age = age
        self.group = group
        self.notes = notes if notes is not None else []

    @abstractmethod
    def get_role(self):
        pass

    def moyenne_notes(self):
        return sum(self.notes) / len(self.notes) if self.notes else 0

class Stagiaire(Person):
    def get_role(self):
        return "Stagiaire"

class Teacher(Person):
    def get_role(self):
        return "Enseignant"

class GestionStagiaires:
    def __init__(self):
        self.__personnes = []
        self.connect_db()
        self.load_personnes_from_db()

    def connect_db(self):
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="YOUR_DB_PASSWORD",
                database="YOUR_DB_NAME"
            )
            self.cur = self.mydb.cursor()
        except Error as e:
            print(f"Erreur de connexion à la base de données : {e}")

    def load_personnes_from_db(self):
        self.__personnes.clear()
        try:
            self.cur.execute("SELECT id, name, age, ed_group, type FROM etudiant")
            for (id_person, nom, age, group, type_person) in self.cur.fetchall():
                self.cur.execute("SELECT note1, note2, note3 FROM notes WHERE id_ed = %s", (id_person,))
                notes_row = self.cur.fetchone()
                notes = [n for n in notes_row if n is not None] if notes_row else []
                if type_person == "Enseignant":
                    self.__personnes.append(Teacher(id_person, nom, age, group, notes))
                else:
                    self.__personnes.append(Stagiaire(id_person, nom, age, group, notes))
        except Error as e:
            print(f"Erreur lors du chargement des personnes : {e}")

    def ajouter_personne(self, id_person, nom, age, group, type_person):
        if any(p.id_person == id_person for p in self.__personnes):
            print("Une personne avec cet ID existe déjà.")
            return False
        if type_person == "Enseignant":
            personne = Teacher(id_person, nom, age, group)
        else:
            personne = Stagiaire(id_person, nom, age, group)
        try:
            sql = "INSERT INTO etudiant (id, name, age, ed_group, type) VALUES (%s, %s, %s, %s, %s)"
            val = (id_person, nom, age, group, type_person)
            self.cur.execute(sql, val)
            self.mydb.commit()
            self.__personnes.append(personne)
            print(f"{type_person} {nom} ajouté avec succès.")
            return True
        except Error as e:
            print(f"Erreur lors de l'ajout : {e}")
            return False

    def afficher_tous_les_personnes(self):
        if not self.__personnes:
            print("Aucun utilisateur trouvé.")
            return
        print("\nListe de tous les utilisateurs :")
        for p in self.__personnes:
            print(f"ID : {p.id_person} | Nom : {p.nom} | Âge : {p.age} | Groupe : {p.group} | Rôle : {p.get_role()}")

    def rechercher_personne(self, id_person):
        for personne in self.__personnes:
            if personne.id_person == id_person:
                print(f"Personne trouvée : ID : {personne.id_person} | Nom : {personne.nom} | Âge : {personne.age} | Groupe : {personne.group} | Rôle : {personne.get_role()}")
                return
        print("Personne non trouvée.")

    def supprimer_personne(self, id_person):
        for personne in self.__personnes:
            if personne.id_person == id_person:
                self.__personnes.remove(personne)
                try:
                    self.cur.execute("DELETE FROM notes WHERE id_ed = %s", (id_person,))
                    self.cur.execute("DELETE FROM etudiant WHERE id = %s", (id_person,))
                    self.mydb.commit()
                    print(f"Personne {personne.nom} supprimée avec succès.")
                    return
                except Error as e:
                    print(f"Erreur lors de la suppression : {e}")
                    return
        print("Personne non trouvée.")

    def calculer_notes(self, id_person):
        for personne in self.__personnes:
            if personne.id_person == id_person:
                notes = []
                for i in range(1, 4):
                    note = input(f"Entrez la note {i} (laisser vide pour aucune) : ")
                    if note == "":
                        notes.append(None)
                    else:
                        try:
                            note = float(note)
                            if 0 <= note <= 20:
                                notes.append(note)
                            else:
                                print("La note doit être comprise entre 0 et 20.")
                                return
                        except ValueError:
                            print("Entrée invalide. Veuillez entrer un nombre valide.")
                            return
                try:
                    self.cur.execute("SELECT id_note FROM notes WHERE id_ed = %s", (id_person,))
                    exists = self.cur.fetchone()
                    if exists:
                        self.cur.execute(
                            "UPDATE notes SET note1=%s, note2=%s, note3=%s WHERE id_ed=%s",
                            (notes[0], notes[1], notes[2], id_person)
                        )
                    else:
                        self.cur.execute(
                            "INSERT INTO notes (id_ed, note1, note2, note3) VALUES (%s, %s, %s, %s)",
                            (id_person, notes[0], notes[1], notes[2])
                        )
                    self.mydb.commit()
                    personne.notes = [n for n in notes if n is not None]
                    print(f"Notes enregistrées pour la personne {personne.nom}.")
                except Error as e:
                    print(f"Erreur lors de l'enregistrement des notes: {e}")
                return
        print("Personne non trouvée.")

    def obtenir_notes(self, id_person):
        for personne in self.__personnes:
            if personne.id_person == id_person:
                self.cur.execute("SELECT note1, note2, note3 FROM notes WHERE id_ed = %s", (id_person,))
                notes_row = self.cur.fetchone()
                notes = [n for n in notes_row if n is not None] if notes_row else []
                personne.notes = notes
                if notes:
                    print(f"Notes pour {personne.nom} : {notes}\nMoyenne : {personne.moyenne_notes():.2f}")
                else:
                    print(f"{personne.nom} n'a aucune note enregistrée.")
                return
        print("Personne non trouvée.")

    def modifier_personne(self, id_person, new_nom, new_age):
        for personne in self.__personnes:
            if personne.id_person == id_person:
                personne.nom = new_nom
                personne.age = new_age
                try:
                    sql = "UPDATE etudiant SET name = %s, age = %s WHERE id = %s"
                    val = (new_nom, new_age, id_person)
                    self.cur.execute(sql, val)
                    self.mydb.commit()
                    print(f"Personne modifiée : Nom : {new_nom}, Âge : {new_age}")
                    return
                except Error as e:
                    print(f"Erreur lors de la modification : {e}")
                    return
        print("Personne non trouvée.")

    def __del__(self):
        try:
            if hasattr(self, 'cur') and self.cur:
                self.cur.close()
            if hasattr(self, 'mydb') and self.mydb:
                self.mydb.close()
        except Exception as e:
            print(f"Erreur lors de la fermeture de la connexion : {e}")

def menu():
    gestion = GestionStagiaires()
    while True:
        print("\n--- Menu Gestion des Utilisateurs ---")
        print("1. Ajouter un utilisateur")
        print("2. Afficher tous les utilisateurs")
        print("3. Rechercher un utilisateur")
        print("4. Supprimer un utilisateur")
        print("5. Saisir les notes d'un utilisateur")
        print("6. Afficher les notes d'un utilisateur")
        print("7. Modifier un utilisateur")
        print("0. Quitter")
        choix = input("Votre choix : ")
        if choix == "1":
            try:
                id_person = int(input("ID : "))
                nom = input("Nom : ")
                # Vérification du nom
                if not nom.replace(" ", "").isalpha():
                    print("Erreur : Le nom doit contenir uniquement des lettres.")
                    continue
                age = int(input("Âge (18-30) : "))
                group = input("Groupe : ")
                type_person = input("Rôle (Stagiaire/Enseignant) : ")
                if type_person not in ["Stagiaire", "Enseignant"]:
                    print("Type invalide.")
                    continue
                gestion.ajouter_personne(id_person, nom, age, group, type_person)
            except Exception as e:
                print(f"Erreur : {e}")
        elif choix == "2":
            gestion.afficher_tous_les_personnes()
        elif choix == "3":
            try:
                id_person = int(input("ID à rechercher : "))
                gestion.rechercher_personne(id_person)
            except Exception as e:
                print(f"Erreur : {e}")
        elif choix == "4":
            try:
                id_person = int(input("ID à supprimer : "))
                gestion.supprimer_personne(id_person)
            except Exception as e:
                print(f"Erreur : {e}")
        elif choix == "5":
            try:
                id_person = int(input("ID pour saisir les notes : "))
                gestion.calculer_notes(id_person)
            except Exception as e:
                print(f"Erreur : {e}")
        elif choix == "6":
            try:
                id_person = int(input("ID pour afficher les notes : "))
                gestion.obtenir_notes(id_person)
            except Exception as e:
                print(f"Erreur : {e}")
        elif choix == "7":
            try:
                id_person = int(input("ID à modifier : "))
                new_nom = input("Nouveau nom : ")
                # Vérification du nom
                if not new_nom.replace(" ", "").isalpha():
                    print("Erreur : Le nom doit contenir uniquement des lettres.")
                    continue
                new_age = int(input("Nouvel âge (18-30) : "))
                gestion.modifier_personne(id_person, new_nom, new_age)
            except Exception as e:
                print(f"Erreur : {e}")
        elif choix == "0":
            print("Au revoir !")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    menu()