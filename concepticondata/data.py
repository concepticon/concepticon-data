# coding: utf8
from __future__ import unicode_literals


CL_TYPES = {
    "acquisition",
    "annotated",
    "areal",
    "basic",
    "documentation",
    "hihi",
    "historical",
    "lolo",
    "naming test",
    "proto-language",
    "questionnaire",
    "ranked",
    "sign language",
    "specific",
    "stable",
    "ultra-stable",
    "unstable",
}

SEMANTICFIELD = {
    "Agriculture and vegetation",
    "Animals",
    "Basic actions and technology",
    "Clothing and grooming",
    "Cognition",
    "Emotions and values",
    "Food and drink",
    "Kinship",
    "Law",
    "Miscellaneous function words",
    "Modern world",
    "Motion",
    "Possession",
    "Quantity",
    "Religion and belief",
    "Sense perception",
    "Social and political relations",
    "Spatial relations",
    "Speech and language",
    "The body",
    "The house",
    "The physical world",
    "Time",
    "Warfare and hunting",
}

ONTOLOGICAL_CATEGORY = {
    "Action/Process",
    "Person/Thing",
    "Classifier",
    "Property",
    "Other",
}

COLUMN_TYPES = {
    "SUBLIST" : "link",
    "URL" : "url",
    "PART_OF_SPEECH" : "string",
    "ENGLISH"    : "language",
    "SPANISH"    : "language",
    "FRENCH"     : "language",
    "GERMAN"     : "language",
    "RUSSIAN"    : "language",
    "CHINESE"    : "language",
    "LATIN"      : "language",
    "BASQUE"     : "language",
    "ESPERANTO"  : "language",
    "SWEDISH"    : "language",
    "SIKUANI"    : "language",
    "PROTOWORLD" : "language",
    "DUTCH"      : "language",
    "TURKISH"    : "language",
    "HAUSA"      : "language",
    "JAPANESE"   : "language",
    "COMMON_CHINESE" : "language",
    "FREQUENCY" : "int or float",
    "RANK" : "int",
    "*SCORE" : "int or float"
}
