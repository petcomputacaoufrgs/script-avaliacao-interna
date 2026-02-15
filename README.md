# Script para Avaliação Interna
#### Projeto: Atividade Internas
#### Linguagem utilizada: Python (versão 3.9.2)
##### Autor Original: [Vic](https://github.com/vickyad)
##### Atualizações por: [Eduardo F.](https://github.com/edufsi)


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
- Arquivo .txt com a lista de alunos -> é importante que os nomes dos alunos sejam exatamente iguais aos nomes colocados no Forms

> Formato do arquivo:
> ```txt
> nome do aluno 1
> nome do aluno 2
> ```

- Arquivo .txt com o email e senha de acesso da conta Google do remetente

> Formato do arquivo:
> ```csv
> [email do remetente] , [senha de acesso do remetente] 
> ```

***Observação:** Como o script usa os nomes para criar diretórios, é indicado que todos os nomes sejam escritos sem nenhum acento ou caracter especial. Apesar disso, um tratamento prévio é feito de qualquer forma*

### Configuração no gmail
O Google tende a não permitir realizar o login pelo `smtplib`, porque ele considera esse tipo de conexão menos segura. Para resolver isso, entre em https://www.google.com/settings/security/lesssecureapps (logado na conta do Google) e ative a opção *'Allow less secure apps'*

![image](https://cms-assets.tutsplus.com/uploads/users/1885/posts/29975/image/secure_apps.png)

### Contantes importantes
- `NUMBER_OF_IGNORED_QUESTIONS`: indica a quantidade de perguntas que não são processadas. As perguntas não processadas são as últimas <NUMBER_OF_IGNORED_QUESTIONS>;
- `RESULT_DIR_NAME`: indica o nome do diretório onde serão armazenados os gráficos e textos gerados
- `DATA_FOR_ALL_DIR_NAME`: indica o nome do diretório onde os gráficos e textos que serão enviados para todos serão armazenados
- `MAIL_SUBJECT`: indica o assunto que aparecerá no email enviado
- `MAIL_CONTENT`: indica o texto que aparecerá no corpo do email enviado
- `FREE_TEXT_QUESTION`: lista das perguntas de texto livre. É importante que o texto das perguntas aqui seja exatamente o texto das perguntas no formulário. Usado para definir quais perguntas vão gerar um arquivo de texto (todas as de texto livre) e quais vão gerar imagens (o restante) 

### Guia do Desenvolvedor (Arquitetura)
Se você vai mexer na lógica do código, aqui está como ele funciona "por baixo do capô".

#### Fluxo de Dados (csv_to_matrix)
O script não utiliza o DataFrame do Pandas diretamente para o processamento, ele converte os dados para uma matriz NumPy pura para facilitar a iteração por linhas/perguntas.

1. **Leitura:** Pandas lê o CSV (pd.read_csv).

2. **Conversão:** O DataFrame é convertido em um dicionário e depois em uma matriz.

3. **Estrutura Final:** A matriz resultante (final_matrix) tem o formato:
Uma lista de listas. Cada lista individual é uma pergunta onde:
- Elemento 0: A Pergunta (Label).
- Elemento 1 a N: As Respostas de cada pessoa.

>Ex: [["Pergunta 1", "Resposta de A", "Resposta de B"], ["Pergunta 2", "Resposta de A", "Resposta de B"]]

#### Roteamento de Arquivos (get_saving_directory e process_matrix)
O script decide onde salvar cada arquivo baseando-se no texto da pergunta:

- **Diretório do Tutor:** Se a string definida na constante TUTOR estiver na pergunta.
- **Diretório do Aluno:** O script usa Regex (r'\[(.+?)]') para procurar nomes entre colchetes na pergunta. Ex: "Como você avalia a participação do [Fulano]?". Se "Fulano" estiver na student_list, o arquivo vai para a pasta dele. Se a pergunta for exatamente um nome de aluno então as respostas também vão para a pasta do aluno num arquivo 'Avaliação_Individual.txt'
- **Diretório Geral:** Se não for nem tutor nem aluno específico, vai para a pasta definida na constante DATA_FOR_ALL_DIR_NAME.



## Melhorias a serem feitas
- Otimização no tempo de execução
- Legendas no eixo x menos quebradas
- Melhoria nos tratamentos de erros que aconteçam durante os processos de processamento dos dados e manipulação dos arquivos
