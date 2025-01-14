from bisect import bisect_right


class GroupTreeNode(dict):
    '''Represents a group in a tree, used when rendering the tree.

    Is a dict, with links to child GroupTreeNodes, so that it is already
    'dictized' for output from the logic layer.
    '''

    def __init__(self, group_dict):
        dict.__init__(self)
        self.update(group_dict)
        self['children'] = []
        # self._children_titles has a 1:1 relationship with values in
        # self.['children'], and is used to help keep them sorted by title
        self._children_titles = []

    def add_child_node(self, child_node):
        '''Adds the child GroupTreeNode to this node, keeping the children
        in alphabetical order by title.
        '''
        title = child_node['title']
        insert_index = bisect_right(self._children_titles, title)
        self['children'].insert(insert_index, child_node)
        self._children_titles.insert(insert_index, title)
