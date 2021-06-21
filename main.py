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

NUMBER_OF_SELF_EVALUATION_QUESTIONS = 3
MAX_FILE_AND_DIR_NAME_LEN = 30
RESULT_DIR_NAME = 'resultados'
DATA_FOR_ALL_DIR_NAME = 'everybody'
CATEGORY = '\033[1;37mCategoria\033[m'
PROCESSING_DATA = '\033[1;37;46mProcessando dados\033[m'
ZIPPING = '\033[1;37;46mZipando arquivos\033[m'
SENDING_MAILS = '\033[1;37;46mMandando emails\033[m'
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
    output_string = unidecode.unidecode(input_string[:30])
    output_string = output_string.replace(' ', '_')
    output_string = re.sub('[?.,/:()\[\]]', '', output_string)
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
    sns.barplot(x=x, y=y, palette='rocket')
    plt.title(graph_title, wrap=True)
    plt.xticks(rotation=35, ha='right', fontsize=6, wrap=True)
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
    file = open(f'{RESULT_DIR_NAME}/{folder_name}/{file_name}.txt', "w")
    file.write(f'{question}\n\n')
    for i in range(len(answer_array)):
        file.write(f'Avaliação {i + 1}\n{answer_array[i]}\n\n')
    file.close()


def csv_to_matrix(file_name: str) -> np.matrix:
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
    data_frame = pd.read_csv(file_name)
    data_frame_dict = data_frame.to_dict()
    data_frame_array = data_frame_dict.values()
    data_values_matrix = list(data_frame_array.values())
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
        return tutor_name, student_list
    elif question in student_list:
        return clean_string(question), student_list
    else:
        regex_search = re.findall(r'\[(.+?)]', question)
        if regex_search:
            student = clean_string(regex_search[0])
            if student not in student_list:
                student_list.append(student)
                create_directory(f'{RESULT_DIR_NAME}/{student}')
            return student, student_list
        else:
            return DATA_FOR_ALL_DIR_NAME, student_list


def zip_all_directories(directories_list: list):
    """ Zip all the directories listed in the list of directories
    :param directories_list: list with all the directories to be zipped
    :return: void
    """
    for directory in directories_list:
        shutil.make_archive(f'{RESULT_DIR_NAME}/{directory}', 'zip', f'{RESULT_DIR_NAME}/{directory}')


def is_free_text_question(question_number: int) -> bool:
    """ Verify if the current question is free text answer
    :param question_number: the column of the question in the csv file
    :return: boolean indicating if is a free text answer or not
    """
    if 94 <= question_number <= 98 or question_number == 100 or question_number == 171 or question_number >= 175:
        return True
    else:
        return False


def process_matrix(matrix: np.matrix, tutor_name: str) -> list:
    """ Process all the information, creating the files necessary in the right folders
    :param matrix: numpy matrix with all the data
    :param tutor_name: name of the tutor's directory (name of the tutor)
    :return: list with all students found in the evaluation
    """
    data_rows = len(matrix)
    student_list = []

    for i in range(1, (data_rows - NUMBER_OF_SELF_EVALUATION_QUESTIONS)):
        current_question = matrix[i][0]
        print(f'{CATEGORY}: {current_question}')
        print(PROCESSING)

        saving_directory, student_list = get_saving_directory(current_question, tutor_name, student_list)
        if current_question in student_list:
            save_answers_in_txt(matrix[i][1:], saving_directory)
        elif is_free_text_question(i):
            save_answers_in_txt(matrix[i][1:], saving_directory, current_question)
        else:
            answer_dict = list_to_occurrences_dict(matrix[i][1:])
            save_graph_to_img(answer_dict, current_question, saving_directory)
        print(DONE)

    return student_list


def get_attach_file(attach_file_name: str) -> MIMEBase:
    """ Get the file to be attached in the mail body
    :param attach_file_name: name of the file to be attached
    :return: a MIMEBase with the file encrypted
    """
    attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload(attach_file.read())
    encoders.encode_base64(payload)  # encode the attachment
    # add payload header with filename
    payload.add_header('Content-Disposition', 'attachment; filename="{}"'.format(Path(attach_file_name).name),
                       filename=attach_file_name)
    return payload


