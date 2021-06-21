# Script para Avaliação Interna
#### Projeto: Atividade Internas
#### Linguagem utilizada: Python (versão 3.9.2)
##### Autor: [Vic](https://github.com/vickyad)


## Descrição
Script feito para processar as respostas da avaliação interna do Forms do Google de forma a manter o processo anônimo.


## Bibliotecas utilizadas
#### Matplotlib
```
pip install matplotlib
```

#### Pandas
```
pip install pandas
```

#### Numpy
```
pip install numpy
```

#### Seaborn
```
pip install seaborn
```

#### Unicode
```
pip install unicode
```


## Como utilizar o script
Para utilizar o script, basta utilizar um ambiente onde o Python esteja configurado. Usando o PyCharm, é só criar um novo projeto e substituir o arquivo `main.py` do projeto gerado pelo `main.py` desse repositório. Depois, basta dar o run e seguir as instruções :D

### Inputs que serão solicitados
- Nome do(a) tutor(a) -> será gerado um diretório com o nome do tutor, então, preferencialmente, só ponha o primeiro nome
- Arquivo .csv gerado pelo forms -> não é preciso nenhum pré-processamento, apenas garanta que a extensão seja csv
- Arquivo .txt com a lista de alunos e seus emails -> é importante que os nomes dos alunos sejam exatamente iguais aos nomes colocados no Forms (apenas o primeiro nome)
> Formato do arquivo:
> ```csv
> [nome do aluno] , [email do aluno] 
> ```
- Arquivo .txt com o email e senha de acesso da conta Google do remetente
> Formato do arquivo:
> ```csv
> [email do remetente] , [senha de acesso do remetente] 
> ```

> ***Observação:** Como o script usa os nomes para criar diretórios, é indicado que todos os nomes sejam escritos sem nenhum acento ou caracter especial. Apesar disso, um tratamento prévio é feito de qualquer forma*

### Configuração no gmail
O Google tende a não permitir realizar o login pelo `smtplib`, porque ele considera esse tipo de conexão menos segura. Para resolver isso, entre em https://www.google.com/settings/security/lesssecureapps (logado na conta do Google) e ative a opção *'Allow less secure apps'*

![image](https://cms-assets.tutsplus.com/uploads/users/1885/posts/29975/image/secure_apps.png)

### Contantes importantes
- `NUMBER_OF_SELF_EVALUATION_QUESTIONS`: indica a quantidade de perguntas na autoavaliação; essas perguntas não são processadas
- `RESULT_DIR_NAME`: indica o nome do diretório onde serão armazenados os gráficos e textos gerados
- `DATA_FOR_ALL_DIR_NAME`: indica o nome do diretório onde os gráficos e textos que serão enviados para todos serão armazenados
- `MAIL_SUBJECT`: indica o assunto que aparecerá no email enviado
- `MAIL_CONTENT`: indica o texto que aparecerá no corpo do email enviado


## Melhorias a serem feitas
- Otimização no tempo de execução
- Legendas no eixo x menos quebradas
- Melhoria nos tratamentos de erros que aconteçam durante os processos de processamento dos dados e manipulação dos arquivos
