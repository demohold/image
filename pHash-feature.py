#encoding='utf-8'

from PIL import Image
from PIL import ImageFilter
from PIL import ImageOps
import math

"""
    缩小图片：32 * 32是一个较好的大小，这样方便DCT计算
    转化为灰度图：把缩放后的图片转化为256阶的灰度图。（具体算法见平均哈希算法步骤）
    计算DCT:DCT把图片分离成分率的集合
    缩小DCT：DCT计算后的矩阵是32 * 32，保留左上角的8 * 8，这些代表的图片的最低频率
    计算平均值：计算缩小DCT后的所有像素点的平均值。
    进一步减小DCT：大于平均值记录为1，反之记录为0.
    得到信息指纹：组合64个信息位，顺序随意保持一致性。
    最后比对两张图片的指纹，获得汉明距离即可
"""

def get_code(List, middle):
    result = []
    for index in range(0, len(List)):
        if List[index] > middle:
            result.append("1")
        else:
            result.append("0")
    return result

def comp_code(code1, code2):
    num = 0
    for index in range(0, len(code1)):
        if str(code1[index]) != str(code2[index]):
            num += 1
    return num

def get_middle(List):
    li = List.copy()
    li.sort()
    value = 0
    if len(li) % 2 == 0:
        index = int((len(li) / 2)) - 1

        value = li[index]
    else:
        index = int((len(li) / 2))
        value = (li[index] + li[index - 1]) / 2
    return value


def get_matrix(image):
    matrix = []
    size = image.size
    for height in range(0, size[1]):
        pixel = []
        for width in range(0, size[0]):
            pixel_value = image.getpixel((width, height))
            pixel.append(pixel_value)
        matrix.append(pixel)

    return matrix


def get_coefficient(n):
    matrix = []
    PI = math.pi
    sqr = math.sqrt(1 / n)
    value = []
    for i in range(0, n):
        value.append(sqr)
    matrix.append(value)

    for i in range(1, n):
        value = []
        for j in range(0, n):
            data = math.sqrt(2.0 / n) * math.cos(i * PI * (j + 0.5) / n);
            value.append(data)
        matrix.append(value)

    return matrix


def get_transposing(matrix):
    new_matrix = []

    for i in range(0, len(matrix)):
        value = []
        for j in range(0, len(matrix[i])):
            value.append(matrix[j][i])
        new_matrix.append(value)

    return new_matrix


def get_mult(matrix1, matrix2):
    new_matrix = []

    for i in range(0, len(matrix1)):
        value_list = []
        for j in range(0, len(matrix1)):
            t = 0.0
            for k in range(0, len(matrix1)):
                t += matrix1[i][k] * matrix2[k][j]
            value_list.append(t)
        new_matrix.append(value_list)

    return new_matrix


def DCT(double_matrix):
    n = len(double_matrix)
    A = get_coefficient(n)
    AT = get_transposing(A)

    temp = get_mult(double_matrix, A)
    DCT_matrix = get_mult(temp, AT)

    return DCT_matrix

def sub_matrix_to_list(DCT_matrix, part_size):
    w, h = part_size
    List = []
    for i in range(0, h):
        for j in range(0, w):
            List.append(DCT_matrix[i][j])
    return List

def classify_DCT(image1, image2, size=(32, 32), part_size=(8, 8)):

    assert size[0] == size[1], "size error"
    assert part_size[0] == part_size[1], "part_size error"

    image1 = image1.resize(size).convert('L').filter(ImageFilter.BLUR)
    image1 = ImageOps.equalize(image1)
    matrix = get_matrix(image1)
    DCT_matrix = DCT(matrix)
    List = sub_matrix_to_list(DCT_matrix, part_size)
    middle = get_middle(List)
    code1 = get_code(List, middle)

    image2 = image2.resize(size).convert('L').filter(ImageFilter.BLUR)
    image2 = ImageOps.equalize(image2)
    matrix = get_matrix(image2)
    DCT_matrix = DCT(matrix)
    List = sub_matrix_to_list(DCT_matrix, part_size)
    middle = get_middle(List)
    code2 = get_code(List, middle)

    return comp_code(code1, code2)


if __name__ == '__main__':

    import os
    import operator

    filename = os.listdir('/Users/apple/PycharmProjects/company-image/hash-feature/picture')
    print('filename:', filename)

    dict = {}
    image1 = Image.open('./text-image/' + filename[1])

    for i in range(1, 20):
        image2 = Image.open('./picture/' + filename[i])
        result = classify_DCT(image1, image2)
        dict[str(filename[i])] = result
    listname = sorted(dict.items(), key=operator.itemgetter(1))

    for i in range(len(listname)):
        print(listname[i][0])

