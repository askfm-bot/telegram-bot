class UserNamesExtractor:
    @staticmethod
    def get_fullname_and_username(chat):
        try:
            full_name = ' '.join([chat.first_name, chat.last_name])
        except:
            full_name = None

        try:
            username = chat.username
        except:
            username = None

        return full_name, username
