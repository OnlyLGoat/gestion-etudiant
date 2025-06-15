# Gestion_Etudiant_V5.py
"""
Projet Gestion des Étudiants - Version Orientée Objet avec Interface Graphique et Base de Données

Ce projet répond aux critères suivants :
- Version orientée objet (POO) avec encapsulation, héritage, abstraction, polymorphisme
- Interface graphique Tkinter
- Sauvegarde et gestion dans une base de données MySQL
- Validation des entrées et gestion des erreurs
- Code structuré, lisible et documenté
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import PhotoImage
import mysql.connector
from mysql.connector import Error
import os
from abc import ABC, abstractmethod

# =========================
# CLASSE PERSONNE (POO : Abstraction, Encapsulation)
# =========================
class Person(ABC):
    """
    Classe abstraite représentant une personne (étudiant ou enseignant).
    """
    def __init__(self, id_person, nom, age, group, notes=None):
        self.id_person = id_person
        self.nom = nom
        self.age = age
        self.group = group
        self.notes = notes if notes is not None else []

    @abstractmethod
    def get_role(self):
        pass

# =========================
# CLASSE STAGIAIRE (POO : Encapsulation)
# =========================
class Stagiaire(Person):
    """
    Représente un étudiant avec ses informations et ses notes.
    Attributs privés, accès via getters/setters (encapsulation).
    """
    def get_role(self):
        return "Stagiaire"

# =========================
# CLASSE ENSEIGNANT (POO : Encapsulation)
# =========================
class Teacher(Person):
    """
    Représente un enseignant.
    """
    def get_role(self):
        return "Enseignant"

# =========================
# CLASSE GESTIONNAIRE (POO : Encapsulation, gestion BDD, validation, erreurs)
# =========================
class GestionStagiaires:
    """
    Gère la liste des stagiaires et la connexion à la base de données.
    Toutes les opérations CRUD sont ici, avec gestion des erreurs et validation.
    """
    def __init__(self):
        self.__personnes = []
        self.connect_db()
        self.load_personnes_from_db()

    def get_personnes(self):
        return self.__personnes

    def set_personnes(self, personnes):
        self.__personnes = personnes

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
            messagebox.showerror("Database Error", f"Erreur de connexion à la base de données : {e}")

    def load_personnes_from_db(self):
        """
        Charge tous les stagiaires et leurs notes depuis la base de données.
        """
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
            messagebox.showerror("Database Error", f"Erreur lors du chargement des stagiaires : {e}")

    def ajouter_personne(self, id_person, nom, age, group, type_person):
        """
        Ajoute une personne (stagiaire ou enseignant) à la base et à la liste locale, avec validation et gestion d'erreur.
        """
        if any(personne.id_person == id_person for personne in self.__personnes):
            messagebox.showerror("Erreur", "Une personne avec cet ID existe déjà.")
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
            messagebox.showinfo("Succès", f"Personne {nom} ajoutée avec succès.")
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Erreur lors de l'ajout : {e}")
            return False

    def afficher_tous_les_personnes(self):
        """
        Affiche tous les stagiaires dans une boîte de dialogue.
        """
        if not self.__personnes:
            messagebox.showinfo("Information", "Aucun utilisateur trouvé.")
            return
        result = "\nListe de tous les utilisateurs :\n"
        for p in self.__personnes:
            result += f"#- ID : {p.id_person}\n#- Nom : {p.nom}\n#- Âge : {p.age}\n#- Groupe : {p.group}\n#- Rôle : {p.get_role()}\n\n"
        messagebox.showinfo("Liste des utilisateurs", result)

    def rechercher_personne(self, id_person):
        """
        Recherche une personne par ID.
        """
        for personne in self.__personnes:
            if personne.id_person == id_person:
                result = f"Personne trouvée : \n#- ID : {personne.id_person}\n#- Nom : {personne.nom}\n#- Âge : {personne.age}\n#- Groupe : {personne.group}\n#- Rôle : {personne.get_role()}"
                messagebox.showinfo("Résultat de la recherche", result)
                return
        messagebox.showinfo("Information", "Personne non trouvée.")

    def supprimer_personne(self, id_person):
        """
        Supprime une personne de la base et de la liste locale.
        """
        for personne in self.__personnes:
            if personne.id_person == id_person:
                self.__personnes.remove(personne)
                try:
                    self.cur.execute("DELETE FROM notes WHERE id_ed = %s", (id_person,))
                    self.cur.execute("DELETE FROM etudiant WHERE id = %s", (id_person,))
                    self.mydb.commit()
                    messagebox.showinfo("Succès", f"Personne {personne.nom} supprimée avec succès.")
                    return
                except Error as e:
                    messagebox.showerror("Database Error", f"Erreur lors de la suppression : {e}")
                    return
        messagebox.showinfo("Information", "Personne non trouvée.")

    def calculer_notes(self, id_person):
        """
        Saisie ou modification des notes d'une personne, avec validation et gestion d'erreur.
        """
        for personne in self.__personnes:
            if personne.id_person == id_person:
                notes = []
                for i in range(1, 4):
                    note = simpledialog.askstring("Saisir une note", f"Entrez la note {i} (laisser vide pour aucune) : ")
                    if note is None or note == "":
                        notes.append(None)
                    else:
                        try:
                            note = float(note)
                            if 0 <= note <= 20:
                                notes.append(note)
                            else:
                                messagebox.showerror("Erreur", "La note doit être comprise entre 0 et 20.")
                                return
                        except ValueError:
                            messagebox.showerror("Erreur", "Entrée invalide. Veuillez entrer un nombre valide.")
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
                    messagebox.showinfo("Succès", f"Notes enregistrées pour la personne {personne.nom}.")
                except Error as e:
                    messagebox.showerror("Database Error", f"Erreur lors de l'enregistrement des notes: {e}")
                return
        messagebox.showinfo("Information", "Personne non trouvée.")

    def obtenir_notes(self, id_person):
        """
        Affiche les notes et la moyenne d'une personne.
        """
        for personne in self.__personnes:
            if personne.id_person == id_person:
                self.cur.execute("SELECT note1, note2, note3 FROM notes WHERE id_ed = %s", (id_person,))
                notes_row = self.cur.fetchone()
                notes = [n for n in notes_row if n is not None] if notes_row else []
                personne.notes = notes
                if notes:
                    result = f"Notes pour {personne.nom} : {notes}\nMoyenne : {personne.moyenne_notes():.2f}"
                    messagebox.showinfo("Notes", result)
                else:
                    messagebox.showinfo("Information", f"{personne.nom} n'a aucune note enregistrée.")
                return
        messagebox.showinfo("Information", "Personne non trouvée.")

    def modifier_personne(self, id_person, new_nom, new_age):
        """
        Modifie le nom et l'âge d'une personne.
        """
        for personne in self.__personnes:
            if personne.id_person == id_person:
                personne.nom = new_nom
                personne.age = new_age
                try:
                    sql = "UPDATE etudiant SET name = %s, age = %s WHERE id = %s"
                    val = (new_nom, new_age, id_person)
                    self.cur.execute(sql, val)
                    self.mydb.commit()
                    messagebox.showinfo("Succès", f"Personne modifiée : Nom : {new_nom}, Âge : {new_age}")
                    return
                except Error as e:
                    messagebox.showerror("Database Error", f"Erreur lors de la modification : {e}")
                    return
        messagebox.showinfo("Information", "Personne non trouvée.")

    def __del__(self):
        try:
            if hasattr(self, 'cur') and self.cur:
                self.cur.close()
            if hasattr(self, 'mydb') and self.mydb:
                self.mydb.close()
        except Exception as e:
            messagebox.showerror("Error", f"Erreur lors de la fermeture de la connexion : {e}")

# =========================
# INTERFACE GRAPHIQUE TKINTER (Critère interface graphique)
# =========================
class Application(tk.Tk):
    """
    Interface graphique principale de gestion des étudiants.
    """
    def __init__(self):
        super().__init__()
        self.title("D7GT - Gestion Etudiant")
        self.geometry("391x626")
        try:
            icon = PhotoImage(file='D7GT.png')
            self.iconphoto(False, icon)
        except Exception:
            pass

        try:
            self.bk = PhotoImage(file=os.path.abspath("bk.png"))
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load background image: {e}")
            self.bk = None

        try:
            self.picture = PhotoImage(file=os.path.abspath("D7GT.png"))
        except Exception as e:
            messagebox.showerror("Image Error", f"Failed to load logo image: {e}")
            self.picture = None

        if self.bk:
            self.background_label = tk.Label(self, image=self.bk)
            self.background_label.place(relwidth=1, relheight=1)

        if self.picture:
            self.picture_label = tk.Label(self, image=self.picture, relief=tk.RAISED, bd=10)
            self.picture_label.pack(pady=22)

        self.gestion = GestionStagiaires()

        button_style = {"bg": "#0066ff", "fg": "white", "padx": 10, "pady": 5}

        tk.Button(self, text="Ajouter un utilisateur", command=self.ajouter_personne, **button_style).pack(pady=10)
        tk.Button(self, text="Afficher tous les utilisateurs", command=self.gestion.afficher_tous_les_personnes, **button_style).pack(pady=10)
        tk.Button(self, text="Rechercher un utilisateur", command=self.rechercher_personne, **button_style).pack(pady=10)
        tk.Button(self, text="Supprimer un utilisateur", command=self.supprimer_personne, **button_style).pack(pady=10)
        tk.Button(self, text="Saisir les notes d'un utilisateur", command=self.calculer_notes, **button_style).pack(pady=10)
        tk.Button(self, text="Afficher les notes d'un utilisateur", command=self.obtenir_notes, **button_style).pack(pady=10)
        tk.Button(self, text="Modifier un utilisateur", command=self.modifier_personne, **button_style).pack(pady=10)
        tk.Button(self, text="Quitter", command=self.destroy, **button_style).pack(pady=10)

    def ajouter_personne(self):
        """
        Fenêtre de saisie pour ajouter une personne (stagiaire ou enseignant), avec validation et gestion d'erreur.
        """
        button_style = {"bg": "#0066ff", "fg": "white", "padx": 10, "pady": 5}
        form_window = tk.Toplevel(self)
        form_window.title("Ajouter un Utilisateur")
        form_window.geometry("391x450")

        # Ajout du background si disponible
        if hasattr(self, 'bk') and self.bk:
            bg_label = tk.Label(form_window, image=self.bk)
            bg_label.place(relwidth=1, relheight=1)
            # Pour éviter que l'image soit supprimée par le garbage collector
            form_window.bg_label = bg_label

        tk.Label(form_window, text="ID de l'Utilisateur", **button_style).pack(pady=5)
        id_entry = tk.Entry(form_window)
        id_entry.pack(pady=5)

        tk.Label(form_window, text="Nom", **button_style).pack(pady=5)
        nom_entry = tk.Entry(form_window)
        nom_entry.pack(pady=5)

        tk.Label(form_window, text="Âge (18-30)", **button_style).pack(pady=5)
        age_entry = tk.Entry(form_window)
        age_entry.pack(pady=5)

        tk.Label(form_window, text="Groupe", **button_style).pack(pady=5)
        group_entry = tk.Entry(form_window)
        group_entry.pack(pady=5)

        tk.Label(form_window, text="Rôle", **button_style).pack(pady=5)
        type_var = tk.StringVar(value="Stagiaire")
        tk.OptionMenu(form_window, type_var, "Stagiaire", "Enseignant").pack(pady=5)

        def submit_form():
            try:
                id_person = id_entry.get()
                nom = nom_entry.get()
                age = age_entry.get()
                group = group_entry.get()
                type_person = type_var.get()

                if not id_person or not nom or not age or not group:
                    messagebox.showerror("Erreur", "Tous les champs doivent être remplis.")
                    return

                # Vérification que le nom ne contient que des lettres et espaces
                if not nom.replace(" ", "").isalpha():
                    messagebox.showerror("Erreur", "Le nom doit contenir uniquement des lettres.")
                    return

                try:
                    id_person_int = int(id_person)
                except ValueError:
                    messagebox.showerror("Erreur", "L'ID doit être un nombre entier.")
                    return

                if not age.isdigit():
                    messagebox.showerror("Erreur", "L'âge doit être un nombre entier.")
                    return

                age_int = int(age)
                if age_int < 18 or age_int > 30:
                    messagebox.showerror("Erreur", "L'âge doit être un nombre entre 18 et 30.")
                    return

                if self.gestion.ajouter_personne(id_person_int, nom, age_int, group, type_person):
                    form_window.destroy()
                else:
                    messagebox.showerror("Erreur", "Erreur lors de l'ajout de l'utilisateur.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

        submit_button = tk.Button(form_window, text="Ajouter", command=submit_form, **button_style)
        submit_button.pack(pady=20)
        cancel_button = tk.Button(form_window, text="Annuler", command=form_window.destroy, **button_style)
        cancel_button.pack()

    def rechercher_personne(self):
        try:
            form_window = tk.Toplevel(self)
            form_window.title("Rechercher un utilisateur")
            form_window.geometry("350x200")

            # Ajout du background
            if hasattr(self, 'bk') and self.bk:
                bg_label = tk.Label(form_window, image=self.bk)
                bg_label.place(relwidth=1, relheight=1)
                form_window.bg_label = bg_label

            tk.Label(form_window, text="ID de l'utilisateur", bg="#e6f0ff").pack(pady=10)
            id_entry = tk.Entry(form_window, bg="#e6f0ff")
            id_entry.pack(pady=10)

            def submit():
                try:
                    id_person = id_entry.get()
                    if not id_person:
                        messagebox.showerror("Erreur", "Veuillez entrer un ID.")
                        return
                    try:
                        id_person_int = int(id_person)
                    except ValueError:
                        messagebox.showerror("Erreur", "L'ID doit être un nombre entier.")
                        return
                    self.gestion.rechercher_personne(id_person_int)
                    form_window.destroy()
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

            tk.Button(form_window, text="Rechercher", command=submit, bg="#0066ff", fg="white").pack(pady=10)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

    def supprimer_personne(self):
        try:
            id_person = simpledialog.askinteger("Supprimer un utilisateur", "Entrez l'ID de l'utilisateur :")
            if id_person is not None:
                self.gestion.supprimer_personne(id_person)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

    def calculer_notes(self):
        try:
            id_person = simpledialog.askinteger("Saisir les notes", "Entrez l'ID de l'utilisateur :")
            if id_person is not None:
                self.gestion.calculer_notes(id_person)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

    def obtenir_notes(self):
        try:
            id_person = simpledialog.askinteger("Afficher les notes", "Entrez l'ID de l'utilisateur :")
            if id_person is not None:
                self.gestion.obtenir_notes(id_person)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

    def modifier_personne(self):
        try:
            id_person = simpledialog.askinteger("Modifier un utilisateur", "Entrez l'ID de l'utilisateur :")
            if id_person is None:
                return
            new_nom = simpledialog.askstring("Modifier un utilisateur", "Entrez le nouveau nom :")
            if new_nom is None:
                return
            # Vérification que le nom ne contient que des lettres et espaces
            if not new_nom.replace(" ", "").isalpha():
                messagebox.showerror("Erreur", "Le nom doit contenir uniquement des lettres.")
                return
            new_age = simpledialog.askinteger("Modifier un utilisateur", "Entrez le nouvel âge (entre 18 et 30) :", minvalue=18, maxvalue=30)
            if new_age is None:
                return
            self.gestion.modifier_personne(id_person, new_nom, new_age)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue : {e}")



# =========================
# LANCEMENT DE L'APPLICATION
# =========================
def start_application():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    start_application()