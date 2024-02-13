from multiprocessing import Process

def bubble_sort(array):
    check = True
    while check == True:
      check = False
      for i in range(0, len(array)-1):
        if array[i] > array[i+1]:
          check = True
          temp = array[i]
          array[i] = array[i+1]
          array[i+1] = temp
    print("Array sorted: ", array)
    file = open('lmao.txt','w')
    file.write("Which goes first?\n")
    file.write("Chicken\n")
    file.close()
    
def bubble_sort2(array):
    check = True
    while check == True:
      check = False
      for i in range(0, len(array)-1):
        if array[i] > array[i+1]:
          check = True
          temp = array[i]
          array[i] = array[i+1]
          array[i+1] = temp
    print("Array sorted 2: ", array)
    file2 = open('lmao2.txt','w')
    file2.write("Which goes first?\n")
    file2.write("Dinosaur\n")
    file2.close()

if __name__ == '__main__':
    p = Process(target=bubble_sort, args=([1,9,4,5,2,6,8,4],))
    l = Process(target=bubble_sort2, args=([1,9,4,5,2,6,8,4],))
    p.start()
    l.start()
    p.join()
    l.join()