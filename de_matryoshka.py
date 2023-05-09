#!/usr/bin/env python3

import inkex

"""
Extension for InkScape 1.2

Extension de-nests groups (a group only containing one group), recursively, for selected groups/items.
Also removes empty groups.
Currently a better alternative is to use Extensions/Arrange/Deep Ungroup...

Author: Cyrille Médard de Chardon
Mail: cyrille.mdc@gmail.com
Date: 2022-04-17
Last change: 2022-04-18
License: GNU GPL v3
"""

def get_attributes(self):
    for att in dir(self):
        try:
            inkex.errormsg((att, getattr(self, att)))
        except:
            None

class DeMatryoshka(inkex.EffectExtension):
     
    def effect(self):
        # For each selected element
        for elem in self.svg.selection:
            self.processGroup(elem)

    def processGroup(self, elem):
        # process only group elements
        if hasattr(elem, 'groupmode') and elem.groupmode == 'group':
            parent = elem.getparent()

            # get the farthest nested group that contains
            # something else than a single group and return a copy
            new_group = self.dematryoshka(elem)
            if new_group == False:
                # it's a dead branch - no content
                return

            parent.add(new_group)

            # delete the nested groups between parent and leaf group
            parent.remove(elem)

            # now drill down, work your way farther down into other subgroups
            for elem in new_group:
                # recursive
                self.processGroup(elem)

    def dematryoshka(self, elem, attribs=None):
        # for group elements
        if hasattr(elem, 'groupmode') and elem.groupmode == 'group':

            # remove empty group
            if len(elem) == 0:
                elem.getparent().remove(elem)
                return False

            # if I'm a group and contain only one group
            if len(elem) == 1:
                # recursive - keep digging until we find the  group that contains data
                single_child = elem[0]

                # need to pass group attributes to the lower nested group (child)
                for attrib in elem.attrib:
                    inkex.utils.debug(attrib)
                    if attrib == "transform":
                        # To do - need to do transfer of attributes
                        get_attributes(elem)
                        get_attributes(single_child)

                # pass first child and group attributes to apply to next child
                result = self.dematryoshka(single_child)

                if result == False:
                    # this must be an empty group now - delete it
                    elem.getparent().remove(elem)
                return result

        # for all non-group elements or groups with two or more children
        # return this 'content' group to replace the original root group
        return elem.copy()
            
if __name__ == '__main__':
    DeMatryoshka().run()
