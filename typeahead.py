from prompt_toolkit.completion import Completer, Completion

class Typeahead(Completer):
    def __init__(self,hints):
        self.hints = hints

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor().lower()
        for hint in self.hints:
            if hint.startswith(word):
                yield Completion(hint, start_position = -len(word))