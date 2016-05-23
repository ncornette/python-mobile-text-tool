
Mobile Text Tools
=================

.. image:: https://travis-ci.org/ncornette/python-mobile-text-tool.svg?branch=master
   :target: https://travis-ci.org/ncornette/python-mobile-text-tool

.. image:: https://codecov.io/gh/ncornette/python-mobile-text-tool/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/ncornette/python-mobile-text-tool

.. image:: https://api.codacy.com/project/badge/Grade/a37555ff09aa4a09a51d7b3a34e810c2
   :target: https://www.codacy.com/app/nicolas-cornette/python-mobile-text-tool?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ncornette/python-mobile-text-tool&amp;utm_campaign=Badge_Grade

.. image:: https://img.shields.io/pypi/v/Mobile-Text-Tool.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/Mobile-Text-Tool

Mobile Text Tools is a set of tools to export translations to ``Android``
and ``IOS`` mobile applications. It provides a data model represented in
``json`` and can read and write different formats.

Features
--------

-  import .csv, .xls, .xlsx, .json
-  export .csv, .json, android resources, ios resoures
-  custom rows format import and export
-  string escape
-  token replacement: you must use the ``{}`` or ``{1}..{n}`` notation
   in source files

CLI
---

::

   $ update_wordings --help
   usage: update_wordings [-h] [-o [OUT_FILE [OUT_FILE ...]]]
                             [-a ANDROID_RES_DIR] [-i IOS_RES_DIR]
                             [--android-resname ANDROID_RESNAME]
                             [--ios-resname IOS_RESNAME] [-s] [-f FORMAT_CONFIG]
                             input_file
   
   Export wordings for Android & IOS.
   
   positional arguments:
     input_file            .csv, .xls, .xlsx, .json formats are supported.
   
   optional arguments:
     -h, --help            show this help message and exit
     -o [OUT_FILE [OUT_FILE ...]], --out-file [OUT_FILE [OUT_FILE ...]]
                           .json or .csv output file path (default: [])
     -a ANDROID_RES_DIR, --android_res_dir ANDROID_RES_DIR
                           resource directory for android strings (default: None)
     -i IOS_RES_DIR, --ios_res_dir IOS_RES_DIR
                           resource directory for ios strings (default: None)
     --android-resname ANDROID_RESNAME
                           filename for android resource (default: strings.xml)
     --ios-resname IOS_RESNAME
                           filename for ios resource (default: i18n.strings)
     -s, --split-files     Export sections as separate ios and android resource
                           files, comment key is used for naming new files
                           (default: False)
     -f FORMAT_CONFIG, --format-config FORMAT_CONFIG
                           excel and csv format specifications config file
                           (default: None)


Default csv and xls format specification configuration :

.. code:: json

   {
     "excel_sheet_reference": 0,
     "key_col": 0,
     "exportable_col": 1,
     "is_comment_col": 2,
     "comment_col": 3,
     "translations_start_col": 4,
     "exportable_value": null,
     "is_comment_value": null,
     "metadata_cols": {}
   }

- ``excel_sheet_reference``: is the worksheet number (int) or name (string) for excel import
- ``exportable_value``: is the value to match in ``exportable_col`` to tell if the value will be exported to Android or IOS, can be a string or a list of strings, ``null`` will match ``True`` for any non empty value in the column.
- ``is_comment_value``: same as ``exportable_value`` to tell if the line is a comment

Example csv or xls table with default format :

+-----------------+--------------+--------------+--------------+-----------+-----------+--------------+
| key             | exportable   | is_comment   | comment      | en        | fr        | de           |
+=================+==============+==============+==============+===========+===========+==============+
| Menu            | Yes          | Yes          |  Menu Screen |           |           |              |
+-----------------+--------------+--------------+--------------+-----------+-----------+--------------+
| menu.welcome    | Yes          |              |              | Welcome   | Bienvenue |  Willkommen  |
+-----------------+--------------+--------------+--------------+-----------+-----------+--------------+
| menu.contact    | Yes          |              |              | Contact   | Contact   |  Kontakt     |
+-----------------+--------------+--------------+--------------+-----------+-----------+--------------+
| Share           | Yes          | Yes          | Share Screen |           |           |              |
+-----------------+--------------+--------------+--------------+-----------+-----------+--------------+
| share.share     | Yes          |              |              | Share     | Partager  |  Teilen      |
+-----------------+--------------+--------------+--------------+-----------+-----------+--------------+


