# seven-food-privacy-api
###

Nome, Endereço, numero telefone, informação de pagamento

sam init
sam build
sam deploy --guided

aws sqs send-message --queue-url https://sqs.us-east-1.amazonaws.com/147397866377/selectgearmotors-documents-queue --message-body "{\"transacao_id\": \"12345\", \"comprador_id\": \"67890\", \"veiculo_id\": \"ABC123\"}"

sam local invoke "DocumentGeneratorFunction" -e event.json
# selectgearmotors-documents-api

Como rodar testes: python -m unittest discover tests


python3 -m venv myenv
linux:
source myenv/bin/activate
Windows:
myenv\Scripts\activate

pip install Flask>=2.0,<3.0
pip install requests==2.25.1
pip install -r requirements.txt -t ./src
pip install -r requirements-test.txt
pip install -r requirements-test.txt

python3 -m unittest discover -s ./tests
