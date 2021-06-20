import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import unidecode
import os
import re

# import shutil
# shutil.make_archive(output_filename, 'zip', dir_name)

# Constants
NUMBER_OF_SELF_EVALUATION_QUESTIONS = 3
RESULT_DIR_NAME = 'resultados'
DATA_FOR_ALL_DIR_NAME = 'everybody'
CATEGORY = '\033[1;37mCategoria'
PROCESSING = '\033[0;33m\tProcessando...'
DONE = '\033[1;32m\tConcluído\n'
ALL_DONE = '\033[1;30;42mTudo feito e pasteurizado\033[m'
TUTOR = 'tutor'


def list_to_occurrences_dict(answer_list: list) -> dict:
    """ Transform the list of answers in a dictionary with the occurrences of each answer
    Example: ['a', 'd', 'b', 'a', 'b', 'b', 'c'] -> {a: 2, b: 3, c: 1, d: 1}
    :param answer_list: list of answers
    :return: a dictionary with all the occurrences of each answer
    """
    unique, counts = np.unique(answer_list, return_counts=True)
    answer_dict = dict(zip(unique, counts))
    return answer_dict


def save_graph_to_img(answer_dict: dict, graph_title: str, folder_name: str):
    """Create and save a graph based on the data given
    :param answer_dict: dictionary with the data
    :param graph_title: the title of the graph
    :param folder_name: name of the dir where the file will be saved
    :return: void
    """
    file_name = generate_file_name(graph_title)
    left = [i for i in range(len(answer_dict))]  # x-coordinates of the left side of each bar
    height = [answer_dict.get(i) for i in answer_dict]  # height of each bar
    tick_label = [i for i in answer_dict]  # label of each bar

    plt.bar(left, height, tick_label=tick_label, width=0.8, color='#98ffa9')  # plot bar graph
    plt.title(graph_title)  # graph title
    plt.xticks(fontsize=9, rotation=45, ha='right', wrap=True)  # adjusting x-axis labels
    plt.tight_layout()  # adjusting graph layout to tight borders

    # saving graph and clearing the figure for the next graph
    plt.savefig(f'{RESULT_DIR_NAME}/{folder_name}/{file_name}.png', bbox_inches='tight')
    plt.clf()


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
    data_values_matrix = []
    for obj in data_frame_array:
        data_values_matrix.append([*obj.values()])
    data_label_matrix = np.array([*data_frame_dict]).transpose()
    final_matrix = np.c_[data_label_matrix, data_values_matrix]

    return final_matrix


def generate_file_name(question: str) -> str:
    """ Create a file name based on the question
    :param question: string containing the question
    :return: file name generated
    """
    file_name = unidecode.unidecode(question[:20])
    file_name = file_name.replace(' ', '_')
    file_name = re.sub('[?.,/:()]', '', file_name)
    return file_name


def save_answers_in_txt(answer_array: np.array_str, folder_name: str, question='Avaliação Individual'):
    """Save all the answers of a question in one '.txt' file
    :param question: the questions made
    :param answer_array: numpy array with all the answers to the question
    :param folder_name: name of the dir where the file will be saved
    :return: void
    """
    file_name = generate_file_name(question)
    np.random.shuffle(answer_array)  # randomize the answer's order to hamper identification
    file = open(f'{RESULT_DIR_NAME}/{folder_name}/{file_name}.txt', "w")
    file.write(f'{question}\n\n')
    for i in range(len(answer_array)):
        file.write(f'Avaliação {i + 1}\n{answer_array[i]}\n\n')
    file.close()


def has_extension(raw_file_name: str) -> bool:
    """Check if the file name given has an extension
    :param raw_file_name: file's name
    :return: boolean indicating if the file has the extension or not
    """
    if len(raw_file_name.split(".")) == 1:
        return False
    return True


def add_extension(raw_file_name: str) -> str:
    """Give the '.csv' extension to the file
    :param raw_file_name: file's name
    :return: file with the '.csv' extension
    """
    return raw_file_name + ".csv"


