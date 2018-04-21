def get_menu_style():
    style_str = "QWidget {\n" + \
                "    color: #eff0f1;\n" + \
    "    background-color: #31363b;\n" + \
    "    selection-background-color: #3daee9;\n" + \
    "    selection-color: #eff0f1;\n" + \
    "    background-clip: border;\n" + \
    "    border-image: none;\n" + \
    "    border: 0px transparent black;\n" + \
    "    outline: 0;\n" + \
    "}\n" + \
    "\n" + \
    "QWidget:item:hover {\n" + \
    "    background-color: #18465d;\n" + \
    "    color: #eff0f1;\n" + \
    "}\n" + \
    "\n" + \
    "QWidget:item:selected {\n" + \
    "    background-color: #18465d;\n" + \
    "}\n" + \
    "QMenuBar {\n" + \
    "    background-color: #31363b;\n" + \
    "    color: #eff0f1;\n" + \
    "}\n" + \
    "\n" + \
    "QWidget:disabled {\n" + \
    "    color: #454545;\n" + \
    "    background-color: #31363b;\n" + \
    "}\n" + \
    "QMenuBar::item {\n" + \
    "    background: transparent;\n" + \
    "}\n" + \
    "\n" + \
    "QMenuBar::item:selected {\n" + \
    "    background: transparent;\n" + \
    "    border: 1px solid #76797C;\n" + \
    "}\n" + \
    "\n" + \
    "QMenuBar::item:pressed {\n" + \
    "    border: 1px solid #76797C;\n" + \
    "    background-color: #3daee9;\n" + \
    "    color: #eff0f1;\n" + \
    "    margin-bottom: -1px;\n" + \
    "    padding-bottom: 1px;\n" + \
    "}\n" + \
    "\n" + \
    "QMenu {\n" + \
    "    border: 1px solid #76797C;\n" + \
    "    color: #eff0f1;\n" + \
    "    margin: 2px;\n" + \
    "}\n" + \
    "\n" + \
    "QMenu::icon {\n" + \
    "    margin: 5px;\n" + \
    "}\n" + \
    "\n" + \
    "QMenu::item {\n" + \
    "    background-color: #31363b;\n" + \
    "    padding: 5px 30px 5px 30px;\n" + \
    "    border: 1px solid transparent;\n" + \
    "    /* reserve space for selection border */\n" + \
    "}\n" + \
    "\n" + \
    "QMenu::item:selected {\n" + \
    "    color: #eff0f1;\n" + \
    "}\n" + \
    "QMenu::item:hover {\n" + \
    "    color: #eff0f1;\n" + \
    "}\n" + \
    "\n" + \
    "QMenu::separator {\n" + \
    "    height: 2px;\n" + \
    "    background: lightblue;\n" + \
    "    margin-left: 10px;\n" + \
    "    margin-right: 5px;\n" + \
    "}\n" + \
    "\n" + \
    "QMenu::indicator {\n" + \
    "    width: 18px;\n" + \
    "    height: 18px;\n" + \
    "}"
    return style_str