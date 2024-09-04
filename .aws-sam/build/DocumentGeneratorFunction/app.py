import json
import boto3
from io import BytesIO, StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Cliente para o S3
s3 = boto3.client('s3')

# Nome do bucket S3 onde os documentos serão armazenados
BUCKET_NAME = 'selectgearmotors-documents-bucket'

def lambda_handler(event, context):
    # Verificar se o evento tem registros
    if 'Records' in event:
        # Processar cada registro da fila SQS
        for record in event['Records']:
            message = json.loads(record['body'])
            
            # Extrair dados da mensagem SQS
            transacao_id = message.get('transacao_id')
            comprador_id = message.get('comprador_id')
            veiculo_id = message.get('veiculo_id')
            
            # Verificar se os dados obrigatórios estão presentes
            if transacao_id and comprador_id and veiculo_id:
                # Gera o documento PDF
                pdf_content = gerar_documento_pdf(transacao_id, comprador_id, veiculo_id)
                
                # Salva o PDF no S3
                salvar_no_s3(pdf_content, f"documentos/{transacao_id}.pdf", 'application/pdf')
                
                # Gera um documento de texto (opcional)
                txt_content = gerar_documento_txt(transacao_id, comprador_id, veiculo_id)
                
                # Salva o documento TXT no S3
                salvar_no_s3(txt_content.encode('utf-8'), f"documentos/{transacao_id}.txt", 'text/plain')

                print(f"Documentos gerados e salvos no S3 para a transação {transacao_id}.")
            else:
                print("Dados incompletos na mensagem SQS.")
    else:
        print("Nenhum registro encontrado no evento.")

def gerar_documento_pdf(transacao_id, comprador_id, veiculo_id):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    pdf.drawString(100, 750, f"Documento da Transação: {transacao_id}")
    pdf.drawString(100, 735, f"Comprador ID: {comprador_id}")
    pdf.drawString(100, 720, f"Veículo ID: {veiculo_id}")
    
    pdf.showPage()
    pdf.save()
    
    buffer.seek(0)
    return buffer.getvalue()

def gerar_documento_txt(transacao_id, comprador_id, veiculo_id):
    documento = StringIO()
    documento.write(f"Documento da Transação: {transacao_id}\n")
    documento.write(f"Comprador ID: {comprador_id}\n")
    documento.write(f"Veículo ID: {veiculo_id}\n")
    
    return documento.getvalue()

def salvar_no_s3(conteudo, chave_arquivo, content_type):
    s3.put_object(Bucket=BUCKET_NAME, Key=chave_arquivo, Body=conteudo, ContentType=content_type)
