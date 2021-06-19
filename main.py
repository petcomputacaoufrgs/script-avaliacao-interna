import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re


def organize_info(info):
    unique, counts = np.unique(info, return_counts=True)
    sorted_info = dict(zip(unique, counts))
    return sorted_info


def draw_graph(organized_data, graph_title, folder_name, img_name):
    # x-coordinates of left sides of bars
    left = [i for i in range(len(organized_data))]

    # heights of bars
    height = [organized_data.get(i) for i in organized_data]

    # labels for bars
    tick_label = [i for i in organized_data]

    # plotting a bar chart
    plt.bar(left, height, tick_label=tick_label, width=0.8, color=['red'])

    # plot title
    plt.title(graph_title)

    # adjusting x-axis labels
    plt.xticks(fontsize=9, rotation=45, ha='right', wrap=True)

    # adjusting graph layout to tight borders
    plt.tight_layout()

    # saving graph and clearing the figure for the next graph
    plt.savefig(f'resultados/{folder_name}/{img_name}.png', bbox_inches='tight')
    plt.clf()


def get_data_matrix(file_name):
    data_frame = pd.read_csv(file_name)
    data_object = data_frame.to_dict()
    data_label = np.array([*data_object]).transpose()
    data_object_array = data_object.values()
    data_values = []
    for obj in data_object_array:
        data_values.append([*obj.values()])
    final_matrix = np.c_[data_label, data_values]

    return final_matrix


def save_texts(text_array, folder_name, file_name):
    np.random.shuffle(text_array)
    f = open(f'resultados/{folder_name}/{file_name}.txt', "w")
    for i in range(len(text_array)):
        f.write(f'Avaliação {i + 1}\n')
        f.write(text_array[i])
        f.write('\n\n')
    f.close()


def check_extension(file_name):
    if len(file_name.split(".")) == 1:
        file_name += ".csv"

    return file_name


def create_directory(directory_name):
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)


if __name__ == '__main__':
    create_directory('resultados')

    tutor_name = input('Insira o nome do(a) tutor(a): ')
    create_directory(f'resultados/{tutor_name}')

    create_directory('resultados/Everybody')

    file_name = input('Insira o nome do arquivo: ')
    file_name = check_extension(file_name)

    data = get_data_matrix(file_name)
    dataRows = len(data)
    currentStudents = 10
    petianeList = []

    for i in range(1, (dataRows - 4)):
        print(f'\033[1;37mCategoria: {data[i][0]}')
        print('\033[0;33m\tProcessando...')
        petiane = re.findall(r'\[(.+?)\]', data[i][0])
        if petiane:
            # Perguntas do grid
            if petiane[0] not in petianeList:
                petianeList.append(*petiane)
                create_directory(f'resultados/{petiane[0]}')
            sorted_info = organize_info(data[i][1:])
            draw_graph(sorted_info, data[i][0], petiane[0], i)
        else:
            # Avaliação individual por texto
            if data[i][0] in petianeList:
                save_texts(data[i][1:], data[i][0], 'avaliacao_individual')
            # Avaliação do tutor
            elif 'tutor' in data[i][0]:
                if 172 <= i <= 174:
                    sorted_info = organize_info(data[i][1:])
                    draw_graph(sorted_info, data[i][0], 'Erika', i)
                else:
                    save_texts(data[i][1:], 'Erika', f'{i}')
            # Outras avaliações
            else:
                if 94 <= i <= 98 or i == 100 or i == 171:
                    save_texts(data[i][1:], 'Everybody', f'{i}')
                else:
                    sorted_info = organize_info(data[i][1:])
                    draw_graph(sorted_info, data[i][0], 'Everybody', i)
        print('\033[1;32m\tConcluído\n')
    print('\033[1;30;42mTudo feito e pasteurizado\033[m')
