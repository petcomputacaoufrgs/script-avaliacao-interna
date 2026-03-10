from collections import defaultdict
import csv

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import unidecode
import shutil
import os
import re
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import warnings


warnings.filterwarnings("ignore", message="Ignoring specified arguments")

# # Define quantas colunas (contando do final para o começo) da tabela final serão ignoradas
# Aqui é só uma porque a última é a pergunta de ponto de compromisso, que só a tutora deve ver
NUMBER_OF_IGNORED_QUESTIONS = 1

MAX_FILE_AND_DIR_NAME_LEN = 60

RESULT_DIR_NAME = 'resultados'
DATA_FOR_ALL_DIR_NAME = 'everybody'
CATEGORY = '\033[1;37mCategoria\033[m'
ZIPPING = '\033[1;37mZipando arquivos\033[m'
SENDING_MAILS = '\033[1;37mMandando emails\033[m'
PROCESSING = '\033[0;33m\tProcessando...\033[m'
DONE = '\033[1;32m\tConcluído\033[m\n'
ALL_PROCESSED_N_FILED = '\033[1;30;42mDados processados e pasteurizados\033[m\n\n'
ALL_ZIPPED = '\033[1;30;42mPastas zippadas\033[m\n\n'
ALL_MAILS_SENT = '\033[1;30;42mEmails enviados\033[m\n\n'
TUTOR = 'tutor'
MAIL_CONTENT = '''Olá,
    Segue o resultado da avaliação interna. 
    Esse email foi mandado usando a biblioteca SMTP de Python, portanto seja bonzinhe com ele.
    Obrigada :D
    '''
MAIL_SUBJECT = 'Avaliação Interna - Resultados'

# Aqui vão todas as questões de texto livre. Elas precisam estar exatamente iguais às do formulário, mais especificamente ao resultado no arquivo .csv
# Se uma questão de texto livre não estiver nessa lista, o programa vai tentar criar um gráfico de barras com as respostas
FREE_TEXT_QUESTION = ['Email address',
                      'Email',
                      'O quão confortável você se sente para compartilhar suas ideias com o grupo?',
                      'O que o grupo está fazendo e deve manter?',
                      'O que o grupo está fazendo e deve parar de fazer?',
                      'O que o grupo não está fazendo e deveria começar a fazer?',
                      'Como você se sente no grupo (acolhido, respeitado, isolado...)',
                      'Voce acredita que o contato com os outros membros e os PET encontros estão ajudando na quarentena?',
                      'Quais suas impressões sobre a liderança neste período? O que vc viu de positivo? O que poderia ser melhor?',
                      'Sobre a atuação do(a) tutor(a) nesse último período, identifique: o que ele(a) deve começar a fazer (start)? O que ele(a) deve parar de fazer (stop)? O que ele(a) deve continuar a fazer (continue)?',
                      'Espaço aberto para seu feedback sobre a atuação do tutor(a). Valem aspectos técnicos, pessoais, de interação ou qualquer outro que vc considere relevante, sejam positivos ou negativos.',
                      'Como você avalia a sua participação no grupo neste último período?',
                      'O que ajudaria você a trabalhar com maior clareza e eficiência nos projetos em que atua?',
                      'Como eliminar o desperdício de tempo e nos mantermos engajados e focados?',
                      'Você tem observado desperdício de tempo na sua atuação? O que mais tem dificultado seu engajamento e foco?',
                      'Quais suas impressões gerais sobre a liderança neste período? O que vc viu de positivo? O que poderia ser melhor?',
                      'Um comportamento coletivo que precisamos ajustar',
                      'Um comportamento coletivo que devemos manter',
                      'UMA ação concreta que me comprometo a realizar no próximo bimestre:',
                      'UM comportamento que preciso melhorar:',
                      'Minha principal contribuição neste bimestre foi:',
                      "Cite UMA contribuição concreta desta pessoa neste bimestre", 
                      "Cite UM comportamento que pode ser aprimorado.", 
                      "Sugestão prática para o próximo bimestre."]


