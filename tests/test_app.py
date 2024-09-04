# -*- coding: utf-8 -*-

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from moto import mock_s3
import boto3
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from lambda_function import lambda_handler, gerar_documento_pdf, gerar_documento_txt, salvar_no_s3, BUCKET_NAME

# Criar mock do bucket S3
@mock_s3
class TestLambdaFunction(unittest.TestCase):

    def setUp(self):
        # Criar bucket S3 mockado
        self.s3 = boto3.client('s3')
        self.s3.create_bucket(Bucket=BUCKET_NAME)
        
        # Exemplo de evento SQS
        self.event = {
            "Records": [
                {
                    "body": json.dumps({
                        "transacao_id": "12345",
                        "comprador_id": "67890",
                        "veiculo_id": "ABC123"
                    })
                }
            ]
        }

    @patch('lambda_function.salvar_no_s3')
    def test_lambda_handler(self, mock_salvar_no_s3):
        # Testar se a função lambda_handler processa a mensagem corretamente
        lambda_handler(self.event, None)
        
        # Verificar se salvar_no_s3 foi chamado duas vezes (uma para o PDF e outra para o TXT)
        self.assertEqual(mock_salvar_no_s3.call_count, 2)
        
        # Verificar se a primeira chamada foi para o PDF
        args_pdf = mock_salvar_no_s3.call_args_list[0][0]
        self.assertTrue(args_pdf[1].endswith('.pdf'))
        
        # Verificar se a segunda chamada foi para o TXT
        args_txt = mock_salvar_no_s3.call_args_list[1][0]
        self.assertTrue(args_txt[1].endswith('.txt'))

    def test_gerar_documento_pdf(self):
        # Testar se o PDF é gerado corretamente
        pdf_content = gerar_documento_pdf("12345", "67890", "ABC123")
        self.assertIsNotNone(pdf_content)
        self.assertIsInstance(pdf_content, bytes)  # PDF deve ser bytes

    def test_gerar_documento_txt(self):
        # Testar se o TXT é gerado corretamente
        txt_content = gerar_documento_txt("12345", "67890", "ABC123")
        self.assertIsNotNone(txt_content)
        self.assertIn("Transação ID: 12345", txt_content)
        self.assertIn("Comprador ID: 67890", txt_content)

    @patch('lambda_function.s3.put_object')
    def test_salvar_no_s3(self, mock_put_object):
        # Testar se salvar_no_s3 chama boto3 corretamente
        salvar_no_s3(b"conteudo_teste", "documentos/teste.txt", 'text/plain')
        
        # Verificar se put_object foi chamado com os parâmetros corretos
        mock_put_object.assert_called_once_with(
            Bucket=BUCKET_NAME,
            Key="documentos/teste.txt",
            Body=b"conteudo_teste",
            ContentType='text/plain'
        )

if __name__ == '__main__':
    unittest.main()
