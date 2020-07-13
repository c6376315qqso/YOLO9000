class tree:
    def __init__(self):
        self.father = []  # 某一节点的父节点
        self.leaf = []  # 某点是否是叶子(0,1)
        self.n = 0  # 树的节点总数
        self.child = []  # 某一节点的子节点的group号
        self.group_num = 0  # 每个节点的子节点们都是一个group
        self.group_size = []  # 某一group的大小
        self.group_offset = []  # 某一group的起点在节点中的下标
        self.id = []  # 某一节点的id

    def read_tree(self, tree_file_path):
        # 从9k.tree读入树
        prev_father = -1
        with open(tree_file_path, "r") as file:
            group_size = 0
            for line in file:
                id, fa = tuple(line.split(" "))
                fa = int(fa)
                group_size += 1
                self.father.append(fa)
                self.child.append(-1)
                self.id.append(id)
                if fa != prev_father:
                    group_size -= 1
                    self.group_offset.append(self.n - group_size)
                    self.group_size.append(group_size)
                    self.group_num += 1
                    group_size = 1
                    prev_father = fa
                if fa != -1:
                    self.child[fa] = self.group_num
                self.n += 1
        self.group_offset.append(self.n - group_size)
        self.group_size.append(group_size)
        self.group_num += 1

        for i in range(self.n):
            if self.child[i] == -1:
                self.leaf.append(1)
            else:
                self.leaf.append(0)

    def get_prob(self, cond_prob, index):
        #  获得某一个节点的绝对概率
        prob = 1
        while index >= 0:
            prob *= cond_prob[index]
            index = self.father[index]
        return prob

    def process_true_prob(self, cond_prob):
        #  将所有节点的条件概率变为绝对概率
        for i in range(self.n):
            if self.father[i] != -1:
                cond_prob[i] *= cond_prob[self.father[i]]

    def predict(self, true_prob, thresh):
        #  从上到下预测一个最大概率的物体下标
        group = 0
        prep = 0
        prei = -1
        while 1:
            base = self.group_offset[group]
            maxp = true_prob[base]
            maxi = base
            for i in range(self.group_size[group]):
                index = base + i
                if true_prob[index] > maxp:
                    maxp = true_prob[index]
                    maxi = index
            if maxp < thresh:
                return prei, prep
            if self.leaf[maxi]:
                return maxi, maxp
            prei, prep = maxi, maxp
            group = self.child[maxi]

    def show(self, index):
        print("节点个数:", self.n)
        print("组个数：", self.group_num)
        print("下标{}的id是：".format(index), self.id[index])
        print("下标{}的父节点是：".format(index), self.father[index])
        print("下标{}的子节点group是：".format(index), self.child[index])
        print("第二组的off_Set:", self.group_offset[1])
        print("第一组的size:", self.group_size[0])
        print("father的size:", len(self.father))


def test():
    t = tree()
    t.read_tree("9k.tree")
    t.show(5)
    import numpy as np
    box_class_prob = np.load(r"C:\Users\Jame Black\Desktop\YAD2K-master\box_class_prob_bird.jpg.npy")
    maxi, maxp = t.predict(box_class_prob, 0.1)
    print(maxi, maxp)
    a = np.array([[[1,2],[3,4]],
                  [[5,6],[7,8]]])

if __name__ == '__main__':
    test()