# Uma lista de perguntas para realizar a desambiguação em situações em que se tem colunas repetidas de alunos.
# Por exemplo, se tiver mais de uma seção com perguntas individuais para os alunos em que a pergunta é apenas o nome do aluno, o programa
# não sabe sobre as seções. Mas ele mantém a ordem, então a lógica aqui é a seguinte:
# Se tiver mais de uma questão que é apenas o nome de um aluno, o programa vai olhar para essa variável aqui e atribuirá 
# as respostas da i-ésima questão de nome de aluno para um arquivo com nome da i-ésima questão de desambiguação
# Por isso, é importante que a ordem das perguntas de desambiguação seja a mesma da ordem das seções de perguntas individuais para os alunos, 
# e que a quantidade de perguntas de desambiguação seja a mesma da quantidade de seções de perguntas individuais para os alunos com o mesmo nome
DESAMBIGUITY_QUESTIONS_FOR_STUDENTS = ["Cite UMA contribuição concreta desta pessoa neste bimestre", 
                                       "Cite UM comportamento que pode ser aprimorado.", 
                                       "Sugestão prática para o próximo bimestre."]


def list_to_occurrences_dict(answer_list: list) -> dict:
    """ Transform the list of answers in a dictionary with the occurrences of each answer
    Example: ['a', 'd', 'b', 'a', 'b', 'b', 'c'] -> {a: 2, b: 3, c: 1, d: 1}
    :param answer_list: list of answers
    :return: a dictionary with all the occurrences of each answer
    """
    unique, counts = np.unique(answer_list, return_counts=True)
    answer_dict = dict(zip(unique, counts))
    return answer_dict


def has_extension(raw_file_name: str) -> bool:
    """Check if the file name given has an extension
    :param raw_file_name: file's name
    :return: boolean indicating if the file has the extension or not
    """
    if len(raw_file_name.split(".")) == 1:
        return False
    return True


def add_extension(raw_file_name: str, file_extension: str) -> str:
    """Give the file extension to the file
    :param raw_file_name: file's name
    :param file_extension: extension of the file
    :return: file with the '.csv' extension
    """
    return raw_file_name + file_extension


def clean_string(input_string: str) -> str:
    """ Create a file name friendly string removing spaces and special characters
    :param input_string: string to be cleaned
    :return: cleaned string generated
    """
    output_string = unidecode.unidecode(input_string[:60]).strip()
    output_string = output_string.replace(' ', '_')
    output_string = re.sub(r'[?.,/:()\[\]]', '', output_string)
    return output_string


def save_graph_to_img(answer_dict: dict, graph_title: str, folder_name: str):
    """Create and save a graph based on the data given
    :param answer_dict: dictionary with the data
    :param graph_title: the title of the graph
    :param folder_name: name of the dir where the file will be saved
    :return: void
    """
    file_name = clean_string(graph_title)
    fig = plt.figure(num=0, figsize=(10, 8), dpi=300)
    sns.set_style('darkgrid')
    x = [*answer_dict]
    y = list(answer_dict.values())
    sns.set_color_codes('pastel')
    sns.barplot(x=x, y=y, palette='rocket', hue=x, legend=False)
    plt.title(graph_title, wrap=True)
    plt.xticks(rotation=35, ha='right', fontsize=6, wrap=True)

    counter = 1
    while(os.path.exists(f'{RESULT_DIR_NAME}/{folder_name}/{file_name}.png')):
        file_name = clean_string(graph_title) + f'_{counter}'
        counter += 1

    fig.savefig(f'{RESULT_DIR_NAME}/{folder_name}/{file_name}.png', pad_inches=4)
    fig.clf()


def save_answers_in_txt(answer_array: np.array_str, folder_name: str, question='Avaliação Individual'):
    """Save all the answers of a question in one '.txt' file
    :param question: the questions made
    :param answer_array: numpy array with all the answers to the question
    :param folder_name: name of the dir where the file will be saved
    :return: void
    """
    file_name = clean_string(question)
    
    np.random.shuffle(answer_array)  # randomize the answer's order to hamper identification

    counter = 1
    while(os.path.exists(f'{RESULT_DIR_NAME}/{folder_name}/{file_name}.txt')):
        file_name = clean_string(question) + f'_{counter}'
        counter += 1

    file = open(f'{RESULT_DIR_NAME}/{folder_name}/{file_name}.txt', "w", encoding='utf-8')
    file.write(f'{question}\n\n')
    for i in range(len(answer_array)):
        file.write(f'Avaliação {i + 1}\n{answer_array[i]}\n\n')
    file.close()


