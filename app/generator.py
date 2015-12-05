# -*- coding: utf-8 -*-

#from __future__ import unicode_literals
from ds import DataStorage

import os
import shutil
import subprocess
import urllib
import imghdr
from string import Template
import pprint

from urllib import FancyURLopener
class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'


class States():
    WAITING = "Waiting..."
    LOADING_REC = "Loading recipes from storage"
    LOADING_TEMP = "Loading templates"
    TEMPLATING = "Templating "
    GENERATING = "Running generation"
    DONE = "Done"
    PAGES_PREP = "Preparing page %d (country: %s)"

symbol_mapping = {
    u"°": u"$^\circ$",
    u"¼": u"1/4",
    u"⁄": u"/",
    u"½": u"1/2",
    u"¾": u"3/4",
    u"–": u"-",
    u"—": u"-",
    u"×": u"$\\times$",
    u"’": u"'",
    u"‘": u"'",
    u"“": u"\"",
    u"”": u"\"",
    u"&": u"\&"

}


class Generator(object):
    output_file = "tex/final.pdf"
    gen_cmd = "pdflatex"
    template_page = "tex/page.tex"
    template_main = "tex/main.tex"
    state = States.WAITING
    def __init__(self):
        self.ds = DataStorage()
        self.pages = []

    def bckp_current(self):
        if os.path.exists(self.output_file):
            shutil.copyfile(self.output_file, "%s.bckp" % self.output_file)

    def generate(self, book_uuid):
        self.state = States.WAITING
        self.bckp_current()
        self.state = States.LOADING_REC
        countries_content = self.ds.get_countries_content(book_uuid)
        self.pages = self.prep_pages(countries_content)
#        with open("tex/blah.tex", "w") as fp:
#            p = "\n\\newpage\n".join(self.pages)
#            fp.write(p)

        self.state = States.TEMPLATING
        book = self.template_book({u"PAGE": "\n\\newpage\n".join(self.pages)})
        with open("tex/final.tex", "w") as fp:
            fp.write(book)

        self.state = States.GENERATING
        self.call_cmd("tex/final.tex")
        self.state = States.DONE

    def compress(self, path):
        resize=500
        quality=30
        cmd = ["convert", path,  "-units", "PixelsPerInch", "-density", "300", "-resize", str(resize), "-quality", str(quality), path]
        self.call_cmd(None, cmd)

    def call_cmd(self, path, cmd=None):
        if not cmd:
            cmd = [self.gen_cmd, "-output-directory=tex/", "-halt-on-error", "-interaction=nonstopmode",  path]
        print("Calling %s" % " ".join(cmd))
        subprocess.call(cmd)

    def template_book(self, data):
        with open(self.template_main, "r") as fp:
            template = fp.read()

        t = Template(template)

        result = t.substitute(data)
        return result

    def template_recipe(self, data):
        with open(self.template_page, "r") as fp:
            template = self.unicodize(fp.read())

        t = Template(template)
        result = t.substitute(data)
        return self.unicodize(result)

    def download_image(self, image_uri, image_name):
        if "." in image_uri[-4:]:
            image_name = "%s%s" % (image_name[0:-3], image_uri[-3:])

        dest = "tex/images"
        if not os.path.isdir(dest):
            os.mkdir(dest)
        path = os.path.join("tex/images", image_name).replace(" ","-").lower()

        #urllib.urlretrieve(image_uri, path)
        myopener = MyOpener()
        myopener.retrieve(image_uri, path)
        #resource = urllib.urlopen(image_uri)
        #with open(path, "wb") as fp:
            #fp.write(resource.read())

        what = imghdr.what(path)
        if what == "jpeg":
            what = "jpg"
        elif what == None:
            what = "jpg"

        if what != path[-3:0]:
            new_path = "%s%s" % (path[0:-3], what)
            os.rename(path, new_path)
            path = new_path

        self.compress(path)
        return path

    def prep_pages(self, content):
        pages = []
        page_num = 1
        for country in content:
            data = {}
            data["country"] = country["country"]
            i = 0
            for recipe in country["recipes"]:
                #if page_num <75 or page_num > 85:
                #    page_num += 1
                #    continue
                    #break
                self.state = States.PAGES_PREP % (page_num, data["country"])
                print(self.state)


                data.update(recipe)
                data["image_uri"] = self.download_image(recipe["image"]["uri"], "%s%d.jpg" % (data["country"], i))
                data["image_source_uri"] = recipe["image"]["source_uri"]
                data["ingredients"] = self.prep_ingredients(recipe["ingredients"])
                data["directions"] = self.prep_directions(recipe["directions"])
                data["description"] = self.replace_symbols(recipe["description"])
                data["title"] = self.replace_symbols(recipe["title"])

                for k, v in data.iteritems():
                    data[k] = self.unicodize(v)

                page = self.template_recipe(data)
                pages.append(self.unicodize(page))
#                with open("tex/blah%s.tex" % page_num, "w") as fp:
#                    fp.write(page)
                i+=1
                page_num += 1
        return pages

    def unicodize(self, data):
        tmp = data
        try:
            if hasattr(data, 'decode'):
                tmp = str(data)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            tmp = str(data.encode('utf-8')) #data.decode("utf-8")

        return tmp

    def prep_ingredients(self, ingredients):
        result = []

        for ing in ingredients:
            title = False
            if ing.startswith("#"):
                ing = "\\textbf{%s}" % ing[1:]
                title = True

            ing = self.replace_symbols(ing)
            #print("%s %s" % (ing, type(ing)))

            if title and len(result)>0:
                result[-1] = result[-1][:-2]+"\n\n"
            result.append("%s %s%s" % ("$\\bullet$" if not title else "", ing, "\\\\*" if title else "\\\\"))


        return "\n".join(result)

    def prep_directions(self, directions):
        result = []
        dir_list = directions.split("\n")
        for direction in dir_list:
            if direction.startswith(u"§"):
                direction = direction[1:]

            direction = direction.strip()
            if len(direction) == 0:
                continue

            if direction[-1:] != ".":
                direction += "."
            if len(direction) > 0:
                direction = self.replace_symbols(direction)

            if direction.startswith("#"):
                dash = direction.find(" -")
                direction = u"\\textbf{%s}%s" % (direction[1:dash], direction[dash:])

            result.append(direction)

        return "\n\n".join(result)

    def replace_symbols(self, text):
        for frm, to in symbol_mapping.iteritems():
            text = text.replace(frm, to)

        return text
