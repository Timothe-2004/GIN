from django.db import connection

def delete_stage_offer():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM stages_stageoffer WHERE id = 1;")
    print("L'offre de stage avec l'ID 1 a été supprimée avec succès.")
if __name__ == "__main__":
    delete_stage_offer()