def csv_to_matrix(file_name: str, student_list: list) -> np.matrix:
    """Create a matrix with all the data given in the '.csv' file
            Input example: Label 1; Label 2; Label 3
                           Value 1; Value 2; Value 3
                           Value 4; Value 5; Value 6
        The conversion process is:
        1. The .csv read is converted to a data frame (data_frame),
        a type of pandas lib that is similar to a table
            Example:    Label 1     Label 2     Label 3
                     0  Value 1     Value 2     Value 3
                     1  Value 4     Value 5     Value 6
        2. The data frame is converted to a dictionary of dictionaries (data_frame_dict)
            Example: {'Label 1': {0: 'Value 1', 1: 'Value 4'},
                      'Label 2': {0: 'Value 2', 1: 'Value 5'},
                      'Label 3': {0: 'Value 3', 1: 'Value 6'}}
        3. The dictionary now is converted in an array of dictionaries
            Example: [{0: 'Value 1', 1: 'Value 4'},
                      {0: 'Value 2', 1: 'Value 5'}
                      {0: 'Value 3', 1: 'Value 6'}]
        Notice that we lost the labels of our outer dictionary, that correspond to our questions.
        For that reason, we use data_label_matrix to store the label an append to the final matrix later
        4. The dictionaries inside the array are converted to array too
            Example: [['Value 1', 'Value 4'],
                      ['Value 2', 'Value 5'],
                      ['Value 3', 'Value 6']]
        In this case, the lost labels are just the row count, so we don't need to store it
        5. Finally, we attach the questions (the labels stored in data_label_matrix) to each row
            Example: [['Label 1', 'Value 1', 'Value 4'],
                      ['Label 2', 'Value 2', 'Value 5'],
                      ['Label 3', 'Value 3', 'Value 6']]
        We use this complicated method to make sure that the answers of a question are in the row and
        simplify the later data process
    :param file_name: name of the '.csv' file
    :return: numpy matrix with all the data organized
    """
    data_frame = read_and_desambiguate_csv(file_name, student_list)

    print(data_frame.columns)
    data_frame_dict = data_frame.to_dict()

    print(data_frame_dict)
    data_frame_array = data_frame_dict.values()
    data_values_matrix = []
    for obj in data_frame_array:
        data_values_matrix.append([*obj.values()])
    data_label_matrix = np.array([*data_frame_dict]).transpose()
    final_matrix = np.c_[data_label_matrix, data_values_matrix]

    return final_matrix


def create_directory(directory_name: str):
    """Create a new directory, if it don't exist yet, with the given name
    :param directory_name: string with the directory name
    :return: void
    """
    directory_name = unidecode.unidecode(directory_name)
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)
        print(f'\033[2;34mPasta {directory_name} criada\033[m')


def get_saving_directory(question: str, tutor_name: str, student_list: list) -> [str, list]:
    """ Get the correct directory to save the current question + answers
    :param question: string that contains the current question
    :param tutor_name: name of the tutor
    :param student_list: list of the current students found
    :return: the name of the correct directory and the student list updated
    """
    if TUTOR in question:
        return tutor_name
    elif clean_string(question) in student_list:
        create_directory(f'{RESULT_DIR_NAME}/{clean_string(question)}')
        return clean_string(question)
    else:
        regex_search = re.findall(r'\[(.+?)]', question)
        if regex_search:
            student = clean_string(regex_search[0])
            if student in student_list:
                create_directory(f'{RESULT_DIR_NAME}/{student}')
                return student
        
        return DATA_FOR_ALL_DIR_NAME


def zip_all_directories(directories_list: list):
    """ Zip all the directories listed in the list of directories
    :param directories_list: list with all the directories to be zipped
    :return: void
    """
    for directory in directories_list:
        shutil.make_archive(f'{RESULT_DIR_NAME}/{directory}', 'zip', f'{RESULT_DIR_NAME}/{directory}')


