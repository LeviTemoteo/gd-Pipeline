from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

def testar_conexao_sheets():
    # 1. Caminho para o seu arquivo credentials.json baixado do Google Cloud
    credentials_path = Path("credentials.json")
    
    # 2. Definir os escopos de acesso necessários
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # 3. Autenticar com o Google
    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    client = gspread.authorize(credentials)

    # 4. Abrir a planilha pelo nome exato que você deu no Google Sheets
    # Substitua "Extreme_Sheets" pelo nome real da sua planilha
    spreadsheet = client.open("Extreme_Sheets")

    # 5. Selecionar a aba "GD Raw Data" (ou criar caso não exista)
    try:
        worksheet = spreadsheet.worksheet("GD Raw Data")
    except gspread.WorksheetNotFound:
        # Se a aba ainda não existir, ele cria automaticamente com 100 linhas e 10 colunas
        worksheet = spreadsheet.add_worksheet(title="GD Raw Data", rows=100, cols=10)

    # 6. Limpar dados antigos (simulando o wipe & replace da sua documentação)
    worksheet.clear()
    

    # 7. Simular dados vindos do SQLite (Cabeçalho + Registros de Exemplo)
    dados_para_enviar = [
            ["level_id", "level_name", "level_type", "difficulty", "attempts", "playtime"],
            ["2241592", "Necropolis", "Online / Daily", "Insane Demon", "1420", "379"],
            ["6839035", "Necropolis copyable", "Editor", "Hard", "50", "120"]
        ]

    # 8. Inserir os dados na planilha de uma vez só
    worksheet.update(dados_para_enviar)
    print("Sucesso! Dados enviados para a aba 'GD Raw Data'.")

if __name__ == "__main__":
    testar_conexao_sheets()