# seven-food-privacy-api
###

Nome, Endereço, numero telefone, informação de pagamento

sam init
sam build
sam deploy --guided

aws sqs send-message --queue-url https://sqs.us-east-1.amazonaws.com/147397866377/selectgearmotors-documents-queue --message-body "{\"transacao_id\": \"12345\", \"comprador_id\": \"67890\", \"veiculo_id\": \"ABC123\"}"

sam local invoke "DocumentGeneratorFunction" -e event.json
# selectgearmotors-documents-api
