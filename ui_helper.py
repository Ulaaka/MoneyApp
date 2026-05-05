
class UserInterfaceHelper:
    """
    The color dictionary for user authentication phase of the app
    """
    color_dic = {
        "login_page": {
            "title_color" :"#32CD32",
            "background_color":"#12355B",
            "login_button_color":{
                "normal":"#32CD32",
                "focus":"#00FF7F"
            },
            "sign_up_button_color":{
                "normal":"#1877F2",
                "focus":"#18d5f2"
            }
        },

        "sign_up_page":{
            "title_color":"#1877F2",
            "background_color":"#12355B",
            "submit_button_color":{
                "normal":"#1877F2",
                "focus":"#18d5F2"
            }
        },
        "validation_page":{
            "title_color":"#1877F2",
            "background_color":"#12355B",
            "submit_button_color":{
                "normal":"#1877F2",
                "focus":"#18d5F2"
            }
        },
        'reset_password':{
            "title_color":"#1877F2",
            "background_color":"#12355B",
            "submit_button_color":{
                "normal":"#1877F2",
                "focus":"#18d5F2"
            }
        }}

    def handle_button_style(if_handle, button_color, hover_color, underline_flag=None):
        """
        Handles different styles of buttons in the user authentication phase of the app
        """

        handle_button_additional = """
            border-radius: 25px;
            padding: 15px;
        """

        if underline_flag:
            underline_button_additional = """
                text-decoration: underline;
                font-size: 15px;
            """
        else:
            underline_button_additional = """
                font-size: 15px;
            """

        if if_handle:
            add_text = handle_button_additional
            add_color = "background-color"
        else:
            add_text = underline_button_additional
            add_color = "color"

        line = f'''
            QPushButton {{
                background-color: {button_color};
                color: white;
                border: none;
                {add_text}
            }}
            QPushButton:hover {{
                {add_color}: {hover_color};
            }}
        '''
        return line