def is_free_text_question(question: str) -> bool:
    """ Verify if the current question is free text answer
    :param question: string with the question
    :return: boolean indicating if is a free text answer or not
    """
    # O regex '\[.+?\]\s*' procura por colchetes, tudo o que tem dentro, 
    # e qualquer espaço em branco logo depois, substituindo por nada ('').
    raw_question = re.sub(r'\[.+?\]\s*', '', question).strip()
    
    if raw_question in FREE_TEXT_QUESTION:
        return True
    else:
        return False


def read_and_desambiguate_csv(caminho_arquivo: str, student_list: list) -> pd.DataFrame:
    """ Lê o CSV ajustando os nomes dos alunos para o formato '[Nome] Pergunta' """
    
    with open(caminho_arquivo, mode='r', encoding='utf-8') as f:
        leitor_csv = csv.reader(f)
        cabecalhos_originais = next(leitor_csv)
        
    contagem_aparicoes = defaultdict(int)
    cabecalhos_corrigidos = []

    # Varre o cabeçalho e aplica a regra dos colchetes: se o nome da coluna for o nome de um aluno, renomeia para "[Nome do Aluno] Pergunta de desambiguação"
    # Ex: "[João da Silva] Cite UMA contribuição concreta desta pessoa neste bimestre"
    for coluna in cabecalhos_originais:
        clean_coluna = clean_string(coluna)

        if clean_coluna in student_list:
            indice_pergunta = contagem_aparicoes[clean_coluna]
            
            novo_nome = f"[{clean_coluna}] {DESAMBIGUITY_QUESTIONS_FOR_STUDENTS[indice_pergunta]}"
            cabecalhos_corrigidos.append(novo_nome)
            
            # Incrementa para que a próxima vez que o nome aparecer, pegue a próxima pergunta da lista de desambiguação
            contagem_aparicoes[clean_coluna] += 1
        else:
            # Se não for nome de aluno (ex: Timestamp, Tutor, etc.), mantém igual
            cabecalhos_corrigidos.append(coluna)

    df = pd.read_csv(caminho_arquivo, header=0, names=cabecalhos_corrigidos, encoding='utf-8')
    
    return df

def process_matrix(matrix: np.matrix, tutor_name: str, student_list: list) -> list:
    """ Process all the information, creating the files necessary in the right folders
    :param matrix: numpy matrix with all the data
    :param tutor_name: name of the tutor's directory (name of the tutor)
    :return: list with all students found in the evaluation
    """
    data_rows = len(matrix)
    

    for i in range(1, (data_rows - NUMBER_OF_IGNORED_QUESTIONS)):
        current_question = matrix[i][0]
        print(f'{CATEGORY}: {current_question}')
        print(PROCESSING)

        saving_directory = get_saving_directory(current_question, tutor_name, student_list)
        if clean_string(current_question) in student_list:
            save_answers_in_txt(matrix[i][1:], saving_directory)
        elif is_free_text_question(current_question):
            save_answers_in_txt(matrix[i][1:], saving_directory, current_question)
        else:
            answer_dict = list_to_occurrences_dict(matrix[i][1:])
            save_graph_to_img(answer_dict, current_question, saving_directory)
        print(DONE)


def get_attach_file(attach_file_name):
    attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload(attach_file.read())
    encoders.encode_base64(payload)  # encode the attachment
    # add payload header with filename
    payload.add_header('Content-Disposition', 'attachment; filename="{}"'.format(Path(attach_file_name).name),
                       filename=attach_file_name)
    return payload


def create_message(receiver, receiver_mail, sender_mail):
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_mail
    message['To'] = receiver_mail
    message['Subject'] = MAIL_SUBJECT

    # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(MAIL_CONTENT, 'plain'))
    everybody_dir = get_attach_file(f'{RESULT_DIR_NAME}/{DATA_FOR_ALL_DIR_NAME}.zip')
    message.attach(everybody_dir)
    student_dir = get_attach_file(f'{RESULT_DIR_NAME}/{receiver}.zip')
    message.attach(student_dir)
    return message.as_string()


