"""
.. module:: StuctureExtractor
    :synopsis:
"""

import document
import json
import string
from bs4 import BeautifulSoup

class StructureExtractor:
    def __init__(self, tokenizer, structure_file):
        """Create a new StructureExtractor.

        :param Tokenizer tokenizer: A tokenizer object
        :param str structure_file: Path to a JSON file that specifies the
        document structure.
        :return: a StructureExtractor instance
        :rtype: StructureExtractor
        """
        self.t = tokenizer
        self.structure_file = open(structure_file, "r")
        self.document_structure = json.load(self.structure_file)

    def extract(file):
        """Extract a list of Documents from a file. This method uses the
        structure_file given in the constructor for rules to identify documents.

        :param file file: The file to extract
        :return: A list of Document objects
        :rtype: list
        """
        
        documents = []
        
        #text = ""
        #with open(file.name, "r", -1) as f: # TODO: this seems a bit ridiculous
        #    for line in f:
        #        text += f.readline() + "\n"
        # TODO: was there a reason the original was written like that?

        with open(file.name, "r") as f:
            doc = BeautifulSoup(f, xml)

        units = self.extract_unit_information(self.document_structure, doc)

        for unit in units:
            d = document.Document(metadata = u.metadata,
                name = "document",
                sentences = u.sentences,
                title = u.name,
                units = u.units)
            documents.append(d)

        return documents
        

    def extract_unit_information(structure, parent_node):
        """Process the given node, according to the given structure, and return
        a list of Unit objects that represent the parent_node.
        
        :param dict structure: A JSON description of the structure
        :param Tag parent_node: A BeautifulSoup object of the parent node.
        :return: A list of Units
        :rtype: Unit
        """

        units = []
        
        unit_xpaths = structure["xpaths"]

        for i in range(0, len(unit_xpaths)):
            xpath = unit_xpaths[i]
            selector = self.make_css_selector(xpath, parent_node)
            nodes = BeautifulSoup()
            if len(selector) == 0:
                nodes.append(parent_node)
            else:
                #TODO: may not work with root nodes, should look into it
                nodes = parent_node.select(selector)
            struc_name = structure["structureName"]
            for node in nodes.children:
                try:
                    metadata_structure = structure["metdata"]
                except NameError:
                    metadata_structure = None

                unit_metadata = self.get_metadata(metadata_structure, node)
                sentences = [] # Sentence objects
                children = [] # Unit objects
                try:
                    #TODO: condense these try-catches
                    child_unit_structures = structure["units"]
                except NameError:
                    child_unit_structures = None

                if child_unit_structures != None:
                    for n in range(0, len(child_unit_structures)):
                        child_structure = child_unit_structures[n]
                        child_type = child_structure["structureName"]
                        if "sentence" in child_type:
                            child_units = self.extract_unit_information(
                                child_structure, node)
                            children.extend(child_units)
                        else:
                            sents = get_sentences(child_structure, node,
                                True)
                units.append(document.unit.Unit(metadata=unit_metadata,
                    units=children, sentences=sents, name=struc_name))
        return units

    #TODO: why does this require a node?
    def make_css_selector(xpath, node):
        """This function transforms xpaths from configuration xml files into
        css selectors for use with BeautifulSoup.
        
        :param string xpath: xpath string from 
        :param Tag node: A BeautifulSoup Tag for the node that requires a
        selector.
        :return: The css selector.
        :rtype: string
        """
        #TODO: condense this?
        if "text()" in xpath:
            xpath = string.replace(xpath, "text()", "")
        if "//" in xpath:
            xpath = string.replace(xpath, "//", " ")
        if "/" in xpath:
            xpath = string.replace(xpath, "//", " > "
        if "." in xpath:
            xpath = string.replace(xpath, ".", " :root")
            
        xpath = xpath.strip()

        if xpath[-1] == ">":
            xpath = xpath[:-1]
        if xpath[0] == ">":
            xpath = xpath[1:]

        return xpath
        

    def get_sentences(structure, parent_node, tokenize):
        """

        :param dict structure: A JSON description of the structure
        :param Tag node: ?
        :param boolean tokenize:
        :return: A list of sentences.
        :rtype: list
        """

        pass

    def get_metadata(metadata_structure, node):
        """

        :param list structure: A JSON description of the structure
        :param Tag node: ?
        :return: A list of metadata
        :rtype: list
        """

        pass

    def get_xpath_attribute(xpath_pattern, attribute, node):
        """

        :param string xpath_pattern:
        :param string attribute:
        :param Tag node:
        :return: A list of strings
        :rtype: list
        """

        pass

    def get_xpath_text(xpath_pattern, node):
        """

        :param string xpath_pattern:
        :param Tag node:
        :return: A list of strings
        :rtype: list
        """
        
        pass