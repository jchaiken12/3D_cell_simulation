import mcell as m

from unedited_cell_10_geometry import *
from collections import Counter

def duplicate_checker(my_counts, my_bool):

    val_dict = my_counts.most_common(1)
    val = list(val_dict.keys())[0]
    if (val_dict[val] > 0):
        print('duplicate occurred')
    else:
        print('duplicate not found')
    print()

    if (my_bool):
        print('Below we present the 3 most common xyz cords that exist')
    else:
        print('Below we present the 3 most common walls that exist')
    print(my_counts.most_common(3))
    print()

def check_duplicate_nodes():
    tuple_list = [tuple(sublist) for sublist in Cell_vertex_list]
    vertex_counts = Counter(tuple_list)

    duplicate_checker(vertex_counts, True)

def check_duplicate_walls():
    tuple_list = [tuple(sublist) for sublist in Cell_wall_list]
    wall_counts = Counter(tuple_list)

    duplicate_checker(wall_counts, False)

def main():
    check_duplicate_nodes()

if __name__=="__main__":
    main()
