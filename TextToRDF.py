# -*- coding: UTF-8 -*-

from rdflib import Namespace, URIRef, Graph, Literal, XSD
from rdflib.namespace import RDF, FOAF
import re
import regex

owl = Namespace("http://www.w3.org/2002/07/owl#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
schema = Namespace("http://schema.org/")
schemax = Namespace("http://topbraid.org/schemax/")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
pr = Namespace("http://ldf.fi/schema/person_registry/")
norssit = Namespace("http://ldf.fi/norssit/")
places = Namespace("http://ldf.fi/places/")
hobby = Namespace("http://ldf.fi/hobbies/")
relatives = Namespace("http://ldf.fi/relatives/")

# TODO: expand list for future decades
relativelist = ["Veli", "Poika", "Veljet", "Tyttärenpojat", "Pojanpoika", "Pojat"]
rel_plural = ["Veljet", "Pojat", "Tyttärenpojat"]
rel_singular = ["Veli", "Poika", "Tyttärenpoika"]
months = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10, 'XI': 11, 'XII': 12}

g = Graph()

# 1800s: pages 59-103
# 1900s: 104-
page = 59
student = 1 # reading the students one at a time, starting from number 1
yearnr = 1887
entry = ""
while(page <= 645):
    #if(page == 645):
    #    print "Last page"
    filename = 'C:\Users\Laura\Documents\Norssin matrikkeli\OCR\img' + str(page).zfill(4) + '-access.jpg.txt'
    f = open(filename, 'r')
    for line in f:
        #if(student >= 972):
        #    print line
        # Run through regular expressions
        line = regex.regular_expressions(line)
        
        # Separate a single entry
        # Start by separating the entry number. Usually followed by a dot, but sometimes not.
        # Special case for unused numbers
        #print student == 2429
        if(student == 2429 or student == 4549):   
            separatedline = line.partition(".—")
        else:
            separatedline = line.partition(" ")
        entrynumber = separatedline[0].replace(".", "") # Note: entrynumber is a string now
        #if(student == 10209):
        #    print entrynumber
        if(entrynumber != str(student + 1) and (student < 10209 or (student == 10209 and not entrynumber.isspace()))):   # test for possibly moving on to the next student
            if(not entrynumber.isspace()):     # remove lines with only whitespace
                yearpagenr = line.replace(" ", "").replace("\n", "")
                if(yearpagenr == str(yearnr) or yearpagenr == str(page - 2)):  # ignore year and page lines
                    if(student == 212 and yearnr == 1888):   # special exception
                        entry = entry + line
                    else:
                        if(yearpagenr == str(yearnr)):
                            #print "Year: " + str(yearnr)
                            yearnr = yearnr + 1
                        #else:
                        #    print "Page: " + str(page)
                        #    print "Student: " + str(student)
                else:
                    entry = entry + line
        # Skip double entries for now (such as "814. = 729.")
        elif(". = " in entry):
            # Move on to the next student
            entry = line
            student = student + 1
        else:
            #print "Starting new entry: " + str(page) + " " + str(student)
            original = entry

            # create RDF from entry and start splitting the entry
            norssi = URIRef("http://ldf.fi/norssit/norssi_" + str(student))
            g.add( (URIRef(norssi), RDF.type , FOAF.Person) )
            g.add( (URIRef(norssi), pr.entryText , Literal(entry, lang='fi') ) )
            g.add( (URIRef(norssi), pr.pageNumber , Literal(page) ) )
            
            fileurl = filename.split("\\")
            imageurl = fileurl[len(fileurl)-1].replace(".txt", "")
            g.add( (URIRef(norssi), pr.pageImageURL , Literal(imageurl) ) )
            
            entry = entry.replace("\n"," ")
            # Sometimes the space is missing between name and birth place
            # (like "Kaarlo Emil.* Hki 9 XI 1878")
            entry = re.split('\. |\.\*', entry)
            
            # Separate name
            name = entry[1].partition(" ")
            surname = name[0].replace(",", "")
            # Sometimes there's also a previous surname
            if(name[2].startswith('(')):
                if(',' in name[2]):
                    name2 = re.split(', |,', name[2])
                    prevsurname = name2[0]
                else:
                    name2 = name[2].split(") ")
                    prevsurname = name2[0] + ")"
                surname = surname + " " + prevsurname
                givenname = name2[1]
            else:
                givenname = name[2]
            g.add( (URIRef(norssi), schema.givenName , Literal(givenname, lang='fi') ) )
            g.add( (URIRef(norssi), schema.familyName , Literal(surname, lang='fi') ) )
            
            # Separate birthplace and birthday
            # Remove common commas left by the image in OCR
            birth = entry[2].replace("*", "").replace(",", "").split()
            # For unknown reasons, year is sometimes separated with a period
            if(len(birth) > 0):
                if(len(birth) < 4):
                    birth.append(entry[3])
                    
                # Check there is actually a birthdate in there (it's missing from some entries)
                if birth[len(birth)-2] in months:       
                    year = birth[len(birth)-1]
                    month = "{0:0=2d}".format(months[birth[-2]])
                    day = regex.regular_expressions_number(birth[-3])
                    day = "{0:0=2d}".format(int(day))
                    birthday = year + "-" + month + "-" + day
                    
                    place = birth[len(birth)-4]
                    if(place == "Hki"): # Special case
                        place = "Helsinki"
                    placeURI = URIRef("http://ldf.fi/places/" + place)
                    # Debug version:
                    # placeURI = URIRef("http://ldf.fi/places/" + place + str(student))
                        
                    g.add( (URIRef(norssi), schema.birthDate , Literal(birthday, datatype=XSD.date) ) )
                    g.add( (URIRef(norssi), schema.birthPlace , placeURI) )
            
            # Enrollment year and matriculation year
            for e in entry:
                if ":lle" in e:
                    # print e
                    # Choose the correct century
                    y = "19"
                    if(yearnr < 1900):
                        y = "18"
                        
                    e2 = e.split(", ")
                    en = e2[0].strip().split()
                    en2 = y + en[len(en)-1]   # TODO: automatically choose 1800s/1900s
                    g.add( (URIRef(norssi), pr.enrollmentYear , Literal(en2, datatype=XSD.gYear) ) ) # ^^xsd:year

                    if len(e2) == 2 and len(e2[1]) > 0:
                        yo = e2[1].split()
                        
                        yo2 = y + yo[len(yo)-1]
                        g.add( (URIRef(norssi), pr.matriculationYear , Literal(yo2, datatype=XSD.gYear) ) ) # ^^xsd:year
                    
                if "Harr " in e:
                    hobbystring = re.sub('^%s' % "— ", "", e)
                    hobbies = hobbystring.split("Harr ")[1]
                    hobbylist = hobbies.split(", ")
                    for h in hobbylist:
                        h = h.replace(" ", "_").replace("-", "_").replace("ä", "a").replace("ö", "o")
                        # Remove mistakes caused by line breaks
                        h = h.replace("__", "")
                        #print h
                        hobbyURI = URIRef("http://ldf.fi/hobbies/" + h)
                        # Debug version: 
                        # hobbyURI = URIRef("http://ldf.fi/hobbies/" + h + str(student))
                        g.add( (URIRef(norssi), schema.hobby , hobbyURI) )
            
            # Last index contains a weird empty line
            # The death date is either second to last or third to last
            deathdate = entry[-2]
            if (not deathdate.startswith("— T") and not deathdate.startswith("- T")):
                deathdate = entry[-3]   # Try another option
            if (deathdate.startswith("— T") or deathdate.startswith("- T")):
                # To prevent problems with lines like "— TI X 1925"
                deathdate = deathdate.replace("— T", "").replace("- T", "")
                death = deathdate.split()  
                if (len(death) > 0):    # There are lines like "- T .", no idea why
                    year = death[-1]
                    # TODO: Currently only lists year for dates with no day
                    # Should be len(death) > 1 with some handling for dayless dates
                    if(len(death) > 2 and death[-2] in months):
                        month = regex.regular_expressions_month(death[-2])
                        month = "{0:0=2d}".format(months[month])
                        day = regex.regular_expressions_number(death[-3])
                        day = "{0:0=2d}".format(int(day))
                        deathday = year + "-" + month + "-" + day
                    else:
                        deathday = year
                            
                    g.add( (URIRef(norssi), schema.deathDate , Literal(deathday) ) )
                else:
                    g.add( (URIRef(norssi), pr.isDeceased , Literal(True ,datatype=XSD.boolean) ) )
        
            # Ignore last piece if it refers to the teacher record, "Ks opettajamatrikkeli" etc.
            rel_entry = entry[-2]
            if("opettaja" in rel_entry):
                rel_entry = entry[-3]
            relative = rel_entry.split()
            if(relative[0] in relativelist):
                #print relative[0]
                if(relative[0] in rel_plural):
                    rel_list = entry[-2].replace(relative[0], "")
                    rel_idx = rel_plural.index(relative[0])
                    rel_numbers = rel_list.split(", ")
                    for n in rel_numbers:
                        rel = rel_singular[rel_idx] + " " + n
                        g.add( (URIRef(norssi), pr.relatedNorssi , Literal(rel, lang='fi') ) )
                else:
                    g.add( (URIRef(norssi), pr.relatedNorssi , Literal(entry[-2], lang='fi') ) )
            
            # Move on to the next student
            #print "Next"
            entry = line
            # Special case: skip unused numbers
            if(student == 2429):
                student = 2450
                entry = ""
            if(student == 4549):
                student = 4560
                entry = ""
            if(student == 5017):
                student = 5020
                entry = ""
            else:
                student = student + 1
                if(page == 645 and student > 10209): # check for end
                    page = page + 1
                    break
        
    # Move to next page
    page = page + 1
    
# create prefixes
g.bind("owl", owl)
g.bind("rdf", rdf)
g.bind("rdfs", rdfs)
g.bind("schema", schema)
g.bind("schemax", schemax)
g.bind("xsd", xsd)
g.bind("person_registry", pr)
g.bind("norssit", norssit)
g.bind("places", places)
g.bind("hobbies", hobby)
g.bind("relatives", relatives)

g.serialize(destination='output.ttl', format='turtle')

# tee eri tiedosto person_registry-schemalle: "tämä on property" + label
# harrastuksista ja paikoista omat tiedostot, skriptissä pidä kirjaa löydetyistä ja lisää tiedostoon kun löytyy uusi
# sukulaisuussuhteista oma sanasto
# kokeile ladata Fusekiin