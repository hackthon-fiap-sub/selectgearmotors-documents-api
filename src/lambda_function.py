import json
import os
import boto3
from io import BytesIO, StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import logging

# Configurar o logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cliente para o S3
s3 = boto3.client('s3')

# Nome do bucket S3 onde os documentos serão armazenados
BUCKET_NAME = os.getenv('BUCKET_NAME')

def lambda_handler(event, context):
    logger.info("Iniciando o processamento da função Lambda")
    
    # Verificar se o evento tem registros
    if 'Records' in event:
        logger.info(f"Total de registros recebidos do SQS: {len(event['Records'])}")
        
        # Processar cada registro da fila SQS
        for record in event['Records']:
            logger.info("Processando um novo registro da fila SQS")
            message = json.loads(record['body'])
            logger.info(f"Mensagem recebida: {message}")
            
            # Extrair dados da mensagem SQS
            transacao_id = message.get('transacao_id')
            comprador_id = message.get('comprador_id')
            veiculo_id = message.get('veiculo_id')
            
            # Verificar se os dados obrigatórios estão presentes
            if transacao_id and comprador_id and veiculo_id:
                logger.info(f"Dados recebidos para a transação {transacao_id}: comprador_id={comprador_id}, veiculo_id={veiculo_id}")
                
                # Gera o documento PDF
                logger.info(f"Gerando documento PDF para a transação {transacao_id}")
                pdf_content = gerar_documento_pdf(transacao_id, comprador_id, veiculo_id)
                
                # Salva o PDF no S3
                logger.info(f"Salvando documento PDF no S3: documentos/{transacao_id}.pdf")
                salvar_no_s3(pdf_content, f"documentos/{transacao_id}.pdf", 'application/pdf')
                
                # Gera um documento de texto (opcional)
                logger.info(f"Gerando documento TXT para a transação {transacao_id}")
                txt_content = gerar_documento_txt(transacao_id, comprador_id, veiculo_id)
                
                # Salva o documento TXT no S3
                logger.info(f"Salvando documento TXT no S3: documentos/{transacao_id}.txt")
                salvar_no_s3(txt_content.encode('utf-8'), f"documentos/{transacao_id}.txt", 'text/plain')

                logger.info(f"Documentos gerados e salvos no S3 para a transação {transacao_id}.")
            else:
                logger.warning("Dados incompletos na mensagem SQS.")
    else:
        logger.warning("Nenhum registro encontrado no evento.")

def gerar_documento_pdf(transacao_id, comprador_id, veiculo_id):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Adicionar o nome da loja e o título do documento
    store_name = "Select Gear Motors"
    transaction_title = "Documento de Transação da Compra"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
     # Definir a fonte para o título (16, negrito) e posicionar no centro da página
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(300, 750, transaction_title)
    
    # Definir a fonte para o nome da loja (14, normal) com espaçamento de um parágrafo
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(300, 730, store_name)
    
    # Adicionar um espaçamento de parágrafo fictício
    text_ficticio = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    pdf.drawString(100, 700, text_ficticio)
    
    # Adicionar um parágrafo em branco (mais espaço antes da próxima linha)
    pdf.drawString(100, 670, "")  # Linha em branco
    
    # Dados da transação com espaçamento
    pdf.setFont("Helvetica", 12)
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.drawString(100, 650, f"Data de geração: {current_date}")
    pdf.drawString(100, 630, f"Transação ID: {transacao_id}")
    pdf.drawString(100, 610, f"Comprador ID: {comprador_id}")
    pdf.drawString(100, 590, f"Veículo ID: {veiculo_id}")
    
    pdf.showPage()
    pdf.save()
    
    buffer.seek(0)
    return buffer.getvalue()

def gerar_documento_txt(transacao_id, comprador_id, veiculo_id):
    documento = StringIO()
    
    # Adicionar o nome da loja e o título do documento no arquivo TXT
    store_name = "Select Gear Motors"
    transaction_title = "Documento de Transação da Compra"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Criar o conteúdo do arquivo TXT
    documento.write(f"{transaction_title:^80}\n")
    documento.write(f"{store_name:^80}\n\n")
    documento.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n\n")
    documento.write("\n")  # Adicionar parágrafo em branco
    documento.write(f"Data de geração: {current_date}\n\n")
    documento.write(f"Transação ID: {transacao_id}\n")
    documento.write(f"Comprador ID: {comprador_id}\n")
    documento.write(f"Veículo ID: {veiculo_id}\n")
    
    return documento.getvalue()

def salvar_no_s3(conteudo, chave_arquivo, content_type):
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=chave_arquivo, Body=conteudo, ContentType=content_type)
        logger.info(f"Arquivo {chave_arquivo} salvo com sucesso no bucket {BUCKET_NAME}.")
    except Exception as e:
        logger.error(f"Erro ao salvar o arquivo {chave_arquivo} no bucket {BUCKET_NAME}: {str(e)}")