def send_mail(receiver, receiver_mail, sender_information):
    text = create_message(receiver, receiver_mail, sender_information[0])

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_information[0], sender_information[1])  # login with mail_id and password
    session.sendmail(sender_information[0], receiver_mail, text)
    session.quit()

    print(f'Email enviado para {receiver_mail} com sucesso')


def get_mail_addresses():
    dictionary = dict()
    file_name = input('Insira o nome do arquivo com a lista de emails: ')
    file = open(f'{file_name}.txt', 'r')
    for line in file:
        line = line.strip('\n')
        (key, val) = line.split(",")
        dictionary[key] = val
    return dictionary


def get_sender_info():
    file_name = input('Insira o nome do arquivo com as informações do remetente: ')
    file = open(f'{file_name}.txt', 'r')
    content = file.read()
    mail, password = content.split(",")
    return [mail, password]


def manage_mails(directories_to_be_saved):
    mail_addresses_list = get_mail_addresses()
    sender_info = get_sender_info()
    for person in mail_addresses_list:
        if person in directories_to_be_saved:
            print(PROCESSING)
            send_mail(person, mail_addresses_list[person], sender_info)
        else:
            print(f'Nenhum diretorio com o nome {person}')


def get_valid_tutor_name():
    tutor_name = input('Insira o nome do(a) tutor(a): ')
    while len(tutor_name) > MAX_FILE_AND_DIR_NAME_LEN:
        tutor_name = input(f'O nome não deve ter mais do que {MAX_FILE_AND_DIR_NAME_LEN} caracteres. \nPor favor, '
                           f'tente novamente: ')
    tutor_name = clean_string(tutor_name)
    return tutor_name


def get_valid_txt_file_name():
    found = False
    input_file = input('Insira o nome do arquivo TXT (com ou sem a extesão): ')

    while not found:
        if not has_extension(input_file):
            input_file = add_extension(input_file, '.txt')
        if os.path.exists(input_file):
            found = True
        else:
            input_file = input('Arquivo não encontrado. \nPor favor, tente novamente: ')
    return input_file


def read_students_file(members_file):
    members = []

    # encoding precisa aceitar caracteres padrão do português, como ´, ~, ç, etc, por isso o 'utf-8'
    file = open(members_file, 'r', encoding='utf-8')
    for line in file:
        line = line.strip('\n')
        members.append(clean_string(line))
    return members

def get_valid_csv_file_name():
    found = False
    input_file = input('Insira o nome do arquivo CSV (com ou sem a extesão): ')

    while not found:
        if not has_extension(input_file):
            input_file = add_extension(input_file, '.csv')
        if os.path.exists(input_file):
            found = True
        else:
            input_file = input('Arquivo não encontrado. \nPor favor, tente novamente: ')
    return input_file


if __name__ == '__main__':
    # create directories where the results will be stored and the 'for all' directory
    create_directory(RESULT_DIR_NAME)
    create_directory(f'{RESULT_DIR_NAME}/{DATA_FOR_ALL_DIR_NAME}')
    
    # set tutor's name and create a directory for them
    tutor = get_valid_tutor_name()
    create_directory(f'{RESULT_DIR_NAME}/{tutor}')

    # get '.csv' input file
    print("Arquivo CSV com os resultados da avaliação interna:")
    csv_file = get_valid_csv_file_name()
    
    print("Arquivo TXT com os nomes dos alunos (um por linha):")
    students_txt_file = get_valid_txt_file_name()

    # get students' names from the input '.txt' file
    students = read_students_file(students_txt_file)
    
    # process all information
    data_matrix = csv_to_matrix(csv_file, students)
    process_matrix(data_matrix, tutor, students)
    print(ALL_PROCESSED_N_FILED)

    # zip each directory
    directories = [DATA_FOR_ALL_DIR_NAME, tutor, *students]
    print(ZIPPING)
    print(PROCESSING)
    zip_all_directories(directories)
    print(ALL_ZIPPED)


    # send all zipped files to mail
   # print(SENDING_MAILS)
   # manage_mails(directories)
   # print(ALL_MAILS_SENT)