def create_message(receiver: str, receiver_mail: str, sender_mail: str) -> str:
    """ Create the mail message to be sent
    :param receiver: receiver name string
    :param receiver_mail: receiver mail string
    :param sender_mail: sender mail string
    :return: message encrypted to string
    """
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


def send_mail(receiver: str, receiver_mail: str, sender_information: list):
    """ Send the mail generated
    :param receiver: receiver name string
    :param receiver_mail: receiver mail string
    :param sender_information: list with the sender mail and password
    :return: void
    """
    text = create_message(receiver, receiver_mail, sender_information[0])

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_information[0], sender_information[1])  # login with mail_id and password
    session.sendmail(sender_information[0], receiver_mail, text)
    session.quit()

    print(f'Email enviado para {receiver_mail} com sucesso')


def get_mail_addresses() -> dict:
    """ Get the file containing the person's name and mails
    :return: dictionary with all person's mail to be sent
    """
    dictionary = dict()
    file_name = get_valid_file_name('Insira o nome do arquivo com a lista de emails (com ou sem extensão): ', '.txt')
    file = open(f'{file_name}.txt', 'r')
    for line in file:
        line = line.strip('\n')
        (key, val) = line.split(",")
        dictionary[key] = val
    return dictionary


def get_sender_info() -> list:
    """ Get sender mail and password
    :return: return the list with the sender information
    """
    file_name = get_valid_file_name('Insira o nome do arquivo com as informações do remetente (com ou sem extensão): ',
                                    '.txt')
    file = open(f'{file_name}.txt', 'r')
    content = file.read()
    mail, password = content.split(",")
    return [mail, password]


def manage_mails(directories_to_be_saved: list):
    """ Get all the mails needed and sent the zipped files to the correct address
    :param directories_to_be_saved: list with all directories existing
    :return: void
    """
    mail_addresses_list = get_mail_addresses()
    sender_info = get_sender_info()
    for person in mail_addresses_list:
        if person in directories_to_be_saved:
            print(PROCESSING)
            send_mail(person, mail_addresses_list[person], sender_info)
        else:
            print(f'Nenhum diretorio com o nome {person}')


def get_valid_tutor_name() -> str:
    """ Get a valid string that represent the tutor's name
    :return: string with a valid tutor's name
    """
    tutor_name = input('Insira o nome do(a) tutor(a): ')
    while len(tutor_name) > MAX_FILE_AND_DIR_NAME_LEN:
        tutor_name = input(f'O nome não deve ter mais do que {MAX_FILE_AND_DIR_NAME_LEN} caracteres. \nPor favor, '
                           f'tente novamente: ')
    tutor_name = clean_string(tutor_name)
    return tutor_name


def get_valid_file_name(message, extension) -> str:
    """ Get a valid file name (file name that exists in the computer)
    :param message: question soliciting the specific file needed
    :param extension: extension of the file
    :return: valid file name
    """
    found = False
    input_file = input(message)

    while not found:
        if not has_extension(input_file):
            input_file = add_extension(input_file, extension)
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
    csv_file = get_valid_file_name('Insira o nome do arquivo CSV com a avaliação interna(com ou sem a extesão): ', '.csv')

    # process all information
    print(PROCESSING_DATA)
    data_matrix = csv_to_matrix(csv_file)
    all_students = process_matrix(data_matrix, tutor)
    print(ALL_PROCESSED_N_FILED)

    # zip each directory
    directories = [DATA_FOR_ALL_DIR_NAME, tutor, all_students]
    print(ZIPPING)
    print(PROCESSING)
    zip_all_directories(directories)
    print(ALL_ZIPPED)

    # send all zipped files to mail
    print(SENDING_MAILS)
    manage_mails(directories)
    print(ALL_MAILS_SENT)