def create_directory(directory_name: str):
    """Create a new directory, if it don't exist yet, with the given name
    :param directory_name: string with the directory name
    :return: void
    """
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)
        print(f'\033[2;34mPasta {directory_name} criada\033[m')


def handle_tutor_question(tutor_name: str, question_number: int, question: str, answer_list: list):
    """ Verify if the tutor's question is multiple choice or free text answer and save it appropriately
    :param tutor_name: name of the tutor
    :param question_number: number of the question in the csv column
    :param question: string that contains the question
    :param answer_list: list with all the answers
    :return: void
    """
    if 172 <= question_number <= 174:
        answer_dict = list_to_occurrences_dict(answer_list)
        save_graph_to_img(answer_dict, question, tutor_name)
    else:
        save_answers_in_txt(answer_list, tutor_name, question)


def handle_student_multiple_choice_question(student_list: list, student_name: str, question: str, answer_list: list) -> list:
    """ Verify if the student's question is multiple choice or free text answer and save it appropriately
    :param student_list: list with all the current students found
    :param student_name: name of the current student
    :param question: string that contains the question
    :param answer_list: list with all the answers
    :return: updated student's list
    """
    if student_name not in student_list:
        student_list.append(student_name)
        create_directory(f'{RESULT_DIR_NAME}/{student_name}')
    answer_dict = list_to_occurrences_dict(answer_list)
    save_graph_to_img(answer_dict, question, student_name)
    return student_list


def handle_for_all_questions(question_number: int, question: str, answer_list: list):
    """ Verify if the question is multiple choice or free text answer and save it appropriately
    :param question_number: number of the question in the csv column
    :param question: string that contains the question
    :param answer_list: list with all the answers
    :return: void
    """
    if 94 <= question_number <= 98 or question_number == 100 or question_number == 171:
        save_answers_in_txt(answer_list, DATA_FOR_ALL_DIR_NAME, question)
    else:
        sorted_info = list_to_occurrences_dict(answer_list)
        save_graph_to_img(sorted_info, question, DATA_FOR_ALL_DIR_NAME)


def process_matrix(matrix: np.matrix, tutor_name: str):
    """ Process all the information, creating the files necessary in the right folders
    :param matrix: numpy matrix with all the data
    :param tutor_name: name of the tutor's directory (name of the tutor)
    :return: void
    """
    data_rows = len(matrix)
    student_list = []

    for i in range(1, (data_rows - NUMBER_OF_SELF_EVALUATION_QUESTIONS)):
        print(f'{CATEGORY}: {matrix[i][0]}')
        print(PROCESSING)

        current_question = matrix[i][0]
        # question for tutor
        if TUTOR in current_question:
            handle_tutor_question(tutor_name, i, current_question, matrix[i][1:])
        # individual feedback for a student
        elif current_question in student_list:
            save_answers_in_txt(matrix[i][1:], current_question)
        else:
            regex_search = re.findall(r'\[(.+?)]', current_question)
            # grid question of all students
            if regex_search:
                student_list = handle_student_multiple_choice_question(student_list, regex_search[0], current_question, matrix[i][1:])
            # collective feedback
            else:
                handle_for_all_questions(i, current_question, matrix[i][1:])
        print(DONE)


if __name__ == '__main__':
    # create directories where the results will be stored and the 'for all' directory
    create_directory(RESULT_DIR_NAME)
    create_directory(f'{RESULT_DIR_NAME}/{DATA_FOR_ALL_DIR_NAME}')

    # set tutor's name and create a directory for them
    tutor = input('Insira o nome do(a) tutor(a): ')
    create_directory(f'{RESULT_DIR_NAME}/{tutor}')

    # get '.csv' input file
    input_file = input('Insira o nome do arquivo CSV (com ou sem a extesão): ')
    if not has_extension(input_file):
        input_file = add_extension(input_file)

    # process all information
    data_matrix = csv_to_matrix(input_file)
    process_matrix(data_matrix, tutor)

    print(ALL_DONE)
