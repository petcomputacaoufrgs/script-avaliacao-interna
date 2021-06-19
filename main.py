import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import re

# Constants
NUMBER_OF_SELF_EVALUATION_QUESTIONS = 4
RESULT_DIR_NAME = 'resultados'
DATA_FOR_ALL_DIR_NAME = 'everybody'
CATEGORY = '\033[1;37mCategoria'
PROCESSING = '\033[0;33m\tProcessando...'
DONE = '\033[1;32m\tConcluído\n'
ALL_DONE = '\033[1;30;42mTudo feito e pasteurizado\033[m'


def organize_info(info: list) -> dict:
    """ Transform the list of answers in a dictionary with the occurrences of each answer
    Example: ['a', 'd', 'b', 'a', 'b', 'b', 'c'] -> {a: 2, b: 3, c: 1, d: 1}
    :param info: list of answers
    :return: a dictionary with all the occurrences of each answer
    """
    unique, counts = np.unique(info, return_counts=True)
    dict_info = dict(zip(unique, counts))
    return dict_info


def save_graph(organized_data: dict, graph_title: str, folder_name: str, file_name: str):
    """Create and save a graph based on the data given
    :param organized_data: dictionary with the data
    :param graph_title: the title of the graph
    :param folder_name: name of the dir where the file will be saved
    :param file_name: name of the file to be saved
    :return: void
    """
    left = [i for i in range(len(organized_data))]  # x-coordinates of the left side of each bar
    height = [organized_data.get(i) for i in organized_data]    # height of each bar
    tick_label = [i for i in organized_data]    # label of each bar

    plt.bar(left, height, tick_label=tick_label, width=0.8, color='#98ffa9')  # plot bar graph
    plt.title(graph_title)  #graph title
    plt.xticks(fontsize=9, rotation=45, ha='right', wrap=True)  # adjusting x-axis labels
    plt.tight_layout()  # adjusting graph layout to tight borders

    # saving graph and clearing the figure for the next graph
    plt.savefig(f'{RESULT_DIR_NAME}/{folder_name}/{file_name}.png', bbox_inches='tight')
    plt.clf()


def get_data_matrix(file_name: str) -> np.matrix:
    """Create a matrix with all the data given in the '.csv' file
    :param file_name: name of the '.csv' file
    :return: numpy matrix with all the data organized
    """
    data_frame = pd.read_csv(file_name)
    data_object = data_frame.to_dict()
    data_label = np.array([*data_object]).transpose()
    data_object_array = data_object.values()
    data_values = []
    for obj in data_object_array:
        data_values.append([*obj.values()])
    final_matrix = np.c_[data_label, data_values]

    return final_matrix


def save_texts(text_array: np.array_str, folder_name: str, file_name: str):
    """Save all the answers of a question in one '.txt' file
    :param text_array: numpy array with all the answers to the question
    :param folder_name: name of the dir where the file will be saved
    :param file_name: name of the file to be saved
    :return: void
    """
    np.random.shuffle(text_array)   # randomize the answer's order to hamper identification
    file = open(f'{RESULT_DIR_NAME}/{folder_name}/{file_name}.txt', "w")
    for i in range(len(text_array)):
        file.write(f'Avaliação {i + 1}\n{text_array[i]}\n\n')
    file.close()


def check_extension(raw_file_name: str) -> str:
    """Check if the file name given has the '.csv' extension. If not, give the extension to the file
    :param raw_file_name: file's name
    :return: file name with guaranteed extension
    """
    if len(raw_file_name.split(".")) == 1:
        raw_file_name += ".csv"

    return raw_file_name


def create_directory(directory_name: str):
    """Create a new directory, if it don't exist yet, with the given name
    :param directory_name: string with the directory name
    :return: void
    """
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)


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
        student = re.findall(r'\[(.+?)\]', matrix[i][0])
        if student:
            # Perguntas do grid
            if student[0] not in student_list:
                student_list.append(*student)
                create_directory(f'{RESULT_DIR_NAME}/{student[0]}')
            sorted_info = organize_info(matrix[i][1:])
            save_graph(sorted_info, matrix[i][0], student[0], i)
        else:
            # Avaliação individual por texto
            if matrix[i][0] in student_list:
                save_texts(matrix[i][1:], matrix[i][0], 'avaliacao_individual')
            # Avaliação do tutor
            elif 'tutor' in matrix[i][0]:
                if 172 <= i <= 174:
                    sorted_info = organize_info(matrix[i][1:])
                    save_graph(sorted_info, matrix[i][0], tutor_name, i)
                else:
                    save_texts(matrix[i][1:], tutor_name, f'{i}')
            # Outras avaliações
            else:
                if 94 <= i <= 98 or i == 100 or i == 171:
                    save_texts(matrix[i][1:], DATA_FOR_ALL_DIR_NAME, f'{i}')
                else:
                    sorted_info = organize_info(matrix[i][1:])
                    save_graph(sorted_info, matrix[i][0], DATA_FOR_ALL_DIR_NAME, i)
        print(DONE)


if __name__ == '__main__':
    # Create directories where the results will be stored and the 'for all' directory
    create_directory(RESULT_DIR_NAME)
    create_directory(f'{RESULT_DIR_NAME}/{DATA_FOR_ALL_DIR_NAME}')

    # Set tutor's name and create a directory for them
    tutor = input('Insira o nome do(a) tutor(a): ')
    create_directory(f'{RESULT_DIR_NAME}/{tutor}')

    # Get '.csv' input file
    input_file = input('Insira o nome do arquivo: ')
    input_file = check_extension(input_file)

    # Process all information
    data_matrix = get_data_matrix(input_file)
    process_matrix(data_matrix, tutor)

    print(ALL_DONE)