To generate translations for android and ios from ``.xlsx`` file :

::

    $ update_wordings my_wordings.xlsx -i out/ios -a out/android

To generate translations from json file for android with custom resource
filename :

::

    $ update_wordings my_wordings.json -a out/android --android-resname my_strings.xml


Python interface
----------------

.. code:: python

    import mobileStrings

Read :
~~~~~~

Function ``read_file(f)`` from module ``text_in`` supports ``.xls``,
``.xlsx``, ``.csv``, ``.json`` file formats.

.. code:: python

    languages, wordings = mobileStrings.text_in.read_file('./test_translations.json')
    print ', '.join(languages)


.. parsed-literal::

    en, fr, de, pt, it, es, nl, zh, ja, pl, pt_BR, ru, id, ko, ar, tr, th, sv


Read custom formats :
~~~~~~~~~~~~~~~~~~~~~

For formats represented as rows like ``.csv`` and ``.xls``, you can
specify columns numbers with ``FormatSpec``

.. code:: python

    specs = mobileStrings.text_in.FormatSpec(0, 1, 2, 3, 4, bool, bool, {}) # Default format_spec (all params are optional)
    
    languages, wordings = mobileStrings.text_in.read_file('./test_translations.csv', specs)
    print ', '.join(languages)


.. parsed-literal::

    en, fr, de, pt, it, es, nl, zh, ja, pl, pt_BR, ru, id, ko, ar, tr, th, sv


Query :
~~~~~~~

To search a wording by its key, you can convert the ``list`` of
``Wording`` to a ``dict``

.. code:: python

    # wordings is a list, create a dict to query
    d = dict((w.key,w) for w in wordings)
    print('# keys: ')
    print '\n'.join(d.keys())
    
    welcome_wording = d.get('menu.welcome')
    
    print('\n# ' +welcome_wording.comment+':')
    print welcome_wording.translations.get('fr')
    print welcome_wording.translations.get('de')


.. parsed-literal::

    # keys: 
    menu.home
    menu.contact
    menu.share
    menu.welcome
    menu.news
    menu.share.not.exported
    menu.infos
    comment.generated
    comment.section
    
    # Title on menu header:
    Bienvenue !
    Willkommen!


Write :
~~~~~~~

Writing is very simple : use a ``write_`` function from the ``text_out``
module. It supports ``Android``, ``IOS``, ``json``, ``csv`` output
formats.

For mobile applications :

.. code:: python

    mobileStrings.text_out.write_android_strings(languages, wordings, '~/dev/myAndProject/res')
    mobileStrings.text_out.write_ios_strings(languages, wordings, '~/dev/myIOSProject/res')

Csv example :

.. code:: python

    import cStringIO
    sf = cStringIO.StringIO()
    
    # Write csv in a file-like object, for the first 3 languages only
    mobileStrings.text_out.write_csv(languages[:3], wordings, sf)
    print sf.getvalue()
    sf.close()


.. parsed-literal::

    key,exportable,is_comment,comment,en,fr,de
    comment.generated,Yes,Yes,Generated by mobile dev tools - Do not modify,,,
    menu.welcome,Yes,,Title on menu header,Welcome!,Bienvenue !,Willkommen!
    menu.home,Yes,,Home item,Home,Accueil,Start
    menu.news,Yes,,News item,News,Actualités,News
    comment.section,Yes,Yes,This is a section,,,
    menu.contact,Yes,,Contact item,Contact,Contact,Kontakt
    menu.infos,Yes,,Information pages item,Info,Infos,Informationen
    menu.share.not.exported,,,Share application item - not exported,Share,Partager,Teilen
    menu.share,Yes,,Share application item,Share,Partager,Teilen
    menu.share,Yes,,Share application item,,Partager,Teilen
    

